# File: AndersonLibrary.py
# Path: AndersonLibrary.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-06
# Last Modified: 2025-07-06  11:26AM
"""
Description: Fixed Anderson's Library Entry Point
Complete application launcher with all PySide6 fixes and enhancements applied.
"""

import sys
import logging
import os
from pathlib import Path
from typing import Optional

# Ensure Source directory is in Python path
SourcePath = Path(__file__).parent / "Source"
if str(SourcePath) not in sys.path:
    sys.path.insert(0, str(SourcePath))

try:
    from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QPixmap, QFont
except ImportError as ImportError:
    print("❌ PySide6 is not installed!")
    print("💡 Please install it with: pip install PySide6")
    sys.exit(1)

# Import our fixed modules
try:
    from Source.Interface.MainWindow import MainWindow
    from Source.Core.DatabaseManager import DatabaseManager
    from Source.Core.BookService import BookService
except ImportError as Error:
    print(f"❌ Failed to import application modules: {Error}")
    print("💡 Make sure all Source files are in place")
    sys.exit(1)


def PrintStartupBanner() -> None:
    """Print the professional startup banner"""
    print("🏔️ Anderson's Library - Professional Edition")
    print("=" * 50)
    print("📚 Digital Library Management System")
    print("🎯 Project Himalaya - BowersWorld.com")
    print("⚡ Modular Architecture - Design Standard v1.8")
    print("=" * 50)


def ValidateEnvironment() -> bool:
    """
    Validate the environment and required files.
    
    Returns:
        True if environment is valid, False otherwise
    """
    print("📁 Checking file structure...")
    
    RequiredFiles = [
        "Source/Data/DatabaseModels.py",
        "Source/Core/DatabaseManager.py", 
        "Source/Core/BookService.py",
        "Source/Interface/FilterPanel.py",
        "Source/Interface/BookGrid.py",
        "Source/Interface/MainWindow.py",
        "Source/Interface/CustomWindow.py"
    ]
    
    MissingFiles = []
    PresentFiles = []
    
    for FilePath in RequiredFiles:
        if Path(FilePath).exists():
            print(f" ✅ {FilePath}")
            PresentFiles.append(FilePath)
        else:
            print(f" ❌ {FilePath}")
            MissingFiles.append(FilePath)
    
    print(f"📊 Files: {len(PresentFiles)} present, {len(MissingFiles)} missing")
    
    # Check database
    print("🗄️ Testing database connection...")
    DatabasePath = Path("Assets/my_library.db")
    if DatabasePath.exists():
        print(f" ✅ Found database: {DatabasePath}")
    else:
        print(f" ⚠️ Database not found: {DatabasePath}")
        print(" 💡 Application will attempt to create/find database")
    
    # Check PySide6
    print("🐍 Testing Python imports...")
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QIcon
        print(" ✅ PySide6 available")
    except ImportError as Error:
        print(f" ❌ PySide6 import error: {Error}")
        return False
    
    print("=" * 50)
    
    if MissingFiles:
        print(f"❌ Missing {len(MissingFiles)} required files!")
        print("💡 Please ensure all Source files are in place")
        return False
    
    print("✅ ENVIRONMENT VALIDATION PASSED")
    return True


