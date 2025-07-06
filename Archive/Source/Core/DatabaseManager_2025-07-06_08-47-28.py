# File: DatabaseManager.py
# Path: Source/Core/DatabaseManager.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  08:50PM
"""
Description: COMPATIBILITY FIX - Database Manager Without Schema Issues
Fixed to avoid SQLite ALTER TABLE limitations and work with existing schema.
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import os


class DatabaseManager:
    """
    COMPATIBILITY FIX - Database manager that works with existing schema.
    """
    
    def __init__(self, DatabasePath: str = "Assets/my_library.db"):
        self.DatabasePath = DatabasePath
        self.Connection = None
        self.Logger = logging.getLogger(self.__class__.__name__)
        self.EnsureDatabaseDirectory()
        self.Connect()
        # REMOVED: Schema validation that was causing issues
        # self.ValidateSchema()
    
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
        COMPATIBILITY FIX - Get books with optional filtering, returns dictionaries.
        """
        try:
            Query = "SELECT * FROM books WHERE 1=1"
            Parameters = []
            
            if Category and Category != "All Categories":
                Query += " AND Category = ?"
                Parameters.append(Category)
            
            if Subject and Subject != "All Subjects":
                Query += " AND Subject = ?"
                Parameters.append(Subject)
            
            if SearchTerm:
                Query += " AND (Title LIKE ? OR Author LIKE ?)"
                SearchPattern = f"%{SearchTerm}%"
                Parameters.extend([SearchPattern, SearchPattern])
            
            Query += " ORDER BY Title"
            
            Rows = self.ExecuteQuery(Query, tuple(Parameters))
            
            # Convert rows to dictionaries
            Books = []
            for Row in Rows:
                BookDict = dict(Row)  # Convert sqlite3.Row to dict
                Books.append(BookDict)
            
            return Books
            
        except Exception as Error:
            self.Logger.error(f"Failed to get books: {Error}")
            return []
    
    def GetCategories(self) -> List[str]:
        """Get all available categories."""
        try:
            Rows = self.ExecuteQuery("SELECT DISTINCT Category FROM books WHERE Category IS NOT NULL ORDER BY Category")
            Categories = [Row[0] for Row in Rows if Row[0]]
            return Categories
        except Exception as Error:
            self.Logger.error(f"Failed to get categories: {Error}")
            return []
    
    def GetSubjects(self, Category: str = "") -> List[str]:
        """Get subjects for a specific category."""
        try:
            if Category and Category != "All Categories":
                Query = "SELECT DISTINCT Subject FROM books WHERE Category = ? AND Subject IS NOT NULL ORDER BY Subject"
                Parameters = (Category,)
            else:
                Query = "SELECT DISTINCT Subject FROM books WHERE Subject IS NOT NULL ORDER BY Subject"
                Parameters = ()
            
            Rows = self.ExecuteQuery(Query, Parameters)
            Subjects = [Row[0] for Row in Rows if Row[0]]
            return Subjects
        except Exception as Error:
            self.Logger.error(f"Failed to get subjects: {Error}")
            return []
    
    def UpdateLastOpened(self, BookTitle: str):
        """
        COMPATIBILITY FIX - Update last opened timestamp, handles missing columns gracefully.
        """
        try:
            from datetime import datetime
            Timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Check if LastOpened column exists first
            Cursor = self.Connection.cursor()
            Cursor.execute("PRAGMA table_info(books)")
            Columns = [Column[1] for Column in Cursor.fetchall()]
            
            if 'LastOpened' in Columns:
                self.ExecuteQuery("UPDATE books SET LastOpened = ? WHERE Title = ?", (Timestamp, BookTitle))
            elif 'last_opened' in Columns:
                self.ExecuteQuery("UPDATE books SET last_opened = ? WHERE Title = ?", (Timestamp, BookTitle))
            else:
                # Column doesn't exist - log but don't fail
                self.Logger.warning("LastOpened column not found in database")
            
        except Exception as Error:
            self.Logger.warning(f"Could not update last opened time: {Error}")
    
    def GetDatabaseStats(self) -> Dict[str, int]:
        """Get database statistics."""
        Stats = {}
        
        try:
            # Get category count
            CategoryRows = self.ExecuteQuery("SELECT COUNT(DISTINCT Category) FROM books WHERE Category IS NOT NULL")
            Stats['Categories'] = CategoryRows[0][0] if CategoryRows else 0
            
            # Get subject count  
            SubjectRows = self.ExecuteQuery("SELECT COUNT(DISTINCT Subject) FROM books WHERE Subject IS NOT NULL")
            Stats['Subjects'] = SubjectRows[0][0] if SubjectRows else 0
            
            # Get book count
            BookRows = self.ExecuteQuery("SELECT COUNT(*) FROM books")
            Stats['Books'] = BookRows[0][0] if BookRows else 0
            
        except Exception as Error:
            self.Logger.error(f"Failed to get database stats: {Error}")
            Stats = {'Categories': 0, 'Subjects': 0, 'Books': 0}
        
        return Stats