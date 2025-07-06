# File: BookService.py
# Path: Source/Core/BookService.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  06:25PM
"""
Description: Fixed Book Service with Database Schema Compatibility
Updated to work with existing lowercase database schema while maintaining PascalCase code standards.
Fixes column name mismatches and adds proper GetSubjectsForCategory method.
"""

import logging
import subprocess
import platform
from typing import List, Optional, Dict, Any
from pathlib import Path

from Source.Core.DatabaseManager import DatabaseManager
from Source.Data.DatabaseModels import Book, SearchCriteria, SearchResult, CreateBookFromDatabaseRow


class BookService:
    """
    Enhanced business logic service for book operations.
    Compatible with existing database schema while providing modern interface.
    """
    
    def __init__(self, DatabaseManager: DatabaseManager):
        """
        Initialize book service with database connection.
        
        Args:
            DatabaseManager: Database connection manager
        """
        self.DatabaseManager = DatabaseManager  # ✅ FIXED: Changed from self.Database
        self.Logger = logging.getLogger(__name__)
        
        # Cache for performance
        self._CategoryCache: Optional[List[str]] = None
        self._SubjectCache: Optional[List[str]] = None
        self._CategorySubjectCache: Optional[Dict[str, List[str]]] = None
        
        self.Logger.info("BookService initialized")
    
    def GetAllBooks(self) -> List[Book]:
        """
        Get all books from database.
        
        Returns:
            List of all Book objects
        """
        try:
            # ✅ FIXED: Use lowercase column names to match existing schema
            Query = """
                SELECT b.id, b.title, b.author, b.category_id, b.subject_id, 
                       b.FilePath, b.ThumbnailPath, c.category, s.subject
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
                LEFT JOIN subjects s ON b.subject_id = s.id
                ORDER BY b.title COLLATE NOCASE
            """
            
            Results = self.DatabaseManager.ExecuteQuery(Query)
            Books = []
            
            for Row in Results:
                BookData = CreateBookFromDatabaseRow(Row)
                Books.append(BookData)
            
            self.Logger.debug(f"Retrieved {len(Books)} books")
            return Books
            
        except Exception as Error:
            self.Logger.error(f"Failed to get all books: {Error}")
            return []
    
    def SearchBooks(self, Criteria: SearchCriteria) -> List[Book]:
        """
        Search books based on criteria.
        
        Args:
            Criteria: Search criteria object
            
        Returns:
            List of matching Book objects
        """
        try:
            # Build WHERE clause
            WhereConditions = []
            Parameters = []
            
            # ✅ FIXED: Use lowercase column names and proper SearchTerm attribute
            # Search term (searches across multiple fields)
            if Criteria.SearchTerm:
                SearchPattern = f"%{Criteria.SearchTerm}%"
                WhereConditions.append("""
                    (b.title LIKE ? OR b.author LIKE ? OR c.category LIKE ? OR s.subject LIKE ?)
                """)
                Parameters.extend([SearchPattern, SearchPattern, SearchPattern, SearchPattern])
            
            # Category filter
            if Criteria.Categories:
                CategoryPlaceholders = ','.join(['?' for _ in Criteria.Categories])
                WhereConditions.append(f"c.category IN ({CategoryPlaceholders})")
                Parameters.extend(Criteria.Categories)
            
            # Subject filter
            if Criteria.Subjects:
                SubjectPlaceholders = ','.join(['?' for _ in Criteria.Subjects])
                WhereConditions.append(f"s.subject IN ({SubjectPlaceholders})")
                Parameters.extend(Criteria.Subjects)
            
            # Authors filter
            if Criteria.Authors:
                AuthorPattern = f"%{Criteria.Authors[0]}%"  # First author for now
                WhereConditions.append("b.author LIKE ?")
                Parameters.append(AuthorPattern)
            
            # Rating filter (if rating column exists)
            if Criteria.MinRating is not None:
                try:
                    # Check if rating column exists
                    TestQuery = "SELECT rating FROM books LIMIT 1"
                    self.DatabaseManager.ExecuteQuery(TestQuery)
                    WhereConditions.append("b.rating >= ?")
                    Parameters.append(Criteria.MinRating)
                except:
                    # Rating column doesn't exist, skip this filter
                    pass
            
            # Build final query with lowercase table and column names
            BaseQuery = """
                SELECT b.id, b.title, b.author, b.category_id, b.subject_id, 
                       b.FilePath, b.ThumbnailPath, c.category, s.subject
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
                LEFT JOIN subjects s ON b.subject_id = s.id
            """
            
            if WhereConditions:
                Query = BaseQuery + " WHERE " + " AND ".join(WhereConditions)
            else:
                Query = BaseQuery
            
            Query += " ORDER BY b.title COLLATE NOCASE"
            
            # Execute query
            Results = self.DatabaseManager.ExecuteQuery(Query, Parameters)
            Books = []
            
            for Row in Results:
                BookData = CreateBookFromDatabaseRow(Row)
                Books.append(BookData)
            
            self.Logger.debug(f"Search returned {len(Books)} books for criteria: {Criteria.GetDescription()}")
            return Books
            
        except Exception as Error:
            self.Logger.error(f"Failed to search books: {Error}")
            return []
    
    def GetCategories(self) -> List[str]:
        """
        Get all unique categories.
        
        Returns:
            List of category names
        """
        if self._CategoryCache is not None:
            return self._CategoryCache
        
        try:
            # ✅ FIXED: Use lowercase table and column names
            Query = "SELECT DISTINCT category FROM categories WHERE category IS NOT NULL ORDER BY category"
            Results = self.DatabaseManager.ExecuteQuery(Query)
            
            Categories = [Row[0] for Row in Results if Row[0]]
            self._CategoryCache = Categories
            
            self.Logger.debug(f"Retrieved {len(Categories)} categories")
            return Categories
            
        except Exception as Error:
            self.Logger.error(f"Failed to get categories: {Error}")
            return []
    
    def GetSubjects(self) -> List[str]:
        """
        Get all unique subjects.
        
        Returns:
            List of subject names
        """
        if self._SubjectCache is not None:
            return self._SubjectCache
        
        try:
            # ✅ FIXED: Use lowercase table and column names
            Query = "SELECT DISTINCT subject FROM subjects WHERE subject IS NOT NULL ORDER BY subject"
            Results = self.DatabaseManager.ExecuteQuery(Query)
            
            Subjects = [Row[0] for Row in Results if Row[0]]
            self._SubjectCache = Subjects
            
            self.Logger.debug(f"Retrieved {len(Subjects)} subjects")
            return Subjects
            
        except Exception as Error:
            self.Logger.error(f"Failed to get subjects: {Error}")
            return []
    
    def GetSubjectsForCategory(self, Category: str) -> List[str]:
        """
        ✅ FIXED: Added missing method for category/subject coordination.
        Get all subjects for a specific category.
        
        Args:
            Category: Category name to get subjects for
            
        Returns:
            List of subject names for the category
        """
        try:
            # Use cache if available
            if self._CategorySubjectCache is None:
                self._BuildCategorySubjectCache()
            
            if self._CategorySubjectCache and Category in self._CategorySubjectCache:
                Subjects = self._CategorySubjectCache[Category]
                self.Logger.debug(f"Retrieved {len(Subjects)} subjects for category '{Category}' from cache")
                return Subjects
            
            # Fallback to direct query with lowercase names
            Query = """
                SELECT DISTINCT s.subject 
                FROM subjects s
                INNER JOIN categories c ON s.category_id = c.id
                WHERE c.category = ? AND s.subject IS NOT NULL 
                ORDER BY s.subject
            """
            
            Results = self.DatabaseManager.ExecuteQuery(Query, [Category])
            Subjects = [Row[0] for Row in Results if Row[0]]
            
            self.Logger.debug(f"Retrieved {len(Subjects)} subjects for category '{Category}'")
            return Subjects
            
        except Exception as Error:
            self.Logger.error(f"Failed to get subjects for category '{Category}': {Error}")
            return []
    
    def _BuildCategorySubjectCache(self) -> None:
        """Build cache of category-subject relationships"""
        try:
            # ✅ FIXED: Use lowercase table and column names
            Query = """
                SELECT c.category, s.subject, COUNT(b.id) as book_count
                FROM categories c
                INNER JOIN subjects s ON s.category_id = c.id
                LEFT JOIN books b ON b.subject_id = s.id
                WHERE c.category IS NOT NULL AND s.subject IS NOT NULL
                GROUP BY c.category, s.subject
                ORDER BY c.category, s.subject
            """
            
            Results = self.DatabaseManager.ExecuteQuery(Query)
            
            Cache = {}
            for Row in Results:
                Category = Row[0]
                Subject = Row[1]
                
                if Category not in Cache:
                    Cache[Category] = []
                Cache[Category].append(Subject)
            
            self._CategorySubjectCache = Cache
            self.Logger.debug(f"Built category-subject cache with {len(Cache)} categories")
            
        except Exception as Error:
            self.Logger.error(f"Failed to build category-subject cache: {Error}")
            self._CategorySubjectCache = {}
    
    def GetAuthors(self) -> List[str]:
        """
        Get all unique authors.
        
        Returns:
            List of author names
        """
        try:
            # ✅ FIXED: Use lowercase table and column names
            Query = "SELECT DISTINCT author FROM books WHERE author IS NOT NULL ORDER BY author"
            Results = self.DatabaseManager.ExecuteQuery(Query)
            
            Authors = [Row[0] for Row in Results if Row[0]]
            
            self.Logger.debug(f"Retrieved {len(Authors)} authors")
            return Authors
            
        except Exception as Error:
            self.Logger.error(f"Failed to get authors: {Error}")
            return []
    
    def GetBookByTitle(self, Title: str) -> Optional[Book]:
        """
        Get a specific book by title.
        
        Args:
            Title: Book title to search for
            
        Returns:
            Book object if found, None otherwise
        """
        try:
            # ✅ FIXED: Use lowercase column names
            Query = """
                SELECT b.id, b.title, b.author, b.category_id, b.subject_id, 
                       b.FilePath, b.ThumbnailPath, c.category, s.subject
                FROM books b
                LEFT JOIN categories c ON b.category_id = c.id
                LEFT JOIN subjects s ON b.subject_id = s.id
                WHERE b.title = ?
            """
            
            Results = self.DatabaseManager.ExecuteQuery(Query, [Title])
            
            if Results:
                Row = Results[0]
                BookData = CreateBookFromDatabaseRow(Row)
                return BookData
            
            return None
            
        except Exception as Error:
            self.Logger.error(f"Failed to get book '{Title}': {Error}")
            return None
    
    def OpenBook(self, Title: str) -> bool:
        """
        Open a book's PDF file.
        
        Args:
            Title: Title of book to open
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get book details
            BookData = self.GetBookByTitle(Title)
            if not BookData or not BookData.FilePath:
                self.Logger.warning(f"Book '{Title}' not found or no file path")
                return False
            
            # Check if file exists
            FilePath = Path(BookData.FilePath)
            if not FilePath.exists():
                # Try alternate path
                AlternatePath = Path("Assets/Books") / f"{Title}.pdf"
                if AlternatePath.exists():
                    FilePath = AlternatePath
                else:
                    self.Logger.warning(f"PDF file not found: {BookData.FilePath}")
                    return False
            
            # Open file with system default application
            System = platform.system()
            
            if System == "Windows":
                subprocess.run(["start", str(FilePath)], shell=True, check=True)
            elif System == "Darwin":  # macOS
                subprocess.run(["open", str(FilePath)], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", str(FilePath)], check=True)
            
            # Update last opened date if column exists
            self._UpdateLastOpened(Title)
            
            self.Logger.info(f"Opened book: '{Title}'")
            return True
            
        except subprocess.CalledProcessError as Error:
            self.Logger.error(f"Failed to open book '{Title}': {Error}")
            return False
        except Exception as Error:
            self.Logger.error(f"Unexpected error opening book '{Title}': {Error}")
            return False
    
    def _UpdateLastOpened(self, Title: str) -> None:
        """Update last opened timestamp for a book (if column exists)"""
        try:
            # Check if last_opened column exists
            TestQuery = "SELECT last_opened FROM books LIMIT 1"
            self.DatabaseManager.ExecuteQuery(TestQuery)
            
            # Column exists, update it
            Query = "UPDATE books SET last_opened = datetime('now') WHERE title = ?"
            self.DatabaseManager.ExecuteNonQuery(Query, [Title])
            
        except Exception:
            # Column doesn't exist or other error, skip update
            pass
    
    def GetStatistics(self) -> Dict[str, Any]:
        """
        Get library statistics.
        
        Returns:
            Dictionary with various statistics
        """
        try:
            Stats = {}
            
            # Total books
            Result = self.DatabaseManager.ExecuteQuery("SELECT COUNT(*) FROM books")
            Stats['TotalBooks'] = Result[0][0] if Result else 0
            
            # Books by category
            Result = self.DatabaseManager.ExecuteQuery("""
                SELECT c.category, COUNT(b.id) 
                FROM categories c
                LEFT JOIN books b ON b.category_id = c.id
                WHERE c.category IS NOT NULL 
                GROUP BY c.category 
                ORDER BY COUNT(b.id) DESC
            """)
            Stats['BooksByCategory'] = {Row[0]: Row[1] for Row in Result}
            
            # Books by subject
            Result = self.DatabaseManager.ExecuteQuery("""
                SELECT s.subject, COUNT(b.id) 
                FROM subjects s
                LEFT JOIN books b ON b.subject_id = s.id
                WHERE s.subject IS NOT NULL 
                GROUP BY s.subject 
                ORDER BY COUNT(b.id) DESC 
                LIMIT 10
            """)
            Stats['TopSubjects'] = {Row[0]: Row[1] for Row in Result}
            
            # Try to get average rating if column exists
            try:
                Result = self.DatabaseManager.ExecuteQuery("""
                    SELECT AVG(rating) 
                    FROM books 
                    WHERE rating IS NOT NULL AND rating > 0
                """)
                Stats['AverageRating'] = round(Result[0][0], 2) if Result and Result[0][0] else 0
            except:
                Stats['AverageRating'] = 0
            
            return Stats
            
        except Exception as Error:
            self.Logger.error(f"Failed to get statistics: {Error}")
            return {}
    
    def RefreshCache(self) -> None:
        """Clear all caches to force data refresh"""
        self._CategoryCache = None
        self._SubjectCache = None
        self._CategorySubjectCache = None
        self.Logger.info("Service caches cleared")