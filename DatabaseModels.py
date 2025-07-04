# File: DatabaseModels.py
# Path: Source/Data/DatabaseModels.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  14:30PM
"""
Description: Anderson's Library Database Models
Core data models for books, categories, and subjects with validation and conversion methods.
Follows single responsibility principle with focused data representation.

Purpose: Provides clean data model classes that encapsulate database entities
and their business rules. Used by all other modules for consistent data handling.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pathlib import Path
import os
import re
from datetime import datetime


@dataclass
class Category:
    """
    Represents a book category in Anderson's Library.
    Maps to categories table in database.
    """
    CategoryId: Optional[int] = None
    CategoryName: str = ""
    
    def __post_init__(self):
        """Validate and normalize category data after initialization"""
        self.CategoryName = self.NormalizeText(self.CategoryName)
    
    @staticmethod
    def NormalizeText(Text: str) -> str:
        """Normalize text for consistent display and comparison"""
        if not Text:
            return ""
        return str(Text).strip().replace('  ', ' ')
    
    def IsValid(self) -> bool:
        """Check if category has valid data"""
        return bool(self.CategoryName and len(self.CategoryName.strip()) > 0)
    
    def ToDictionary(self) -> Dict[str, Any]:
        """Convert category to dictionary for serialization"""
        return {
            'CategoryId': self.CategoryId,
            'CategoryName': self.CategoryName
        }
    
    @classmethod
    def FromDictionary(cls, Data: Dict[str, Any]) -> 'Category':
        """Create category from dictionary data"""
        return cls(
            CategoryId=Data.get('CategoryId'),
            CategoryName=Data.get('CategoryName', '')
        )
    
    def __str__(self) -> str:
        """String representation for display"""
        return self.CategoryName
    
    def __eq__(self, Other) -> bool:
        """Equality comparison based on normalized name"""
        if not isinstance(Other, Category):
            return False
        return self.CategoryName.lower() == Other.CategoryName.lower()
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries"""
        return hash(self.CategoryName.lower())


