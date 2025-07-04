#!/usr/bin/env python3
# File: MigrateToModular.py
# Path: MigrateToModular.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  04:12PM
"""
Description: Anderson's Library Migration Helper
Automates the migration from monolithic Andy.py to the new modular architecture.
Handles file copying, structure creation, and validation.
"""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime

class MigrationHelper:
    """Helps migrate Anderson's Library to modular architecture"""
    
    def __init__(self):
        self.BaseDir = Path(".")
        self.RequiredDirs = [
            "Source",
            "Source/Data", 
            "Source/Core",
            "Source/Interface",
            "Source/Utils",
            "Source/Framework"
        ]
        
        self.RequiredFiles = {
            # Source files that should exist
            "Source/Data/DatabaseModels.py": "Data models and structures",
            "Source/Core/DatabaseManager.py": "Database operations",
            "Source/Core/BookService.py": "Business logic",
            "Source/Interface/FilterPanel.py": "Search and filter UI",
            "Source/Interface/BookGrid.py": "Book display grid",
            "Source/Interface/MainWindow.py": "Main application window"
        }
        
        self.InitFiles = [
            "Source/__init__.py",
            "Source/Data/__init__.py", 
            "Source/Core/__init__.py",
            "Source/Interface/__init__.py",
            "Source/Utils/__init__.py",
            "Source/Framework/__init__.py"
        ]
    
    def PrintHeader(self):
        """Print migration header"""
        print("🏔️ Anderson's Library - Modular Migration")
        print("=" * 50)
        print("📚 Migrating to Professional Architecture")
        print("🎯 Design Standard v1.8 Compliant")
        print("⚡ From Monolithic to Modular")
        print("=" * 50)
    
    def CreateDirectories(self):
        """Create required directory structure"""
        print("\n📁 Creating directory structure...")
        
        for Dir in self.RequiredDirs:
            DirPath = self.BaseDir / Dir
            if not DirPath.exists():
                DirPath.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ Created: {Dir}")
            else:
                print(f"   ✅ Exists: {Dir}")
    
    def CreateInitFiles(self):
        """Create __init__.py files for Python packages"""
        print("\n📄 Creating __init__.py files...")
        
        InitContents = {
            "Source/__init__.py": '''"""Anderson's Library Source Package"""
__version__ = "1.0.0"
__author__ = "Herb Bowers"
''',
            "Source/Data/__init__.py": '''"""Data Layer Package"""
from .DatabaseModels import BookRecord, SearchCriteria, SearchResult
__all__ = ['BookRecord', 'SearchCriteria', 'SearchResult']
''',
            "Source/Core/__init__.py": '''"""Core Services Package"""
from .DatabaseManager import DatabaseManager
from .BookService import BookService
__all__ = ['DatabaseManager', 'BookService']
''',
            "Source/Interface/__init__.py": '''"""User Interface Package"""
from .MainWindow import AndersonMainWindow, RunApplication
__all__ = ['AndersonMainWindow', 'RunApplication']
''',
            "Source/Utils/__init__.py": '''"""Utilities Package"""
__all__ = []
''',
            "Source/Framework/__init__.py": '''"""Framework Package"""
__all__ = []
'''
        }
        
        for InitFile in self.InitFiles:
            InitPath = self.BaseDir / InitFile
            if not InitPath.exists():
                Content = InitContents.get(InitFile, '"""Package init file"""')
                InitPath.write_text(Content)
                print(f"   ✅ Created: {InitFile}")
            else:
                print(f"   ✅ Exists: {InitFile}")
    
    def CopyCustomWindow(self):
        """Copy existing CustomWindow.py to new location"""
        print("\n🪟 Copying CustomWindow.py...")
        
        # Look for existing CustomWindow.py
        PossiblePaths = [
            "CustomWindow.py",
            "./CustomWindow.py", 
            "../CustomWindow.py"
        ]
        
        SourcePath = None
        for Path in PossiblePaths:
            if os.path.exists(Path):
                SourcePath = Path
                break
        
        if SourcePath:
            DestPath = "Source/Interface/CustomWindow.py"
            try:
                shutil.copy2(SourcePath, DestPath)
                print(f"   ✅ Copied: {SourcePath} → {DestPath}")
                
                # Update the header in the copied file
                self.UpdateFileHeader(DestPath)
                
            except Exception as Error:
                print(f"   ❌ Failed to copy: {Error}")
                return False
        else:
            print("   ⚠️  CustomWindow.py not found in current directory")
            print("   💡 Please copy it manually to Source/Interface/CustomWindow.py")
            return False
        
        return True
    
    def UpdateFileHeader(self, FilePath):
        """Update file header to match Design Standard v1.8"""
        try:
            with open(FilePath, 'r', encoding='utf-8') as File:
                Content = File.read()
            
            # Simple header update - just add if missing
            if "# File:" not in Content and "# Path:" not in Content:
                FileName = os.path.basename(FilePath)
                HeaderComment = f'''# File: {FileName}
# Path: {FilePath}
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  04:12PM
"""
Description: {FileName.replace('.py', '')} - BowersWorld Framework Component
Migrated from monolithic architecture to modular design.
"""

'''
                Content = HeaderComment + Content
                
                with open(FilePath, 'w', encoding='utf-8') as File:
                    File.write(Content)
                
                print(f"   📝 Updated header in {FileName}")
                
        except Exception as Error:
            print(f"   ⚠️  Could not update header: {Error}")
    
    def ValidateStructure(self):
        """Validate the migrated structure"""
        print("\n🔍 Validating migration...")
        
        Issues = []
        
        # Check directories
        for Dir in self.RequiredDirs:
            if not (self.BaseDir / Dir).exists():
                Issues.append(f"Missing directory: {Dir}")
        
        # Check required files (that should have been created by artifacts)
        for File, Description in self.RequiredFiles.items():
            if not (self.BaseDir / File).exists():
                Issues.append(f"Missing file: {File} ({Description})")
        
        # Check CustomWindow
        if not (self.BaseDir / "Source/Interface/CustomWindow.py").exists():
            Issues.append("Missing CustomWindow.py - copy manually")
        
        # Check database
        DatabasePaths = [
            "Assets/my_library.db",
            "Data/my_library.db",
            "Data/Databases/my_library.db" 
        ]
        
        DatabaseFound = any(os.path.exists(Path) for Path in DatabasePaths)
        if not DatabaseFound:
            Issues.append("Database file not found")
        
        if Issues:
            print("   ❌ Validation Issues:")
            for Issue in Issues:
                print(f"      • {Issue}")
            return False
        else:
            print("   ✅ Migration validation passed!")
            return True
    
    def CreateEntryPoint(self):
        """Create the new entry point script"""
        print("\n🚀 Creating entry point...")
        
        EntryScript = "AndersonLibrary.py"
        if not os.path.exists(EntryScript):
            print(f"   ⚠️  {EntryScript} not found")
            print("   💡 Use the AndersonLibrary.py artifact from this session")
        else:
            print(f"   ✅ Entry point ready: {EntryScript}")
    
    def PrintNextSteps(self):
        """Print next steps for user"""
        print("\n" + "=" * 50)
        print("✅ MIGRATION HELPER COMPLETE")
        print("=" * 50)
        print("📋 Next Steps:")
        print("   1. Copy the 4 main module files from the artifacts:")
        print("      • DatabaseModels.py → Source/Data/")
        print("      • FilterPanel.py → Source/Interface/")
        print("      • BookGrid.py → Source/Interface/")
        print("      • MainWindow.py → Source/Interface/")
        print("   2. Copy AndersonLibrary.py to project root")
        print("   3. Install dependencies: pip install -r requirements.txt")
        print("   4. Run: python AndersonLibrary.py")
        print("=" * 50)
        print("🎉 Welcome to Professional Architecture!")
    
    def RunMigration(self):
        """Run the complete migration process"""
        self.PrintHeader()
        
        # Create structure
        self.CreateDirectories()
        self.CreateInitFiles()
        
        # Copy existing files
        self.CopyCustomWindow()
        
        # Create entry point
        self.CreateEntryPoint()
        
        # Validate
        IsValid = self.ValidateStructure()
        
        # Print next steps
        self.PrintNextSteps()
        
        return IsValid

def Main():
    """Main migration entry point"""
    try:
        Helper = MigrationHelper()
        Success = Helper.RunMigration()
        return 0 if Success else 1
        
    except Exception as Error:
        print(f"❌ Migration failed: {Error}")
        return 1

if __name__ == "__main__":
    sys.exit(Main())