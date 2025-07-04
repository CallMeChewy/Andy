#!/usr/bin/env python3
# File: CustomWindowFix.py
# Path: CustomWindowFix.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  05:35PM
"""
Description: CustomWindow Parameter Fix for Anderson's Library
Fixes the missing 'title' parameter issue in MainWindow.py when calling CustomWindow.__init__()
"""

import os
import sys
import re

def FixCustomWindowInit():
    """Fix the CustomWindow initialization in MainWindow.py"""
    
    print("🔧 Anderson's Library - CustomWindow Fix")
    print("=" * 50)
    print("🛠️  Fixing CustomWindow title parameter in MainWindow.py")
    
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
    
    # Find the CustomWindow class definition line
    Lines = Content.split('\n')
    Fixed = False
    
    for i, Line in enumerate(Lines):
        LineNum = i + 1
        
        # Look for the class definition
        if 'class AndersonMainWindow(CustomWindow):' in Line:
            print(f"✅ Found class definition at line {LineNum}")
            
            # Look for the __init__ method in the next few lines
            for j in range(i, min(i + 20, len(Lines))):
                if 'def __init__(self):' in Lines[j]:
                    print(f"✅ Found __init__ method at line {j + 1}")
                    
                    # Look for super().__init__() call in the next few lines
                    for k in range(j, min(j + 15, len(Lines))):
                        if 'super().__init__()' in Lines[k]:
                            # Replace with title parameter
                            Lines[k] = Lines[k].replace(
                                'super().__init__()', 
                                'super().__init__("Anderson\'s Library - Professional Edition")'
                            )
                            print(f"✅ Fixed line {k + 1}: Added title parameter to super().__init__()")
                            Fixed = True
                            break
                        elif 'super(AndersonMainWindow, self).__init__()' in Lines[k]:
                            # Alternative super() syntax
                            Lines[k] = Lines[k].replace(
                                'super(AndersonMainWindow, self).__init__()', 
                                'super(AndersonMainWindow, self).__init__("Anderson\'s Library - Professional Edition")'
                            )
                            print(f"✅ Fixed line {k + 1}: Added title parameter to super() call")
                            Fixed = True
                            break
                    
                    if Fixed:
                        break
            
            if Fixed:
                break
    
    if not Fixed:
        # Try a more general approach - look for any super().__init__() calls
        for i, Line in enumerate(Lines):
            if 'super().__init__()' in Line and 'AndersonMainWindow' in Lines[max(0, i-10):i+1]:
                Lines[i] = Line.replace(
                    'super().__init__()', 
                    'super().__init__("Anderson\'s Library - Professional Edition")'
                )
                print(f"✅ Fixed line {i + 1}: Added title parameter to super().__init__()")
                Fixed = True
                break
    
    if Fixed:
        # Write back to file
        try:
            NewContent = '\n'.join(Lines)
            with open(MainWindowPath, 'w', encoding='utf-8') as File:
                File.write(NewContent)
            
            print("✅ CustomWindow fix applied successfully!")
            return True
            
        except Exception as Error:
            print(f"❌ Error writing fixed file: {Error}")
            return False
    else:
        print("⚠️  Could not automatically fix the issue")
        print("💡 Manual fix needed:")
        print("   1. Open Source/Interface/MainWindow.py")
        print("   2. Find line with super().__init__()")
        print("   3. Change it to: super().__init__(\"Anderson's Library - Professional Edition\")")
        return False


def AlternativeFix():
    """Alternative fix: Modify CustomWindow to make title optional"""
    print("\n🔧 Alternative Fix: Making CustomWindow title optional")
    
    CustomWindowPath = "Source/Interface/CustomWindow.py"
    
    if not os.path.exists(CustomWindowPath):
        print(f"❌ File not found: {CustomWindowPath}")
        return False
    
    try:
        with open(CustomWindowPath, 'r', encoding='utf-8') as File:
            Content = File.read()
        
        # Look for __init__ method and make title optional
        if 'def __init__(self, title):' in Content:
            Content = Content.replace(
                'def __init__(self, title):',
                'def __init__(self, title="Application"):'
            )
            print("✅ Made title parameter optional in CustomWindow")
            
            with open(CustomWindowPath, 'w', encoding='utf-8') as File:
                File.write(Content)
            
            return True
        elif 'def __init__(self, title,' in Content:
            # More complex constructor - need to be more careful
            Lines = Content.split('\n')
            for i, Line in enumerate(Lines):
                if 'def __init__(self, title,' in Line and 'title=' not in Line:
                    Lines[i] = Line.replace('title,', 'title="Application",')
                    print(f"✅ Made title parameter optional in CustomWindow at line {i + 1}")
                    
                    NewContent = '\n'.join(Lines)
                    with open(CustomWindowPath, 'w', encoding='utf-8') as File:
                        File.write(NewContent)
                    
                    return True
        
        print("⚠️  Could not automatically modify CustomWindow constructor")
        return False
        
    except Exception as Error:
        print(f"❌ Error modifying CustomWindow: {Error}")
        return False


def ValidateFix():
    """Validate that the fix works by checking syntax"""
    print("\n🔍 Validating fix...")
    
    try:
        # Try to import the modules to see if they work
        import subprocess
        Result = subprocess.run([
            sys.executable, '-c', 
            'import sys; sys.path.insert(0, "."); from Source.Interface.MainWindow import AndersonMainWindow'
        ], capture_output=True, text=True, cwd='.')
        
        if Result.returncode == 0:
            print("✅ Import test passed!")
            return True
        else:
            print(f"❌ Import test failed: {Result.stderr}")
            return False
            
    except Exception as Error:
        print(f"❌ Validation error: {Error}")
        return False


def Main():
    """Main fix application"""
    print("🏔️ Anderson's Library - CustomWindow Fix")
    print("=" * 50)
    print("🛠️  Fixing CustomWindow title parameter issue")
    print("=" * 50)
    
    # Try primary fix first
    if FixCustomWindowInit():
        print("✅ Primary fix applied (added title to super().__init__)")
    else:
        # Try alternative fix
        if AlternativeFix():
            print("✅ Alternative fix applied (made title optional)")
        else:
            print("❌ Both automatic fixes failed")
            print("\n💡 Manual Fix Instructions:")
            print("   Option 1: Edit Source/Interface/MainWindow.py")
            print("   Find: super().__init__()")
            print("   Replace: super().__init__(\"Anderson's Library\")")
            print("\n   Option 2: Edit Source/Interface/CustomWindow.py")
            print("   Find: def __init__(self, title):")
            print("   Replace: def __init__(self, title=\"Application\"):")
            return 1
    
    # Validate the fix
    if ValidateFix():
        print("\n" + "=" * 50)
        print("🎉 CUSTOMWINDOW FIX SUCCESSFUL!")
        print("=" * 50)
        print("🚀 Now try running: python AndersonLibrary.py")
        print("🎉 Anderson's Library should launch!")
        return 0
    else:
        print("\n⚠️  Fix applied but validation failed")
        print("💡 Try running manually: python AndersonLibrary.py")
        return 1


if __name__ == "__main__":
    sys.exit(Main())