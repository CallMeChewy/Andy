# File: BookService.py
# Path: Source/Core/BookService.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  15:00PM
"""
Description: Anderson's Library Book Service
Business logic for book operations including filtering, opening, and management.
Separates book-related logic from UI components for better modularity.

Purpose: Provides high-level book operations and business rules while maintaining
separation between data access and user interface components.
"""

import os
import webbrowser
import logging
from typing import List, Optional, Dict, Any, Callable
from pathlib import Path

from .DatabaseManager import DatabaseManager
from ..Data.DatabaseModels import Book, Category, Subject


class BookService:
    """
    Handles all business logic related to book operations.
    Provides clean interface for book filtering, opening, and management.
    """
    
    def __init__(self, DatabaseManager: DatabaseManager):
        """
        Initialize book service with database manager.
        
        Args:
            DatabaseManager: Database manager instance for data access
        """
        self.Database = DatabaseManager
        self.Logger = logging.getLogger(__name__)
        
        # Cache for performance optimization
        self._CategoryCache: List[Category] = []
        self._AllBooksCache: List[Book] = []
        self._CacheValid = False
        
        # Current filter state
        self.CurrentCategory: Optional[str] = None
        self.CurrentSubject: Optional[str] = None
        self.CurrentSearchTerm: str = ""
        self.CurrentBooks: List[Book] = []
        
        # Event callbacks for UI updates
        self.OnBooksChanged: Optional[Callable[[List[Book]], None]] = None
        self.OnFilterChanged: Optional[Callable[[], None]] = None
        self.OnBookOpened: Optional[Callable[[Book], None]] = None
        
        self.Logger.info("BookService initialized successfully")
    
    # =================================================================
    # CACHE MANAGEMENT
    # =================================================================
    
    def RefreshCache(self) -> None:
        """Refresh internal caches with latest database data"""
        try:
            self._CategoryCache = self.Database.GetAllCategories()
            self._AllBooksCache = self.Database.GetAllBooks()
            self._CacheValid = True
            
            self.Logger.info(f"Cache refreshed: {len(self._CategoryCache)} categories, "
                           f"{len(self._AllBooksCache)} books")
                           
        except Exception as Error:
            self.Logger.error(f"Failed to refresh cache: {Error}")
            self._CacheValid = False
            raise
    
    def _EnsureCacheValid(self) -> None:
        """Ensure cache is valid, refresh if necessary"""
        if not self._CacheValid:
            self.RefreshCache()
    
    # =================================================================
    # CATEGORY OPERATIONS
    # =================================================================
    
    def GetAllCategories(self) -> List[Category]:
        """
        Get all available categories.
        
        Returns:
            List of Category objects sorted alphabetically
        """
        self._EnsureCacheValid()
        return self._CategoryCache.copy()
    
    def GetCategoryNames(self) -> List[str]:
        """
        Get list of category names for dropdown population.
        
        Returns:
            List of category name strings
        """
        Categories = self.GetAllCategories()
        return [Cat.CategoryName for Cat in Categories if Cat.CategoryName]
    
    def SetCurrentCategory(self, CategoryName: Optional[str]) -> None:
        """
        Set current category filter and clear dependent filters.
        
        Args:
            CategoryName: Category to filter by, None to clear filter
        """
        self.CurrentCategory = CategoryName
        self.CurrentSubject = None  # Clear subject when category changes
        self._UpdateCurrentBooks()
        
        # Notify UI of filter change
        if self.OnFilterChanged:
            self.OnFilterChanged()
    
    # =================================================================
    # SUBJECT OPERATIONS
    # =================================================================
    
    def GetSubjectsForCurrentCategory(self) -> List[Subject]:
        """
        Get subjects for currently selected category.
        
        Returns:
            List of Subject objects for current category
        """
        if not self.CurrentCategory:
            return []
        
        try:
            return self.Database.GetSubjectsByCategory(self.CurrentCategory)
        except Exception as Error:
            self.Logger.error(f"Failed to get subjects for category '{self.CurrentCategory}': {Error}")
            return []
    
    def GetSubjectNamesForCurrentCategory(self) -> List[str]:
        """
        Get subject names for current category for dropdown population.
        
        Returns:
            List of subject name strings
        """
        Subjects = self.GetSubjectsForCurrentCategory()
        return [Sub.SubjectName for Sub in Subjects if Sub.SubjectName]
    
    def SetCurrentSubject(self, SubjectName: Optional[str]) -> None:
        """
        Set current subject filter.
        
        Args:
            SubjectName: Subject to filter by, None to clear filter
        """
        self.CurrentSubject = SubjectName
        self._UpdateCurrentBooks()
        
        # Notify UI of filter change
        if self.OnFilterChanged:
            self.OnFilterChanged()
    
    # =================================================================
    # BOOK OPERATIONS
    # =================================================================
    
    def GetCurrentBooks(self) -> List[Book]:
        """
        Get books based on current filter state.
        
        Returns:
            List of Book objects matching current filters
        """
        return self.CurrentBooks.copy()
    
    def SearchBooks(self, SearchTerm: str) -> List[Book]:
        """
        Search books by title and update current filter state.
        
        Args:
            SearchTerm: Search text to match against book titles
            
        Returns:
            List of Book objects matching search criteria
        """
        self.CurrentSearchTerm = SearchTerm.strip()
        
        if len(self.CurrentSearchTerm) <= 1:
            # Clear search results for short terms
            self.CurrentBooks = []
        else:
            try:
                self.CurrentBooks = self.Database.SearchBooks(self.CurrentSearchTerm)
                self.Logger.info(f"Search for '{self.CurrentSearchTerm}' returned {len(self.CurrentBooks)} books")
            except Exception as Error:
                self.Logger.error(f"Search failed for term '{self.CurrentSearchTerm}': {Error}")
                self.CurrentBooks = []
        
        # Notify UI of book changes
        if self.OnBooksChanged:
            self.OnBooksChanged(self.CurrentBooks)
        
        return self.GetCurrentBooks()
    
    def ClearSearch(self) -> None:
        """Clear search term and return to filtered view"""
        self.CurrentSearchTerm = ""
        self._UpdateCurrentBooks()
    
    def OpenBook(self, BookTitle: str) -> bool:
        """
        Open book PDF in default application.
        
        Args:
            BookTitle: Title of book to open
            
        Returns:
            True if book was opened successfully, False otherwise
        """
        try:
            # Find book by title
            TargetBook = None
            for Book in self.CurrentBooks:
                if Book.Title == BookTitle:
                    TargetBook = Book
                    break
            
            if not TargetBook:
                self.Logger.warning(f"Book not found in current selection: '{BookTitle}'")
                return False
            
            # Construct file path
            PdfPath = TargetBook.GetFullPath()
            
            # Verify file exists
            if not os.path.exists(PdfPath):
                self.Logger.error(f"PDF file not found: {PdfPath}")
                return False
            
            # Open with default application
            webbrowser.open_new(PdfPath)
            
            # Notify UI of book opened
            if self.OnBookOpened:
                self.OnBookOpened(TargetBook)
            
            self.Logger.info(f"Successfully opened book: {BookTitle}")
            return True
            
        except Exception as Error:
            self.Logger.error(f"Failed to open book '{BookTitle}': {Error}")
            return False
    
    def GetBookByTitle(self, Title: str) -> Optional[Book]:
        """
        Get book object by title from current selection.
        
        Args:
            Title: Book title to search for
            
        Returns:
            Book object if found, None otherwise
        """
        for Book in self.CurrentBooks:
            if Book.Title == Title:
                return Book
        return None
    
    def ValidateBookFiles(self) -> Dict[str, Any]:
        """
        Validate that PDF files exist for all books in current selection.
        
        Returns:
            Dictionary with validation results and statistics
        """
        Results = {
            'TotalBooks': len(self.CurrentBooks),
            'ValidFiles': 0,
            'MissingFiles': 0,
            'MissingFilesList': []
        }
        
        for Book in self.CurrentBooks:
            FilePath = Book.GetFullPath()
            if os.path.exists(FilePath):
                Results['ValidFiles'] += 1
            else:
                Results['MissingFiles'] += 1
                Results['MissingFilesList'].append({
                    'Title': Book.Title,
                    'ExpectedPath': FilePath
                })
        
        self.Logger.info(f"File validation: {Results['ValidFiles']} valid, "
                        f"{Results['MissingFiles']} missing out of {Results['TotalBooks']} books")
        
        return Results
    
    # =================================================================
    # FILTER MANAGEMENT
    # =================================================================
    
    def _UpdateCurrentBooks(self) -> None:
        """Update current books based on active filters"""
        try:
            if self.CurrentSearchTerm:
                # Search mode - ignore other filters
                return  # Search results already set in SearchBooks()
            
            elif self.CurrentSubject:
                # Subject filter active
                self.CurrentBooks = self.Database.GetBooksBySubject(self.CurrentSubject)
                self.Logger.info(f"Subject filter '{self.CurrentSubject}' returned {len(self.CurrentBooks)} books")
            
            elif self.CurrentCategory:
                # Category filter active - get all subjects for category
                Subjects = self.GetSubjectsForCurrentCategory()
                self.CurrentBooks = []
                
                for Subject in Subjects:
                    SubjectBooks = self.Database.GetBooksBySubject(Subject.SubjectName)
                    self.CurrentBooks.extend(SubjectBooks)
                
                self.Logger.info(f"Category filter '{self.CurrentCategory}' returned {len(self.CurrentBooks)} books")
            
            else:
                # No filters active
                self.CurrentBooks = []
            
            # Notify UI of book changes
            if self.OnBooksChanged:
                self.OnBooksChanged(self.CurrentBooks)
                
        except Exception as Error:
            self.Logger.error(f"Failed to update current books: {Error}")
            self.CurrentBooks = []
    
    def ClearAllFilters(self) -> None:
        """Clear all active filters and return to initial state"""
        self.CurrentCategory = None
        self.CurrentSubject = None
        self.CurrentSearchTerm = ""
        self.CurrentBooks = []
        
        # Notify UI of changes
        if self.OnFilterChanged:
            self.OnFilterChanged()
        
        if self.OnBooksChanged:
            self.OnBooksChanged(self.CurrentBooks)
    
    def GetFilterState(self) -> Dict[str, Any]:
        """
        Get current filter state for UI synchronization.
        
        Returns:
            Dictionary with current filter values
        """
        return {
            'Category': self.CurrentCategory,
            'Subject': self.CurrentSubject,
            'SearchTerm': self.CurrentSearchTerm,
            'BookCount': len(self.CurrentBooks),
            'HasActiveFilters': bool(self.CurrentCategory or self.CurrentSubject or self.CurrentSearchTerm)
        }
    
    # =================================================================
    # STATISTICS AND REPORTING
    # =================================================================
    
    def GetLibraryStatistics(self) -> Dict[str, Any]:
        """
        Get comprehensive library statistics.
        
        Returns:
            Dictionary with various statistics about the library
        """
        self._EnsureCacheValid()
        
        Stats = {
            'TotalCategories': len(self._CategoryCache),
            'TotalBooks': len(self._AllBooksCache),
            'CurrentBookCount': len(self.CurrentBooks),
            'DatabaseStats': {}
        }
        
        try:
            # Get database-level statistics
            Stats['DatabaseStats'] = self.Database.GetDatabaseStats()
            
            # Calculate category distribution
            CategoryDistribution = {}
            for Book in self._AllBooksCache:
                CategoryName = Book.CategoryName or 'Uncategorized'
                CategoryDistribution[CategoryName] = CategoryDistribution.get(CategoryName, 0) + 1
            
            Stats['CategoryDistribution'] = CategoryDistribution
            Stats['LargestCategory'] = max(CategoryDistribution.items(), key=lambda x: x[1]) if CategoryDistribution else ('None', 0)
            
        except Exception as Error:
            self.Logger.error(f"Failed to calculate library statistics: {Error}")
        
        return Stats
    
    def GetBooksByCategory(self, CategoryName: str) -> List[Book]:
        """
        Get all books in a specific category regardless of current filters.
        
        Args:
            CategoryName: Category name to get books for
            
        Returns:
            List of Book objects in the specified category
        """
        try:
            # Get all subjects for category
            Subjects = self.Database.GetSubjectsByCategory(CategoryName)
            AllBooks = []
            
            for Subject in Subjects:
                SubjectBooks = self.Database.GetBooksBySubject(Subject.SubjectName)
                AllBooks.extend(SubjectBooks)
            
            return AllBooks
            
        except Exception as Error:
            self.Logger.error(f"Failed to get books for category '{CategoryName}': {Error}")
            return []
    
    # =================================================================
    # EVENT MANAGEMENT
    # =================================================================
    
    def SetEventHandlers(self, 
                        OnBooksChanged: Optional[Callable[[List[Book]], None]] = None,
                        OnFilterChanged: Optional[Callable[[], None]] = None,
                        OnBookOpened: Optional[Callable[[Book], None]] = None) -> None:
        """
        Set event handlers for UI communication.
        
        Args:
            OnBooksChanged: Called when book list changes
            OnFilterChanged: Called when filters change
            OnBookOpened: Called when a book is opened
        """
        if OnBooksChanged:
            self.OnBooksChanged = OnBooksChanged
        if OnFilterChanged:
            self.OnFilterChanged = OnFilterChanged
        if OnBookOpened:
            self.OnBookOpened = OnBookOpened
        
        self.Logger.info("Event handlers configured")
