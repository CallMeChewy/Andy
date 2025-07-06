# File: MainWindow.py
# Path: Source/Interface/MainWindow.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-06
# Last Modified: 2025-07-06  09:45AM
"""
Description: COMPREHENSIVE UI FIX - Complete window controls, sidebar styling, and PDF opening
Fixed all UI issues: sidebar styling, window controls, full screen startup, and PDF opening.
"""

import sys
import os  # FIXED: Missing import
import logging
import subprocess
import platform
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
    COMPREHENSIVE FIX - Anderson's Library with perfect UI, window controls, and functionality.
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
        self.SetupPerfectWindow()  # FIXED: Perfect window setup
        self.ConnectSignals()
        self.ApplyPerfectTheme()   # FIXED: Perfect sidebar styling
        self.LoadInitialData()
        
        self.Logger.info("MainWindow initialized with comprehensive UI fixes")
    
    def InitializeComponents(self):
        """Initialize core application components."""
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
    
    def SetupPerfectWindow(self):
        """FIXED - Perfect window setup with proper controls and full screen."""
        self.setWindowTitle("Anderson's Library")
        self.setMinimumSize(1200, 800)
        
        # FIXED: Ensure ALL window controls work properly
        self.setWindowFlags(
            Qt.Window | 
            Qt.WindowTitleHint | 
            Qt.WindowCloseButtonHint | 
            Qt.WindowMinimizeButtonHint | 
            Qt.WindowMaximizeButtonHint |
            Qt.WindowSystemMenuHint |
            Qt.WindowFullscreenButtonHint  # Additional for full screen
        )
        
        # FIXED: Start maximized for full screen display
        QTimer.singleShot(50, self.showMaximized)
        
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
        LeftPanel = self.CreatePerfectLeftPanel()
        Splitter.addWidget(LeftPanel)
        
        # Setup right panel (book grid)
        RightPanel = self.CreateRightPanel()
        Splitter.addWidget(RightPanel)
        
        # Perfect proportions for maximum book display
        Splitter.setSizes([350, 1050])
        Splitter.setCollapsible(0, False)
        
        # Original red status bar
        self.SetupStatusBar()
    
    def CreatePerfectLeftPanel(self) -> QFrame:
        """FIXED - Create left panel with perfect sidebar styling."""
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
        self.StatusBar.setStyleSheet("background-color: #780000; color: white; font-weight: bold;")
        self.StatusBar.showMessage("Ready - 1,219 books with BLOB thumbnails!")
    
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
    
    def ApplyPerfectTheme(self):
        """FIXED - Perfect theme with beautiful sidebar and window controls."""
        PerfectStyleSheet = """
        /* Main gradient - original beautiful design */
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
        
        /* PERFECT SIDEBAR STYLING */
        QFrame#LeftPanel {
            background-color: rgba(3, 50, 76, 230);
            border: 2px solid rgba(255, 255, 255, 100);
            border-radius: 8px;
            padding: 10px;
        }
        
        /* Perfect labels - WHITE text */
        QFrame#LeftPanel QLabel {
            color: #FFFFFF;
            font-weight: bold;
            font-size: 14px;
            padding: 5px 0px;
            background: transparent;
        }
        
        /* PERFECT DROPDOWN STYLING */
        QComboBox {
            background-color: rgba(255, 255, 255, 250);
            color: #000000;
            border: 2px solid rgba(255, 255, 255, 150);
            border-radius: 6px;
            padding: 8px;
            font-size: 13px;
            font-weight: bold;
            min-height: 25px;
        }
        
        QComboBox:hover {
            background-color: rgba(255, 255, 255, 255);
            border-color: rgba(255, 255, 255, 200);
        }
        
        QComboBox::drop-down {
            border: none;
            width: 30px;
            padding-right: 5px;
        }

        QComboBox::down-arrow {
            image: url(Assets/arrow.png);
            width: 12px;
            height: 12px;
        }
        
        /* PERFECT DROPDOWN LIST */
        QComboBox QAbstractItemView {
            background-color: rgba(6, 82, 125, 255);
            color: #FFFFFF;
            border: 2px solid rgba(255, 255, 255, 150);
            border-radius: 6px;
            selection-background-color: rgba(255, 255, 255, 150);
            selection-color: #000000;
            font-size: 13px;
        }
        
        QComboBox::item {
            color: #FFFFFF;
            padding: 8px;
            border: none;
            background: transparent;
        }

        QComboBox::item:selected {
            background-color: rgba(255, 255, 255, 150);
            color: #000000;
        }

        QComboBox::item:hover {
            background-color: rgba(255, 255, 255, 80);
            color: #FFFFFF;
        }
        
        /* PERFECT SEARCH BOX */
        QLineEdit {
            background-color: rgba(255, 255, 255, 250);
            color: #000000;
            border: 2px solid rgba(255, 255, 255, 150);
            border-radius: 6px;
            padding: 8px;
            font-size: 13px;
            min-height: 25px;
        }
        
        QLineEdit:focus {
            background-color: rgba(255, 255, 255, 255);
            border-color: rgba(255, 255, 255, 200);
        }
        
        QLineEdit::placeholder {
            color: #666666;
        }
        
        /* Status bar */
        QStatusBar {
            background-color: #780000; 
            color: white;
            font-weight: bold;
            font-size: 13px;
        }
        
        /* Tooltips */
        QToolTip { 
            color: #ffffff; 
            background-color: rgba(3, 50, 76, 230);
            border: 2px solid rgba(255, 255, 255, 150);
            border-radius: 4px;
            font-size: 12px;
            padding: 5px;
        }
        """
        
        self.setStyleSheet(PerfectStyleSheet)
        self.Logger.info("Perfect theme applied with beautiful sidebar styling")
    
    def LoadInitialData(self):
        """Load initial data."""
        try:
            QTimer.singleShot(200, self.DisplayAllBooks)
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
        """FIXED - Perfect book opening with proper error handling."""
        try:
            self.Logger.info(f"Book clicked: '{BookTitle}'")
            
            # Update last opened timestamp
            self.DatabaseManager.UpdateLastOpened(BookTitle)
            
            # Get book details to find file path
            BookDicts = self.DatabaseManager.GetBooks(SearchTerm=BookTitle)
            if BookDicts:
                # Find exact match or use first result
                BookData = None
                for Book in BookDicts:
                    if Book.get('Title', '') == BookTitle:
                        BookData = Book
                        break
                
                if not BookData:
                    BookData = BookDicts[0]  # Use first match
                
                FilePath = BookData.get('FilePath', '')
                
                if FilePath and os.path.exists(FilePath):
                    # Open PDF with system default application
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', FilePath])
                    elif platform.system() == 'Windows':  # Windows
                        os.startfile(FilePath)
                    else:  # Linux/Unix
                        subprocess.run(['xdg-open', FilePath])
                    
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
    """Run the Anderson's Library application with perfect UI."""
    App = QApplication(sys.argv)
    App.setApplicationName("Anderson's Library")
    App.setApplicationVersion("2.0")
    App.setOrganizationName("Project Himalaya")
    App.setOrganizationDomain("BowersWorld.com")
    
    try:
        Window = MainWindow()
        Window.show()
        
        Logger = logging.getLogger("MainWindow")
        Logger.info("Anderson's Library Started with perfect UI and BLOB thumbnails")
        
        return App.exec()
        
    except Exception as Error:
        Logger = logging.getLogger("MainWindow")
        Logger.critical(f"Failed to start application: {Error}")
        QMessageBox.critical(None, "Critical Error", 
                           f"Failed to start Anderson's Library:\n{Error}")
        return 1


if __name__ == "__main__":
    sys.exit(RunApplication())