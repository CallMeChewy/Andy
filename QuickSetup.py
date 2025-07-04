#!/usr/bin/env python3
# File: QuickSetup.py
# Path: QuickSetup.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  16:20PM
"""
Description: Quick Setup for Anderson's Library Migration
Fast setup script to create minimal structure for immediate migration testing.
Gets you running with the new modular architecture in under 60 seconds.

Purpose: Creates just the essential directories and __init__.py files needed
to test the new modular architecture right away.
"""

import os
from pathlib import Path


def CreateQuickStructure():
    """Create minimal structure for immediate testing"""
    print("🚀 Anderson's Library - Quick Migration Setup")
    print("=" * 50)
    
    # Essential directories
    Directories = [
        "Source",
        "Source/Data", 
        "Source/Core",
        "Source/Interface"
    ]
    
    # Create directories
    print("📁 Creating directories...")
    for Dir in Directories:
        Path(Dir).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {Dir}")
    
    # Create essential __init__.py files
    print("\n📄 Creating __init__.py files...")
    InitFiles = [
        "Source/__init__.py",
        "Source/Data/__init__.py", 
        "Source/Core/__init__.py",
        "Source/Interface/__init__.py"
    ]
    
    for InitFile in InitFiles:
        with open(InitFile, 'w') as f:
            f.write('# Anderson\'s Library Package\n')
        print(f"   ✅ {InitFile}")
    
    # Create simple entry point
    print("\n🎯 Creating entry point...")
    EntryPoint = '''#!/usr/bin/env python3
"""Anderson's Library - Quick Start"""

import sys
from pathlib import Path

# Add Source to path
sys.path.insert(0, str(Path(__file__).parent / "Source"))

try:
    from Interface.MainWindow import RunApplication
    sys.exit(RunApplication())
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("📝 Make sure you've copied all the module files to Source/")
    sys.exit(1)
'''
    
    with open("RunAnderson.py", 'w') as f:
        f.write(EntryPoint)
    
    # Make executable
    if os.name != 'nt':
        os.chmod("RunAnderson.py", 0o755)
    
    print("   ✅ RunAnderson.py")
    
    print("\n🎉 QUICK SETUP COMPLETE!")
    print("\n📋 NEXT STEPS:")
    print("1. Copy the 6 module files to their locations:")
    print("   • DatabaseModels.py     → Source/Data/")
    print("   • DatabaseManager.py    → Source/Core/")
    print("   • BookService.py        → Source/Core/")
    print("   • FilterPanel.py        → Source/Interface/")
    print("   • BookGrid.py           → Source/Interface/")
    print("   • MainWindow.py         → Source/Interface/")
    print("2. Copy CustomWindow.py    → Source/Interface/")
    print("3. Run: python RunAnderson.py")
    print("\n🚀 Ready to test the new architecture!")


if __name__ == "__main__":
    CreateQuickStructure()