@dataclass
class Subject:
    """
    Represents a book subject within a category.
    Maps to subjects table in database.
    """
    SubjectId: Optional[int] = None
    CategoryId: Optional[int] = None
    SubjectName: str = ""
    CategoryName: str = ""  # For display purposes
    
    def __post_init__(self):
        """Validate and normalize subject data after initialization"""
        self.SubjectName = self.NormalizeText(self.SubjectName)
        self.CategoryName = self.NormalizeText(self.CategoryName)
    
    @staticmethod
    def NormalizeText(Text: str) -> str:
        """Normalize text for consistent display and comparison"""
        if not Text:
            return ""
        return str(Text).strip().replace('  ', ' ')
    
    def IsValid(self) -> bool:
        """Check if subject has valid data"""
        return bool(self.SubjectName and len(self.SubjectName.strip()) > 0)
    
    def HasCategory(self) -> bool:
        """Check if subject is associated with a category"""
        return self.CategoryId is not None and self.CategoryId > 0
    
    def ToDictionary(self) -> Dict[str, Any]:
        """Convert subject to dictionary for serialization"""
        return {
            'SubjectId': self.SubjectId,
            'CategoryId': self.CategoryId,
            'SubjectName': self.SubjectName,
            'CategoryName': self.CategoryName
        }
    
    @classmethod
    def FromDictionary(cls, Data: Dict[str, Any]) -> 'Subject':
        """Create subject from dictionary data"""
        return cls(
            SubjectId=Data.get('SubjectId'),
            CategoryId=Data.get('CategoryId'),
            SubjectName=Data.get('SubjectName', ''),
            CategoryName=Data.get('CategoryName', '')
        )
    
    def GetFullName(self) -> str:
        """Get subject name with category for display"""
        if self.CategoryName:
            return f"{self.CategoryName} → {self.SubjectName}"
        return self.SubjectName
    
    def __str__(self) -> str:
        """String representation for display"""
        return self.SubjectName
    
    def __eq__(self, Other) -> bool:
        """Equality comparison based on normalized name and category"""
        if not isinstance(Other, Subject):
            return False
        return (self.SubjectName.lower() == Other.SubjectName.lower() and 
                self.CategoryId == Other.CategoryId)
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries"""
        return hash((self.SubjectName.lower(), self.CategoryId))


@dataclass
class Book:
    """
    Represents a book in Anderson's Library with all metadata.
    Maps to books table in database plus file system information.
    """
    BookId: Optional[int] = None
    Title: str = ""
    CategoryId: Optional[int] = None
    SubjectId: Optional[int] = None
    FileName: str = ""
    FilePath: str = ""
    
    # Display names for UI
    CategoryName: str = ""
    SubjectName: str = ""
    
    # File system information
    FileSize: Optional[int] = None
    FileSizeMB: Optional[float] = None
    LastModified: Optional[datetime] = None
    CoverImagePath: str = ""
    HasCover: bool = False
    
    def __post_init__(self):
        """Validate and normalize book data after initialization"""
        self.Title = self.NormalizeText(self.Title)
        self.FileName = self.NormalizeText(self.FileName)
        self.CategoryName = self.NormalizeText(self.CategoryName)
        self.SubjectName = self.NormalizeText(self.SubjectName)
        
        # Auto-calculate cover image path if not provided
        if not self.CoverImagePath and self.FileName:
            self.CoverImagePath = self.GetCoverImagePath()
            self.HasCover = self.CheckCoverExists()
        
        # Auto-calculate file size in MB if file size is available
        if self.FileSize and not self.FileSizeMB:
            self.FileSizeMB = self.FileSize / (1024 * 1024)
    
    @staticmethod
    def NormalizeText(Text: str) -> str:
        """Normalize text for consistent display and comparison"""
        if not Text:
            return ""
        return str(Text).strip().replace('  ', ' ')
    
    def IsValid(self) -> bool:
        """Check if book has minimum required data"""
        return bool(self.Title and self.FileName)
    
    def HasCategory(self) -> bool:
        """Check if book is assigned to a category"""
        return self.CategoryId is not None and self.CategoryId > 0
    
    def HasSubject(self) -> bool:
        """Check if book is assigned to a subject"""
        return self.SubjectId is not None and self.SubjectId > 0
    
    def GetDisplayTitle(self) -> str:
        """Get title for display, falling back to filename if no title"""
        if self.Title:
            return self.Title
        elif self.FileName:
            return Path(self.FileName).stem  # Remove .pdf extension
        return "Unknown Title"
    
    def GetCoverImagePath(self) -> str:
        """Generate expected cover image path based on filename"""
        if not self.FileName:
            return ""
        
        BaseName = Path(self.FileName).stem
        return f"Anderson eBooks/Covers/{BaseName}.png"
    
    def CheckCoverExists(self) -> bool:
        """Check if cover image file actually exists"""
        if not self.CoverImagePath:
            return False
        return os.path.exists(self.CoverImagePath)
    
    def GetFileSizeDisplay(self) -> str:
        """Get human-readable file size"""
        if self.FileSizeMB:
            if self.FileSizeMB < 1:
                return f"{self.FileSizeMB * 1024:.0f} KB"
            else:
                return f"{self.FileSizeMB:.1f} MB"
        return "Unknown size"
    
    def GetFullPath(self) -> str:
        """Get complete file path for opening"""
        if self.FilePath:
            return self.FilePath
        elif self.FileName:
            return f"Anderson eBooks/{self.FileName}"
        return ""
    
    def FileExists(self) -> bool:
        """Check if the PDF file actually exists"""
        FullPath = self.GetFullPath()
        return bool(FullPath and os.path.exists(FullPath))
    
    def GetCategorySubjectDisplay(self) -> str:
        """Get category and subject for display"""
        if self.CategoryName and self.SubjectName:
            return f"{self.CategoryName} → {self.SubjectName}"
        elif self.CategoryName:
            return self.CategoryName
        elif self.SubjectName:
            return self.SubjectName
        return "Uncategorized"
    
    def ToDictionary(self) -> Dict[str, Any]:
        """Convert book to dictionary for serialization"""
        return {
            'BookId': self.BookId,
            'Title': self.Title,
            'CategoryId': self.CategoryId,
            'SubjectId': self.SubjectId,
            'FileName': self.FileName,
            'FilePath': self.FilePath,
            'CategoryName': self.CategoryName,
            'SubjectName': self.SubjectName,
            'FileSize': self.FileSize,
            'FileSizeMB': self.FileSizeMB,
            'LastModified': self.LastModified.isoformat() if self.LastModified else None,
            'CoverImagePath': self.CoverImagePath,
            'HasCover': self.HasCover
        }
    
    @classmethod
    def FromDictionary(cls, Data: Dict[str, Any]) -> 'Book':
        """Create book from dictionary data"""
        LastModified = None
        if Data.get('LastModified'):
            try:
                LastModified = datetime.fromisoformat(Data['LastModified'])
            except (ValueError, TypeError):
                pass
        
        return cls(
            BookId=Data.get('BookId'),
            Title=Data.get('Title', ''),
            CategoryId=Data.get('CategoryId'),
            SubjectId=Data.get('SubjectId'),
            FileName=Data.get('FileName', ''),
            FilePath=Data.get('FilePath', ''),
            CategoryName=Data.get('CategoryName', ''),
            SubjectName=Data.get('SubjectName', ''),
            FileSize=Data.get('FileSize'),
            FileSizeMB=Data.get('FileSizeMB'),
            LastModified=LastModified,
            CoverImagePath=Data.get('CoverImagePath', ''),
            HasCover=Data.get('HasCover', False)
        )
    
    def __str__(self) -> str:
        """String representation for display"""
        return self.GetDisplayTitle()
    
    def __eq__(self, Other) -> bool:
        """Equality comparison based on filename (unique identifier)"""
        if not isinstance(Other, Book):
            return False
        return self.FileName.lower() == Other.FileName.lower()
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries"""
        return hash(self.FileName.lower())


