# File: BookService.py
# Path: Source/Core/BookService.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04 06:30PM
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
from ..Data.DatabaseModels import Book, Category, Subject, SearchCriteria, SearchResult, LibraryStatistics


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
        
        self.Logger.info("BookService initialized successfully")
    
    def GetAllCategories(self) -> List[Category]:
        """
        Get all available categories.
        
        Returns:
            List of Category objects sorted alphabetically
        """
        return self.Database.GetAllCategories()

    def GetAuthors(self) -> List[str]:
        """
        Get all unique author names.

        Returns:
            List of author name strings.
        """
        # This will return an empty list if the author column doesn't exist,
        # which is handled in the DatabaseManager.
        return self.Database.GetAllAuthors()
    
    def SearchBooks(self, Criteria: SearchCriteria) -> SearchResult:
        """
        Search books based on the provided criteria.

        Args:
            Criteria: SearchCriteria object with all filter and sort options.

        Returns:
            SearchResult object with the list of books and search metadata.
        """
        try:
            # Pass complete search criteria to database manager
            Books = self.Database.SearchBooksWithCriteria(Criteria)
            return SearchResult(Books=Books, Success=True, SearchCriteria=Criteria)
        except Exception as e:
            self.Logger.error(f"Error searching books: {e}")
            return SearchResult(Success=False, ErrorMessage=str(e))

    def GetAllBooks(self) -> SearchResult:
        """
        Get all books from the library.

        Returns:
            SearchResult object with all books.
        """
        try:
            Books = self.Database.GetAllBooks()
            return SearchResult(Books=Books, Success=True)
        except Exception as e:
            self.Logger.error(f"Error getting all books: {e}")
            return SearchResult(Success=False, ErrorMessage=str(e))

    def GetLibraryStatistics(self) -> LibraryStatistics:
        """
        Get comprehensive library statistics.
        
        Returns:
            LibraryStatistics object with various statistics about the library
        """
        try:
            DbStats = self.Database.GetDatabaseStats()
            Authors = self.GetAuthors()
            return LibraryStatistics(
                TotalBooks=DbStats.get('Books', 0),
                TotalCategories=DbStats.get('Categories', 0),
                TotalAuthors=len(Authors),
            )
        except Exception as e:
            self.Logger.error(f"Error getting library statistics: {e}")
            return LibraryStatistics()

    def UpdateLastAccessed(self, BookId: int):
        """
        Updates the last accessed time for a book.

        Args:
            BookId: The ID of the book to update.
        """
        # This is a placeholder for now. In a real application, you would
        # have a method in DatabaseManager to update the LastAccessed field.
        self.Logger.info(f"Updating last accessed time for book {BookId}")
