#!/usr/bin/env python3
# File: CopyModulesToStructure.py  
# Path: CopyModulesToStructure.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  16:25PM
"""
Description: Module File Placement Helper
Assists with copying the new modular components to their proper locations
in the Source/ directory structure for Anderson's Library.

Purpose: Automates the placement of refactored modules into the correct
directory structure, reducing setup errors and ensuring proper organization.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple


class ModulePlacementHelper:
    """Helps place module files in the correct directory structure"""
    
    def __init__(self):
        """Initialize the placement helper"""
        self.BaseDirectory = Path(".")
        self.SourceDirectory = self.BaseDirectory / "Source"
        
        # Define where each module should go
        self.ModuleTargets: Dict[str, str] = {
            "DatabaseModels.py": "Source/Data/",
            "DatabaseManager.py": "Source/Core/",
            "BookService.py": "Source/Core/",
            "FilterPanel.py": "Source/Interface/",
            "BookGrid.py": "Source/Interface/",
            "MainWindow.py": "Source/Interface/",
            "CustomWindow.py": "Source/Interface/"  # User's existing file
        }
        
        print("📋 Anderson's Library - Module Placement Helper")
        print("=" * 55)
    
    def CheckStructureExists(self) -> bool:
        """Check if the Source/ structure exists"""
        RequiredDirectories = [
            "Source",
            "Source/Data",
            "Source/Core", 
            "Source/Interface"
        ]
        
        Missing = []
        for Directory in RequiredDirectories:
            if not (self.BaseDirectory / Directory).exists():
                Missing.append(Directory)
        
        if Missing:
            print("❌ Missing required directories:")
            for Dir in Missing:
                print(f"   📂 {Dir}")
            print("\n💡 Run QuickSetup.py first to create the structure!")
            return False
        
        print("✅ Source directory structure exists")
        return True
    
    def FindModuleFiles(self) -> Dict[str, Path]:
        """Find module files in current directory"""
        FoundFiles = {}
        
        print("\n🔍 Looking for module files...")
        
        for ModuleFile in self.ModuleTargets.keys():
            # Look in current directory first
            CurrentPath = self.BaseDirectory / ModuleFile
            
            if CurrentPath.exists():
                FoundFiles[ModuleFile] = CurrentPath
                print(f"   ✅ Found: {ModuleFile}")
            else:
                print(f"   ❌ Missing: {ModuleFile}")
        
        return FoundFiles
    
    def CopyModuleFiles(self, FoundFiles: Dict[str, Path]) -> int:
        """Copy found module files to their target locations"""
        SuccessCount = 0
        
        print("\n📁 Copying modules to target locations...")
        
        for ModuleFile, SourcePath in FoundFiles.items():
            TargetDirectory = self.BaseDirectory / self.ModuleTargets[ModuleFile]
            TargetPath = TargetDirectory / ModuleFile
            
            try:
                # Ensure target directory exists
                TargetDirectory.mkdir(parents=True, exist_ok=True)
                
                # Copy the file
                shutil.copy2(SourcePath, TargetPath)
                
                print(f"   ✅ {ModuleFile} → {self.ModuleTargets[ModuleFile]}")
                SuccessCount += 1
                
            except Exception as Error:
                print(f"   ❌ Failed to copy {ModuleFile}: {Error}")
        
        return SuccessCount
    
    def ValidateInstallation(self) -> List[str]:
        """Validate that all modules are properly placed"""
        Issues = []
        
        print("\n🔍 Validating installation...")
        
        for ModuleFile, TargetDirectory in self.ModuleTargets.items():
            TargetPath = self.BaseDirectory / TargetDirectory / ModuleFile
            
            if TargetPath.exists():
                print(f"   ✅ {TargetDirectory}{ModuleFile}")
            else:
                Issues.append(f"{TargetDirectory}{ModuleFile}")
                print(f"   ❌ Missing: {TargetDirectory}{ModuleFile}")
        
        return Issues
    
    def GenerateInstructions(self, MissingFiles: List[str]) -> None:
        """Generate manual copy instructions for missing files"""
        if not MissingFiles:
            return
        
        print("\n📋 MANUAL COPY INSTRUCTIONS:")
        print("Copy these files manually if they exist:")
        
        for ModuleFile in self.ModuleTargets.keys():
            TargetLocation = self.ModuleTargets[ModuleFile]
            print(f"   📄 {ModuleFile} → {TargetLocation}")
        
        print("\n💡 Make sure file names match exactly (including case)")
    
    def CreateTestScript(self) -> None:
        """Create a test script to verify the installation"""
        TestScript = '''#!/usr/bin/env python3
"""Test script for Anderson's Library modular architecture"""

