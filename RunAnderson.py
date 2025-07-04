#!/usr/bin/env python3
# File: RunAnderson.py
# Path: RunAnderson.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  16:35PM
"""
Description: Anderson's Library - Professional Edition Launcher
Main entry point for the modular Anderson's Library application.
Provides clean startup and comprehensive error handling.

Purpose: Serves as the primary executable for Anderson's Library,
coordinating application startup and initialization with professional error handling.
"""

import sys
import os
import logging
from pathlib import Path

def SetupPythonPath():
    """Add Source directory to Python path for imports"""
    SourcePath = Path(__file__).parent / "Source"
    if SourcePath.exists():
        sys.path.insert(0, str(SourcePath))
        return True
    else:
        print(f"❌ Source directory not found: {SourcePath}")
        print("📁 Make sure the modular structure is set up correctly")
        return False

def ConfigureLogging():
    """Set up logging for the application"""
    try:
        # Create logs directory if it doesn't exist
        LogsDir = Path("Logs")
        LogsDir.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(name)s - %(levelname)s: %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(LogsDir / 'anderson_library.log', mode='a')
            ]
        )
        
        return True
    except Exception as Error:
        print(f"⚠️ Could not configure logging: {Error}")
        # Continue without file logging
        logging.basicConfig(level=logging.INFO)
        return False

def ValidateEnvironment():
    """Validate the environment before starting"""
    Issues = []
    
    # Check for required directories
    RequiredDirs = ["Source", "Source/Data", "Source/Core", "Source/Interface"]
    for Dir in RequiredDirs:
        if not Path(Dir).exists():
            Issues.append(f"Missing directory: {Dir}")
    
    # Check for essential files
    EssentialFiles = [
        "Source/Data/DatabaseModels.py",
        "Source/Core/DatabaseManager.py",
        "Source/Core/BookService.py",
        "Source/Interface/MainWindow.py"
    ]
    
    for File in EssentialFiles:
        if not Path(File).exists():
            Issues.append(f"Missing file: {File}")
    
    # Check for database
    DatabasePaths = [
        "Assets/my_library.db",
        "Data/Databases/my_library.db",
        "my_library.db"
    ]
    
    DatabaseFound = any(Path(db).exists() for db in DatabasePaths)
    if not DatabaseFound:
        Issues.append("No database found at expected locations")
    
    return Issues

def ShowStartupBanner():
    """Display startup banner"""
    print("🏔️ Anderson's Library - Professional Edition")
    print("=" * 50)
    print("📚 Digital Library Management System")
    print("🎯 Project Himalaya - BowersWorld.com")
    print("⚡ Modular Architecture - Design Standard v1.8")
    print("=" * 50)

def Main() -> int:
    """
    Main application entry point with comprehensive error handling.
    
    Returns:
        Application exit code (0 for success, 1 for error)
    """
    try:
        # Show startup banner
        ShowStartupBanner()
        
        # Set up Python path
        if not SetupPythonPath():
            return 1
        
        # Configure logging
        ConfigureLogging()
        
        # Validate environment
        Issues = ValidateEnvironment()
        if Issues:
            print("❌ Environment validation failed:")
            for Issue in Issues:
                print(f"   • {Issue}")
            print("\n💡 Run TestImports.py to diagnose issues")
            return 1
        
        print("✅ Environment validation passed")
        print("🚀 Starting Anderson's Library...")
        print()
        
        # Import and run the application
        try:
            from Interface.MainWindow import RunApplication
        except ImportError as Error:
            print(f"❌ Failed to import MainWindow: {Error}")
            print("📝 Make sure all modules are in the correct locations")
            print("🧪 Run TestImports.py for detailed diagnostics")
            return 1
        
        # Run the application
        print("📖 Launching Anderson's Library interface...")
        ExitCode = RunApplication()
        
        print("\n👋 Anderson's Library closed successfully")
        logging.info("Application closed normally")
        return ExitCode
        
    except KeyboardInterrupt:
        print("\n⚠️ Application interrupted by user")
        logging.info("Application interrupted by user")
        return 0
        
    except Exception as Error:
        print(f"\n❌ Critical Error: {Error}")
        logging.exception("Critical application error")
        print("\n🔧 Troubleshooting suggestions:")
        print("   • Check that all module files are present")
        print("   • Verify database file exists and is accessible")
        print("   • Run TestImports.py for detailed diagnostics")
        print("   • Check the log file in Logs/anderson_library.log")
        return 1

def ShowUsage():
    """Show usage information"""
    print("📚 Anderson's Library - Professional Edition")
    print()
    print("USAGE:")
    print("  python RunAnderson.py")
    print()
    print("REQUIREMENTS:")
    print("  • Python 3.8+")
    print("  • PySide6")
    print("  • SQLite database (my_library.db)")
    print("  • Complete modular source structure")
    print()
    print("DIAGNOSTICS:")
    print("  python TestImports.py    - Test module imports")
    print()
    print("SETUP:")
    print("  python QuickSetup.py     - Create basic structure")
    print()
    print("For more information, see README.md")

if __name__ == "__main__":
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', 'help']:
            ShowUsage()
            sys.exit(0)
        elif sys.argv[1] in ['-v', '--version', 'version']:
            print("Anderson's Library Professional Edition v2.0")
            print("Built with Design Standard v1.8")
            sys.exit(0)
    
    # Run the application
    ExitCode = Main()
    sys.exit(ExitCode)
