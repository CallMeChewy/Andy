#!/usr/bin/env python3
# File: SyntaxFix.py
# Path: SyntaxFix.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  05:30PM
"""
Description: Syntax Fix for Anderson's Library DatabaseModels
Quick fix for unclosed parenthesis syntax error in DatabaseModels.py
"""

import os
import sys

def FixSyntaxError():
    """Fix the unclosed parenthesis in DatabaseModels.py"""
    
    print("🔧 Anderson's Library - Syntax Fix")
    print("=" * 50)
    print("🐛 Fixing unclosed parenthesis in DatabaseModels.py")
    
    DatabaseModelsPath = "Source/Data/DatabaseModels.py"
    
    # Check if file exists
    if not os.path.exists(DatabaseModelsPath):
        print(f"❌ File not found: {DatabaseModelsPath}")
        return False
    
    # Read current content
    try:
        with open(DatabaseModelsPath, 'r', encoding='utf-8') as File:
            Lines = File.readlines()
    except Exception as Error:
        print(f"❌ Error reading file: {Error}")
        return False
    
    print(f"📄 File has {len(Lines)} lines")
    
    # Find and fix common syntax issues
    Fixed = False
    
    # Check around line 515 (give or take a few lines)
    for i in range(max(0, 510), min(len(Lines), 520)):
        Line = Lines[i]
        LineNum = i + 1
        
        # Look for common syntax issues
        if Line.strip().endswith(',') and 'def ' in Line:
            # Function definition ending with comma instead of colon
            Lines[i] = Line.replace(',', ':')
            print(f"✅ Fixed line {LineNum}: Changed trailing comma to colon")
            Fixed = True
            
        elif '(' in Line and ')' not in Line and not Line.strip().endswith('\\'):
            # Unclosed parenthesis - look for the next line to close it
            if i + 1 < len(Lines):
                NextLine = Lines[i + 1].strip()
                if NextLine and not NextLine.startswith(')'):
                    # Add closing parenthesis to current line
                    Lines[i] = Line.rstrip() + ')\n'
                    print(f"✅ Fixed line {LineNum}: Added missing closing parenthesis")
                    Fixed = True
        
        elif Line.strip() == 'try:' and i + 1 < len(Lines):
            # Check if there's proper indentation after try
            NextLine = Lines[i + 1]
            if not NextLine.startswith('        '):  # Should be indented
                Lines[i + 1] = '        ' + NextLine.lstrip()
                print(f"✅ Fixed line {LineNum + 1}: Fixed indentation after try:")
                Fixed = True
    
    # Look for specific common issues in the entire file
    for i, Line in enumerate(Lines):
        LineNum = i + 1
        
        # Fix return statement with missing closing parenthesis
        if 'return str(Data.get(' in Line and Line.count('(') > Line.count(')'):
            # Find where the return statement should end
            if not Line.rstrip().endswith(')'):
                Lines[i] = Line.rstrip() + ')\n'
                print(f"✅ Fixed line {LineNum}: Added missing closing parenthesis to return statement")
                Fixed = True
        
        # Fix function calls with unclosed parentheses
        if 'logging.error(f' in Line and Line.count('(') > Line.count(')'):
            if not Line.rstrip().endswith(')'):
                Lines[i] = Line.rstrip() + ')\n'
                print(f"✅ Fixed line {LineNum}: Added missing closing parenthesis to logging call")
                Fixed = True
    
    # Check for the specific error pattern around line 515
    if len(Lines) > 515:
        Line515 = Lines[514]  # Line 515 (0-indexed)
        print(f"🔍 Line 515 content: {repr(Line515)}")
        
        # Common fixes for line 515
        if 'try:' in Line515 and not Line515.strip().endswith(':'):
            Lines[514] = Line515.rstrip() + ':\n'
            print("✅ Fixed line 515: Added missing colon after try")
            Fixed = True
        
        elif 'except' in Line515 and not Line515.strip().endswith(':'):
            Lines[514] = Line515.rstrip() + ':\n'
            print("✅ Fixed line 515: Added missing colon after except")
            Fixed = True
        
        elif Line515.count('(') > Line515.count(')'):
            # Add missing closing parenthesis
            Lines[514] = Line515.rstrip() + ')\n'
            print("✅ Fixed line 515: Added missing closing parenthesis")
            Fixed = True
    
    if not Fixed:
        # Try a more aggressive fix - look for the CreateAuthorFromRow function
        for i, Line in enumerate(Lines):
            if 'def CreateAuthorFromRow' in Line:
                LineNum = i + 1
                print(f"🔍 Found CreateAuthorFromRow at line {LineNum}")
                
                # Check the return statement in this function
                for j in range(i, min(i + 10, len(Lines))):
                    if 'return str(' in Lines[j] and Lines[j].count('(') > Lines[j].count(')'):
                        Lines[j] = Lines[j].rstrip() + ')\n'
                        print(f"✅ Fixed line {j + 1}: Added missing closing parenthesis to return statement")
                        Fixed = True
                        break
                break
    
    if Fixed:
        # Write back to file
        try:
            with open(DatabaseModelsPath, 'w', encoding='utf-8') as File:
                File.writelines(Lines)
            
            print("✅ Syntax fixes applied successfully!")
            return True
            
        except Exception as Error:
            print(f"❌ Error writing fixed file: {Error}")
            return False
    else:
        print("🔍 No obvious syntax issues found. Let me show you line 515:")
        if len(Lines) > 515:
            for i in range(max(0, 512), min(len(Lines), 518)):
                LineNum = i + 1
                print(f"   {LineNum:3}: {Lines[i].rstrip()}")
        
        # Manual fix suggestion
        print("\n💡 Manual fix suggestion:")
        print("   Check line 515 in Source/Data/DatabaseModels.py")
        print("   Look for missing closing parenthesis ')' or colon ':'")
        print("   Common issues: function calls, return statements, try/except blocks")
        
        return False


def ValidateSyntax():
    """Validate Python syntax by attempting to compile"""
    print("\n🔍 Validating Python syntax...")
    
    DatabaseModelsPath = "Source/Data/DatabaseModels.py"
    
    try:
        with open(DatabaseModelsPath, 'r', encoding='utf-8') as File:
            Content = File.read()
        
        # Try to compile the code
        compile(Content, DatabaseModelsPath, 'exec')
        print("✅ Python syntax is valid!")
        return True
        
    except SyntaxError as Error:
        print(f"❌ Syntax error still present:")
        print(f"   Line {Error.lineno}: {Error.text}")
        print(f"   Error: {Error.msg}")
        return False
    except Exception as Error:
        print(f"❌ Other error: {Error}")
        return False


def Main():
    """Main syntax fix"""
    print("🏔️ Anderson's Library - Syntax Fix")
    print("=" * 50)
    print("🐛 Fixing unclosed parenthesis syntax error")
    print("=" * 50)
    
    # Apply fixes
    if FixSyntaxError():
        # Validate syntax
        if ValidateSyntax():
            print("\n" + "=" * 50)
            print("🎉 SYNTAX FIXED SUCCESSFULLY!")
            print("=" * 50)
            print("🚀 Now try running: python AndersonLibrary.py")
            return 0
        else:
            print("\n⚠️  Some syntax issues may remain")
            print("💡 Check the error message above and fix manually")
            return 1
    else:
        print("\n🔍 Automatic fix not applied")
        print("💡 Manual inspection required")
        return 1


if __name__ == "__main__":
    sys.exit(Main())