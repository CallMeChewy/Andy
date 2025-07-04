# File: DatabaseManager.py
# Path: Source/Core/DatabaseManager.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  14:45PM
"""
Description: Anderson's Library Database Manager
Centralized SQLite database operations with connection management and error handling.
Returns clean model objects instead of raw database tuples.

Purpose: Provides single point of database access for all Anderson's Library operations.
Handles connection lifecycle, transactions, and data conversion to model objects.
"""

import sqlite3
import os
import logging
from typing import List, Optional, Tuple, Any, Dict
from contextlib import contextmanager
from pathlib import Path

# Import our data models
from ..Data.DatabaseModels import Book, Category, Subject, CreateBookFromRow, CreateCategoryFromRow, CreateSubjectFromRow


class DatabaseManager:
    """
    Manages all SQLite database operations for Anderson's Library.
    Provides clean interface with model objects and proper error handling.
    """
    
    def __init__(self, DatabasePath: str = "Assets/my_library.db"):
        """
        Initialize database manager with connection path.
        
        Args:
            DatabasePath: Path to SQLite database file
        """
        self.DatabasePath = DatabasePath
        self.ConnectionPool = {}
        self.Logger = logging.getLogger(__name__)
        
        # Validate database exists
        if not os.path.exists(DatabasePath):
            raise FileNotFoundError(f"Database not found: {DatabasePath}")
        
        # Test connection on initialization
        self._TestConnection()
    
    def _TestConnection(self) -> bool:
        """Test database connection and basic functionality"""
        try:
            with self.GetConnection() as Connection:
                Cursor = Connection.cursor()
                Cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                TableCount = Cursor.fetchone()[0]
                
                if TableCount == 0:
                    raise ValueError("Database appears to be empty (no tables found)")
                
                self.Logger.info(f"Database connection successful: {TableCount} tables found")
                return True
                
        except Exception as Error:
            self.Logger.error(f"Database connection test failed: {Error}")
            raise
    
    @contextmanager
    def GetConnection(self):
        """
        Get database connection with automatic cleanup.
        Uses context manager for proper resource management.
        """
        Connection = None
        try:
            Connection = sqlite3.connect(self.DatabasePath)
            Connection.row_factory = sqlite3.Row  # Enable column access by name
            yield Connection
        except sqlite3.Error as Error:
            if Connection:
                Connection.rollback()
            self.Logger.error(f"Database error: {Error}")
            raise
        finally:
            if Connection:
                Connection.close()
    
    def ExecuteQuery(self, Query: str, Parameters: Tuple = ()) -> List[sqlite3.Row]:
        """
        Execute SELECT query and return results.
        
        Args:
            Query: SQL SELECT statement
            Parameters: Query parameters for safe substitution
            
        Returns:
            List of database rows
        """
        try:
            with self.GetConnection() as Connection:
                Cursor = Connection.cursor()
                Cursor.execute(Query, Parameters)
                return Cursor.fetchall()
                
        except sqlite3.Error as Error:
            self.Logger.error(f"Query execution failed: {Query} - {Error}")
            raise
    
    def ExecuteNonQuery(self, Query: str, Parameters: Tuple = ()) -> int:
        """
        Execute INSERT/UPDATE/DELETE query.
        
        Args:
            Query: SQL statement
            Parameters: Query parameters for safe substitution
            
        Returns:
            Number of affected rows
        """
        try:
            with self.GetConnection() as Connection:
                Cursor = Connection.cursor()
                Cursor.execute(Query, Parameters)
                Connection.commit()
                return Cursor.rowcount
                
        except sqlite3.Error as Error:
            self.Logger.error(f"Non-query execution failed: {Query} - {Error}")
            raise
    
    # =================================================================
    # CATEGORY OPERATIONS
    # =================================================================
    
    def GetAllCategories(self) -> List[Category]:
        """
        Get all categories ordered alphabetically.
        
        Returns:
            List of Category objects
        """
        Query = "SELECT id, category FROM categories ORDER BY category ASC"
        Rows = self.ExecuteQuery(Query)
        
        Categories = []
        for Row in Rows:
            CategoryObj = Category(CategoryId=Row['id'], CategoryName=Row['category'])
            Categories.append(CategoryObj)
        
        return Categories
    
    def GetCategoryById(self, CategoryId: int) -> Optional[Category]:
        """
        Get category by ID.
        
        Args:
            CategoryId: Category identifier
            
        Returns:
            Category object or None if not found
        """
        Query = "SELECT id, category FROM categories WHERE id = ?"
        Rows = self.ExecuteQuery(Query, (CategoryId,))
        
        if Rows:
            Row = Rows[0]
            return Category(CategoryId=Row['id'], CategoryName=Row['category'])
        
        return None
    
    def GetCategoryByName(self, CategoryName: str) -> Optional[Category]:
        """
        Get category by name (case-insensitive).
        
        Args:
            CategoryName: Category name to search for
            
        Returns:
            Category object or None if not found
        """
        Query = "SELECT id, category FROM categories WHERE LOWER(category) = LOWER(?)"
        Rows = self.ExecuteQuery(Query, (CategoryName,))
        
        if Rows:
            Row = Rows[0]
            return Category(CategoryId=Row['id'], CategoryName=Row['category'])
        
        return None
    
    # =================================================================
    # SUBJECT OPERATIONS  
    # =================================================================
    
    def GetSubjectsByCategory(self, CategoryName: str) -> List[Subject]:
        """
        Get all subjects for a specific category.
        
        Args:
            CategoryName: Category name to filter by
            
        Returns:
            List of Subject objects
        """
        Query = """
            SELECT s.id, s.category_id, s.subject, c.category 
            FROM subjects s
            JOIN categories c ON s.category_id = c.id
            WHERE c.category = ?
            ORDER BY s.subject ASC
        """
        Rows = self.ExecuteQuery(Query, (CategoryName,))
        
        Subjects = []
        for Row in Rows:
            SubjectObj = Subject(
                SubjectId=Row['id'],
                CategoryId=Row['category_id'],
                SubjectName=Row['subject'],
                CategoryName=Row['category']
            )
            Subjects.append(SubjectObj)
        
        return Subjects
    
    def GetSubjectById(self, SubjectId: int) -> Optional[Subject]:
        """
        Get subject by ID with category information.
        
        Args:
            SubjectId: Subject identifier
            
        Returns:
            Subject object or None if not found
        """
        Query = """
            SELECT s.id, s.category_id, s.subject, c.category 
            FROM subjects s
            LEFT JOIN categories c ON s.category_id = c.id
            WHERE s.id = ?
        """
        Rows = self.ExecuteQuery(Query, (SubjectId,))
        
        if Rows:
            Row = Rows[0]
            return Subject(
                SubjectId=Row['id'],
                CategoryId=Row['category_id'],
                SubjectName=Row['subject'],
                CategoryName=Row['category'] or ""
            )
        
        return None
    
    def GetAllSubjects(self) -> List[Subject]:
        """
        Get all subjects with category information.
        
        Returns:
            List of Subject objects ordered by category then subject
        """
        Query = """
            SELECT s.id, s.category_id, s.subject, c.category 
            FROM subjects s
            LEFT JOIN categories c ON s.category_id = c.id
            ORDER BY c.category ASC, s.subject ASC
        """
        Rows = self.ExecuteQuery(Query)
        
        Subjects = []
        for Row in Rows:
            SubjectObj = Subject(
                SubjectId=Row['id'],
                CategoryId=Row['category_id'],
                SubjectName=Row['subject'],
                CategoryName=Row['category'] or ""
            )
            Subjects.append(SubjectObj)
        
        return Subjects
    
    # =================================================================
    # BOOK OPERATIONS
    # =================================================================
    
    def GetBooksBySubject(self, SubjectName: str) -> List[Book]:
        """
        Get all books for a specific subject.
        
        Args:
            SubjectName: Subject name to filter by
            
        Returns:
            List of Book objects
        """
        Query = """
            SELECT b.id, b.title, b.category_id, b.subject_id,
                   c.category, s.subject
            FROM books b
            LEFT JOIN categories c ON b.category_id = c.id
            LEFT JOIN subjects s ON b.subject_id = s.id
            WHERE s.subject = ?
            ORDER BY b.title ASC
        """
        Rows = self.ExecuteQuery(Query, (SubjectName,))
        
        return self._ConvertRowsToBooks(Rows)
    
    def SearchBooks(self, SearchTerm: str) -> List[Book]:
        """
        Search books by title (case-insensitive).
        
        Args:
            SearchTerm: Search text to match against titles
            
        Returns:
            List of Book objects matching search criteria
        """
        Query = """
            SELECT b.id, b.title, b.category_id, b.subject_id,
                   c.category, s.subject
            FROM books b
            LEFT JOIN categories c ON b.category_id = c.id
            LEFT JOIN subjects s ON b.subject_id = s.id
            WHERE b.title LIKE ? 
            ORDER BY b.title COLLATE NOCASE ASC
        """
        SearchPattern = f"%{SearchTerm}%"
        Rows = self.ExecuteQuery(Query, (SearchPattern,))
        
        return self._ConvertRowsToBooks(Rows)
    
    def GetAllBooks(self) -> List[Book]:
        """
        Get all books with category and subject information.
        
        Returns:
            List of all Book objects
        """
        Query = """
            SELECT b.id, b.title, b.category_id, b.subject_id,
                   c.category, s.subject
            FROM books b
            LEFT JOIN categories c ON b.category_id = c.id
            LEFT JOIN subjects s ON b.subject_id = s.id
            ORDER BY b.title ASC
        """
        Rows = self.ExecuteQuery(Query)
        
        return self._ConvertRowsToBooks(Rows)
    
    def GetBookById(self, BookId: int) -> Optional[Book]:
        """
        Get book by ID with full category and subject information.
        
        Args:
            BookId: Book identifier
            
        Returns:
            Book object or None if not found
        """
        Query = """
            SELECT b.id, b.title, b.category_id, b.subject_id,
                   c.category, s.subject
            FROM books b
            LEFT JOIN categories c ON b.category_id = c.id
            LEFT JOIN subjects s ON b.subject_id = s.id
            WHERE b.id = ?
        """
        Rows = self.ExecuteQuery(Query, (BookId,))
        
        if Rows:
            Books = self._ConvertRowsToBooks(Rows)
            return Books[0] if Books else None
        
        return None
    
    def GetBookByTitle(self, Title: str) -> Optional[Book]:
        """
        Get book by exact title match.
        
        Args:
            Title: Exact book title
            
        Returns:
            Book object or None if not found
        """
        Query = """
            SELECT b.id, b.title, b.category_id, b.subject_id,
                   c.category, s.subject
            FROM books b
            LEFT JOIN categories c ON b.category_id = c.id
            LEFT JOIN subjects s ON b.subject_id = s.id
            WHERE b.title = ?
        """
        Rows = self.ExecuteQuery(Query, (Title,))
        
        if Rows:
            Books = self._ConvertRowsToBooks(Rows)
            return Books[0] if Books else None
        
        return None
    
    # =================================================================
    # UTILITY METHODS
    # =================================================================
    
    def _ConvertRowsToBooks(self, Rows: List[sqlite3.Row]) -> List[Book]:
        """
        Convert database rows to Book objects with enhanced filename generation.
        
        Args:
            Rows: Database rows from book queries
            
        Returns:
            List of Book objects
        """
        Books = []
        for Row in Rows:
            # Generate filename from title if not stored in database
            FileName = self._GenerateFilenameFromTitle(Row['title'])
            
            BookObj = Book(
                BookId=Row['id'],
                Title=Row['title'],
                CategoryId=Row['category_id'],
                SubjectId=Row['subject_id'],
                CategoryName=Row['category'] or "",
                SubjectName=Row['subject'] or "",
                FileName=FileName
            )
            Books.append(BookObj)
        
        return Books
    
    def _GenerateFilenameFromTitle(self, Title: str) -> str:
        """
        Generate PDF filename from book title.
        Assumes title matches filename without .pdf extension.
        
        Args:
            Title: Book title
            
        Returns:
            Generated filename with .pdf extension
        """
        if not Title:
            return ""
        
        # For now, assume title equals filename (current database structure)
        # Future enhancement: store actual filenames in database
        return f"{Title}.pdf"
    
    def GetDatabaseStats(self) -> Dict[str, int]:
        """
        Get database statistics for dashboard display.
        
        Returns:
            Dictionary with counts of categories, subjects, books
        """
        Stats = {}
        
        try:
            # Get category count
            CategoryRows = self.ExecuteQuery("SELECT COUNT(*) FROM categories")
            Stats['Categories'] = CategoryRows[0][0] if CategoryRows else 0
            
            # Get subject count
            SubjectRows = self.ExecuteQuery("SELECT COUNT(*) FROM subjects")
            Stats['Subjects'] = SubjectRows[0][0] if SubjectRows else 0
            
            # Get book count
            BookRows = self.ExecuteQuery("SELECT COUNT(*) FROM books")
            Stats['Books'] = BookRows[0][0] if BookRows else 0
            
        except Exception as Error:
            self.Logger.error(f"Failed to get database stats: {Error}")
            Stats = {'Categories': 0, 'Subjects': 0, 'Books': 0}
        
        return Stats
    
    def ValidateDatabase(self) -> List[str]:
        """
        Validate database integrity and return list of issues found.
        
        Returns:
            List of validation error messages (empty if no issues)
        """
        Issues = []
        
        try:
            # Check for required tables
            RequiredTables = ['categories', 'subjects', 'books']
            Query = "SELECT name FROM sqlite_master WHERE type='table'"
            Rows = self.ExecuteQuery(Query)
            ExistingTables = [Row['name'] for Row in Rows]
            
            for Table in RequiredTables:
                if Table not in ExistingTables:
                    Issues.append(f"Missing required table: {Table}")
            
            # Check for orphaned records
            OrphanQuery = """
                SELECT COUNT(*) FROM subjects s 
                LEFT JOIN categories c ON s.category_id = c.id 
                WHERE c.id IS NULL
            """
            OrphanRows = self.ExecuteQuery(OrphanQuery)
            OrphanCount = OrphanRows[0][0] if OrphanRows else 0
            
            if OrphanCount > 0:
                Issues.append(f"Found {OrphanCount} orphaned subjects")
            
        except Exception as Error:
            Issues.append(f"Database validation failed: {Error}")
        
        return Issues
