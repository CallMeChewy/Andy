#!/usr/bin/env python3
# File: AndersonLibrary.py
# Path: AndersonLibrary.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  04:12PM
"""
Description: Anderson's Library - Professional Edition Entry Point
Main entry point for the modular Anderson's Library application.
Replaces the old Andy.py and RunAnderson.py scripts.
"""

import sys
import os
import logging
from pathlib import Path

def ValidateEnvironment():
    """
    Validate that all required files and dependencies are present.
    Returns (IsValid, ErrorMessages)
    """
    Errors = []
    
    print("🏔️ Anderson's Library - Professional Edition")
    print("=" * 50)
    print("📚 Digital Library Management System")
    print("🎯 Project Himalaya - BowersWorld.com")
    print("⚡ Modular Architecture - Design Standard v1.8")
    print("=" * 50)
    
    # Check for required files
    RequiredFiles = [
        "Source/Data/DatabaseModels.py",
        "Source/Core/DatabaseManager.py",
        "Source/Core/BookService.py",
        "Source/Interface/FilterPanel.py",
        "Source/Interface/BookGrid.py",
        "Source/Interface/MainWindow.py",
        "Source/Interface/CustomWindow.py"
    ]
    
    print("📁 Checking file structure...")
    MissingFiles = []
    for FilePath in RequiredFiles:
        if os.path.exists(FilePath):
            print(f"   ✅ {FilePath}")
        else:
            print(f"   ❌ {FilePath}")
            MissingFiles.append(FilePath)
    
    if MissingFiles:
        Errors.append(f"Missing files: {', '.join(MissingFiles)}")
    
    print(f"📊 Files: {len(RequiredFiles) - len(MissingFiles)} present, {len(MissingFiles)} missing")
    
    if MissingFiles:
        print("📋 Missing files:")
        for File in MissingFiles:
            print(f"   📄 {File}")
        
        if "Source/Interface/CustomWindow.py" in MissingFiles:
            print("💡 Don't forget to copy your existing CustomWindow.py!")
    
    # Check for database
    DatabasePaths = [
        "Assets/my_library.db",
        "Data/my_library.db", 
        "Data/Databases/my_library.db",
        "my_library.db"
    ]
    
    print("🗄️  Testing database connection...")
    DatabaseFound = False
    for DbPath in DatabasePaths:
        if os.path.exists(DbPath):
            print(f"   ✅ Found database: {DbPath}")
            DatabaseFound = True
            break
    
    if not DatabaseFound:
        print("   ❌ No database file found")
        Errors.append("Database file not found")
    
    # Check Python dependencies
    print("🐍 Testing Python imports...")
    try:
        import PySide6
        print("   ✅ PySide6 available")
    except ImportError:
        print("   ❌ PySide6 not installed")
        Errors.append("PySide6 not installed - run: pip install PySide6")
    
    print("=" * 50)
    
    if Errors:
        print("❌ VALIDATION ISSUES FOUND")
        print("📝 Please resolve the issues above before running the application")
        for Error in Errors:
            print(f"   • {Error}")
        print("=" * 50)
        return False, Errors
    else:
        print("✅ ENVIRONMENT VALIDATION PASSED")
        print("🚀 Starting Anderson's Library...")
        print("=" * 50)
        return True, []

def SetupPythonPath():
    """Add current directory to Python path for imports"""
    CurrentDir = os.path.dirname(os.path.abspath(__file__))
    if CurrentDir not in sys.path:
        sys.path.insert(0, CurrentDir)

def Main():
    """Main entry point"""
    try:
        # Validate environment first
        IsValid, Errors = ValidateEnvironment()
        if not IsValid:
            print("\n💡 Run TestImports.py to diagnose issues")
            return 1
        
        # Setup Python path
        SetupPythonPath()
        
        # Import and run the application
        from Source.Interface.MainWindow import RunApplication
        return RunApplication()
        
    except ImportError as Error:
        print(f"❌ Import Error: {Error}")
        print("💡 Make sure all required files are in place")
        print("💡 Run TestImports.py to diagnose import issues")
        return 1
        
    except Exception as Error:
        print(f"❌ Startup Error: {Error}")
        logging.error(f"Application startup failed: {Error}")
        return 1

if __name__ == "__main__":
    sys.exit(Main())