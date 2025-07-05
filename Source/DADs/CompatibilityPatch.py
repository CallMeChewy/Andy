#!/usr/bin/env python3
# File: CompatibilityPatch.py
# Path: CompatibilityPatch.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  05:25PM
"""
Description: Compatibility Patch for Anderson's Library DatabaseModels
Adds missing legacy compatibility functions to DatabaseModels.py to support
the transition from old monolithic code to new modular architecture.
"""

import os
import sys
from pathlib import Path

def ApplyCompatibilityPatch():
    """Apply compatibility patch to DatabaseModels.py"""
    
    print("🔧 Anderson's Library - Compatibility Patch")
    print("=" * 50)
    print("📄 Adding legacy function support to DatabaseModels.py")
    
    DatabaseModelsPath = "Source/Data/DatabaseModels.py"
    
    # Check if file exists
    if not os.path.exists(DatabaseModelsPath):
        print(f"❌ File not found: {DatabaseModelsPath}")
        return False
    
    # Read current content
    try:
        with open(DatabaseModelsPath, 'r', encoding='utf-8') as File:
            Content = File.read()
    except Exception as Error:
        print(f"❌ Error reading file: {Error}")
        return False
    
    # Check if already patched
    if "CreateCategoryFromRow" in Content and "def CreateCategoryFromRow" in Content:
        print("✅ Already patched - compatibility functions found")
        return True
    
    # Compatibility functions to add
    CompatibilityFunctions = '''

# ================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# ================================================================
# These functions provide compatibility with the old monolithic code
# that expects specific function names and signatures.

def CreateCategoryFromRow(Data: Dict[str, Any]) -> CategoryInfo:
    """
    Legacy compatibility function to create CategoryInfo from database row.
    Maps old database row format to new CategoryInfo dataclass.
    """
    try:
        return CategoryInfo(
            Name=str(Data.get('Name', Data.get('Category', Data.get('name', '')))),
            BookCount=int(Data.get('BookCount', Data.get('Count', Data.get('count', 0)))),
            ParentCategory=str(Data.get('ParentCategory', Data.get('parent', ''))),
            Description=str(Data.get('Description', Data.get('description', ''))),
            DisplayOrder=int(Data.get('DisplayOrder', Data.get('order', 0)))
        )
    except Exception as Error:
        logging.error(f"Error creating CategoryInfo from data: {Error}")
        return CategoryInfo()


def CreateSubjectFromRow(Data: Dict[str, Any]) -> CategoryInfo:
    """
    Legacy compatibility function to create Subject (CategoryInfo) from database row.
    Subjects are treated as categories in the new architecture.
    """
    try:
        return CategoryInfo(
            Name=str(Data.get('Subject', Data.get('Name', Data.get('subject', '')))),
            BookCount=int(Data.get('BookCount', Data.get('Count', Data.get('count', 0)))),
            ParentCategory=str(Data.get('ParentSubject', Data.get('parent', ''))),
            Description=str(Data.get('Description', Data.get('description', ''))),
            DisplayOrder=int(Data.get('DisplayOrder', Data.get('order', 0)))
        )
    except Exception as Error:
        logging.error(f"Error creating Subject from data: {Error}")
        return CategoryInfo()


def CreateAuthorFromRow(Data: Dict[str, Any]) -> str:
    """
    Legacy compatibility function to extract author name from database row.
    Returns the author name as a simple string.
    """
    try:
        return str(Data.get('Author', Data.get('author', Data.get('Name', '')))
    except Exception as Error:
        logging.error(f"Error extracting author from data: {Error}")
        return ""


def GetBookById(BookId: int, Books: List[BookRecord]) -> Optional[BookRecord]:
    """
    Legacy compatibility function to find a book by ID.
    Searches through a list of BookRecord objects.
    """
    try:
        for Book in Books:
            if Book.Id == BookId:
                return Book
        return None
    except Exception as Error:
        logging.error(f"Error finding book by ID {BookId}: {Error}")
        return None


def GetBooksByCategory(Category: str, Books: List[BookRecord]) -> List[BookRecord]:
    """
    Legacy compatibility function to filter books by category.
    Returns all books matching the specified category.
    """
    try:
        return [Book for Book in Books if Book.Category.lower() == Category.lower()]
    except Exception as Error:
        logging.error(f"Error filtering books by category {Category}: {Error}")
        return []


def GetBooksByAuthor(Author: str, Books: List[BookRecord]) -> List[BookRecord]:
    """
    Legacy compatibility function to filter books by author.
    Returns all books by the specified author.
    """
    try:
        return [Book for Book in Books if Author.lower() in Book.Author.lower()]
    except Exception as Error:
        logging.error(f"Error filtering books by author {Author}: {Error}")
        return []


def FormatFileSize(SizeBytes: int) -> str:
    """
    Legacy compatibility function for file size formatting.
    Alias for BookRecord.GetFileSizeFormatted() method.
    """
    try:
        if SizeBytes < 1024:
            return f"{SizeBytes} bytes"
        elif SizeBytes < 1024 * 1024:
            return f"{SizeBytes / 1024:.1f} KB"
        elif SizeBytes < 1024 * 1024 * 1024:
            return f"{SizeBytes / (1024 * 1024):.1f} MB"
        else:
            return f"{SizeBytes / (1024 * 1024 * 1024):.1f} GB"
    except Exception as Error:
        logging.error(f"Error formatting file size {SizeBytes}: {Error}")
        return "Unknown"


def ValidateBookData(Data: Dict[str, Any]) -> bool:
    """
    Legacy compatibility function to validate book data dictionary.
    Checks if required fields are present and valid.
    """
    try:
        RequiredFields = ['Title', 'FileName', 'FilePath']
        for Field in RequiredFields:
            if Field not in Data or not Data[Field]:
                return False
        return True
    except Exception as Error:
        logging.error(f"Error validating book data: {Error}")
        return False


# ================================================================
# ADDITIONAL COMPATIBILITY ALIASES
# ================================================================

# Function aliases for different naming conventions
CreateBookFromDict = CreateBookRecordFromDict  # Alternative alias
CreateCategoryFromDict = CreateCategoryFromRow  # Dict vs Row naming
CreateSubjectFromDict = CreateSubjectFromRow    # Dict vs Row naming

# Class aliases for old naming conventions  
BookData = BookRecord           # Alternative class name
CategoryData = CategoryInfo     # Alternative class name
SubjectData = CategoryInfo      # Alternative class name
LibraryStats = LibraryStatistics # Shorter alias

# Legacy constants that might be expected
DEFAULT_CATEGORY = "Uncategorized"
DEFAULT_LANGUAGE = "English"
DEFAULT_FILE_FORMAT = "PDF"
MAX_RATING = 5
MIN_RATING = 0
'''

    # Add the compatibility functions to the end of the file
    NewContent = Content + CompatibilityFunctions
    
    # Write back to file
    try:
        with open(DatabaseModelsPath, 'w', encoding='utf-8') as File:
            File.write(NewContent)
        
        print("✅ Compatibility patch applied successfully!")
        print("📝 Added the following legacy functions:")
        print("   • CreateCategoryFromRow")
        print("   • CreateSubjectFromRow") 
        print("   • CreateAuthorFromRow")
        print("   • GetBookById")
        print("   • GetBooksByCategory")
        print("   • GetBooksByAuthor")
        print("   • FormatFileSize")
        print("   • ValidateBookData")
        print("📝 Added compatibility aliases:")
        print("   • CreateBookFromDict")
        print("   • CreateCategoryFromDict")
        print("   • CreateSubjectFromDict")
        print("   • BookData, CategoryData, SubjectData")
        print("   • LibraryStats")
        
        return True
        
    except Exception as Error:
        print(f"❌ Error writing patched file: {Error}")
        return False


