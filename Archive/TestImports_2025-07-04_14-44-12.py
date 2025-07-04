#!/usr/bin/env python3
# File: TestImports.py
# Path: TestImports.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  16:30PM
"""
Description: Anderson's Library Module Import Test
Tests that all modular components can be imported correctly after migration.
Validates the new professional architecture is properly configured.

Purpose: Provides quick validation that the modular refactor was successful
and all components are accessible for the Anderson's Library application.
"""

import sys
import os
from pathlib import Path

def TestImports():
    """Test that all modules can be imported successfully"""
    print("🧪 Testing Anderson's Library Module Imports")
    print("=" * 50)
    
    # Add Source to Python path
    SourcePath = Path(__file__).parent / "Source"
    if SourcePath.exists():
        sys.path.insert(0, str(SourcePath))
        print(f"✅ Added to path: {SourcePath}")
    else:
        print(f"❌ Source directory not found: {SourcePath}")
        print("📁 Make sure you've run the setup scripts first")
        return False
    
    print("\n🔍 Testing module imports...")
    
    # Define modules to test with their expected classes
    TestModules = [
        ("Data.DatabaseModels", ["Book", "Category", "Subject"], "Data models"),
        ("Core.DatabaseManager", ["DatabaseManager"], "Database operations"),
        ("Core.BookService", ["BookService"], "Business logic"),
        ("Interface.FilterPanel", ["FilterPanel"], "Filter sidebar"),
        ("Interface.BookGrid", ["BookGrid"], "Book display grid"),
        ("Interface.MainWindow", ["MainWindow"], "Main application window")
    ]
    
    SuccessCount = 0
    FailedCount = 0
    
    for ModuleName, Classes, Description in TestModules:
        try:
            # Test module import
            Module = __import__(ModuleName, fromlist=Classes)
            
            # Test class imports
            MissingClasses = []
            for ClassName in Classes:
                if not hasattr(Module, ClassName):
                    MissingClasses.append(ClassName)
            
            if MissingClasses:
                print(f"   ⚠️  {ModuleName}: Missing classes {MissingClasses}")
                FailedCount += 1
            else:
                print(f"   ✅ {ModuleName} - {Description}")
                SuccessCount += 1
                
        except ImportError as Error:
            print(f"   ❌ {ModuleName}: {Error}")
            FailedCount += 1
        except Exception as Error:
            print(f"   ❌ {ModuleName}: Unexpected error - {Error}")
            FailedCount += 1
    
    # Test CustomWindow import (user's existing file)
    try:
        from Interface.CustomWindow import CustomWindow
        print(f"   ✅ Interface.CustomWindow - Custom window framework")
        SuccessCount += 1
    except ImportError as Error:
        print(f"   ⚠️  Interface.CustomWindow: {Error}")
        print(f"      💡 Copy your CustomWindow.py to Source/Interface/")
        FailedCount += 1
    
    # Generate summary
    print("\n" + "=" * 50)
    print("📊 IMPORT TEST RESULTS")
    print("=" * 50)
    print(f"✅ Successful imports: {SuccessCount}")
    print(f"❌ Failed imports: {FailedCount}")
    
    if FailedCount == 0:
        print("\n🎉 ALL IMPORTS SUCCESSFUL!")
        print("🚀 Ready to run: python RunAnderson.py")
        print("📚 Your modular Anderson's Library is ready!")
        return True
    else:
        print(f"\n⚠️  {FailedCount} imports failed")
        print("\n🔧 TROUBLESHOOTING:")
        
        if FailedCount == len(TestModules) + 1:
            print("   📁 Check that Source/ directory structure exists")
            print("   📄 Verify all modules are in correct locations")
            print("   🏗️ Run setup scripts if needed")
        else:
            print("   📄 Check file locations match the expected structure:")
            print("      • Source/Data/DatabaseModels.py")
            print("      • Source/Core/DatabaseManager.py")
            print("      • Source/Core/BookService.py") 
            print("      • Source/Interface/FilterPanel.py")
            print("      • Source/Interface/BookGrid.py")
            print("      • Source/Interface/MainWindow.py")
            print("      • Source/Interface/CustomWindow.py")
        
        return False

def CheckFileStructure():
    """Check if all expected files are present"""
    print("\n📁 Checking file structure...")
    
    ExpectedFiles = [
        "Source/Data/DatabaseModels.py",
        "Source/Core/DatabaseManager.py", 
        "Source/Core/BookService.py",
        "Source/Interface/FilterPanel.py",
        "Source/Interface/BookGrid.py",
        "Source/Interface/MainWindow.py",
        "Source/Interface/CustomWindow.py"
    ]
    
    MissingFiles = []
    PresentFiles = []
    
    for FilePath in ExpectedFiles:
        if os.path.exists(FilePath):
            PresentFiles.append(FilePath)
            print(f"   ✅ {FilePath}")
        else:
            MissingFiles.append(FilePath)
            print(f"   ❌ {FilePath}")
    
    print(f"\n📊 Files: {len(PresentFiles)} present, {len(MissingFiles)} missing")
    
    if MissingFiles:
        print("\n📋 Missing files:")
        for File in MissingFiles:
            print(f"   📄 {File}")
        
        if "Source/Interface/CustomWindow.py" in MissingFiles:
            print("\n💡 Don't forget to copy your existing CustomWindow.py!")
    
    return len(MissingFiles) == 0

def TestDatabaseConnection():
    """Test database connection if possible"""
    print("\n🗄️  Testing database connection...")
    
    DatabasePaths = [
        "Assets/my_library.db",
        "Data/Databases/my_library.db", 
        "my_library.db"
    ]
    
    DatabaseFound = False
    for DbPath in DatabasePaths:
        if os.path.exists(DbPath):
            print(f"   ✅ Found database: {DbPath}")
            DatabaseFound = True
            break
    
    if not DatabaseFound:
        print("   ⚠️  No database found at expected locations:")
        for DbPath in DatabasePaths:
            print(f"      📄 {DbPath}")
        print("   💡 Make sure your SQLite database is accessible")
    
    return DatabaseFound

def Main():
    """Main test execution"""
    try:
        print("🏔️ Anderson's Library - Professional Edition")
        print("Import Validation Test")
        print()
        
        # Check file structure first
        FilesOk = CheckFileStructure()
        
        # Test imports
        ImportsOk = TestImports()
        
        # Test database
        DatabaseOk = TestDatabaseConnection()
        
        # Final status
        print("\n" + "=" * 50)
        if FilesOk and ImportsOk:
            print("🎉 MIGRATION VALIDATION SUCCESSFUL!")
            print("✅ All modules imported correctly")
            print("✅ File structure is correct")
            if DatabaseOk:
                print("✅ Database found")
            print("\n🚀 Ready to run your professional Anderson's Library!")
            print("   python RunAnderson.py")
        else:
            print("❌ VALIDATION ISSUES FOUND")
            print("📝 Please resolve the issues above before running the application")
        
        print("=" * 50)
        
        return FilesOk and ImportsOk
        
    except Exception as Error:
        print(f"❌ Test failed with error: {Error}")
        return False

if __name__ == "__main__":
    Success = Main()
    sys.exit(0 if Success else 1)
