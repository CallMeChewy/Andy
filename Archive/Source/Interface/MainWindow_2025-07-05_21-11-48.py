# File: MainWindow.py
# Path: Source/Interface/MainWindow.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  08:30PM
"""
Description: Enhanced Main Window with Theme Support and Proper Shutdown
Main application window with improved visual design and error handling.
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
from Source.Utils.ColorTheme import ColorTheme


class MainWindow(QMainWindow):
    """
    Enhanced main application window with professional theming and proper resource management.
    """
    
    def __init__(self):
        super().__init__()
        self.Logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize core components
        self.DatabaseManager = None
        self.BookService = None
        self.FilterPanel = None
        self.BookGrid = None
        self.ColorTheme = ColorTheme()
        
        # Initialize UI
        self.InitializeComponents()
        self.SetupUI()
        self.ConnectSignals()
        self.ApplyTheme()
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
        """
        Create the left panel containing filters and search.
        
        Returns:
            QFrame containing the left panel
        """
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
        """
        Create the right panel containing the book grid.
        
        Returns:
            QFrame containing the right panel
        """
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
        
        # Add permanent widgets to status bar if needed
        # Example: self.StatusBar.addPermanentWidget(some_widget)
    
    def ConnectSignals(self):
        """Connect signals between components."""
        try:
            # Connect filter panel signals
            self.FilterPanel.SearchRequested.connect(self.OnSearchRequested)
            self.FilterPanel.FiltersChanged.connect(self.OnFiltersChanged)
            
            # Connect book grid signals
            self.BookGrid.BookClicked.connect(self.OnBookClicked)
            
            self.Logger.info("Signals connected successfully")
            
        except Exception as Error:
            self.Logger.error(f"Failed to connect signals: {Error}")
    
    def ApplyTheme(self):
        """Apply the professional color theme to the window."""
        try:
            StyleSheet = self.ColorTheme.GetStyleSheet("Professional")
            self.setStyleSheet(StyleSheet)
            self.Logger.info("Theme applied successfully")
        except Exception as Error:
            self.Logger.error(f"Failed to apply theme: {Error}")
    
    def LoadInitialData(self):
        """Load initial data and display all books."""
        try:
            # Small delay to ensure UI is fully rendered
            QTimer.singleShot(100, self.DisplayAllBooks)
        except Exception as Error:
            self.Logger.error(f"Failed to load initial data: {Error}")
    
    def DisplayAllBooks(self):
        """Display all books in the grid."""
        try:
            Books = self.BookService.GetBooks()
            self.BookGrid.DisplayBooks(Books)
            
            BookCount = len(Books)
            self.StatusBar.showMessage(f"Showing all books: {BookCount} books found")
            self.Logger.info(f"Displayed {BookCount} books")
            
        except Exception as Error:
            self.Logger.error(f"Failed to display books: {Error}")
            self.StatusBar.showMessage("Error loading books")
    
    def OnSearchRequested(self, SearchTerm: str):
        """
        Handle search request.
        
        Args:
            SearchTerm: The search term entered by user
        """
        try:
            self.Logger.info(f"Search requested: '{SearchTerm}'")
            
            Books = self.BookService.SearchBooks(SearchTerm)
            self.BookGrid.DisplayBooks(Books)
            
            BookCount = len(Books)
            self.StatusBar.showMessage(f"Search results for '{SearchTerm}': {BookCount} books found")
            
        except Exception as Error:
            self.Logger.error(f"Search failed: {Error}")
            self.StatusBar.showMessage(f"Search error: {Error}")
    
    def OnFiltersChanged(self, Category: str, Subject: str):
        """
        Handle filter changes.
        
        Args:
            Category: Selected category
            Subject: Selected subject
        """
        try:
            self.Logger.info(f"Filters changed: Category='{Category}', Subject='{Subject}'")
            
            Books = self.BookService.GetBooksByFilters(Category, Subject)
            self.BookGrid.DisplayBooks(Books)
            
            BookCount = len(Books)
            if Category == "All Categories" and Subject == "All Subjects":
                self.StatusBar.showMessage(f"Showing all books: {BookCount} books found")
            else:
                FilterText = f"{Category}"
                if Subject and Subject != "All Subjects":
                    FilterText += f" → {Subject}"
                self.StatusBar.showMessage(f"Showing books: {FilterText}")
                
        except Exception as Error:
            self.Logger.error(f"Filter change failed: {Error}")
            self.StatusBar.showMessage(f"Filter error: {Error}")
    
    def OnBookClicked(self, BookTitle: str):
        """
        Handle book click event.
        
        Args:
            BookTitle: Title of the clicked book
        """
        try:
            self.Logger.info(f"Book clicked: '{BookTitle}'")
            
            # Update last opened timestamp
            self.DatabaseManager.UpdateLastOpened(BookTitle)
            
            # Emit book service event
            self.BookService.OpenBook(BookTitle)
            
            # Update status bar
            self.StatusBar.showMessage(f"Book opened: '{BookTitle}'")
            
            # Log the event
            self.Logger.info(f"Book opened: '{BookTitle}'")
            
        except Exception as Error:
            self.Logger.error(f"Failed to open book '{BookTitle}': {Error}")
            self.StatusBar.showMessage(f"Error opening book: {Error}")
    
    def closeEvent(self, event):
        """
        Handle application close event with proper cleanup.
        
        Args:
            event: Close event
        """
        try:
            self.Logger.info("Application shutdown initiated")
            
            # Close database connection properly
            if self.DatabaseManager:
                self.DatabaseManager.Close()
                self.Logger.info("Database connection closed")
            
            # Accept the close event
            event.accept()
            self.Logger.info("🏔️ Anderson's Library - Professional Edition Closed 🏔️")
            
        except Exception as Error:
            self.Logger.error(f"Error during shutdown: {Error}")
            # Accept the event anyway to ensure application closes
            event.accept()


def RunApplication():
    """
    Run the Anderson's Library application.
    
    Returns:
        Application exit code
    """
    # Create application
    App = QApplication(sys.argv)
    App.setApplicationName("Anderson's Library - Professional Edition")
    App.setApplicationVersion("2.0")
    App.setOrganizationName("Project Himalaya")
    App.setOrganizationDomain("BowersWorld.com")
    
    # Set application icon if available
    try:
        if hasattr(QIcon, 'fromTheme'):
            App.setWindowIcon(QIcon.fromTheme('application-library'))
    except:
        pass  # Icon not critical
    
    # Create and show main window
    try:
        Window = MainWindow()
        Window.show()
        
        # Log successful startup
        Logger = logging.getLogger("MainWindow")
        Logger.info("🏔️ Anderson's Library - Professional Edition Started 🏔️")
        
        # Run application
        return App.exec()
        
    except Exception as Error:
        # Log critical error
        Logger = logging.getLogger("MainWindow")
        Logger.critical(f"Failed to start application: {Error}")
        
        # Show error message
        QMessageBox.critical(None, "Critical Error", 
                           f"Failed to start Anderson's Library:\n{Error}")
        return 1


if __name__ == "__main__":
    sys.exit(RunApplication())