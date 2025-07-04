#!/usr/bin/env python3
# File: AndersonLibrary.py
# Path: AndersonLibrary.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  14:09PM
"""
Description: Anderson's Library - Professional Edition
Main entry point for the modular Anderson's Library application.
Provides clean startup and error handling for the complete application.

Purpose: Serves as the primary executable for Anderson's Library,
coordinating application startup and initialization.
"""

import sys
import os
import logging
from pathlib import Path

# Add Source directory to Python path for imports
SourcePath = Path(__file__).parent / "Source"
sys.path.insert(0, str(SourcePath))

try:
    from Interface.MainWindow import RunApplication
except ImportError as Error:
    print(f"❌ Import Error: {Error}")
    print("📁 Make sure the Source directory structure is complete")
    print("🔧 Run SetupProjectStructure.py to create the proper structure")
    sys.exit(1)


def Main() -> int:
    """
    Main application entry point with error handling.
    
    Returns:
        Application exit code (0 for success, 1 for error)
    """
    try:
        print("🏔️ Starting Anderson's Library - Professional Edition")
        print("📚 Project Himalaya - BowersWorld.com")
        print("=" * 50)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(name)s - %(levelname)s: %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('anderson_library.log', mode='a')
            ]
        )
        
        # Run the application
        ExitCode = RunApplication()
        
        print("👋 Anderson's Library closed successfully")
        return ExitCode
        
    except KeyboardInterrupt:
        print("\n⚠️ Application interrupted by user")
        return 0
        
    except Exception as Error:
        print(f"❌ Critical Error: {Error}")
        logging.exception("Critical application error")
        return 1


if __name__ == "__main__":
    sys.exit(Main())