import sys
from pathlib import Path

# Add Source to Python path
sys.path.insert(0, str(Path(__file__).parent / "Source"))

def TestImports():
    """Test that all modules can be imported"""
    print("🧪 Testing module imports...")
    
    TestModules = [
        ("Data.DatabaseModels", "Book, Category, Subject"),
        ("Core.DatabaseManager", "DatabaseManager"),
        ("Core.BookService", "BookService"),
        ("Interface.FilterPanel", "FilterPanel"),
        ("Interface.BookGrid", "BookGrid"),
        ("Interface.MainWindow", "MainWindow")
    ]
    
    Success = 0
    Failed = 0
    
    for ModuleName, Classes in TestModules:
        try:
            exec(f"from {ModuleName} import {Classes}")
            print(f"   ✅ {ModuleName}")
            Success += 1
        except ImportError as Error:
            print(f"   ❌ {ModuleName}: {Error}")
            Failed += 1
    
    print(f"\\n📊 Results: {Success} successful, {Failed} failed")
    
    if Failed == 0:
        print("🎉 All modules imported successfully!")
        print("🚀 Ready to run: python RunAnderson.py")
        return True
    else:
        print("⚠️ Some modules failed to import")
        print("📝 Check file locations and __init__.py files")
        return False

if __name__ == "__main__":
    TestImports()
'''
        
        TestPath = self.BaseDirectory / "TestImports.py"
        with open(TestPath, 'w') as f:
            f.write(TestScript)
        
        if os.name != 'nt':
            os.chmod(TestPath, 0o755)
        
        print("✅ Created TestImports.py")
    
    def RunFullProcess(self) -> None:
        """Run the complete module placement process"""
        try:
            # Check structure exists
            if not self.CheckStructureExists():
                return
            
            # Find module files
            FoundFiles = self.FindModuleFiles()
            
            if not FoundFiles:
                print("\n❌ No module files found!")
                self.GenerateInstructions([])
                return
            
            # Copy files
            SuccessCount = self.CopyModuleFiles(FoundFiles)
            
            # Validate installation
            Issues = self.ValidateInstallation()
            
            # Create test script
            self.CreateTestScript()
            
            # Generate final report
            print("\n" + "=" * 55)
            print("📊 MODULE PLACEMENT COMPLETE!")
            print("=" * 55)
            print(f"✅ Successfully placed: {SuccessCount} modules")
            
            if Issues:
                print(f"❌ Missing modules: {len(Issues)}")
                print("\n📋 Still needed:")
                for Issue in Issues:
                    print(f"   📄 {Issue}")
            else:
                print("🎉 All modules placed successfully!")
                print("\n🚀 NEXT STEPS:")
                print("1. Run: python TestImports.py")
                print("2. If tests pass, run: python RunAnderson.py")
                print("3. Your app should work exactly like before!")
            
            print("=" * 55)
            
        except Exception as Error:
            print(f"❌ Error during placement: {Error}")


def Main():
    """Main entry point"""
    Helper = ModulePlacementHelper()
    Helper.RunFullProcess()


if __name__ == "__main__":
    Main()
