# File: DatabaseManager.py
# Path: Source/Core/DatabaseManager.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  08:30PM
"""
Description: Enhanced Database Manager with Schema Fixes
Handles all database operations with proper error handling and schema management.
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import os


class DatabaseManager:
    """
    Enhanced database manager with proper schema handling and connection management.
    """
    
    def __init__(self, DatabasePath: str = "Assets/my_library.db"):
        self.DatabasePath = DatabasePath
        self.Connection = None
        self.Logger = logging.getLogger(self.__class__.__name__)
        self.EnsureDatabaseDirectory()
        self.Connect()
        self.ValidateSchema()
    
    def EnsureDatabaseDirectory(self):
        """Ensure the database directory exists."""
        DatabaseDir = Path(self.DatabasePath).parent
        DatabaseDir.mkdir(parents=True, exist_ok=True)
    
    def Connect(self) -> bool:
        """
        Connect to the SQLite database.
        
        Returns:
            True if connection successful, False otherwise
        """
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
        """
        Close the database connection properly.
        Fixed: Added missing Close method that was causing shutdown errors.
        """
        try:
            if self.Connection:
                self.Connection.close()
                self.Connection = None
                self.Logger.info("Database connection closed successfully")
        except Exception as Error:
            self.Logger.error(f"Error closing database connection: {Error}")
    
    def ValidateSchema(self):
        """
        Validate and update database schema to ensure all required columns exist.
        """
        try:
            self.CreateMissingTables()
            self.AddMissingColumns()
            self.Logger.info("Database schema validation completed")
        except Exception as Error:
            self.Logger.error(f"Schema validation failed: {Error}")
    
    def CreateMissingTables(self):
        """Create any missing tables."""
        # Books table with all required columns
        BooksTableSQL = """
        CREATE TABLE IF NOT EXISTS books (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT NOT NULL,
            Author TEXT,
            Category TEXT,
            Subject TEXT,
            FilePath TEXT,
            ThumbnailPath TEXT,
            DateAdded TEXT,
            LastOpened TEXT,
            Rating INTEGER DEFAULT 0,
            Notes TEXT,
            FileSize INTEGER,
            PageCount INTEGER,
            CreatedBy TEXT DEFAULT 'System',
            CreatedDate TEXT DEFAULT CURRENT_TIMESTAMP,
            LastModifiedBy TEXT DEFAULT 'System',
            LastModifiedDate TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # Categories table
        CategoriesTableSQL = """
        CREATE TABLE IF NOT EXISTS categories (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CategoryName TEXT UNIQUE NOT NULL,
            Description TEXT,
            CreatedDate TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # Subjects table
        SubjectsTableSQL = """
        CREATE TABLE IF NOT EXISTS subjects (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            SubjectName TEXT NOT NULL,
            CategoryID INTEGER,
            Description TEXT,
            CreatedDate TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (CategoryID) REFERENCES categories (ID)
        )
        """
        
        self.ExecuteQuery(BooksTableSQL)
        self.ExecuteQuery(CategoriesTableSQL)
        self.ExecuteQuery(SubjectsTableSQL)
    
    def AddMissingColumns(self):
        """Add any missing columns to existing tables."""
        # Check for missing columns in books table
        MissingColumns = [
            ("last_opened", "TEXT"),
            ("LastOpened", "TEXT"),
            ("ThumbnailPath", "TEXT"),
            ("Rating", "INTEGER DEFAULT 0"),
            ("Notes", "TEXT"),
            ("FileSize", "INTEGER"),
            ("PageCount", "INTEGER"),
            ("CreatedBy", "TEXT DEFAULT 'System'"),
            ("CreatedDate", "TEXT DEFAULT CURRENT_TIMESTAMP"),
            ("LastModifiedBy", "TEXT DEFAULT 'System'"),
            ("LastModifiedDate", "TEXT DEFAULT CURRENT_TIMESTAMP")
        ]
        
        for ColumnName, ColumnType in MissingColumns:
            self.AddColumnIfNotExists("books", ColumnName, ColumnType)
    
    def AddColumnIfNotExists(self, TableName: str, ColumnName: str, ColumnType: str):
        """
        Add a column to a table if it doesn't exist.
        
        Args:
            TableName: Name of the table
            ColumnName: Name of the column to add
            ColumnType: SQL type definition for the column
        """
        try:
            # Check if column exists
            Cursor = self.Connection.cursor()
            Cursor.execute(f"PRAGMA table_info({TableName})")
            Columns = [Column[1] for Column in Cursor.fetchall()]
            
            if ColumnName not in Columns:
                AlterSQL = f"ALTER TABLE {TableName} ADD COLUMN {ColumnName} {ColumnType}"
                self.ExecuteQuery(AlterSQL)
                self.Logger.info(f"Added missing column {ColumnName} to {TableName}")
                
        except Exception as Error:
            self.Logger.warning(f"Could not add column {ColumnName} to {TableName}: {Error}")
    
    def ExecuteQuery(self, Query: str, Parameters: Tuple = ()) -> List[sqlite3.Row]:
        """
        Execute a SQL query with proper error handling.
        
        Args:
            Query: SQL query string
            Parameters: Query parameters tuple
            
        Returns:
            List of result rows
        """
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
        Get books with optional filtering.
        
        Args:
            Category: Category filter (empty for all)
            Subject: Subject filter (empty for all)
            SearchTerm: Search term for title/author (empty for all)
            
        Returns:
            List of book dictionaries
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
        """
        Get all available categories.
        
        Returns:
            List of category names
        """
        try:
            Rows = self.ExecuteQuery("SELECT DISTINCT Category FROM books WHERE Category IS NOT NULL ORDER BY Category")
            Categories = [Row[0] for Row in Rows if Row[0]]
            return Categories
        except Exception as Error:
            self.Logger.error(f"Failed to get categories: {Error}")
            return []
    
    def GetSubjects(self, Category: str = "") -> List[str]:
        """
        Get subjects for a specific category.
        
        Args:
            Category: Category name (empty for all subjects)
            
        Returns:
            List of subject names
        """
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
        Update the last opened timestamp for a book.
        
        Args:
            BookTitle: Title of the book that was opened
        """
        try:
            from datetime import datetime
            Timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Try both column names for compatibility
            UpdateQueries = [
                "UPDATE books SET LastOpened = ? WHERE Title = ?",
                "UPDATE books SET last_opened = ? WHERE Title = ?"
            ]
            
            for Query in UpdateQueries:
                try:
                    self.ExecuteQuery(Query, (Timestamp, BookTitle))
                    break  # If successful, stop trying other queries
                except:
                    continue  # Try next query if this one fails
            
        except Exception as Error:
            self.Logger.warning(f"Could not update last opened time: {Error}")
    
    def GetDatabaseStats(self) -> Dict[str, int]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with counts of categories, subjects, books
        """
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