def ValidatePatch():
    """Validate that the patch was applied correctly"""
    print("\n🔍 Validating patch...")
    
    DatabaseModelsPath = "Source/Data/DatabaseModels.py"
    
    try:
        with open(DatabaseModelsPath, 'r', encoding='utf-8') as File:
            Content = File.read()
        
        # Check for key functions
        RequiredFunctions = [
            "def CreateCategoryFromRow",
            "def CreateSubjectFromRow", 
            "def CreateAuthorFromRow",
            "CreateBookFromRow =",  # Alias
            "BookData =",           # Alias
        ]
        
        Missing = []
        for Function in RequiredFunctions:
            if Function not in Content:
                Missing.append(Function)
        
        if Missing:
            print("⚠️  Some functions may be missing:")
            for Func in Missing:
                print(f"   • {Func}")
            return False
        else:
            print("✅ All compatibility functions verified!")
            return True
            
    except Exception as Error:
        print(f"❌ Error validating patch: {Error}")
        return False


def BackupOriginal():
    """Create backup of original file"""
    DatabaseModelsPath = "Source/Data/DatabaseModels.py"
    BackupPath = "Source/Data/DatabaseModels_backup.py"
    
    try:
        if os.path.exists(DatabaseModelsPath) and not os.path.exists(BackupPath):
            import shutil
            shutil.copy2(DatabaseModelsPath, BackupPath)
            print(f"💾 Backup created: {BackupPath}")
            return True
    except Exception as Error:
        print(f"⚠️  Could not create backup: {Error}")
        return False


def Main():
    """Main patch application"""
    print("🏔️ Anderson's Library - Compatibility Patch")
    print("=" * 50)
    print("🎯 Adding legacy function support for smooth migration")
    print("=" * 50)
    
    # Create backup first
    BackupOriginal()
    
    # Apply patch
    if ApplyCompatibilityPatch():
        # Validate patch
        if ValidatePatch():
            print("\n" + "=" * 50)
            print("🎉 PATCH APPLIED SUCCESSFULLY!")
            print("=" * 50)
            print("🚀 Now try running: python AndersonLibrary.py")
            print("💡 Your legacy code should now work with the new modular architecture!")
            return 0
        else:
            print("\n⚠️  Patch applied but validation failed")
            return 1
    else:
        print("\n❌ Patch application failed")
        return 1


if __name__ == "__main__":
    sys.exit(Main())