def CreateSplashScreen(App: QApplication) -> Optional[QSplashScreen]:
    """Create and show a splash screen"""
    try:
        # Try to load splash image
        SplashPath = Path("Assets/BowersWorld.png")
        if SplashPath.exists():
            SplashPixmap = QPixmap(str(SplashPath))
            SplashScreen = QSplashScreen(SplashPixmap)
        else:
            # Create simple splash without image
            SplashPixmap = QPixmap(400, 200)
            SplashPixmap.fill(Qt.blue)
            SplashScreen = QSplashScreen(SplashPixmap)
        
        SplashScreen.show()
        SplashScreen.showMessage("Loading Anderson's Library...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        App.processEvents()
        
        return SplashScreen
        
    except Exception as Error:
        logging.warning(f"Failed to create splash screen: {Error}")
        return None


def InitializeLogging() -> None:
    """Initialize application logging"""
    # Create logs directory if it doesn't exist
    LogsDir = Path("Logs")
    LogsDir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(name)s - %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler(LogsDir / "anderson_library.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )


def RunApplication() -> int:
    """
    Run the complete Anderson's Library application with all fixes.
    
    Returns:
        Application exit code
    """
    try:
        # Print startup banner
        PrintStartupBanner()
        
        # Validate environment
        if not ValidateEnvironment():
            print("❌ Environment validation failed!")
            print("💡 Please fix the issues above and try again")
            return 1
        
        # Initialize logging
        InitializeLogging()
        Logger = logging.getLogger("AndersonLibrary")
        
        print("🚀 Starting Anderson's Library...")
        print("=" * 50)
        
        # Create QApplication
        App = QApplication.instance()
        if App is None:
            App = QApplication(sys.argv)
        
        # Set application properties
        App.setApplicationName("Anderson's Library")
        App.setApplicationVersion("2.0")
        App.setOrganizationName("Project Himalaya")
        App.setOrganizationDomain("BowersWorld.com")
        
        # Set application font
        Font = QFont("Ubuntu", 10)
        App.setFont(Font)
        
        # Show splash screen
        SplashScreen = CreateSplashScreen(App)
        
        try:
            # Create main window with fixed implementation
            Logger.info("Creating main window...")
            MainWindowInstance = MainWindow()
            
            # Hide splash screen
            if SplashScreen:
                SplashScreen.finish(MainWindowInstance)
            
            # Show main window
            MainWindowInstance.show()
            
            # ✅ Fixed: Ensure full screen display after a brief delay
            def ShowFullScreen():
                try:
                    Screen = App.primaryScreen()
                    if Screen:
                        ScreenGeometry = Screen.availableGeometry()
                        MainWindowInstance.setGeometry(ScreenGeometry)
                        Logger.info(f"Main window set to full screen: {ScreenGeometry}")
                    else:
                        MainWindowInstance.showMaximized()
                        Logger.info("Main window maximized")
                except Exception as Error:
                    Logger.error(f"Failed to set full screen: {Error}")
                    MainWindowInstance.showMaximized()
            
            # Use timer to ensure window is shown before setting geometry
            QTimer.singleShot(200, ShowFullScreen)
            
            Logger.info("Anderson's Library started successfully")
            
            # Run the event loop
            ExitCode = App.exec()
            Logger.info(f"Application exited with code: {ExitCode}")
            return ExitCode
            
        except Exception as Error:
            Logger.error(f"Failed to start main window: {Error}")
            
            # Hide splash screen if still showing
            if SplashScreen:
                SplashScreen.hide()
            
            # Show error message
            QMessageBox.critical(
                None,
                "Application Error",
                f"Failed to start Anderson's Library:\n\n{Error}\n\nPlease check the console for details."
            )
            return 1
            
    except Exception as Error:
        print(f"❌ Critical error: {Error}")
        return 1


def ShowQuickHelp() -> None:
    """Show quick help information"""
    print("\n🆘 Anderson's Library - Quick Help")
    print("=" * 40)
    print("📋 Common Issues:")
    print("• Missing PySide6: pip install PySide6")
    print("• Missing files: Check Source/ directory structure")
    print("• Database issues: Ensure Assets/my_library.db exists")
    print("• Import errors: Verify all __init__.py files exist")
    print("\n📁 Required Directory Structure:")
    print("Source/")
    print("├── Core/")
    print("├── Data/") 
    print("├── Interface/")
    print("└── Utils/")
    print("\n🔗 Contact: HimalayaProject1@gmail.com")


if __name__ == "__main__":
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--help", "-h", "help"]:
            ShowQuickHelp()
            sys.exit(0)
        elif sys.argv[1] in ["--version", "-v"]:
            print("Anderson's Library v2.0 - Professional Edition")
            print("Built with Design Standard v1.8")
            sys.exit(0)
    
    # Run the application
    ExitCode = RunApplication()
    sys.exit(ExitCode)