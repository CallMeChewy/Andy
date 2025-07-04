#!/usr/bin/env python3
# File: SetupProjectStructure.py
# Path: SetupProjectStructure.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  16:15PM
"""
Description: Anderson's Library Project Structure Setup
Creates the complete modular directory structure with proper __init__.py files.
Follows Design Standard v1.8 for professional Python project organization.

Purpose: Automates the creation of the new modular architecture for Anderson's Library,
ensuring proper Python package structure and Design Standard compliance.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple


class ProjectStructureBuilder:
    """
    Builds the complete Anderson's Library modular project structure.
    Creates directories and __init__.py files following Design Standard v1.8.
    """
    
    def __init__(self, BaseDirectory: str = "."):
        """
        Initialize project structure builder.
        
        Args:
            BaseDirectory: Root directory for project structure
        """
        self.BaseDirectory = Path(BaseDirectory)
        self.CreatedDirectories: List[Path] = []
        self.CreatedFiles: List[Path] = []
        self.CurrentDate = datetime.now().strftime("%Y-%m-%d")
        self.CurrentDateTime = datetime.now().strftime("%Y-%m-%d  %H:%M%p")
        
        print("🏔️ Anderson's Library - Project Structure Builder")
        print("=" * 60)
        print(f"📁 Base Directory: {self.BaseDirectory.absolute()}")
        print(f"📅 Date: {self.CurrentDate}")
        print("=" * 60)
    
    def CreateDirectoryStructure(self) -> None:
        """Create the complete directory structure"""
        print("\n🏗️ Creating Directory Structure...")
        
        # Define the complete directory structure
        Directories = [
            # Source code directories
            "Source",
            "Source/Data",
            "Source/Core", 
            "Source/Interface",
            "Source/Utils",
            "Source/Framework",
            
            # Configuration and assets
            "Config",
            "Assets",
            "Assets/Icons",
            
            # Data directories
            "Data",
            "Data/Databases",
            "Data/Cache",
            "Data/Backups",
            
            # Scripts directories  
            "Scripts",
            "Scripts/Deployment",
            "Scripts/Development", 
            "Scripts/Maintenance",
            "Scripts/Migration",
            "Scripts/System",
            
            # Documentation and tests
            "Docs",
            "Tests",
            "Tests/Unit",
            "Tests/Integration",
            "Tests/Data",
            
            # Legacy and updates
            "Legacy",
            "Updates",
            
            # Web interface (future)
            "WebPages",
            "WebPages/Assets",
            "WebPages/CSS",
            "WebPages/JS"
        ]
        
        # Create each directory
        for DirectoryPath in Directories:
            FullPath = self.BaseDirectory / DirectoryPath
            self._CreateDirectory(FullPath)
        
        print(f"✅ Created {len(self.CreatedDirectories)} directories")
    
    def CreateInitFiles(self) -> None:
        """Create __init__.py files for Python packages"""
        print("\n📄 Creating __init__.py Files...")
        
        # Define packages that need __init__.py files
        PackageDefinitions = [
            # Main source packages
            ("Source", "Anderson's Library Source Package", "Main source code package for Anderson's Library application."),
            ("Source/Data", "Data Models Package", "Data models and database schema definitions."),
            ("Source/Core", "Core Business Logic Package", "Core business logic and service layer components."),
            ("Source/Interface", "User Interface Package", "User interface components and widgets."),
            ("Source/Utils", "Utilities Package", "Utility functions and helper classes."),
            ("Source/Framework", "Framework Package", "Reusable framework components and base classes."),
            
            # Test packages
            ("Tests", "Test Suite Package", "Complete test suite for Anderson's Library."),
            ("Tests/Unit", "Unit Tests Package", "Unit tests for individual components."),
            ("Tests/Integration", "Integration Tests Package", "Integration tests for component interactions."),
        ]
        
        # Create __init__.py for each package
        for PackagePath, Title, Description in PackageDefinitions:
            FullPath = self.BaseDirectory / PackagePath
            if FullPath.exists():
                InitFilePath = FullPath / "__init__.py"
                self._CreateInitFile(InitFilePath, Title, Description, PackagePath)
        
        print(f"✅ Created {len(self.CreatedFiles)} __init__.py files")
    
    def CreateEntryPoint(self) -> None:
        """Create main application entry point"""
        print("\n🚀 Creating Application Entry Point...")
        
        EntryPointPath = self.BaseDirectory / "AndersonLibrary.py"
        EntryPointContent = f'''#!/usr/bin/env python3
# File: AndersonLibrary.py
# Path: AndersonLibrary.py
# Standard: AIDEV-PascalCase-1.8
# Created: {self.CurrentDate}
# Last Modified: {self.CurrentDateTime}
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
    print(f"❌ Import Error: {{Error}}")
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
        print("\\n⚠️ Application interrupted by user")
        return 0
        
    except Exception as Error:
        print(f"❌ Critical Error: {{Error}}")
        logging.exception("Critical application error")
        return 1


if __name__ == "__main__":
    sys.exit(Main())
'''
        
        self._WriteFile(EntryPointPath, EntryPointContent)
        
        # Make it executable on Unix-like systems
        if os.name != 'nt':  # Not Windows
            try:
                os.chmod(EntryPointPath, 0o755)
                print("✅ Made AndersonLibrary.py executable")
            except:
                pass
        
        print("✅ Created AndersonLibrary.py entry point")
    
    def CreateRequirementsFile(self) -> None:
        """Create requirements.txt file"""
        print("\n📦 Creating Requirements File...")
        
        RequirementsPath = self.BaseDirectory / "requirements.txt"
        RequirementsContent = f'''# Anderson's Library - Requirements
# Generated: {self.CurrentDate}
# Standard: AIDEV-PascalCase-1.8

# Core GUI Framework
PySide6>=6.5.0

# Database Operations
# (SQLite is built into Python)

# Image Processing (for cover thumbnails)
Pillow>=9.0.0

# PDF Processing (future enhancement)
PyPDF2>=3.0.0

# Development and Testing
pytest>=7.0.0
pytest-cov>=4.0.0

# Code Quality
black>=22.0.0
flake8>=4.0.0

# Logging and Utilities
colorlog>=6.0.0

# Documentation (future)
sphinx>=4.0.0
sphinx-rtd-theme>=1.0.0
'''
        
        self._WriteFile(RequirementsPath, RequirementsContent)
        print("✅ Created requirements.txt")
    
    def CreateGitignore(self) -> None:
        """Create .gitignore file following Design Standard v1.8"""
        print("\n🚫 Creating .gitignore File...")
        
        GitignorePath = self.BaseDirectory / ".gitignore"
        GitignoreContent = f'''# Anderson's Library - .gitignore
# Generated: {self.CurrentDate}
# Standard: AIDEV-PascalCase-1.8

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environments
venv/
env/
ENV/
.venv/
.env/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Anderson's Library Specific
Data/Databases/*.db
Data/Databases/*.db-*
Data/Cache/
Data/Backups/
Logs/
*.log

# Sensitive Configuration
Config/Production/secrets.json
Config/Production/api_keys.json
.env
.env.local
.env.production

# Large Files
Assets/Books/
Assets/Covers/
Assets/Thumbs/

# Temporary Files
tmp/
temp/
*.tmp
*.temp

# OS Generated
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Coverage Reports
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover

# Testing
.pytest_cache/
.tox/

# Documentation builds
docs/_build/
docs/build/

# Project-specific exclusions
anderson-library-service-key.json
config/
secrets/

# Directories to ignore
node_modules/
'''
        
        self._WriteFile(GitignorePath, GitignoreContent)
        print("✅ Created .gitignore")
    
    def CreateReadme(self) -> None:
        """Create README.md file"""
        print("\n📖 Creating README.md File...")
        
        ReadmePath = self.BaseDirectory / "README.md"
        ReadmeContent = f'''# 📚 Anderson's Library - Professional Edition

**A modular, professional digital library management system built with Python and PySide6.**

## 🏔️ Project Himalaya - BowersWorld.com

*Generated: {self.CurrentDate}*  
*Standard: AIDEV-PascalCase-1.8*

---

## ✨ Features

- 📖 **Digital Library Management** - Organize and browse thousands of PDF books
- 🔍 **Intelligent Search** - Find books by title, category, or subject  
- 📂 **Category Organization** - Hierarchical category and subject structure
- 🎨 **Beautiful Interface** - Custom-designed responsive interface
- 🏗️ **Modular Architecture** - Professional, maintainable code structure
- 🔒 **Data Integrity** - SQLite database with proper normalization

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- PySide6
- SQLite database with your book collection

### Installation
```bash
# Clone the repository
git clone https://github.com/YourUsername/andersons-library.git
cd andersons-library

# Install dependencies
pip install -r requirements.txt

# Run the application
python AndersonLibrary.py
```

## 🏗️ Architecture

### Modular Structure
```
Source/
├── Data/              # Data models and validation
├── Core/              # Business logic and services  
├── Interface/         # UI components and widgets
├── Utils/             # Utility functions
└── Framework/         # Reusable framework components
```

### Key Components
- **DatabaseManager** - Clean database operations
- **BookService** - Business logic for book operations
- **FilterPanel** - Category and search interface
- **BookGrid** - Responsive book display grid
- **MainWindow** - Application orchestrator

## 📊 Database Schema

The application uses a normalized SQLite database:
- **Categories** - Book categories (Programming, Science, etc.)
- **Subjects** - Subcategories within each category
- **Books** - Individual book records with metadata

## 🎯 Design Standards

This project follows **AIDEV-PascalCase-1.8** standards:
- ✅ PascalCase naming throughout
- ✅ Comprehensive file headers
- ✅ ~300 line module limit
- ✅ Single responsibility principle
- ✅ Proper error handling and logging

## 🧪 Testing

```bash
# Run unit tests
pytest Tests/Unit/

# Run integration tests  
pytest Tests/Integration/

# Run all tests with coverage
pytest --cov=Source Tests/
```

## 🔧 Development

### Adding New Features
1. Create focused modules in appropriate Source/ subdirectory
2. Follow Design Standard v1.8 naming and structure
3. Add comprehensive tests in Tests/ directory
4. Update documentation

### Code Quality
```bash
# Format code
black Source/

# Check style
flake8 Source/

# Type checking (future)
mypy Source/
```

## 📁 Project Structure

```
├── AndersonLibrary.py          # Main application entry point
├── Source/                     # Source code packages
│   ├── Data/                  # Data models and schemas  
│   ├── Core/                  # Business logic services
│   ├── Interface/             # UI components
│   ├── Utils/                 # Utility functions
│   └── Framework/             # Reusable framework
├── Assets/                    # Images, icons, resources
├── Config/                    # Configuration files
├── Data/                      # Database and data files
├── Scripts/                   # Utility and maintenance scripts
├── Tests/                     # Test suites
├── Docs/                      # Documentation
└── requirements.txt           # Python dependencies
```

## 🌟 Future Roadmap

- 🌐 **Web Interface** - Convert to web application
- 📱 **Mobile App** - Responsive mobile interface  
- 🔍 **Full-Text Search** - Search within PDF content
- 🤖 **AI Integration** - Intelligent book recommendations
- ☁️ **Cloud Sync** - Multi-device synchronization

## 📝 License

© 2025 BowersWorld.com - Project Himalaya  
Licensed under MIT License

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Follow Design Standard v1.8
4. Commit changes (`git commit -m 'Add AmazingFeature'`)
5. Push to branch (`git push origin feature/AmazingFeature`)
6. Open Pull Request

## 📞 Support

- **Documentation:** `/Docs` directory
- **Issues:** GitHub Issues
- **Contact:** BowersWorld.com

---

**Built with ❤️ using AIDEV-PascalCase-1.8 Standards**
'''
        
        self._WriteFile(ReadmePath, ReadmeContent)
        print("✅ Created README.md")
    
    def GenerateSummaryReport(self) -> None:
        """Generate final setup summary report"""
        print("\n" + "=" * 60)
        print("📊 PROJECT STRUCTURE SETUP COMPLETE!")
        print("=" * 60)
        print(f"📁 Base Directory: {self.BaseDirectory.absolute()}")
        print(f"📅 Created: {self.CurrentDate}")
        print()
        
        print("📈 STATISTICS:")
        print(f"   📂 Directories Created: {len(self.CreatedDirectories)}")
        print(f"   📄 Files Created: {len(self.CreatedFiles)}")
        print()
        
        print("🏗️ DIRECTORY STRUCTURE:")
        for Directory in sorted(self.CreatedDirectories):
            RelativePath = Directory.relative_to(self.BaseDirectory)
            print(f"   📂 {RelativePath}")
        print()
        
        print("📄 FILES CREATED:")
        for File in sorted(self.CreatedFiles):
            RelativePath = File.relative_to(self.BaseDirectory)
            print(f"   📄 {RelativePath}")
        print()
        
        print("🚀 NEXT STEPS:")
        print("1. Copy your existing CustomWindow.py to Source/Interface/")
        print("2. Copy your database file to Data/Databases/")
        print("3. Install dependencies: pip install -r requirements.txt")
        print("4. Copy the 6 modular components to their proper locations")
        print("5. Run: python AndersonLibrary.py")
        print()
        print("✅ PROJECT STRUCTURE READY FOR MIGRATION!")
        print("=" * 60)
    
    # =================================================================
    # HELPER METHODS
    # =================================================================
    
    def _CreateDirectory(self, DirectoryPath: Path) -> None:
        """Create directory if it doesn't exist"""
        try:
            DirectoryPath.mkdir(parents=True, exist_ok=True)
            self.CreatedDirectories.append(DirectoryPath)
            print(f"   📂 {DirectoryPath.relative_to(self.BaseDirectory)}")
        except Exception as Error:
            print(f"   ❌ Failed to create {DirectoryPath}: {Error}")
    
    def _CreateInitFile(self, FilePath: Path, Title: str, Description: str, PackagePath: str) -> None:
        """Create __init__.py file with proper header"""
        Content = f'''# File: __init__.py
# Path: {PackagePath}/__init__.py
# Standard: AIDEV-PascalCase-1.8
# Created: {self.CurrentDate}
# Last Modified: {self.CurrentDateTime}
"""
Description: {Title}
{Description}

Purpose: Package initialization for {PackagePath} module. Provides clean
import interfaces and package-level configuration.
"""

# Package version and metadata
__version__ = "2.0.0"
__author__ = "Herb Bowers - Project Himalaya"
__email__ = "HimalayaProject1@gmail.com"

# Package-level imports can be added here as needed
# Example:
# from .module_name import ClassName

__all__ = [
    # Add public interface exports here
]
'''
        
        self._WriteFile(FilePath, Content)
    
    def _WriteFile(self, FilePath: Path, Content: str) -> None:
        """Write content to file"""
        try:
            with open(FilePath, 'w', encoding='utf-8') as File:
                File.write(Content)
            self.CreatedFiles.append(FilePath)
            print(f"   📄 {FilePath.relative_to(self.BaseDirectory)}")
        except Exception as Error:
            print(f"   ❌ Failed to create {FilePath}: {Error}")
    
    def BuildCompleteStructure(self) -> None:
        """Build the complete project structure"""
        try:
            self.CreateDirectoryStructure()
            self.CreateInitFiles()
            self.CreateEntryPoint()
            self.CreateRequirementsFile()
            self.CreateGitignore()
            self.CreateReadme()
            self.GenerateSummaryReport()
            
        except Exception as Error:
            print(f"❌ Error building project structure: {Error}")
            raise


def Main() -> int:
    """Main execution function"""
    try:
        print("🏔️ ANDERSON'S LIBRARY - PROJECT STRUCTURE BUILDER")
        print("Standard: AIDEV-PascalCase-1.8")
        print("Building professional modular architecture...")
        print()
        
        # Get base directory from command line or use current
        BaseDir = sys.argv[1] if len(sys.argv) > 1 else "."
        
        # Create project structure
        Builder = ProjectStructureBuilder(BaseDir)
        Builder.BuildCompleteStructure()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        return 1
        
    except Exception as Error:
        print(f"\n❌ Setup failed: {Error}")
        return 1


if __name__ == "__main__":
    ExitCode = Main()
    sys.exit(ExitCode)
