# File: MainWindow.py
# Path: Source/Interface/MainWindow.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  09:15PM
"""
Description: FINAL UI/UX FIXES - Readable Text + Working Category/Subject Filters
Fixed contrast issues and category/subject filtering functionality.
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
    FINAL FIX - Main window with readable text and working filters.
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
        self.ApplyFixedTheme()  # FIXED: Better contrast
        self.SetInitialState()  # FIXED: No books on startup
        
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
        """Setup the main user interface for maximum image display."""
        self.setWindowTitle("🏔️ Anderson's Library - Professional Edition")
        self.setMinimumSize(1200, 800)
        
        # FIXED: Start maximized for maximum image display
        self.showMaximized()
        
        # Create central widget
        CentralWidget = QWidget()
        self.setCentralWidget(CentralWidget)
        
        # Create main layout with splitter for resizable panels
        MainLayout = QHBoxLayout(CentralWidget)
        MainLayout.setContentsMargins(5, 5, 5, 5)  # Smaller margins for more space
        
        # Create splitter for resizable panels
        Splitter = QSplitter(Qt.Horizontal)
        MainLayout.addWidget(Splitter)
        
        # Setup left panel (filters) - narrower for more book space
        LeftPanel = self.CreateLeftPanel()
        Splitter.addWidget(LeftPanel)
        
        # Setup right panel (book grid)
        RightPanel = self.CreateRightPanel()
        Splitter.addWidget(RightPanel)
        
        # FIXED: Optimize for maximum book display - smaller left panel
        Splitter.setSizes([280, 1400])  # Left: 280px, Right: most space
        Splitter.setCollapsible(0, False)  # Don't allow left panel to collapse
        
        # Setup status bar
        self.SetupStatusBar()
    
    def CreateLeftPanel(self) -> QFrame:
        """Create the left panel with proper contrast."""
        LeftPanel = QFrame()
        LeftPanel.setObjectName("LeftPanel")
        LeftPanel.setFrameStyle(QFrame.StyledPanel)
        LeftPanel.setFixedWidth(280)  # FIXED: Narrower for more book space
        
        # Left panel layout
        LeftLayout = QVBoxLayout(LeftPanel)
        LeftLayout.setContentsMargins(12, 12, 12, 12)
        LeftLayout.setSpacing(8)
        
        # Add filter panel
        LeftLayout.addWidget(self.FilterPanel)
        
        # Add stretch to push everything to top
        LeftLayout.addStretch()
        
        return LeftPanel
    
    def CreateRightPanel(self) -> QFrame:
        """Create the right panel for maximum book display."""
        RightPanel = QFrame()
        RightPanel.setFrameStyle(QFrame.StyledPanel)
        
        # Right panel layout with minimal margins
        RightLayout = QVBoxLayout(RightPanel)
        RightLayout.setContentsMargins(2, 2, 2, 2)  # Minimal margins
        
        # Add book grid
        RightLayout.addWidget(self.BookGrid)
        
        return RightPanel
    
    def SetupStatusBar(self):
        """Setup the status bar."""
        self.StatusBar = QStatusBar()
        self.setStatusBar(self.StatusBar)
        self.StatusBar.showMessage("Ready - Select a category to browse books")
    
    def ConnectSignals(self):
        """FIXED: Connect signals using ALL possible signal names."""
        try:
            # Try multiple signal names for maximum compatibility
            SignalConnections = 0
            
            # Search signals
            for SearchSignal in ['SearchRequested', 'searchRequested', 'search_requested']:
                if hasattr(self.FilterPanel, SearchSignal):
                    getattr(self.FilterPanel, SearchSignal).connect(self.OnSearchRequested)
                    SignalConnections += 1
                    break
            
            # Filter signals  
            for FilterSignal in ['FilterChanged', 'FiltersChanged', 'filterChanged', 'filter_changed']:
                if hasattr(self.FilterPanel, FilterSignal):
                    getattr(self.FilterPanel, FilterSignal).connect(self.OnFiltersChanged)
                    SignalConnections += 1
                    break
            
            # Book click signals
            for BookSignal in ['BookClicked', 'bookClicked', 'book_clicked']:
                if hasattr(self.BookGrid, BookSignal):
                    getattr(self.BookGrid, BookSignal).connect(self.OnBookClicked)
                    SignalConnections += 1
                    break
            
            self.Logger.info(f"Connected {SignalConnections} signals successfully")
            
        except Exception as Error:
            self.Logger.error(f"Failed to connect signals: {Error}")
    
    def ApplyFixedTheme(self):
        """FIXED: Apply theme with MAXIMUM contrast for readability."""
        StyleSheet = """
        /* Main Window - Light background */
        QMainWindow {
            background-color: #f8f9fa;
            color: #2c3e50;
        }
        
        /* Left Panel - Dark blue with BRIGHT WHITE text */
        QFrame#LeftPanel {
            background-color: #2c3e50;
            border: 2px solid #34495e;
            border-radius: 8px;
            padding: 8px;
        }
        
        /* CRITICAL FIX: Force WHITE text on ALL panel elements */
        QFrame#LeftPanel * {
            color: #ffffff !important;
        }
        
        /* Panel Labels - BRIGHT WHITE text */
        QFrame#LeftPanel QLabel {
            color: #ffffff !important;
            font-weight: bold;
            font-size: 14px !important;
            padding: 6px 0px;
            background: transparent;
        }
        
        /* ComboBox - White background, dark text, larger */
        QComboBox {
            background-color: #ffffff !important;
            border: 2px solid #bdc3c7;
            border-radius: 6px;
            padding: 10px;
            color: #2c3e50 !important;
            font-size: 13px !important;
            min-height: 28px;
            font-weight: normal;
        }
        
        QComboBox:focus {
            border-color: #3498db;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 25px;
        }
        
        /* LineEdit (Search) - White background, dark text, larger */
        QLineEdit {
            background-color: #ffffff !important;
            border: 2px solid #bdc3c7;
            border-radius: 6px;
            padding: 10px;
            color: #2c3e50 !important;
            font-size: 13px !important;
            min-height: 28px;
        }
        
        QLineEdit:focus {
            border-color: #3498db;
        }
        
        QLineEdit::placeholder {
            color: #7f8c8d !important;
        }
        
        /* Status Bar - Light background, larger text */
        QStatusBar {
            background-color: #ecf0f1;
            border-top: 1px solid #bdc3c7;
            color: #2c3e50;
            font-size: 13px;
            padding: 8px;
            font-weight: bold;
        }
        
        /* Right Panel - Clean white */
        QFrame {
            background-color: #ffffff;
            border: 1px solid #e1e8ed;
        }
        """
        
        self.setStyleSheet(StyleSheet)
        self.Logger.info("FIXED high contrast theme applied")
    
    def SetInitialState(self):
        """FIXED: Show empty state on startup, not all books."""
        try:
            # Show empty message instead of all books
            self.BookGrid.DisplayBooks([])  # Empty list
            self.StatusBar.showMessage("Ready - Select a category to browse books")
            self.Logger.info("Application ready - empty state displayed")
        except Exception as Error:
            self.Logger.error(f"Failed to set initial state: {Error}")
    
    def OnSearchRequested(self, SearchTerm):
        """FIXED: Handle search with better error handling."""
        try:
            # Handle different search term formats
            if hasattr(SearchTerm, 'SearchTerm'):
                Term = SearchTerm.SearchTerm
            else:
                Term = str(SearchTerm).strip()
            
            self.Logger.info(f"Search requested: '{Term}'")
            
            if not Term:
                # Empty search - show empty state
                self.BookGrid.DisplayBooks([])
                self.StatusBar.showMessage("Ready - Enter search term or select category")
                return
            
            # Use database manager search directly for reliability
            BookRows = self.DatabaseManager.GetBooks(SearchTerm=Term)
            BookDicts = self.ConvertRowsToBooks(BookRows)
            self.BookGrid.DisplayBooks(BookDicts)
            
            BookCount = len(BookDicts)
            self.StatusBar.showMessage(f"Search results for '{Term}': {BookCount} books found")
            
        except Exception as Error:
            self.Logger.error(f"Search failed: {Error}")
            self.StatusBar.showMessage(f"Search error: {Error}")
            self.BookGrid.DisplayBooks([])  # Show empty on error
    
    def OnFiltersChanged(self, Category, Subject=None):
        """FIXED: Handle category/subject filtering with debugging."""
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
                # Show empty state for "All Categories"
                self.BookGrid.DisplayBooks([])
                self.StatusBar.showMessage("Select a specific category to view books")
                return
            
            # Use database manager filter directly
            BookRows = self.DatabaseManager.GetBooks(Category=Cat, Subject=Sub)
            BookDicts = self.ConvertRowsToBooks(BookRows)
            
            self.Logger.info(f"Database returned {len(BookRows)} books for Category='{Cat}', Subject='{Sub}'")
            
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
            self.BookGrid.DisplayBooks([])  # Show empty on error
    
    def ConvertRowsToBooks(self, Rows):
        """Convert database rows to Book dictionaries."""
        Books = []
        for Row in Rows:
            try:
                if hasattr(Row, 'keys'):
                    # Row is dict-like (sqlite3.Row)
                    BookDict = dict(Row)
                else:
                    # Row is tuple - create basic dict
                    BookDict = {
                        'Title': Row[0] if len(Row) > 0 else 'Unknown',
                        'Author': Row[1] if len(Row) > 1 else 'Unknown',
                        'Category': Row[2] if len(Row) > 2 else 'General',
                        'Subject': Row[3] if len(Row) > 3 else 'General'
                    }
                Books.append(BookDict)
            except Exception as Error:
                self.Logger.warning(f"Failed to convert row to book: {Error}")
                continue
        
        return Books
    
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