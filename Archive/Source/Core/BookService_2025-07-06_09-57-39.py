# File: BookService.py
# Path: Source/Core/BookService.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-06
# Last Modified: 2025-07-06  09:35AM
"""
Description: FIXED - Book Service for New Relational Schema
Updated to work with the new relational schema using category_id/subject_id and BLOB thumbnails.
"""

import logging
import subprocess
import platform
import os
from typing import List, Optional, Dict, Any
from pathlib import Path

from Source.Core.DatabaseManager import DatabaseManager


class BookService:
    """
    FIXED - Business logic service for book operations using new relational schema.
    Compatible with new database schema with category_id/subject_id and BLOB thumbnails.
    """
    
    def __init__(self, DatabaseManager: DatabaseManager):
        """
        Initialize book service with database connection.
        
        Args:
            DatabaseManager: Database connection manager
        """
        self.DatabaseManager = DatabaseManager
        self.Logger = logging.getLogger(__name__)
        
        # Cache for performance
        self._CategoryCache: Optional[List[str]] = None
        self._SubjectCache: Optional[List[str]] = None
        self._CategorySubjectCache: Optional[Dict[str, List[str]]] = None
        
        self.Logger.info("BookService initialized with new relational schema")
    
    def GetAllBooks(self) -> List[Dict[str, Any]]:
        """
        Get all books from database using new schema.
        
        Returns:
            List of all Book dictionaries
        """
        try:
            Books = self.DatabaseManager.GetBooks()
            self.Logger.debug(f"Retrieved {len(Books)} books using new schema")
            return Books
            
        except Exception as Error:
            self.Logger.error(f"Failed to get all books: {Error}")
            return []
    
    def SearchBooks(self, SearchTerm: str) -> List[Dict[str, Any]]:
        """
        Search books based on search term using new schema.
        
        Args:
            SearchTerm: Search term to look for
            
        Returns:
            List of matching Book dictionaries
        """
        try:
            Books = self.DatabaseManager.GetBooks(SearchTerm=SearchTerm)
            self.Logger.debug(f"Search for '{SearchTerm}' returned {len(Books)} books")
            return Books
            
        except Exception as Error:
            self.Logger.error(f"Failed to search books: {Error}")
            return []
    
    def GetBooksByFilters(self, Category: str = "", Subject: str = "") -> List[Dict[str, Any]]:
        """
        Get books filtered by category and/or subject using new schema.
        
        Args:
            Category: Category name to filter by
            Subject: Subject name to filter by
            
        Returns:
            List of filtered Book dictionaries
        """
        try:
            Books = self.DatabaseManager.GetBooks(Category=Category, Subject=Subject)
            self.Logger.debug(f"Filter Category='{Category}', Subject='{Subject}' returned {len(Books)} books")
            return Books
            
        except Exception as Error:
            self.Logger.error(f"Failed to filter books: {Error}")
            return []
    
    def GetCategories(self) -> List[str]:
        """
        Get all available categories using new schema.
        
        Returns:
            List of category names
        """
        try:
            if self._CategoryCache is None:
                self._CategoryCache = self.DatabaseManager.GetCategories()
            
            return self._CategoryCache.copy()
            
        except Exception as Error:
            self.Logger.error(f"Failed to get categories: {Error}")
            return []
    
    def GetSubjects(self, Category: str = "") -> List[str]:
        """
        Get subjects for a specific category using new schema.
        
        Args:
            Category: Category name to get subjects for
            
        Returns:
            List of subject names
        """
        try:
            Subjects = self.DatabaseManager.GetSubjects(Category)
            return Subjects
            
        except Exception as Error:
            self.Logger.error(f"Failed to get subjects: {Error}")
            return []
    
    def OpenBook(self, BookTitle: str) -> bool:
        """
        FIXED - Open a book PDF using system default application.
        
        Args:
            BookTitle: Title of book to open
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get book details using new schema
            Books = self.DatabaseManager.GetBooks(SearchTerm=BookTitle)
            
            if not Books:
                self.Logger.warning(f"Book not found: {BookTitle}")
                return False
            
            # Find exact match by title
            BookData = None
            for Book in Books:
                if Book.get('Title', '') == BookTitle:
                    BookData = Book
                    break
            
            if not BookData:
                # Use first result if no exact match
                BookData = Books[0]
            
            FilePath = BookData.get('FilePath', '')
            
            if not FilePath:
                self.Logger.warning(f"No file path for book: {BookTitle}")
                return False
            
            if not os.path.exists(FilePath):
                self.Logger.warning(f"File does not exist: {FilePath}")
                return False
            
            # Open PDF with system default application
            if platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', FilePath], check=True)
            elif platform.system() == 'Windows':  # Windows
                os.startfile(FilePath)
            else:  # Linux/Unix
                subprocess.run(['xdg-open', FilePath], check=True)
            
            # Update last opened timestamp
            self.DatabaseManager.UpdateLastOpened(BookTitle)
            
            self.Logger.info(f"Successfully opened book: {BookTitle}")
            return True
            
        except subprocess.CalledProcessError as Error:
            self.Logger.error(f"Failed to open book '{BookTitle}': {Error}")
            return False
        except Exception as Error:
            self.Logger.error(f"Error opening book '{BookTitle}': {Error}")
            return False
    
    def GetBookDetails(self, BookTitle: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific book.
        
        Args:
            BookTitle: Title of the book
            
        Returns:
            Book dictionary or None if not found
        """
        try:
            Books = self.DatabaseManager.GetBooks(SearchTerm=BookTitle)
            
            # Find exact match
            for Book in Books:
                if Book.get('Title', '') == BookTitle:
                    return Book
            
            # Return first match if no exact match
            return Books[0] if Books else None
            
        except Exception as Error:
            self.Logger.error(f"Failed to get book details: {Error}")
            return None
    
    def GetDatabaseStats(self) -> Dict[str, int]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with counts of categories, subjects, books
        """
        try:
            return self.DatabaseManager.GetDatabaseStats()
        except Exception as Error:
            self.Logger.error(f"Failed to get database stats: {Error}")
            return {'Categories': 0, 'Subjects': 0, 'Books': 0}
    
    def ClearCache(self):
        """Clear internal caches to force refresh from database."""
        self._CategoryCache = None
        self._SubjectCache = None
        self._CategorySubjectCache = None
        self.Logger.info("BookService caches cleared")