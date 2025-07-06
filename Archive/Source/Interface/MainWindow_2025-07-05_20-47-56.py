# File: MainWindow.py
# Path: Source/Interface/MainWindow.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  07:40PM
"""
Description: MainWindow with Simple Interface Compatibility
Updated to work with plain List[Book] instead of SearchResult objects.
Orchestrates FilterPanel and BookGrid with correct event handling workflow.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QMessageBox, QLabel
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap, QFont

# Import our modules
from Source.Core.DatabaseManager import DatabaseManager
from Source.Core.BookService import BookService
from Source.Interface.FilterPanel import FilterPanel
from Source.Interface.BookGrid import BookGrid
from Source.Data.DatabaseModels import SearchCriteria, Book


class MainWindow(QMainWindow):
    """
    MainWindow with simple interface compatibility.
    Works with plain List[Book] instead of SearchResult objects.
    Handles complete workflow: Category selection → Subject population → Book display.
    """
    
    def __init__(self, DatabasePath: str = "Assets/my_library.db", *args, **kwargs):
        """
        Initialize main window with simple interface coordination.
        
        Args:
            DatabasePath: Path to SQLite database
        """
        super().__init__(*args, **kwargs)
        
        # Initialize logging
        self.Logger = logging.getLogger(__name__)
        
        # Core dependencies
        try:
            self.DatabaseManager = DatabaseManager(DatabasePath)
            self.BookService = BookService(self.DatabaseManager)
        except Exception as Error:
            self.Logger.error(f"Failed to initialize services: {Error}")
            QMessageBox.critical(None, "Database Error", f"Failed to connect to database:\n{Error}")
            sys.exit(1)
        
        # UI Components
        self.FilterPanel = None
        self.BookGrid = None
        self.StatusBar = None
        
        # Window setup
        self._SetupWindow()
        self._CreateUI()
        self._ConnectSignals()
        self._SetInitialState()
        
        self.Logger.info("MainWindow initialized successfully")
    
    def _SetupWindow(self) -> None:
        """Configure main window properties"""
        self.setWindowTitle("Anderson's Library - Professional Edition")
        self.setMinimumSize(1000, 600)
        
        # Set window icon if available
        IconPath = Path("Assets/icon.png")
        if IconPath.exists():
            self.setWindowIcon(QIcon(str(IconPath)))
        
        # Set initial size and position
        self.resize(1200, 800)
        
        # Apply window styling
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                          stop:0 rgba(0, 50, 100, 255),
                                          stop:1 rgba(0, 100, 150, 255));
            }
        """)
    
    def _CreateUI(self) -> None:
        """Create the user interface"""
        # Central widget
        CentralWidget = QWidget()
        self.setCentralWidget(CentralWidget)
        
        # Main layout (horizontal split)
        MainLayout = QHBoxLayout(CentralWidget)
        MainLayout.setContentsMargins(0, 0, 0, 0)
        MainLayout.setSpacing(0)
        
        # Create components
        self.FilterPanel = FilterPanel(self.BookService)
        self.BookGrid = BookGrid(self.BookService)
        
        # Create splitter for resizable panes
        Splitter = QSplitter(Qt.Orientation.Horizontal)
        Splitter.addWidget(self.FilterPanel)
        Splitter.addWidget(self.BookGrid)
        
        # Set splitter proportions (filter panel fixed, grid gets remainder)
        Splitter.setSizes([320, 880])
        Splitter.setCollapsible(0, False)  # Filter panel can't be collapsed
        
        MainLayout.addWidget(Splitter)
        
        # Status bar
        self.StatusBar = QStatusBar()
        self.StatusBar.setStyleSheet("""
            QStatusBar {
                background-color: rgba(0, 50, 100, 200);
                color: white;
                border-top: 1px solid rgba(255, 255, 255, 100);
                font-size: 11px;
                padding: 2px;
            }
        """)
        self.setStatusBar(self.StatusBar)
        
        # Set initial status
        self.StatusBar.showMessage("Select a category to begin browsing your library")
    
    def _ConnectSignals(self) -> None:
        """Connect component signals to handlers"""
        if self.FilterPanel:
            # Filter changes (category/subject selections)
            self.FilterPanel.FilterChanged.connect(self._OnFilterChanged)
            
            # Search requests (search box usage)
            self.FilterPanel.SearchRequested.connect(self._OnSearchRequested)
            
            # Status updates from filter panel
            self.FilterPanel.StatusUpdate.connect(self._OnStatusUpdate)
        
        if self.BookGrid:
            # Status updates from book grid
            self.BookGrid.StatusUpdate.connect(self._OnStatusUpdate)
            
            # Book opened events
            self.BookGrid.BookOpened.connect(self._OnBookOpened)
    
    def _SetInitialState(self) -> None:
        """Set initial application state"""
        # Display welcome message in grid
        self.BookGrid.DisplayBooks([])  # Empty list shows "no books" message
        
        # Log startup
        self.Logger.info("Application ready - awaiting user interaction")
    
    def _OnFilterChanged(self, Criteria: SearchCriteria) -> None:
        """
        ✅ FIXED: Handle filter changes with simple List[Book] interface.
        Called when user selects category/subject combinations.
        
        Args:
            Criteria: Filter criteria with categories/subjects
        """
        try:
            self.Logger.debug(f"Filter changed: {Criteria.GetDescription()}")
            
            # Get books matching criteria - now returns plain List[Book]
            Books = self.BookService.SearchBooks(Criteria)
            
            # Display books in grid
            self.BookGrid.DisplayBooks(Books)
            
            # Update status
            if Criteria.Categories and Criteria.Subjects:
                StatusText = f"Category: {Criteria.Categories[0]} → Subject: {Criteria.Subjects[0]} ({len(Books)} books)"
            elif Criteria.Categories:
                StatusText = f"Category: {Criteria.Categories[0]} ({len(Books)} books)"
            else:
                StatusText = f"Showing {len(Books)} books"
                
            self.StatusBar.showMessage(StatusText)
            
        except Exception as Error:
            self.Logger.error(f"Failed to process filter change: {Error}")
            self.BookGrid.DisplayBooks([])  # Clear grid on error
            self.StatusBar.showMessage(f"Error loading books: {Error}")
    
    def _OnSearchRequested(self, Criteria: SearchCriteria) -> None:
        """
        ✅ FIXED: Handle search requests with simple List[Book] interface.
        Called when user types in search box.
        
        Args:
            Criteria: Search criteria with search term
        """
        try:
            self.Logger.debug(f"Search requested: '{Criteria.SearchTerm}'")
            
            # Get books matching search - now returns plain List[Book]
            Books = self.BookService.SearchBooks(Criteria)
            
            # Display search results
            self.BookGrid.DisplayBooks(Books)
            
            # Update status
            SearchTerm = Criteria.SearchTerm
            StatusText = f"Search results for '{SearchTerm}': {len(Books)} books found"
            self.StatusBar.showMessage(StatusText)
            
        except Exception as Error:
            self.Logger.error(f"Failed to process search: {Error}")
            self.BookGrid.DisplayBooks([])  # Clear grid on error
            self.StatusBar.showMessage(f"Search error: {Error}")
    
    def _OnStatusUpdate(self, StatusText: str) -> None:
        """
        Handle status updates from components.
        
        Args:
            StatusText: Status message to display
        """
        self.StatusBar.showMessage(StatusText)
    
    def _OnBookOpened(self, BookTitle: str) -> None:
        """
        Handle book opened events.
        
        Args:
            BookTitle: Title of opened book
        """
        self.Logger.info(f"Book opened: '{BookTitle}'")
        self.StatusBar.showMessage(f"Opened: {BookTitle}")
    
    def closeEvent(self, Event) -> None:
        """Handle application closing"""
        try:
            # Close database connection
            if hasattr(self, 'DatabaseManager'):
                self.DatabaseManager.Close()
            
            self.Logger.info("Application closing cleanly")
            Event.accept()
            
        except Exception as Error:
            self.Logger.error(f"Error during shutdown: {Error}")
            Event.accept()  # Close anyway
    
    # =================================================================
    # PUBLIC INTERFACE
    # =================================================================
    
    def RefreshData(self) -> None:
        """Refresh all data from database"""
        try:
            if self.FilterPanel:
                self.FilterPanel.RefreshData()
            
            if self.BookGrid:
                self.BookGrid.DisplayBooks([])
            
            self.StatusBar.showMessage("Data refreshed - select a category to begin")
            self.Logger.info("Data refreshed successfully")
            
        except Exception as Error:
            self.Logger.error(f"Failed to refresh data: {Error}")
            self.StatusBar.showMessage(f"Refresh error: {Error}")
    
    def GetApplicationState(self) -> dict:
        """
        Get current application state for debugging.
        
        Returns:
            Dictionary with current state information
        """
        State = {
            'WindowSize': [self.width(), self.height()],
            'DatabaseConnected': hasattr(self, 'DatabaseManager') and self.DatabaseManager.IsConnected(),
            'BooksDisplayed': len(self.BookGrid.GetCurrentBooks()) if self.BookGrid else 0,
            'GridStatistics': self.BookGrid.GetGridStatistics() if self.BookGrid else {},
            'FilterCriteria': self.FilterPanel.GetCurrentCriteria().__dict__ if self.FilterPanel else {},
            'StatusMessage': self.StatusBar.currentMessage() if self.StatusBar else ""
        }
        
        return State


def RunApplication() -> None:
    """Run the Anderson's Library application"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    Logger = logging.getLogger(__name__)
    
    try:
        # Create application
        App = QApplication(sys.argv)
        App.setApplicationName("Anderson's Library")
        App.setApplicationVersion("2.0 Professional")
        
        # Create and show main window
        Window = MainWindow()
        Window.show()
        
        Logger.info("🏔️ Anderson's Library - Professional Edition Started 🏔️")
        
        # Run application
        sys.exit(App.exec())
        
    except Exception as Error:
        Logger.error(f"Application failed to start: {Error}")
        if 'App' in locals():
            QMessageBox.critical(None, "Startup Error", f"Failed to start Anderson's Library:\n\n{Error}")
        sys.exit(1)


if __name__ == "__main__":
    RunApplication()