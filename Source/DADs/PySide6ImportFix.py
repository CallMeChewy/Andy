#!/usr/bin/env python3
# File: PySide6ImportFix.py
# Path: PySide6ImportFix.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  04:12PM
"""
Description: PySide6 Import Fix for Anderson's Library
Quick fix for PySide6 import issues where QAction moved from QtWidgets to QtGui.
"""

import os
import re

def FixPySide6Imports():
    """Fix PySide6 import issues in the modular files"""
    
    print("🔧 Fixing PySide6 import issues...")
    
    # Files to fix
    FilesToFix = [
        "Source/Interface/MainWindow.py",
        "Source/Interface/BookGrid.py",
        "Source/Interface/FilterPanel.py"
    ]
    
    # Import fixes
    Fixes = [
        # Move QAction from QtWidgets to QtGui
        {
            "pattern": r"from PySide6\.QtWidgets import \((.*?)QAction(.*?)\)",
            "replacement": lambda m: f"from PySide6.QtWidgets import ({m.group(1).replace('QAction, ', '').replace(', QAction', '')}{m.group(2)})"
        },
        # Add QAction to QtGui imports
        {
            "pattern": r"from PySide6\.QtGui import (.*?)(?=\n)",
            "replacement": lambda m: f"from PySide6.QtGui import {m.group(1).rstrip()}, QAction" if "QAction" not in m.group(1) else m.group(0)
        },
        # Fix pyqtSignal to Signal
        {
            "pattern": r"pyqtSignal",
            "replacement": "Signal"
        },
        # Add QApplication import to BookGrid if missing
        {
            "pattern": r"from PySide6\.QtWidgets import \((.*?)\)(?=.*BookGrid)",
            "replacement": lambda m: f"from PySide6.QtWidgets import ({m.group(1).rstrip()}, QApplication)" if "QApplication" not in m.group(1) else m.group(0)
        }
    ]
    
    for FilePath in FilesToFix:
        if os.path.exists(FilePath):
            print(f"   🔧 Fixing {FilePath}...")
            
            try:
                # Read file
                with open(FilePath, 'r', encoding='utf-8') as File:
                    Content = File.read()
                
                OriginalContent = Content
                
                # Apply specific fixes for each file
                if "MainWindow.py" in FilePath:
                    # Fix MainWindow imports
                    Content = re.sub(
                        r"from PySide6\.QtWidgets import \(QApplication, QMainWindow, QHBoxLayout, QVBoxLayout,\s*QWidget, QMenuBar, QStatusBar, QToolBar, QAction,",
                        "from PySide6.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, \n                               QWidget, QMenuBar, QStatusBar, QToolBar,",
                        Content
                    )
                    
                    Content = re.sub(
                        r"from PySide6\.QtGui import QIcon, QPixmap, QFont, QKeySequence, QShortcut\n",
                        "from PySide6.QtGui import QIcon, QPixmap, QFont, QKeySequence, QShortcut, QAction\n",
                        Content
                    )
                
                elif "BookGrid.py" in FilePath:
                    # Fix BookGrid imports
                    if "QApplication" not in Content and "QApplication.processEvents()" in Content:
                        Content = re.sub(
                            r"from PySide6\.QtWidgets import \((.*?QGroupBox)\)",
                            r"from PySide6.QtWidgets import (\1,\n                               QApplication)",
                            Content
                        )
                    
                    # Fix pyqtSignal
                    Content = Content.replace("pyqtSignal", "Signal")
                    Content = Content.replace(", pyqtSignal,", ",")
                
                # Write back if changed
                if Content != OriginalContent:
                    with open(FilePath, 'w', encoding='utf-8') as File:
                        File.write(Content)
                    print(f"      ✅ Fixed imports in {FilePath}")
                else:
                    print(f"      ➡️  No changes needed in {FilePath}")
                    
            except Exception as Error:
                print(f"      ❌ Error fixing {FilePath}: {Error}")
        else:
            print(f"   ❌ File not found: {FilePath}")
    
    print("✅ PySide6 import fixes complete!")

def Main():
    """Main entry point"""
    print("🏔️ Anderson's Library - PySide6 Import Fix")
    print("=" * 50)
    
    FixPySide6Imports()
    
    print("\n🚀 Try running Anderson's Library again:")
    print("python AndersonLibrary.py")

if __name__ == "__main__":
    Main()
