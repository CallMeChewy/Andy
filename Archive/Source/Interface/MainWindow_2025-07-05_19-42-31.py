# File: MainWindow.py
# Path: Source/Interface/MainWindow.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  01:34PM
"""
Description: Enhanced Main Window with Icons and Improved Styling
Standard Qt design with Assets/ folder icons and enhanced visual elements.
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
from PySide6.QtGui import QIcon, QPixmap

# Import our modules
from Source.Core.DatabaseManager import DatabaseManager
from Source.Core.BookService import BookService
from Source.Interface.FilterPanel import FilterPanel
from Source.Interface.BookGrid import BookGrid


class MainWindow(QMainWindow):
    """Enhanced main window with icons and improved styling."""
    
    def __init__(self, DatabasePath: str = "Assets/my_library.db"):
        super().__init__()
        
        self.Logger = logging.getLogger(__name__)
        self.DatabasePath = DatabasePath
        
        # Initialize components
        self.DatabaseManager: Optional[DatabaseManager] = None
        self.BookService: Optional[BookService] = None
        self.FilterPanel: Optional[FilterPanel] = None
        self.BookGrid: Optional[BookGrid] = None
        
        # Initialize UI
        self._InitializeWindow()
        self._ApplyEnhancedStyling()
        self._InitializeServices()
        self._SetupUI()
        self._ConnectSignals()
        
        self.Logger.info("Enhanced main window initialized")
    
    def _InitializeWindow(self) -> None:
        """Initialize window with icon and properties"""
        self.setWindowTitle("Anderson's Library")
        self.setMinimumSize(1000, 600)
        
        # Set multiple icon sizes for better display
        IconPaths = [
            Path("Assets/icon.png"),
            Path("Assets/BowersWorld.png"),
            Path("Assets/library/icon.png")
        ]
        
        for IconPath in IconPaths:
            if IconPath.exists():
                self.setWindowIcon(QIcon(str(IconPath)))
                self.Logger.info(f"Set window icon: {IconPath}")
                break
    
    def _ApplyEnhancedStyling(self) -> None:
        """Apply enhanced styling with better visual hierarchy"""
        self.setStyleSheet("""
            /* Main window gradient background */
            QMainWindow {
                background-color: qlineargradient(
                    spread:repeat, x1:1, y1:0, x2:1, y2:1, 
                    stop:0.00480769 rgba(3, 50, 76, 255), 
                    stop:0.293269 rgba(6, 82, 125, 255), 
                    stop:0.514423 rgba(8, 117, 178, 255), 
                    stop:0.745192 rgba(7, 108, 164, 255), 
                    stop:1 rgba(3, 51, 77, 255)
                );
                color: #FFFFFF;
            }
            
            /* Splitter styling */
            QSplitter::handle {
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            
            QSplitter::handle:hover {
                background-color: rgba(255, 255, 255, 0.5);
            }
            
            /* Status bar enhancement */
            QStatusBar {
                background-color: #780000; 
                color: white;
                font-weight: bold;
                border-top: 2px solid #aa0000;
            }
            
            /* Scroll area enhancements */
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
        """Initialize database and business services"""
        try:
            self.DatabaseManager = DatabaseManager(self.DatabasePath)
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
        """Set up enhanced user interface"""
        # Create central widget
        CentralWidget = QWidget()
        self.setCentralWidget(CentralWidget)
        
        # Create main layout
        MainLayout = QVBoxLayout(CentralWidget)
        MainLayout.setContentsMargins(0, 0, 0, 0)
        
        # Create horizontal splitter
        self.Splitter = QSplitter(Qt.Horizontal)
        MainLayout.addWidget(self.Splitter)
        
        # Create enhanced filter panel
        self.FilterPanel = FilterPanel(self.BookService)
        self.FilterPanel.setMinimumWidth(320)
        self.FilterPanel.setMaximumWidth(400)
        self.Splitter.addWidget(self.FilterPanel)
        
        # Create book grid
        self.BookGrid = BookGrid(self.BookService)
        self.Splitter.addWidget(self.BookGrid)
        
        # Set splitter proportions (25% filter, 75% books)
        self.Splitter.setSizes([350, 1050])
        self.Splitter.setStretchFactor(0, 0)  
        self.Splitter.setStretchFactor(1, 1)  
        self.Splitter.setCollapsible(0, False)
        
        # Enhanced status bar
        self.StatusBar = QStatusBar()
        self.setStatusBar(self.StatusBar)
        self.StatusBar.showMessage("🚀 Anderson's Library - Ready to explore your collection!")
        
        self.Logger.info("Enhanced UI components created")
    
    def _ConnectSignals(self) -> None:
        """Connect component signals"""
        if self.FilterPanel and self.BookGrid:
            self.FilterPanel.SearchRequested.connect(self.BookGrid.FilterBooks)
            self.FilterPanel.FilterChanged.connect(self.BookGrid.FilterBooks)
            self.BookGrid.StatusUpdate.connect(self.StatusBar.showMessage)
            self.Logger.info("Component signals connected")
    
    def resizeEvent(self, Event) -> None:
        """Handle window resize with grid refresh"""
        super().resizeEvent(Event)
        if self.BookGrid:
            QTimer.singleShot(50, self.BookGrid.RefreshLayout)
    
    def closeEvent(self, Event) -> None:
        """Handle application close"""
        try:
            self.Logger.info("Application closing")
            Event.accept()
        except Exception as Error:
            self.Logger.error(f"Error during close: {Error}")
            Event.accept()


def CreateAndShowMainWindow(DatabasePath: str = "Assets/my_library.db") -> MainWindow:
    """Create and show the enhanced main window."""
    try:
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(name)s - %(levelname)s: %(message)s'
        )
        
        MainWindowInstance = MainWindow(DatabasePath)
        MainWindowInstance.showMaximized()
        return MainWindowInstance
        
    except Exception as Error:
        logging.error(f"Failed to create main window: {Error}")
        raise


def RunApplication() -> int:
    """Run the enhanced application."""
    try:
        App = QApplication.instance()
        if App is None:
            App = QApplication(sys.argv)
        
        MainWindowInstance = CreateAndShowMainWindow()
        return App.exec()
        
    except Exception as Error:
        logging.error(f"Application failed: {Error}")
        return 1


if __name__ == "__main__":
    sys.exit(RunApplication())
