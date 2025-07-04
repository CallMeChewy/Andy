#!/usr/bin/env python3
# File: FinalImportFix.py
# Path: FinalImportFix.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  05:55PM
"""
Description: Final Import Fix for Anderson's Library
Adds missing QSizePolicy import to MainWindow.py - the final fix needed!
"""

import os
import sys
import re

def AddMissingImports():
    """Add missing QSizePolicy import to MainWindow.py"""
    
    print("🔧 Anderson's Library - Final Import Fix")
    print("=" * 50)
    print("📦 Adding missing QSizePolicy import to MainWindow.py")
    
    MainWindowPath = "Source/Interface/MainWindow.py"
    
    # Check if file exists
    if not os.path.exists(MainWindowPath):
        print(f"❌ File not found: {MainWindowPath}")
        return False
    
    # Read current content
    try:
        with open(MainWindowPath, 'r', encoding='utf-8') as File:
            Content = File.read()
    except Exception as Error:
        print(f"❌ Error reading file: {Error}")
        return False
    
    # Check if QSizePolicy is already imported
    if 'QSizePolicy' in Content and 'from PySide6.QtWidgets import' in Content:
        print("🔍 Checking current imports...")
        
        Lines = Content.split('\n')
        Fixed = False
        
        # Find the QtWidgets import line and add QSizePolicy
        for i, Line in enumerate(Lines):
            if 'from PySide6.QtWidgets import' in Line and 'QSizePolicy' not in Line:
                # Add QSizePolicy to the import
                if Line.endswith(')'):
                    # Multi-line import - add before the closing parenthesis
                    Lines[i] = Line.replace(')', ', QSizePolicy)')
                else:
                    # Single line import - add at the end
                    Lines[i] = Line + ', QSizePolicy'
                
                print(f"✅ Added QSizePolicy to imports at line {i + 1}")
                Fixed = True
                break
        
        # If we couldn't find a single line, look for multi-line imports
        if not Fixed:
            for i, Line in enumerate(Lines):
                if 'from PySide6.QtWidgets import (' in Line:
                    # This is the start of a multi-line import
                    # Find the end and add QSizePolicy before the closing )
                    for j in range(i, min(i + 10, len(Lines))):
                        if ')' in Lines[j] and 'QSizePolicy' not in Lines[j]:
                            Lines[j] = Lines[j].replace(')', ', QSizePolicy)')
                            print(f"✅ Added QSizePolicy to multi-line imports at line {j + 1}")
                            Fixed = True
                            break
                    break
        
        if Fixed:
            # Write back to file
            try:
                NewContent = '\n'.join(Lines)
                with open(MainWindowPath, 'w', encoding='utf-8') as File:
                    File.write(NewContent)
                
                print("✅ Import fix applied successfully!")
                return True
                
            except Exception as Error:
                print(f"❌ Error writing fixed file: {Error}")
                return False
        else:
            print("⚠️  Could not automatically add QSizePolicy to imports")
            return False
    else:
        print("❌ Could not find PySide6.QtWidgets import line")
        return False


def ValidateImports():
    """Validate that all required imports are present"""
    print("\n🔍 Validating imports...")
    
    MainWindowPath = "Source/Interface/MainWindow.py"
    
    try:
        with open(MainWindowPath, 'r', encoding='utf-8') as File:
            Content = File.read()
        
        RequiredImports = [
            'QApplication', 'QMainWindow', 'QWidget', 'QMenuBar', 
            'QStatusBar', 'QToolBar', 'QMessageBox', 'QProgressBar',
            'QLabel', 'QSplitter', 'QSizePolicy'
        ]
        
        MissingImports = []
        for Import in RequiredImports:
            if Import not in Content:
                MissingImports.append(Import)
        
        if MissingImports:
            print(f"⚠️  Still missing imports: {', '.join(MissingImports)}")
            return False
        else:
            print("✅ All required imports found!")
            return True
            
    except Exception as Error:
        print(f"❌ Validation error: {Error}")
        return False


def CheckForOtherMissingImports():
    """Check MainWindow.py for any other potentially missing imports"""
    print("\n🔍 Checking for other potential import issues...")
    
    MainWindowPath = "Source/Interface/MainWindow.py"
    
    try:
        with open(MainWindowPath, 'r', encoding='utf-8') as File:
            Content = File.read()
        
        # Common PySide6 classes that might be missing
        PotentialMissing = []
        
        # Check for Qt classes used but not imported
        QtClasses = [
            'QVBoxLayout', 'QHBoxLayout', 'QPushButton', 'QComboBox',
            'QLineEdit', 'QTextEdit', 'QDialog', 'QFileDialog',
            'QScrollArea', 'QFrame', 'QGroupBox', 'QCheckBox',
            'QRadioButton', 'QSlider', 'QSpinBox', 'QDateEdit',
            'QListWidget', 'QTreeWidget', 'QTableWidget'
        ]
        
        for ClassName in QtClasses:
            if ClassName in Content and f'import.*{ClassName}' not in Content:
                # This class is used but might not be imported
                if 'from PySide6.QtWidgets import' in Content:
                    # Check if it's in the QtWidgets import line
                    ImportLines = [line for line in Content.split('\n') if 'from PySide6.QtWidgets import' in line]
                    ImportText = ' '.join(ImportLines)
                    if ClassName not in ImportText:
                        PotentialMissing.append(ClassName)
        
        if PotentialMissing:
            print(f"⚠️  Potentially missing imports: {', '.join(PotentialMissing[:5])}")  # Show first 5
            return PotentialMissing
        else:
            print("✅ No obvious missing imports detected")
            return []
            
    except Exception as Error:
        print(f"❌ Error checking imports: {Error}")
        return []


def Main():
    """Main import fix"""
    print("🏔️ Anderson's Library - Final Import Fix")
    print("=" * 50)
    print("📦 Adding missing QSizePolicy import")
    print("💡 This should be the FINAL fix needed!")
    print("=" * 50)
    
    # Apply the fix
    if AddMissingImports():
        # Validate imports
        if ValidateImports():
            print("\n" + "=" * 50)
            print("🎉 FINAL IMPORT FIX SUCCESSFUL!")
            print("=" * 50)
            print("🚀 Now try running: python AndersonLibrary.py")
            print("🎉 Anderson's Library should fully launch!")
            print("🏔️ Welcome to Professional Modular Architecture!")
            
            # Check for any other potential issues
            CheckForOtherMissingImports()
            
            return 0
        else:
            print("\n⚠️  Import fix applied but validation shows other missing imports")
            return 1
    else:
        print("\n❌ Could not automatically fix imports")
        print("💡 Manual fix:")
        print("   Edit Source/Interface/MainWindow.py")
        print("   Add QSizePolicy to the PySide6.QtWidgets import line")
        print("   Example: from PySide6.QtWidgets import (..., QSizePolicy)")
        return 1


if __name__ == "__main__":
    sys.exit(Main())