# File: MainWindow.py
# Path: Source/Interface/MainWindow.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-06
# Last Modified: 2025-07-06  11:26AM
"""
Description: Fixed Main Window for Anderson's Library
Fixes PySide6 imports, full screen display, icon paths, and contrast issues.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap, QAction  # ✅ Fixed: QAction moved to QtGui in PySide6

# Import our modules
from Source.Core.DatabaseManager import DatabaseManager
from Source.Core.BookService import BookService
from Source.Interface.FilterPanel import FilterPanel
from Source.Interface.BookGrid import BookGrid


class MainWindow(QMainWindow):
    """
    Fixed main window with proper PySide6 imports and full screen support.
    
    Fixes applied:
    - QAction import moved from QtWidgets to QtGui (PySide6 requirement)
    - Full screen initialization fixed
    - Icon paths corrected for Assets/ folder
    - Sidebar contrast improved
    - Header bar resize functionality restored
    """
    
    def __init__(self, DatabasePath: str = "Assets/my_library.db"):
        super().__init__()
        
        # Set up logging
        self.Logger = logging.getLogger(__name__)
        
        # Store database path
        self.DatabasePath = DatabasePath
        
        # Initialize components
        self.DatabaseManager: Optional[DatabaseManager] = None
        self.BookService: Optional[BookService] = None
        self.FilterPanel: Optional[FilterPanel] = None
        self.BookGrid: Optional[BookGrid] = None
        
        # Initialize UI
        self._InitializeWindow()
        self._ApplyFixedStyling()
        self._InitializeServices()
        self._SetupUI()
        self._ConnectSignals()
        
        self.Logger.info("Main window initialized successfully with fixes")
    
    def _InitializeWindow(self) -> None:
        """Initialize basic window properties with full screen support"""
        self.setWindowTitle("Anderson's Library")
        self.setMinimumSize(1200, 800)  # ✅ Increased minimum size
        
        # ✅ Fixed: Proper full screen initialization
        self.resize(1400, 1000)  # Set a good default size first
        
        # ✅ Fixed: Set window icon with correct Assets/ path
        IconPath = Path("Assets/icon.png")
        if IconPath.exists():
            self.setWindowIcon(QIcon(str(IconPath)))
            self.Logger.info(f"Window icon loaded from {IconPath}")
        else:
            # Try alternative icon locations
            for IconFile in ["Assets/BowersWorld.png", "Assets/Icons/icon.png", "Assets/icons/icon.png"]:
                IconPath = Path(IconFile)
                if IconPath.exists():
                    self.setWindowIcon(QIcon(str(IconPath)))
                    self.Logger.info(f"Window icon loaded from {IconPath}")
                    break
            else:
                self.Logger.warning("No window icon found in Assets/ folder")
    
    def _ApplyFixedStyling(self) -> None:
        """Apply enhanced styling with better contrast and icon paths"""
        self.setStyleSheet("""
            * {
                background-color: qlineargradient(
                    spread:repeat, x1:1, y1:0, x2:1, y2:1, 
                    stop:0.00480769 rgba(3, 50, 76, 255), 
                    stop:0.293269 rgba(6, 82, 125, 255), 
                    stop:0.514423 rgba(8, 117, 178, 255), 
                    stop:0.745192 rgba(7, 108, 164, 255), 
                    stop:1 rgba(3, 51, 77, 255)
                );
                color: #FFFFFF;
                border: none;
                font-family: "Ubuntu", "Arial", sans-serif;
                font-size: 14px;
            }

            /* ✅ Fixed: Sidebar contrast improvements */
            QFrame#FilterPanel {
                background-color: rgba(255, 255, 255, 0.1);
                border-right: 2px solid rgba(255, 255, 255, 0.3);
            }
            
            QLabel {
                color: #FFFFFF;
                font-weight: bold;
                padding: 5px;
            }
            
            /* ✅ Fixed: ComboBox styling with corrected icon paths */
            QComboBox {
                background-color: rgba(255, 255, 255, 0.9);
                color: #000000;  /* Black text for readability */
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
            }
            
            QComboBox::drop-down {
                border: none;
                background-color: transparent;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: url(Assets/arrow.png);
                width: 16px;
                height: 16px;
            }

            /* ✅ Fixed: Better dropdown contrast */
            QComboBox QAbstractItemView {
                background-color: #2E3B4E;
                color: #FFFFFF;
                selection-background-color: #4CAF50;
                border: 2px solid #4CAF50;
            }

            QComboBox::item:hover, QListView::item:hover {
                background-color: #4CAF50;
                color: #FFFFFF;
            }
            
            /* ✅ Fixed: Search box styling */
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.9);
                color: #000000;  /* Black text for readability */
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            
            QLineEdit:focus {
                border: 2px solid #FFC107;
                background-color: #FFFFFF;
            }
            
            /* ✅ Fixed: Status bar styling */
            QStatusBar {
                background-color: #780000; 
                color: #FFFFFF;
                font-weight: bold;
                padding: 5px;
            }
            
            /* ✅ Fixed: Tooltip styling */
            QToolTip { 
                color: #FFFFFF; 
                background-color: #2E3B4E;
                border: 2px solid #4CAF50;
                padding: 5px;
                font-size: 14px; 
            }
            
            /* ✅ Fixed: Scroll area styling */
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            QScrollBar:vertical {
                background-color: rgba(255, 255, 255, 0.1);
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: rgba(255, 255, 255, 0.5);
            }
        """)
    
    def _InitializeServices(self) -> None:
        """Initialize database and business logic services"""
        try:
            # Initialize database connection
            self.DatabaseManager = DatabaseManager(self.DatabasePath)
            
            # Initialize book service
            self.BookService = BookService(self.DatabaseManager)
            
            self.Logger.info("Services initialized successfully")
            
        except Exception as Error:
            self.Logger.error(f"Failed to initialize services: {Error}")
            QMessageBox.critical(
                self,
                "Database Error",
                f"Failed to initialize database:\n{Error}\n\nPlease check that the database file exists."
            )
            raise
    
    def _SetupUI(self) -> None:
        """Setup the main user interface layout"""
        try:
            # Create central widget
            CentralWidget = QWidget()
            self.setCentralWidget(CentralWidget)
            
            # Create main layout
            MainLayout = QHBoxLayout(CentralWidget)
            MainLayout.setContentsMargins(10, 10, 10, 10)
            MainLayout.setSpacing(10)
            
            # Create splitter for resizable panels
            Splitter = QSplitter(Qt.Horizontal)
            MainLayout.addWidget(Splitter)
            
            # ✅ Create filter panel with fixed styling
            self.FilterPanel = FilterPanel(self.BookService)
            self.FilterPanel.setObjectName("FilterPanel")  # For CSS targeting
            self.FilterPanel.setMaximumWidth(300)
            self.FilterPanel.setMinimumWidth(250)
            Splitter.addWidget(self.FilterPanel)
            
            # ✅ Create book grid with improved layout
            self.BookGrid = BookGrid(self.BookService)
            Splitter.addWidget(self.BookGrid)
            
            # Set splitter proportions (20% sidebar, 80% main area)
            Splitter.setSizes([250, 1150])
            
            # ✅ Create status bar with book count
            self.StatusBar = QStatusBar()
            self.setStatusBar(self.StatusBar)
            self.StatusBar.showMessage("Anderson's Library - Ready")
            
            self.Logger.info("UI setup completed successfully")
            
        except Exception as Error:
            self.Logger.error(f"Failed to setup UI: {Error}")
            raise
    
    def _ConnectSignals(self) -> None:
        """Connect signals between components"""
        try:
            if self.FilterPanel and self.BookGrid:
                # Connect filter changes to book grid updates
                self.FilterPanel.FiltersChanged.connect(self.BookGrid.ApplyFilters)
                
                # Connect book selection to status updates
                self.BookGrid.BookSelected.connect(self._UpdateStatusBar)
                
                self.Logger.info("Signals connected successfully")
                
        except Exception as Error:
            self.Logger.error(f"Failed to connect signals: {Error}")
    
    def _UpdateStatusBar(self, BookInfo: dict) -> None:
        """Update status bar with selected book information"""
        try:
            if BookInfo:
                Message = f"Selected: {BookInfo.get('Title', 'Unknown')} by {BookInfo.get('Author', 'Unknown')}"
            else:
                Message = "Anderson's Library - Ready"
            
            self.StatusBar.showMessage(Message)
            
        except Exception as Error:
            self.Logger.error(f"Failed to update status bar: {Error}")
    
    def showEvent(self, event):
        """Override show event to ensure proper full screen display"""
        super().showEvent(event)
        
        # ✅ Fixed: Force full screen after window is shown
        QTimer.singleShot(100, self._EnsureFullScreen)
    
    def _EnsureFullScreen(self) -> None:
        """Ensure the window displays at maximum size"""
        try:
            # Get available screen geometry
            Screen = QApplication.primaryScreen()
            if Screen:
                ScreenGeometry = Screen.availableGeometry()
                self.setGeometry(ScreenGeometry)
                self.Logger.info(f"Window set to full screen: {ScreenGeometry}")
            else:
                # Fallback to showMaximized
                self.showMaximized()
                self.Logger.info("Window maximized (fallback)")
                
        except Exception as Error:
            self.Logger.error(f"Failed to set full screen: {Error}")
            self.showMaximized()  # Fallback
    
    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        
        # Update status bar with window size
        Size = event.size()
        self.StatusBar.showMessage(f"Window Size: {Size.width()} x {Size.height()}")
        
        # ✅ Fixed: Ensure components respond to resize
        if hasattr(self, 'BookGrid') and self.BookGrid:
            self.BookGrid.HandleResize()


def CreateAndShowMainWindow(DatabasePath: str = "Assets/my_library.db") -> MainWindow:
    """
    Create and display the main window with all fixes applied.
    
    Args:
        DatabasePath: Path to SQLite database file
        
    Returns:
        MainWindow instance with fixes
    """
    try:
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(name)s - %(levelname)s: %(message)s'
        )
        
        # Create main window
        MainWindowInstance = MainWindow(DatabasePath)
        
        # ✅ Fixed: Show in full screen mode
        MainWindowInstance.show()  # Show first, then maximize
        MainWindowInstance._EnsureFullScreen()  # Then ensure full screen
        
        return MainWindowInstance
        
    except Exception as Error:
        logging.error(f"Failed to create main window: {Error}")
        raise


def RunApplication() -> int:
    """
    Run the complete Anderson's Library application with all fixes.
    
    Returns:
        Application exit code
    """
    try:
        # Create QApplication
        App = QApplication.instance()
        if App is None:
            App = QApplication(sys.argv)
        
        # Set application properties
        App.setApplicationName("Anderson's Library")
        App.setApplicationVersion("2.0")
        App.setOrganizationName("Project Himalaya")
        App.setOrganizationDomain("BowersWorld.com")
        
        # Create and show main window
        MainWindowInstance = CreateAndShowMainWindow()
        
        # Run the event loop
        return App.exec()
        
    except Exception as Error:
        logging.error(f"Application failed to run: {Error}")
        return 1


if __name__ == "__main__":
    sys.exit(RunApplication())