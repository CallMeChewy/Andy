# File: MainWindow.py
# Path: Source/Interface/MainWindow.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  08:50PM
"""
Description: COMPATIBILITY FIX - Main Window Working with Existing Interface
Fixed to work with existing FilterPanel and BookService interface.
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
    COMPATIBILITY FIX - Main window that works with existing FilterPanel and BookService.
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
        self.ApplyHighContrastTheme()  # Better theme
        self.LoadInitialData()
        
        self.Logger.info("MainWindow initialized successfully")
    
    def InitializeComponents(self):
        """Initialize core application components."""
        try:
            # Initialize database manager
            self.DatabaseManager = DatabaseManager()
            
            # Initialize book service
            self.BookService = BookService(self.DatabaseManager)
            
            # Initialize UI components
            self.FilterPanel = FilterPanel(self.BookService)
            self.BookGrid = BookGrid()
            
        except Exception as Error:
            self.Logger.error(f"Failed to initialize components: {Error}")
            QMessageBox.critical(self, "Initialization Error", 
                               f"Failed to initialize application components:\n{Error}")
            sys.exit(1)
    
    def SetupUI(self):
        """Setup the main user interface."""
        self.setWindowTitle("🏔️ Anderson's Library - Professional Edition")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Create central widget
        CentralWidget = QWidget()
        self.setCentralWidget(CentralWidget)
        
        # Create main layout with splitter for resizable panels
        MainLayout = QHBoxLayout(CentralWidget)
        MainLayout.setContentsMargins(10, 10, 10, 10)
        
        # Create splitter for resizable panels
        Splitter = QSplitter(Qt.Horizontal)
        MainLayout.addWidget(Splitter)
        
        # Setup left panel (filters)
        LeftPanel = self.CreateLeftPanel()
        Splitter.addWidget(LeftPanel)
        
        # Setup right panel (book grid)
        RightPanel = self.CreateRightPanel()
        Splitter.addWidget(RightPanel)
        
        # Set splitter proportions (left panel smaller)
        Splitter.setSizes([300, 1100])  # Left panel: 300px, Right panel: remainder
        Splitter.setCollapsible(0, False)  # Don't allow left panel to collapse
        
        # Setup status bar
        self.SetupStatusBar()
    
    def CreateLeftPanel(self) -> QFrame:
        """Create the left panel containing filters and search."""
        LeftPanel = QFrame()
        LeftPanel.setObjectName("LeftPanel")
        LeftPanel.setFrameStyle(QFrame.StyledPanel)
        LeftPanel.setFixedWidth(350)  # Fixed width for consistency
        
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
        """Create the right panel containing the book grid."""
        RightPanel = QFrame()
        RightPanel.setFrameStyle(QFrame.StyledPanel)
        
        # Right panel layout
        RightLayout = QVBoxLayout(RightPanel)
        RightLayout.setContentsMargins(5, 5, 5, 5)
        
        # Add book grid
        RightLayout.addWidget(self.BookGrid)
        
        return RightPanel
    
    def SetupStatusBar(self):
        """Setup the status bar."""
        self.StatusBar = QStatusBar()
        self.setStatusBar(self.StatusBar)
        self.StatusBar.showMessage("Application ready - awaiting user interaction")
    
    def ConnectSignals(self):
        """COMPATIBILITY FIX - Connect signals using EXISTING signal names."""
        try:
            # FIXED: Check for correct signal names from existing FilterPanel
            if hasattr(self.FilterPanel, 'SearchRequested'):
                self.FilterPanel.SearchRequested.connect(self.OnSearchRequested)
            
            # FIXED: Use correct signal name (FilterChanged not FiltersChanged)
            if hasattr(self.FilterPanel, 'FilterChanged'):
                self.FilterPanel.FilterChanged.connect(self.OnFiltersChanged)
            
            # FIXED: Check for BookGrid signals
            if hasattr(self.BookGrid, 'BookClicked'):
                self.BookGrid.BookClicked.connect(self.OnBookClicked)
            
            self.Logger.info("Signals connected successfully")
            
        except Exception as Error:
            self.Logger.error(f"Failed to connect signals: {Error}")
    
    def ApplyHighContrastTheme(self):
        """Apply a high contrast theme that's actually readable."""
        StyleSheet = """
        /* Main Window - Light background */
        QMainWindow {
            background-color: #f5f5f5;
            color: #2c3e50;
        }
        
        /* Left Panel - Dark blue with WHITE text */
        QFrame#LeftPanel {
            background-color: #2c3e50;
            border: 2px solid #34495e;
            border-radius: 8px;
            padding: 10px;
        }
        
        /* Panel Labels - WHITE text for maximum contrast */
        QFrame#LeftPanel QLabel {
            color: #ffffff;
            font-weight: bold;
            font-size: 13px;
            padding: 5px 0px;
        }
        
        /* ComboBox - White background, dark text */
        QComboBox {
            background-color: #ffffff;
            border: 2px solid #bdc3c7;
            border-radius: 6px;
            padding: 8px;
            color: #2c3e50;
            font-size: 12px;
            min-height: 25px;
        }
        
        QComboBox:focus {
            border-color: #3498db;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 25px;
        }
        
        /* LineEdit (Search) - White background, dark text */
        QLineEdit {
            background-color: #ffffff;
            border: 2px solid #bdc3c7;
            border-radius: 6px;
            padding: 8px;
            color: #2c3e50;
            font-size: 12px;
            min-height: 25px;
        }
        
        QLineEdit:focus {
            border-color: #3498db;
        }
        
        /* Status Bar - Light background */
        QStatusBar {
            background-color: #ecf0f1;
            border-top: 1px solid #bdc3c7;
            color: #2c3e50;
            font-size: 12px;
            padding: 5px;
        }
        
        /* Right Panel */
        QFrame {
            background-color: #ffffff;
            border: 1px solid #e1e8ed;
        }
        """
        
        self.setStyleSheet(StyleSheet)
        self.Logger.info("High contrast theme applied")
    
    def LoadInitialData(self):
        """Load initial data and display all books."""
        try:
            QTimer.singleShot(100, self.DisplayAllBooks)
        except Exception as Error:
            self.Logger.error(f"Failed to load initial data: {Error}")
    
    def DisplayAllBooks(self):
        """COMPATIBILITY FIX - Display all books using existing interface."""
        try:
            # FIXED: Use existing BookService method
            if hasattr(self.BookService, 'GetAllBooks'):
                Books = self.BookService.GetAllBooks()
            elif hasattr(self.BookService, 'SearchBooks'):
                # If no GetAllBooks, try empty search
                from Source.Data.DatabaseModels import SearchCriteria
                EmptyCriteria = SearchCriteria()
                SearchResult = self.BookService.SearchBooks(EmptyCriteria)
                Books = SearchResult.Books if hasattr(SearchResult, 'Books') else SearchResult
            else:
                # Fallback - use database directly
                BookRows = self.DatabaseManager.GetBooks()
                Books = self.ConvertRowsToBooks(BookRows)
            
            # FIXED: Convert Book objects to dictionaries for new BookGrid
            BookDicts = self.ConvertBooksToDict(Books)
            self.BookGrid.DisplayBooks(BookDicts)
            
            BookCount = len(Books)
            self.StatusBar.showMessage(f"Showing all books: {BookCount} books found")
            self.Logger.info(f"Displayed {BookCount} books")
            
        except Exception as Error:
            self.Logger.error(f"Failed to display books: {Error}")
            self.StatusBar.showMessage("Error loading books")
    
    def ConvertBooksToDict(self, Books):
        """Convert Book objects to dictionaries for new BookGrid interface."""
        BookDicts = []
        for Book in Books:
            if hasattr(Book, '__dict__'):
                # Book is an object - convert to dict
                BookDict = {
                    'Title': getattr(Book, 'Title', getattr(Book, 'title', 'Unknown')),
                    'Author': getattr(Book, 'Author', getattr(Book, 'author', 'Unknown')),
                    'Category': getattr(Book, 'Category', getattr(Book, 'category', 'General')),
                    'Subject': getattr(Book, 'Subject', getattr(Book, 'subject', 'General')),
                    'FilePath': getattr(Book, 'FilePath', getattr(Book, 'filepath', '')),
                    'ThumbnailPath': getattr(Book, 'ThumbnailPath', getattr(Book, 'thumbnailpath', ''))
                }
            elif isinstance(Book, dict):
                # Already a dict
                BookDict = Book
            else:
                # Unknown format - create basic dict
                BookDict = {'Title': str(Book), 'Author': 'Unknown', 'Category': 'General'}
            
            BookDicts.append(BookDict)
        
        return BookDicts
    
    def ConvertRowsToBooks(self, Rows):
        """Convert database rows to Book dictionaries."""
        Books = []
        for Row in Rows:
            if hasattr(Row, 'keys'):
                # Row is dict-like
                BookDict = dict(Row)
            else:
                # Row is tuple - create basic dict
                BookDict = {
                    'Title': Row[0] if len(Row) > 0 else 'Unknown',
                    'Author': Row[1] if len(Row) > 1 else 'Unknown',
                    'Category': Row[2] if len(Row) > 2 else 'General'
                }
            Books.append(BookDict)
        return Books
    
    def OnSearchRequested(self, SearchTerm):
        """Handle search request - COMPATIBILITY FIX."""
        try:
            self.Logger.info(f"Search requested: '{SearchTerm}'")
            
            # Handle different search term formats
            if hasattr(SearchTerm, 'SearchTerm'):
                # SearchCriteria object
                Term = SearchTerm.SearchTerm
            else:
                # String
                Term = str(SearchTerm)
            
            # Use existing database manager search
            BookRows = self.DatabaseManager.GetBooks(SearchTerm=Term)
            BookDicts = self.ConvertRowsToBooks(BookRows)
            self.BookGrid.DisplayBooks(BookDicts)
            
            BookCount = len(BookDicts)
            self.StatusBar.showMessage(f"Search results for '{Term}': {BookCount} books found")
            
        except Exception as Error:
            self.Logger.error(f"Search failed: {Error}")
            self.StatusBar.showMessage(f"Search error: {Error}")
    
    def OnFiltersChanged(self, Category, Subject=None):
        """Handle filter changes - COMPATIBILITY FIX."""
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
            
            # Use existing database manager filter
            BookRows = self.DatabaseManager.GetBooks(Category=Cat, Subject=Sub)
            BookDicts = self.ConvertRowsToBooks(BookRows)
            self.BookGrid.DisplayBooks(BookDicts)
            
            BookCount = len(BookDicts)
            if Cat and Sub:
                self.StatusBar.showMessage(f"Showing books: {Cat} → {Sub}")
            elif Cat:
                self.StatusBar.showMessage(f"Showing books: {Cat}")
            else:
                self.StatusBar.showMessage(f"Showing all books: {BookCount} books found")
                
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
            
            # FIXED: Use correct method name
            if self.DatabaseManager and hasattr(self.DatabaseManager, 'Close'):
                self.DatabaseManager.Close()
                self.Logger.info("Database connection closed")
            
            event.accept()
            self.Logger.info("🏔️ Anderson's Library - Professional Edition Closed 🏔️")
            
        except Exception as Error:
            self.Logger.error(f"Error during shutdown: {Error}")
            event.accept()


def RunApplication():
    """Run the Anderson's Library application."""
    App = QApplication(sys.argv)
    App.setApplicationName("Anderson's Library - Professional Edition")
    App.setApplicationVersion("2.0")
    App.setOrganizationName("Project Himalaya")
    App.setOrganizationDomain("BowersWorld.com")
    
    try:
        Window = MainWindow()
        Window.show()
        
        Logger = logging.getLogger("MainWindow")
        Logger.info("🏔️ Anderson's Library - Professional Edition Started 🏔️")
        
        return App.exec()
        
    except Exception as Error:
        Logger = logging.getLogger("MainWindow")
        Logger.critical(f"Failed to start application: {Error}")
        QMessageBox.critical(None, "Critical Error", 
                           f"Failed to start Anderson's Library:\n{Error}")
        return 1


if __name__ == "__main__":
    sys.exit(RunApplication())