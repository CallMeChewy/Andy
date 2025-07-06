# File: DatabaseManager.py
# Path: Source/Core/DatabaseManager.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  09:25PM
"""
Description: FIXED - Database Manager with Correct Column Names
Fixed to use actual database column names (lowercase) instead of PascalCase.
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import os


class DatabaseManager:
    """
    FIXED - Database manager that uses actual database column names.
    """
    
    def __init__(self, DatabasePath: str = "Assets/my_library.db"):
        self.DatabasePath = DatabasePath
        self.Connection = None
        self.Logger = logging.getLogger(self.__class__.__name__)
        self.EnsureDatabaseDirectory()
        self.Connect()
    
    def EnsureDatabaseDirectory(self):
        """Ensure the database directory exists."""
        DatabaseDir = Path(self.DatabasePath).parent
        DatabaseDir.mkdir(parents=True, exist_ok=True)
    
    def Connect(self) -> bool:
        """Connect to the SQLite database."""
        try:
            self.Connection = sqlite3.connect(self.DatabasePath)
            self.Connection.row_factory = sqlite3.Row  # Enable column access by name
            
            # Test connection
            Cursor = self.Connection.cursor()
            Cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            Tables = Cursor.fetchall()
            TableCount = len(Tables)
            
            self.Logger.info(f"Database connection successful: {TableCount} tables found")
            return True
            
        except Exception as Error:
            self.Logger.error(f"Database connection failed: {Error}")
            return False
    
    def Close(self):
        """Close the database connection properly."""
        try:
            if self.Connection:
                self.Connection.close()
                self.Connection = None
                self.Logger.info("Database connection closed successfully")
        except Exception as Error:
            self.Logger.error(f"Error closing database connection: {Error}")
    
    def ExecuteQuery(self, Query: str, Parameters: Tuple = ()) -> List[sqlite3.Row]:
        """Execute a SQL query with proper error handling."""
        try:
            if not self.Connection:
                self.Logger.error("No database connection available")
                return []
            
            Cursor = self.Connection.cursor()
            Cursor.execute(Query, Parameters)
            
            # For SELECT queries, return results
            if Query.strip().upper().startswith('SELECT'):
                Results = Cursor.fetchall()
                return Results
            else:
                # For INSERT/UPDATE/DELETE queries, commit changes
                self.Connection.commit()
                return []
                
        except sqlite3.Error as Error:
            self.Logger.error(f"Database error: {Error}")
            self.Logger.error(f"Query execution failed: {Query} - {Error}")
            return []
        except Exception as Error:
            self.Logger.error(f"Unexpected error executing query: {Error}")
            return []
    
    def GetBooks(self, Category: str = "", Subject: str = "", SearchTerm: str = "") -> List[Dict[str, Any]]:
        """
        FIXED - Get books using actual database column names (lowercase).
        """
        try:
            # FIXED: Use lowercase column names that actually exist in database
            Query = "SELECT * FROM books WHERE 1=1"
            Parameters = []
            
            if Category and Category != "All Categories":
                # FIXED: Use lowercase 'category' not 'Category' 
                Query += " AND category = ?"
                Parameters.append(Category)
            
            if Subject and Subject != "All Subjects":
                # FIXED: Use lowercase 'subject' not 'Subject'
                Query += " AND subject = ?"
                Parameters.append(Subject)
            
            if SearchTerm:
                # FIXED: Use lowercase 'title' and 'author' column names
                Query += " AND (title LIKE ? OR author LIKE ?)"
                SearchPattern = f"%{SearchTerm}%"
                Parameters.extend([SearchPattern, SearchPattern])
            
            # FIXED: Use lowercase 'title' for ordering
            Query += " ORDER BY title"
            
            Rows = self.ExecuteQuery(Query, tuple(Parameters))
            
            # Convert rows to dictionaries with PascalCase keys for compatibility
            Books = []
            for Row in Rows:
                # Convert database row (lowercase) to expected format (PascalCase)
                BookDict = {
                    'Title': Row.get('title', Row.get('Title', 'Unknown')),
                    'Author': Row.get('author', Row.get('Author', 'Unknown')),  
                    'Category': Row.get('category', Row.get('Category', 'General')),
                    'Subject': Row.get('subject', Row.get('Subject', 'General')),
                    'FilePath': Row.get('filepath', Row.get('FilePath', '')),
                    'ThumbnailPath': Row.get('thumbnailpath', Row.get('ThumbnailPath', ''))
                }
                Books.append(BookDict)
            
            return Books
            
        except Exception as Error:
            self.Logger.error(f"Failed to get books: {Error}")
            return []
    
    def GetCategories(self) -> List[str]:
        """FIXED - Get categories using lowercase column name."""
        try:
            # FIXED: Use lowercase 'category' column name
            Rows = self.ExecuteQuery("SELECT DISTINCT category FROM books WHERE category IS NOT NULL ORDER BY category")
            Categories = [Row[0] for Row in Rows if Row[0]]
            return Categories
        except Exception as Error:
            self.Logger.error(f"Failed to get categories: {Error}")
            return []
    
    def GetSubjects(self, Category: str = "") -> List[str]:
        """FIXED - Get subjects using lowercase column names."""
        try:
            if Category and Category != "All Categories":
                # FIXED: Use lowercase column names
                Query = "SELECT DISTINCT subject FROM books WHERE category = ? AND subject IS NOT NULL ORDER BY subject"
                Parameters = (Category,)
            else:
                Query = "SELECT DISTINCT subject FROM books WHERE subject IS NOT NULL ORDER BY subject"
                Parameters = ()
            
            Rows = self.ExecuteQuery(Query, Parameters)
            Subjects = [Row[0] for Row in Rows if Row[0]]
            return Subjects
        except Exception as Error:
            self.Logger.error(f"Failed to get subjects: {Error}")
            return []
    
    def UpdateLastOpened(self, BookTitle: str):
        """
        FIXED - Update last opened timestamp using correct column names.
        """
        try:
            from datetime import datetime
            Timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Check if last_opened column exists
            Cursor = self.Connection.cursor()
            Cursor.execute("PRAGMA table_info(books)")
            Columns = [Column[1] for Column in Cursor.fetchall()]
            
            if 'last_opened' in Columns:
                # FIXED: Use lowercase column names
                self.ExecuteQuery("UPDATE books SET last_opened = ? WHERE title = ?", (Timestamp, BookTitle))
            elif 'LastOpened' in Columns:
                self.ExecuteQuery("UPDATE books SET LastOpened = ? WHERE Title = ?", (Timestamp, BookTitle))
            else:
                self.Logger.warning("Last opened column not found in database")
            
        except Exception as Error:
            self.Logger.warning(f"Could not update last opened time: {Error}")
    
    def GetDatabaseStats(self) -> Dict[str, int]:
        """FIXED - Get database statistics using lowercase column names."""
        Stats = {}
        
        try:
            # FIXED: Use lowercase column names
            CategoryRows = self.ExecuteQuery("SELECT COUNT(DISTINCT category) FROM books WHERE category IS NOT NULL")
            Stats['Categories'] = CategoryRows[0][0] if CategoryRows else 0
            
            SubjectRows = self.ExecuteQuery("SELECT COUNT(DISTINCT subject) FROM books WHERE subject IS NOT NULL")
            Stats['Subjects'] = SubjectRows[0][0] if SubjectRows else 0
            
            BookRows = self.ExecuteQuery("SELECT COUNT(*) FROM books")
            Stats['Books'] = BookRows[0][0] if BookRows else 0
            
        except Exception as Error:
            self.Logger.error(f"Failed to get database stats: {Error}")
            Stats = {'Categories': 0, 'Subjects': 0, 'Books': 0}
        
        return Stats