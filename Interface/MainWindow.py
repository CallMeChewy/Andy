# File: MainWindow.py
# Path: Source/Interface/MainWindow.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  15:45PM
"""
Description: Anderson's Library Main Window
Primary application window that orchestrates all components and maintains application state.
Integrates FilterPanel, BookGrid, and CustomWindow framework for cohesive user experience.

Purpose: Serves as the main application controller, coordinating between UI components
and business logic while maintaining clean separation of concerns.
"""

import sys
import os
import logging
from typing import Optional, List
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QMessageBox
from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont

# Import custom window framework
from .CustomWindow import CustomWindow

# Import core business logic
from ..Core.DatabaseManager import DatabaseManager
from ..Core.BookService import BookService

# Import UI components  
from .FilterPanel import FilterPanel
from .BookGrid import BookGrid

# Import data models
from ..Data.DatabaseModels import Book


class MainWindow(QMainWindow):
    """
    Main application window orchestrating all components.
    Provides the primary user interface for Anderson's Library.
    """
    
    def __init__(self, DatabasePath: str = "Assets/my_library.db", *args, **kwargs):
        """
        Initialize main window with database connection.
        
        Args:
            DatabasePath: Path to SQLite database file
        """
        super().__init__(*args, **kwargs)
        
        # Initialize logging
        self.Logger = logging.getLogger(__name__)
        
        # Core components
        self.DatabaseManager: Optional[DatabaseManager] = None
        self.BookService: Optional[BookService] = None
        
        # UI components
        self.FilterPanel: Optional[FilterPanel] = None
        self.BookGrid: Optional[BookGrid] = None
        self.CustomWindowWrapper: Optional[CustomWindow] = None
        
        # Layout components
        self.MainWidget: Optional[QWidget] = None
        self.MainLayout: Optional[QHBoxLayout] = None
        
        # Application state
        self.DatabasePath = DatabasePath
        self.CurrentBooks: List[Book] = []
        
        # Initialize application
        self._InitializeDatabase()
        self._InitializeServices()
        self._SetupUserInterface()
        self._ConnectComponents()
        self._ApplyStyles()
        
        self.Logger.info("MainWindow initialized successfully")
    
    def _InitializeDatabase(self) -> None:
        """Initialize database manager and validate connection"""
        try:
            self.DatabaseManager = DatabaseManager(self.DatabasePath)
            
            # Validate database integrity
            ValidationIssues = self.DatabaseManager.ValidateDatabase()
            if ValidationIssues:
                self.Logger.warning(f"Database validation issues: {ValidationIssues}")
                
            self.Logger.info("Database connection established")
            
        except Exception as Error:
            self.Logger.error(f"Database initialization failed: {Error}")
            QMessageBox.critical(
                self,
                "Database Error",
                f"Failed to connect to database:\n\n{Error}\n\nPlease check that the database file exists and is accessible."
            )
            sys.exit(1)
    
    def _InitializeServices(self) -> None:
        """Initialize business logic services"""
        try:
            # Create book service with database dependency
            self.BookService = BookService(self.DatabaseManager)
            
            # Set up event handlers for service callbacks
            self.BookService.SetEventHandlers(
                OnBooksChanged=self._OnBooksChanged,
                OnFilterChanged=self._OnFilterChanged,
                OnBookOpened=self._OnBookOpened
            )
            
            self.Logger.info("Business services initialized")
            
        except Exception as Error:
            self.Logger.error(f"Service initialization failed: {Error}")
            raise
    
    def _SetupUserInterface(self) -> None:
        """Create and configure user interface components"""
        # Create main widget and layout
        self.MainWidget = QWidget()
        self.setCentralWidget(self.MainWidget)
        
        self.MainLayout = QHBoxLayout(self.MainWidget)
        self.MainLayout.setContentsMargins(0, 0, 0, 0)
        
        # Create filter panel (left sidebar)
        self.FilterPanel = FilterPanel(self.BookService)
        self.FilterPanel.setFixedWidth(300)  # Match original design
        self.MainLayout.addWidget(self.FilterPanel)
        
        # Create book grid (main display area)
        self.BookGrid = BookGrid(self.BookService)
        self.MainLayout.addWidget(self.BookGrid)
        
        # Enable mouse tracking for the main window
        self.setMouseTracking(True)
        
        self.Logger.info("User interface components created")
    
    def _ConnectComponents(self) -> None:
        """Connect UI components with event handlers"""
        # Connect filter panel events
        if self.FilterPanel:
            self.FilterPanel.SetEventHandlers(
                OnBookSelected=self._OnBookSelectedFromFilter
            )
        
        # Connect book grid events  
        if self.BookGrid:
            self.BookGrid.SetEventHandlers(
                OnBookOpened=self._OnBookOpenedFromGrid
            )
        
        self.Logger.info("Component event handlers connected")
    
    def _ApplyStyles(self) -> None:
        """Apply application-wide styling to match original design"""
        # Set window properties
        self.setWindowTitle("Anderson's Library")
        self.setMouseTracking(True)
        
        # Apply the original blue gradient background style
        StyleSheet = """
            * {
                background-color: qlineargradient(spread:repeat, x1:1, y1:0, x2:1, y2:1, 
                    stop:0.00480769 rgba(3, 50, 76, 255), 
                    stop:0.293269 rgba(6, 82, 125, 255), 
                    stop:0.514423 rgba(8, 117, 178, 255), 
                    stop:0.745192 rgba(7, 108, 164, 255), 
                    stop:1 rgba(3, 51, 77, 255));
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
        """
        
        self.setStyleSheet(StyleSheet)
        self.Logger.info("Application styling applied")
    
    # =================================================================
    # EVENT HANDLERS FROM SERVICES
    # =================================================================
    
    def _OnBooksChanged(self, Books: List[Book]) -> None:
        """
        Handle book list changes from BookService.
        
        Args:
            Books: Updated list of books
        """
        self.CurrentBooks = Books
        
        # Update book grid display
        if self.BookGrid:
            self.BookGrid.UpdateBooks(Books)
        
        self.Logger.info(f"Book display updated: {len(Books)} books")
    
    def _OnFilterChanged(self) -> None:
        """Handle filter state changes from BookService"""
        # Get current filter state for logging
        if self.BookService:
            FilterState = self.BookService.GetFilterState()
            self.Logger.info(f"Filters changed: {FilterState}")
    
    def _OnBookOpened(self, BookData: Book) -> None:
        """
        Handle book opened events from BookService.
        
        Args:
            BookData: Book that was opened
        """
        self.Logger.info(f"Book opened: {BookData.Title}")
    
    # =================================================================
    # EVENT HANDLERS FROM UI COMPONENTS
    # =================================================================
    
    def _OnBookSelectedFromFilter(self, BookTitle: str) -> None:
        """
        Handle book selection from filter panel.
        
        Args:
            BookTitle: Title of selected book
        """
        self.OpenBook(BookTitle)
    
    def _OnBookOpenedFromGrid(self, BookTitle: str) -> None:
        """
        Handle book opened from grid display.
        
        Args:
            BookTitle: Title of opened book
        """
        self.Logger.info(f"Book opened from grid: {BookTitle}")
    
    # =================================================================
    # PUBLIC INTERFACE METHODS
    # =================================================================
    
    def OpenBook(self, BookTitle: str) -> None:
        """
        Open book with confirmation dialog (matching original behavior).
        
        Args:
            BookTitle: Title of book to open
        """
        if not BookTitle or not self.BookService:
            return
        
        try:
            # Get book data
            BookData = self.BookService.GetBookByTitle(BookTitle)
            if not BookData:
                QMessageBox.warning(self, "Book Not Found", f"Could not find book: {BookTitle}")
                return
            
            # Create confirmation dialog (matching original design)
            MessageBox = QMessageBox()
            MessageBox.setWindowTitle("Selected Book")
            MessageBox.setText(f"Would you like to read:\n\n{BookTitle}")
            
            # Try to set book cover as icon
            CoverPath = BookData.GetCoverImagePath()
            if os.path.exists(CoverPath):
                from PySide6.QtGui import QPixmap
                MessageBox.setIconPixmap(QPixmap(CoverPath))
            
            MessageBox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
            MessageBox.setDefaultButton(QMessageBox.Ok)
            
            # Apply styling to match original
            MessageBox.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                }
                QPushButton {
                    min-height: 30px;
                    min-width: 70px;
                    font-size: 16px;
                }
            """)
            
            # Show dialog and handle response
            ReturnValue = MessageBox.exec()
            if ReturnValue == QMessageBox.Ok:
                Success = self.BookService.OpenBook(BookTitle)
                if not Success:
                    QMessageBox.warning(
                        self, 
                        "File Not Found", 
                        f"Could not open PDF file for: {BookTitle}\n\nThe file may have been moved or deleted."
                    )
                    
        except Exception as Error:
            self.Logger.error(f"Error opening book '{BookTitle}': {Error}")
            QMessageBox.critical(self, "Error", f"An error occurred while opening the book:\n\n{Error}")
    
    def RefreshData(self) -> None:
        """Refresh all data from database"""
        try:
            if self.BookService:
                self.BookService.RefreshCache()
            
            if self.FilterPanel:
                self.FilterPanel.RefreshData()
            
            self.Logger.info("Data refreshed successfully")
            
        except Exception as Error:
            self.Logger.error(f"Error refreshing data: {Error}")
            QMessageBox.warning(self, "Refresh Error", f"Could not refresh data:\n\n{Error}")
    
    def GetLibraryStatistics(self) -> dict:
        """
        Get comprehensive library statistics.
        
        Returns:
            Dictionary with library statistics
        """
        if self.BookService:
            return self.BookService.GetLibraryStatistics()
        return {}
    
    def ShowAbout(self) -> None:
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Anderson's Library",
            "Anderson's Library - Digital Book Management System\n\n"
            "Built with Python, PySide6, and the AIDEV-PascalCase-1.8 Standard\n\n"
            "Project Himalaya - BowersWorld.com\n"
            "© 2025 Herb Bowers"
        )
    
    # =================================================================
    # WINDOW MANAGEMENT
    # =================================================================
    
    def WrapWithCustomWindow(self) -> CustomWindow:
        """
        Wrap this window with CustomWindow framework.
        
        Returns:
            CustomWindow wrapper instance
        """
        try:
            self.CustomWindowWrapper = CustomWindow("Anderson's Library", self)
            self.Logger.info("Custom window wrapper applied")
            return self.CustomWindowWrapper
            
        except Exception as Error:
            self.Logger.error(f"Failed to create custom window wrapper: {Error}")
            raise
    
    def resizeEvent(self, Event) -> None:
        """Handle window resize events"""
        super().resizeEvent(Event)
        
        # Trigger book grid layout recalculation
        if self.BookGrid:
            # Use a small delay to avoid excessive updates during resize
            QTimer.singleShot(50, self.BookGrid.RefreshLayout)
    
    def closeEvent(self, Event) -> None:
        """Handle window close events"""
        try:
            # Save any necessary state here
            self.Logger.info("Application closing")
            Event.accept()
            
        except Exception as Error:
            self.Logger.error(f"Error during application close: {Error}")
            Event.accept()  # Close anyway


def CreateAndShowMainWindow(DatabasePath: str = "Assets/my_library.db") -> CustomWindow:
    """
    Factory function to create and display the main application window.
    
    Args:
        DatabasePath: Path to SQLite database file
        
    Returns:
        CustomWindow wrapper for the main window
    """
    try:
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(name)s - %(levelname)s: %(message)s'
        )
        
        # Create main window
        MainWindowInstance = MainWindow(DatabasePath)
        
        # Wrap with custom window framework
        CustomWindowInstance = MainWindowInstance.WrapWithCustomWindow()
        
        # Show maximized (matching original behavior)
        CustomWindowInstance.showMaximized()
        
        return CustomWindowInstance
        
    except Exception as Error:
        logging.error(f"Failed to create main window: {Error}")
        raise


def RunApplication() -> int:
    """
    Run the complete Anderson's Library application.
    
    Returns:
        Application exit code
    """
    try:
        # Create QApplication
        App = QApplication(sys.argv)
        
        # Set application properties
        App.setApplicationName("Anderson's Library")
        App.setApplicationVersion("2.0")
        App.setOrganizationName("BowersWorld.com")
        
        # Create and show main window
        MainWindow = CreateAndShowMainWindow()
        
        # Run application event loop
        return App.exec()
        
    except Exception as Error:
        logging.error(f"Application failed to start: {Error}")
        return 1


# Entry point for direct execution
if __name__ == "__main__":
    ExitCode = RunApplication()
    sys.exit(ExitCode)
