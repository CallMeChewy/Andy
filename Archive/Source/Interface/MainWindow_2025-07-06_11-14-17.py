# File: MainWindow.py
# Path: Source/Interface/MainWindow.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-06
# Last Modified: 2025-07-06  09:35AM
"""
Description: FIXED - Full Screen + Dropdown Styling + PDF Opening
Fixed window controls, dropdown text styling, and PDF opening functionality.
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
    FIXED - Anderson's Library with proper window controls and dropdown styling.
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
        self.ApplyFixedTheme()  # FIXED: Better dropdown styling
        self.LoadInitialData()
        
        self.Logger.info("MainWindow initialized with fixed styling and window controls")
    
    def InitializeComponents(self):
        """Initialize core application components with new database path."""
        try:
            # Use the updated database path with BLOB thumbnails
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
        """FIXED - Setup UI with proper window controls and full screen."""
        self.setWindowTitle("Anderson's Library")
        self.setMinimumSize(1200, 800)
        
        # FIXED: Ensure window has proper controls and starts maximized
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | 
                           Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint |
                           Qt.WindowSystemMenuHint)
        
        # Start maximized for full screen display
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
    
    def ApplyFixedTheme(self):
        """FIXED - Apply theme with correct dropdown styling."""
        # Original beautiful blue gradient + FIXED dropdown styling
        FixedStyleSheet = """
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

        /* FIXED: Dropdown styling - black text only on selected display, white in list */
        QComboBox {
            color: #000000;  /* Black text for selected display */
            background-color: rgba(255, 255, 255, 240);
            padding: 8px;
            border: 2px solid rgba(255, 255, 255, 100);
            border-radius: 4px;
            font-size: 13px;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 25px;
        }

        QComboBox::down-arrow {
            image: url(Assets/arrow.png);
        }

        /* FIXED: Dropdown list styling - WHITE text on blue background */
        QComboBox QAbstractItemView {
            color: #ffffff;  /* WHITE text in dropdown list */
            background-color: rgba(6, 82, 125, 255);  /* Blue background matching gradient */
            border: 2px solid rgba(255, 255, 255, 150);
            border-radius: 4px;
            selection-background-color: rgba(255, 255, 255, 100);
            selection-color: #000000;  /* Black text when selected */
        }
        
        QComboBox::item {
            color: #ffffff;  /* WHITE text for each item */
            padding: 8px;
            border: none;
        }

        QComboBox::item:hover {
            background-color: rgba(255, 255, 255, 50);
            color: #ffffff;
        }

        QComboBox::item:selected {
            background-color: rgba(255, 255, 255, 150);
            color: #000000;  /* Black text when selected */
        }
        
        /* Search box styling */
        QLineEdit {
            color: #000000;  /* Black text in search box */
            background-color: rgba(255, 255, 255, 240);
            padding: 8px;
            border: 2px solid rgba(255, 255, 255, 100);
            border-radius: 4px;
            font-size: 13px;
        }
        
        QLineEdit:focus {
            border-color: rgba(255, 255, 255, 200);
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
        
        self.setStyleSheet(FixedStyleSheet)
        self.Logger.info("Fixed theme applied with correct dropdown styling")
    
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
        """FIXED - Handle book click with proper PDF opening."""
        try:
            self.Logger.info(f"Book clicked: '{BookTitle}'")
            
            # Update last opened timestamp
            self.DatabaseManager.UpdateLastOpened(BookTitle)
            
            # FIXED: Open PDF using system default application
            import subprocess
            import platform
            
            # Get book details to find file path
            BookDicts = self.DatabaseManager.GetBooks(SearchTerm=BookTitle)
            if BookDicts:
                BookData = BookDicts[0]
                FilePath = BookData.get('FilePath', '')
                
                if FilePath and os.path.exists(FilePath):
                    # Open PDF with system default application
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.call(['open', FilePath])
                    elif platform.system() == 'Windows':  # Windows
                        os.startfile(FilePath)
                    else:  # Linux/Unix
                        subprocess.call(['xdg-open', FilePath])
                    
                    self.StatusBar.showMessage(f"Opened: '{BookTitle}'")
                    self.Logger.info(f"Successfully opened PDF: {FilePath}")
                else:
                    self.StatusBar.showMessage(f"PDF file not found for: '{BookTitle}'")
                    self.Logger.warning(f"PDF file not found: {FilePath}")
            else:
                self.StatusBar.showMessage(f"Book not found: '{BookTitle}'")
                self.Logger.warning(f"Book not found in database: {BookTitle}")
            
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
    """Run the Anderson's Library application with fixed window controls."""
    App = QApplication(sys.argv)
    App.setApplicationName("Anderson's Library")
    App.setApplicationVersion("2.0")
    App.setOrganizationName("Project Himalaya")
    App.setOrganizationDomain("BowersWorld.com")
    
    try:
        Window = MainWindow()
        Window.show()
        
        Logger = logging.getLogger("MainWindow")
        Logger.info("Anderson's Library Started with fixed controls and BLOB thumbnails")
        
        return App.exec()
        
    except Exception as Error:
        Logger = logging.getLogger("MainWindow")
        Logger.critical(f"Failed to start application: {Error}")
        QMessageBox.critical(None, "Critical Error", 
                           f"Failed to start Anderson's Library:\n{Error}")
        return 1


if __name__ == "__main__":
    sys.exit(RunApplication())