# File: BookService.py
# Path: Source/Core/BookService.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  05:31PM
"""
Description: Enhanced Book Service with Category/Subject Coordination
Adds GetSubjectsForCategory method to support proper filter panel workflow.
Maintains all existing functionality while adding category-subject relationship queries.
"""

import logging
import subprocess
import platform
from typing import List, Optional, Dict, Any
from pathlib import Path

from Source.Core.DatabaseManager import DatabaseManager
from Source.Data.DatabaseModels import Book, SearchCriteria, SearchResult


class BookService:
    """
    Enhanced business logic service for book operations.
    Provides category/subject coordination and comprehensive search capabilities.
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
        
        self.Logger.info("BookService initialized")
    
    def GetAllBooks(self) -> List[Book]:
        """
        Get all books from database.
        
        Returns:
            List of all Book objects
        """
        try:
            Query = """
                SELECT BookTitle, Category, Subject, Authors, Pages, Rating, 
                       AddedDate, LastOpened, FilePath, FileSize
                FROM Books 
                ORDER BY BookTitle
            """
            
            Results = self.DatabaseManager.ExecuteQuery(Query)
            Books = []
            
            for Row in Results:
                BookData = Book(
                    Title=Row[0],
                    Category=Row[1],
                    Subject=Row[2],
                    Authors=Row[3],
                    Pages=Row[4],
                    Rating=Row[5],
                    AddedDate=Row[6],
                    LastOpened=Row[7],
                    FilePath=Row[8],
                    FileSize=Row[9]
                )
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
            
            # Search term (searches across multiple fields)
            if Criteria.SearchTerm:
                SearchPattern = f"%{Criteria.SearchTerm}%"
                WhereConditions.append("""
                    (BookTitle LIKE ? OR Authors LIKE ? OR Category LIKE ? OR Subject LIKE ?)
                """)
                Parameters.extend([SearchPattern, SearchPattern, SearchPattern, SearchPattern])
            
            # Category filter
            if Criteria.Categories:
                CategoryPlaceholders = ','.join(['?' for _ in Criteria.Categories])
                WhereConditions.append(f"Category IN ({CategoryPlaceholders})")
                Parameters.extend(Criteria.Categories)
            
            # Subject filter
            if Criteria.Subjects:
                SubjectPlaceholders = ','.join(['?' for _ in Criteria.Subjects])
                WhereConditions.append(f"Subject IN ({SubjectPlaceholders})")
                Parameters.extend(Criteria.Subjects)
            
            # Authors filter
            if Criteria.Authors:
                AuthorPattern = f"%{Criteria.Authors[0]}%"  # First author for now
                WhereConditions.append("Authors LIKE ?")
                Parameters.append(AuthorPattern)
            
            # Rating filter
            if Criteria.MinRating is not None:
                WhereConditions.append("Rating >= ?")
                Parameters.append(Criteria.MinRating)
            
            # Build final query
            BaseQuery = """
                SELECT BookTitle, Category, Subject, Authors, Pages, Rating, 
                       AddedDate, LastOpened, FilePath, FileSize
                FROM Books
            """
            
            if WhereConditions:
                Query = BaseQuery + " WHERE " + " AND ".join(WhereConditions)
            else:
                Query = BaseQuery
            
            Query += " ORDER BY BookTitle"
            
            # Execute query
            Results = self.DatabaseManager.ExecuteQuery(Query, Parameters)
            Books = []
            
            for Row in Results:
                BookData = Book(
                    Title=Row[0],
                    Category=Row[1],
                    Subject=Row[2],
                    Authors=Row[3],
                    Pages=Row[4],
                    Rating=Row[5],
                    AddedDate=Row[6],
                    LastOpened=Row[7],
                    FilePath=Row[8],
                    FileSize=Row[9]
                )
                Books.append(BookData)
            
            self.Logger.debug(f"Search returned {len(Books)} books for criteria: {Criteria}")
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
            Query = "SELECT DISTINCT Category FROM Books WHERE Category IS NOT NULL ORDER BY Category"
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
            Query = "SELECT DISTINCT Subject FROM Books WHERE Subject IS NOT NULL ORDER BY Subject"
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
            
            # Fallback to direct query
            Query = """
                SELECT DISTINCT Subject 
                FROM Books 
                WHERE Category = ? AND Subject IS NOT NULL 
                ORDER BY Subject
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
            Query = """
                SELECT Category, Subject, COUNT(*) as BookCount
                FROM Books 
                WHERE Category IS NOT NULL AND Subject IS NOT NULL
                GROUP BY Category, Subject
                ORDER BY Category, Subject
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
            Query = "SELECT DISTINCT Authors FROM Books WHERE Authors IS NOT NULL ORDER BY Authors"
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
            Query = """
                SELECT BookTitle, Category, Subject, Authors, Pages, Rating, 
                       AddedDate, LastOpened, FilePath, FileSize
                FROM Books 
                WHERE BookTitle = ?
            """
            
            Results = self.DatabaseManager.ExecuteQuery(Query, [Title])
            
            if Results:
                Row = Results[0]
                BookData = Book(
                    Title=Row[0],
                    Category=Row[1],
                    Subject=Row[2],
                    Authors=Row[3],
                    Pages=Row[4],
                    Rating=Row[5],
                    AddedDate=Row[6],
                    LastOpened=Row[7],
                    FilePath=Row[8],
                    FileSize=Row[9]
                )
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
            
            # Update last opened date
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
        """Update last opened timestamp for a book"""
        try:
            Query = "UPDATE Books SET LastOpened = datetime('now') WHERE BookTitle = ?"
            self.DatabaseManager.ExecuteNonQuery(Query, [Title])
            
        except Exception as Error:
            self.Logger.error(f"Failed to update last opened for '{Title}': {Error}")
    
    def GetStatistics(self) -> Dict[str, Any]:
        """
        Get library statistics.
        
        Returns:
            Dictionary with various statistics
        """
        try:
            Stats = {}
            
            # Total books
            Result = self.DatabaseManager.ExecuteQuery("SELECT COUNT(*) FROM Books")
            Stats['TotalBooks'] = Result[0][0] if Result else 0
            
            # Books by category
            Result = self.DatabaseManager.ExecuteQuery("""
                SELECT Category, COUNT(*) 
                FROM Books 
                WHERE Category IS NOT NULL 
                GROUP BY Category 
                ORDER BY COUNT(*) DESC
            """)
            Stats['BooksByCategory'] = {Row[0]: Row[1] for Row in Result}
            
            # Books by subject
            Result = self.DatabaseManager.ExecuteQuery("""
                SELECT Subject, COUNT(*) 
                FROM Books 
                WHERE Subject IS NOT NULL 
                GROUP BY Subject 
                ORDER BY COUNT(*) DESC 
                LIMIT 10
            """)
            Stats['TopSubjects'] = {Row[0]: Row[1] for Row in Result}
            
            # Average rating
            Result = self.DatabaseManager.ExecuteQuery("""
                SELECT AVG(Rating) 
                FROM Books 
                WHERE Rating IS NOT NULL AND Rating > 0
            """)
            Stats['AverageRating'] = round(Result[0][0], 2) if Result and Result[0][0] else 0
            
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