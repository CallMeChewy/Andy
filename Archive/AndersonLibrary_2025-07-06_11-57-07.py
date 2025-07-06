#!/usr/bin/env python3
# File: AndersonLibrary.py
# Path: AndersonLibrary.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  01:34PM
"""
Description: Anderson's Library - Professional Edition Entry Point
Main launcher using standard Qt design (no CustomWindow dependency).
Clean, simple, and maintainable application entry point.
"""

import sys
import os
from pathlib import Path

def main():
    """Main application entry point"""
    
    print("🏔️ Anderson's Library - Professional Edition")
    print("=" * 50)
    print("📚 Digital Library Management System")
    print("🎯 Project Himalaya - BowersWorld.com")
    print("⚡ Standard Qt Design - Design Standard v1.8")
    print("=" * 50)
    
    # Validate file structure
    print("📁 Checking file structure...")
    
    required_files = [
        "Source/Data/DatabaseModels.py",
        "Source/Core/DatabaseManager.py", 
        "Source/Core/BookService.py",
        "Source/Interface/FilterPanel.py",
        "Source/Interface/BookGrid.py",
        "Source/Interface/MainWindow.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f" ✅ {file_path}")
        else:
            print(f" ❌ {file_path}")
            missing_files.append(file_path)
    
    print(f"📊 Files: {len(required_files) - len(missing_files)} present, {len(missing_files)} missing")
    
    if missing_files:
        print("\n❌ Missing required files:")
        for file_path in missing_files:
            print(f"   • {file_path}")
        print("\n💡 Please ensure all required files are in place")
        return 1
    
    # Check database
    print("🗄️ Testing database connection...")
    db_path = "Assets/my_library.db"
    if Path(db_path).exists():
        print(f" ✅ Found database: {db_path}")
    else:
        print(f" ❌ Database not found: {db_path}")
        print("💡 Please ensure the database file exists")
        return 1
    
    # Test Python imports
    print("🐍 Testing Python imports...")
    try:
        from PySide6.QtWidgets import QApplication
        print(" ✅ PySide6 available")
    except ImportError as e:
        print(f" ❌ PySide6 import failed: {e}")
        print("💡 Install with: pip install PySide6")
        return 1
    
    print("=" * 50)
    print("✅ ENVIRONMENT VALIDATION PASSED")
    print("🚀 Starting Anderson's Library...")
    print("=" * 50)
    
    # Import and run the application
    try:
        # Add project root to Python path so Source modules can import each other
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        # Import and run main window
        from Source.Interface.MainWindow import RunApplication
        
        return RunApplication()
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure all required files are in place")
        return 1
    except Exception as e:
        print(f"❌ Application Error: {e}")
        print("💡 Check the application logs for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())
