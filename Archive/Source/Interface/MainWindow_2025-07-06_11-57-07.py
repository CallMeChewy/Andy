# File: MainWindow.py
# Path: Source/Interface/MainWindow.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-06
# Last Modified: 2025-07-06  08:55AM
"""
Description: UPDATED DATABASE PATH - Anderson's Library Main Window
Updated to use the new database location with BLOB thumbnails and relational schema.
"""

import sys
import logging
from typing import List, Dict, Any

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QFrame, QStatusBar, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon

from Source.Core.DatabaseManager import DatabaseManager
from Source.Core.BookService import BookService
from Source.Interface.FilterPanel import FilterPanel
from Source.Interface.BookGrid import BookGrid


class MainWindow(QMainWindow):
    """
    UPDATED - Anderson's Library with new database path and BLOB thumbnail support.
    """
    
    def __init__(self):
        super().__init__()
        self.Logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize core components
        self.DatabaseManager = None
        self.BookService = None
        self.FilterPanel = None
        self.BookGrid = None
        
        # Initialize UI
        self.InitializeComponents()
        self.SetupUI()
        self.ConnectSignals()
        self.ApplyOriginalBeautifulTheme()
        self.LoadInitialData()
        
        self.Logger.info("MainWindow initialized with new database schema")
    
    def InitializeComponents(self):
        """Initialize core application components with new database path."""
        try:
            # NEW: Use the updated database path with BLOB thumbnails
            self.DatabaseManager = DatabaseManager("Data/Databases/MyLibrary.db")
            self.BookService = BookService(self.DatabaseManager)
            self.FilterPanel = FilterPanel(self.BookService)
            self.BookGrid = BookGrid()
            
        except Exception as Error:
            self.Logger.error(f"Failed to initialize components: {Error}")
            QMessageBox.critical(self, "Initialization Error", 
                               f"Failed to initialize application components:\n{Error}")
            sys.exit(1)
    
    def SetupUI(self):
        """Setup the main user interface."""
        self.setWindowTitle("Anderson's Library")
        self.setMinimumSize(1200, 800)
        
        # Start maximized
        self.showMaximized()
        
        # Create central widget
        CentralWidget = QWidget()
        self.setCentralWidget(CentralWidget)
        
        # Create main layout
        MainLayout = QHBoxLayout(CentralWidget)
        MainLayout.setContentsMargins(5, 5, 5, 5)
        
        # Create splitter
        Splitter = QSplitter(Qt.Horizontal)
        MainLayout.addWidget(Splitter)
        
        # Setup left panel (filters)
        LeftPanel = self.CreateLeftPanel()
        Splitter.addWidget(LeftPanel)
        
        # Setup right panel (book grid)
        RightPanel = self.CreateRightPanel()
        Splitter.addWidget(RightPanel)
        
        # Original proportions
        Splitter.setSizes([350, 1050])
        Splitter.setCollapsible(0, False)
        
        # Original red status bar
        self.SetupStatusBar()
    
    def CreateLeftPanel(self) -> QFrame:
        """Create the left panel with original styling."""
        LeftPanel = QFrame()
        LeftPanel.setObjectName("LeftPanel")
        LeftPanel.setFrameStyle(QFrame.StyledPanel)
        LeftPanel.setFixedWidth(350)
        
        # Left panel layout
        LeftLayout = QVBoxLayout(LeftPanel)
        LeftLayout.setContentsMargins(15, 15, 15, 15)
        LeftLayout.setSpacing(10)
        
        # Add filter panel
        LeftLayout.addWidget(self.FilterPanel)
        
        # Add stretch to push everything to top
        LeftLayout.addStretch()
        
        return LeftPanel
    
    def CreateRightPanel(self) -> QFrame:
        """Create the right panel."""
        RightPanel = QFrame()
        RightPanel.setFrameStyle(QFrame.StyledPanel)
        
        # Right panel layout
        RightLayout = QVBoxLayout(RightPanel)
        RightLayout.setContentsMargins(5, 5, 5, 5)
        
        # Add book grid
        RightLayout.addWidget(self.BookGrid)
        
        return RightPanel
    
    def SetupStatusBar(self):
        """Setup the original red status bar."""
        self.StatusBar = QStatusBar()
        self.setStatusBar(self.StatusBar)
        self.StatusBar.setStyleSheet("background-color: #780000; color: white;")
        self.StatusBar.showMessage("Ready - Now with BLOB thumbnails and relational schema!")
    
    def ConnectSignals(self):
        """Connect signals with compatibility for different versions."""
        try:
            # Try multiple signal names for maximum compatibility
            if hasattr(self.FilterPanel, 'SearchRequested'):
                self.FilterPanel.SearchRequested.connect(self.OnSearchRequested)
            
            if hasattr(self.FilterPanel, 'FilterChanged'):
                self.FilterPanel.FilterChanged.connect(self.OnFiltersChanged)
            elif hasattr(self.FilterPanel, 'FiltersChanged'):
                self.FilterPanel.FiltersChanged.connect(self.OnFiltersChanged)
            
            if hasattr(self.BookGrid, 'BookClicked'):
                self.BookGrid.BookClicked.connect(self.OnBookClicked)
            
            self.Logger.info("Signals connected successfully")
            
        except Exception as Error:
            self.Logger.error(f"Failed to connect signals: {Error}")
    
    def ApplyOriginalBeautifulTheme(self):
        """Apply the original beautiful blue gradient theme."""
        # The exact original stylesheet that made it beautiful
        OriginalStyleSheet = """
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
        """
        
        self.setStyleSheet(OriginalStyleSheet)
        self.Logger.info("Original beautiful blue gradient theme applied")
    
    def LoadInitialData(self):
        """Load initial data."""
        try:
            QTimer.singleShot(100, self.DisplayAllBooks)
        except Exception as Error:
            self.Logger.error(f"Failed to load initial data: {Error}")
    
    def DisplayAllBooks(self):
        """Display all books using the new schema."""
        try:
            # Use new database manager with relational schema
            BookDicts = self.DatabaseManager.GetBooks()
            self.BookGrid.DisplayBooks(BookDicts)
            
            BookCount = len(BookDicts)
            self.StatusBar.showMessage(f"Showing all books: {BookCount} books with BLOB thumbnails")
            self.Logger.info(f"Displayed {BookCount} books with new schema")
            
        except Exception as Error:
            self.Logger.error(f"Failed to display books: {Error}")
            self.StatusBar.showMessage("Error loading books")
    
    def OnSearchRequested(self, SearchTerm):
        """Handle search request."""
        try:
            # Handle different search term formats
            if hasattr(SearchTerm, 'SearchTerm'):
                Term = SearchTerm.SearchTerm
            else:
                Term = str(SearchTerm).strip()
            
            self.Logger.info(f"Search requested: '{Term}'")
            
            if not Term:
                self.DisplayAllBooks()
                return
            
            # Use new database manager search
            BookDicts = self.DatabaseManager.GetBooks(SearchTerm=Term)
            self.BookGrid.DisplayBooks(BookDicts)
            
            BookCount = len(BookDicts)
            self.StatusBar.showMessage(f"Search results for '{Term}': {BookCount} books found")
            
        except Exception as Error:
            self.Logger.error(f"Search failed: {Error}")
            self.StatusBar.showMessage(f"Search error: {Error}")
    
    def OnFiltersChanged(self, Category, Subject=None):
        """Handle category/subject filtering with new schema."""
        try:
            # Handle different parameter formats
            if hasattr(Category, 'Categories'):
                # SearchCriteria object
                Cat = Category.Categories[0] if Category.Categories else ""
                Sub = Category.Subjects[0] if Category.Subjects else ""
            else:
                # String parameters
                Cat = str(Category) if Category else ""
                Sub = str(Subject) if Subject else ""
            
            self.Logger.info(f"Filters changed: Category='{Cat}', Subject='{Sub}'")
            
            # Handle "All Categories" case
            if Cat == "All Categories" or not Cat:
                self.DisplayAllBooks()
                return
            
            # Use new database manager filter with JOINs
            BookDicts = self.DatabaseManager.GetBooks(Category=Cat, Subject=Sub)
            self.BookGrid.DisplayBooks(BookDicts)
            
            BookCount = len(BookDicts)
            if Cat and Sub and Sub != "All Subjects":
                self.StatusBar.showMessage(f"Showing books: {Cat} → {Sub} ({BookCount} books)")
            elif Cat:
                self.StatusBar.showMessage(f"Showing books: {Cat} ({BookCount} books)")
            else:
                self.StatusBar.showMessage(f"Showing {BookCount} books")
                
        except Exception as Error:
            self.Logger.error(f"Filter change failed: {Error}")
            self.StatusBar.showMessage(f"Filter error: {Error}")
    
    def OnBookClicked(self, BookTitle: str):
        """Handle book click event."""
        try:
            self.Logger.info(f"Book clicked: '{BookTitle}'")
            
            # Update last opened timestamp
            self.DatabaseManager.UpdateLastOpened(BookTitle)
            
            # Try to use BookService if available
            if hasattr(self.BookService, 'OpenBook'):
                self.BookService.OpenBook(BookTitle)
            
            # Update status bar
            self.StatusBar.showMessage(f"Book opened: '{BookTitle}'")
            
        except Exception as Error:
            self.Logger.error(f"Failed to open book '{BookTitle}': {Error}")
            self.StatusBar.showMessage(f"Error opening book: {Error}")
    
    def closeEvent(self, event):
        """Handle application close event with proper cleanup."""
        try:
            self.Logger.info("Application shutdown initiated")
            
            if self.DatabaseManager and hasattr(self.DatabaseManager, 'Close'):
                self.DatabaseManager.Close()
                self.Logger.info("Database connection closed")
            
            event.accept()
            self.Logger.info("Anderson's Library Closed")
            
        except Exception as Error:
            self.Logger.error(f"Error during shutdown: {Error}")
            event.accept()


def RunApplication():
    """Run the Anderson's Library application with new database schema."""
    App = QApplication(sys.argv)
    App.setApplicationName("Anderson's Library")
    App.setApplicationVersion("2.0")
    App.setOrganizationName("Project Himalaya")
    App.setOrganizationDomain("BowersWorld.com")
    
    try:
        Window = MainWindow()
        Window.show()
        
        Logger = logging.getLogger("MainWindow")
        Logger.info("Anderson's Library Started with BLOB thumbnails")
        
        return App.exec()
        
    except Exception as Error:
        Logger = logging.getLogger("MainWindow")
        Logger.critical(f"Failed to start application: {Error}")
        QMessageBox.critical(None, "Critical Error", 
                           f"Failed to start Anderson's Library:\n{Error}")
        return 1


if __name__ == "__main__":
    sys.exit(RunApplication())