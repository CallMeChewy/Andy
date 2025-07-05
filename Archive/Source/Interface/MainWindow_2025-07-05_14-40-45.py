# File: MainWindow.py
# Path: Source/Interface/MainWindow.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  01:34PM
"""
Description: Main Application Window for Anderson's Library - Standard Qt Design
Uses standard QMainWindow instead of CustomWindow framework.
Maintains original blue gradient theme and functionality.
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
from PySide6.QtGui import QIcon

# Import our modules
sys.path.append(str(Path(__file__).parent.parent))
from Source.Core.DatabaseManager import DatabaseManager
from Source.Core.BookService import BookService
from Source.Interface.FilterPanel import FilterPanel
from Source.Interface.BookGrid import BookGrid


class MainWindow(QMainWindow):
    """
    Main application window using standard Qt design.
    Orchestrates FilterPanel and BookGrid components.
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
        self._ApplyOriginalStyling()
        self._InitializeServices()
        self._SetupUI()
        self._ConnectSignals()
        
        self.Logger.info("Main window initialized successfully")
    
    def _InitializeWindow(self) -> None:
        """Initialize basic window properties"""
        self.setWindowTitle("Anderson's Library")
        self.setMinimumSize(1000, 600)
        
        # Set window icon if available
        IconPath = Path("Assets/icon.png")
        if IconPath.exists():
            self.setWindowIcon(QIcon(str(IconPath)))
    
    def _ApplyOriginalStyling(self) -> None:
        """Apply the original blue gradient theme from Legacy/Andy.py"""
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
            }

            QComboBox::down-arrow {
                image: url(Assets/arrow.png);
            }

            QComboBox::item:hover, QListView::item:hover {
                border: 3px solid red;
            }
            
            QToolTip { 
                color: #ffffff; 
                border: none; 
                font-size: 16px; 
            }
            
            QStatusBar {
                background-color: #780000; 
                color: white;
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
        """Set up the user interface components"""
        # Create central widget
        CentralWidget = QWidget()
        self.setCentralWidget(CentralWidget)
        
        # Create main layout
        MainLayout = QVBoxLayout(CentralWidget)
        MainLayout.setContentsMargins(0, 0, 0, 0)
        
        # Create horizontal splitter
        self.Splitter = QSplitter(Qt.Horizontal)
        MainLayout.addWidget(self.Splitter)
        
        # Create filter panel (left side)
        self.FilterPanel = FilterPanel(self.BookService)
        self.FilterPanel.setMinimumWidth(320)
        self.FilterPanel.setMaximumWidth(400)
        self.Splitter.addWidget(self.FilterPanel)
        
        # Create book grid (right side)
        self.BookGrid = BookGrid(self.BookService)
        self.Splitter.addWidget(self.BookGrid)
        
        # Set splitter proportions (25% filter, 75% books)
        self.Splitter.setSizes([350, 1050])
        self.Splitter.setStretchFactor(0, 0)  # Filter panel doesn't stretch
        self.Splitter.setStretchFactor(1, 1)  # Book grid stretches
        
        # Prevent filter panel from being collapsed
        self.Splitter.setCollapsible(0, False)
        
        # Create status bar
        self.StatusBar = QStatusBar()
        self.setStatusBar(self.StatusBar)
        self.StatusBar.showMessage("Ready - Use search and filters to find books")
        
        self.Logger.info("UI components created successfully")
    
    def _ConnectSignals(self) -> None:
        """Connect signals between components"""
        if self.FilterPanel and self.BookGrid:
            # Connect search/filter signals
            self.FilterPanel.SearchRequested.connect(self.BookGrid.FilterBooks)
            self.FilterPanel.FilterChanged.connect(self.BookGrid.FilterBooks)
            
            # Connect status updates
            self.BookGrid.StatusUpdate.connect(self.StatusBar.showMessage)
            
            self.Logger.info("Component signals connected")
    
    def resizeEvent(self, Event) -> None:
        """Handle window resize events"""
        super().resizeEvent(Event)
        
        # Trigger book grid layout recalculation with small delay
        if self.BookGrid:
            QTimer.singleShot(50, self.BookGrid.RefreshLayout)
    
    def closeEvent(self, Event) -> None:
        """Handle window close events"""
        try:
            self.Logger.info("Application closing")
            Event.accept()
            
        except Exception as Error:
            self.Logger.error(f"Error during application close: {Error}")
            Event.accept()  # Close anyway


def CreateAndShowMainWindow(DatabasePath: str = "Assets/my_library.db") -> MainWindow:
    """
    Factory function to create and display the main application window.
    
    Args:
        DatabasePath: Path to SQLite database file
        
    Returns:
        MainWindow instance
    """
    try:
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(name)s - %(levelname)s: %(message)s'
        )
        
        # Create main window
        MainWindowInstance = MainWindow(DatabasePath)
        
        # Show maximized (matching original behavior)
        MainWindowInstance.showMaximized()
        
        return MainWindowInstance
        
    except Exception as Error:
        logging.error(f"Failed to create main window: {Error}")
        raise


def RunApplication() -> int:
    """
    Run the complete Anderson's Library application with standard Qt design.
    
    Returns:
        Application exit code
    """
    try:
        # Create QApplication
        App = QApplication.instance()
        if App is None:
            App = QApplication(sys.argv)
        
        # Create and show main window
        MainWindowInstance = CreateAndShowMainWindow()
        
        # Run the event loop
        return App.exec()
        
    except Exception as Error:
        logging.error(f"Application failed to run: {Error}")
        return 1


if __name__ == "__main__":
    sys.exit(RunApplication())