class ModelValidator:
    """
    Utility class for validating model data and business rules.
    Provides centralized validation logic for all models.
    """
    
    @staticmethod
    def ValidateCategory(CategoryData: Dict[str, Any]) -> List[str]:
        """Validate category data and return list of error messages"""
        Errors = []
        
        CategoryName = CategoryData.get('CategoryName', '').strip()
        if not CategoryName:
            Errors.append("Category name is required")
        elif len(CategoryName) > 100:
            Errors.append("Category name must be 100 characters or less")
        
        return Errors
    
    @staticmethod
    def ValidateSubject(SubjectData: Dict[str, Any]) -> List[str]:
        """Validate subject data and return list of error messages"""
        Errors = []
        
        SubjectName = SubjectData.get('SubjectName', '').strip()
        if not SubjectName:
            Errors.append("Subject name is required")
        elif len(SubjectName) > 100:
            Errors.append("Subject name must be 100 characters or less")
        
        CategoryId = SubjectData.get('CategoryId')
        if CategoryId is not None and (not isinstance(CategoryId, int) or CategoryId < 1):
            Errors.append("Category ID must be a positive integer")
        
        return Errors
    
    @staticmethod
    def ValidateBook(BookData: Dict[str, Any]) -> List[str]:
        """Validate book data and return list of error messages"""
        Errors = []
        
        Title = BookData.get('Title', '').strip()
        FileName = BookData.get('FileName', '').strip()
        
        if not Title and not FileName:
            Errors.append("Either title or filename is required")
        
        if FileName:
            if not FileName.lower().endswith('.pdf'):
                Errors.append("Filename must have .pdf extension")
            elif len(FileName) > 255:
                Errors.append("Filename must be 255 characters or less")
        
        if Title and len(Title) > 500:
            Errors.append("Title must be 500 characters or less")
        
        for IdField in ['CategoryId', 'SubjectId']:
            IdValue = BookData.get(IdField)
            if IdValue is not None and (not isinstance(IdValue, int) or IdValue < 1):
                Errors.append(f"{IdField} must be a positive integer")
        
        return Errors


# Module-level utility functions for common operations
def CreateCategoryFromRow(DatabaseRow: tuple) -> Category:
    """Create Category object from database row tuple"""
    if len(DatabaseRow) >= 2:
        return Category(CategoryId=DatabaseRow[0], CategoryName=DatabaseRow[1])
    return Category()


def CreateSubjectFromRow(DatabaseRow: tuple) -> Subject:
    """Create Subject object from database row tuple"""
    if len(DatabaseRow) >= 3:
        return Subject(
            SubjectId=DatabaseRow[0],
            CategoryId=DatabaseRow[1],
            SubjectName=DatabaseRow[2]
        )
    return Subject()


def CreateBookFromRow(DatabaseRow: tuple) -> Book:
    """Create Book object from database row tuple"""
    if len(DatabaseRow) >= 4:
        return Book(
            BookId=DatabaseRow[0],
            Title=DatabaseRow[1],
            CategoryId=DatabaseRow[2],
            SubjectId=DatabaseRow[3]
        )
    return Book()
