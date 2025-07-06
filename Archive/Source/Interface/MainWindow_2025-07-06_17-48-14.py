# File: MainWindow.py
# Path: Source/Interface/MainWindow.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-06
# Last Modified: 2025-07-06  12:15PM
"""
Description: MainWindow Content Widget (Like Original)
Simple content widget that gets wrapped by CustomWindow externally.
Follows the original Andy.py pattern exactly.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap

# Import our modules
from Source.Core.DatabaseManager import DatabaseManager
from Source.Core.BookService import BookService
from Source.Interface.FilterPanel import FilterPanel
from Source.Interface.BookGrid import BookGrid


class MainWindow(QWidget):
    """
    Main window content widget (like original Andy.py).
    This is just the content - gets wrapped by CustomWindow externally.
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
        
        # Initialize the widget
        self._InitializeServices()
        self._SetupUI()
        self._ConnectSignals()
        
        self.Logger.info("MainWindow content widget initialized (original pattern)")
    
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
        """Setup the main user interface layout"""
        try:
            # Create main layout
            MainLayout = QHBoxLayout(self)
            MainLayout.setContentsMargins(10, 10, 10, 10)
            MainLayout.setSpacing(10)
            
            # Create splitter for resizable panels
            Splitter = QSplitter(Qt.Horizontal)
            MainLayout.addWidget(Splitter)
            
            # Create filter panel
            self.FilterPanel = FilterPanel(self.BookService)
            self.FilterPanel.setMaximumWidth(300)
            self.FilterPanel.setMinimumWidth(250)
            Splitter.addWidget(self.FilterPanel)
            
            # Create book grid
            self.BookGrid = BookGrid(self.BookService)
            Splitter.addWidget(self.BookGrid)
            
            # Set splitter proportions (20% sidebar, 80% main area)
            Splitter.setSizes([250, 1150])
            
            self.Logger.info("UI setup completed successfully")
            
        except Exception as Error:
            self.Logger.error(f"Failed to setup UI: {Error}")
            raise
    
    def _ConnectSignals(self) -> None:
        """Connect signals between components"""
        try:
            if self.FilterPanel and self.BookGrid:
                # Connect filter changes to book grid updates
                self.FilterPanel.FiltersChanged.connect(self.BookGrid.ApplyFilters)
                
                # Connect book selection to status updates
                self.BookGrid.BookSelected.connect(self._OnBookSelected)
                
                self.Logger.info("Signals connected successfully")
                
        except Exception as Error:
            self.Logger.error(f"Failed to connect signals: {Error}")
    
    def _OnBookSelected(self, BookInfo: dict) -> None:
        """Handle book selection (update parent CustomWindow status)"""
        try:
            # Find the CustomWindow parent and update its status bar
            Parent = self.parent()
            while Parent and not hasattr(Parent, 'get_status_bar'):
                Parent = Parent.parent()
            
            if Parent and hasattr(Parent, 'get_status_bar'):
                StatusBar = Parent.get_status_bar()
                if BookInfo:
                    Message = f"Selected: {BookInfo.get('Title', 'Unknown')} by {BookInfo.get('Author', 'Unknown')}"
                else:
                    Message = "Anderson's Library - Ready"
                StatusBar.showMessage(Message)
                self.Logger.debug(f"Status updated: {Message}")
            
        except Exception as Error:
            self.Logger.error(f"Failed to handle book selection: {Error}")
    
    def resizeEvent(self, Event) -> None:
        """Handle window resize events (like original)"""
        super().resizeEvent(Event)
        
        # Update status bar with window size (like original)
        try:
            Parent = self.parent()
            while Parent and not hasattr(Parent, 'get_status_bar'):
                Parent = Parent.parent()
            
            if Parent and hasattr(Parent, 'get_status_bar'):
                Size = Event.size()
                Width = Size.width()
                Height = Size.height()
                StatusBar = Parent.get_status_bar()
                StatusBar.showMessage(f"Window Size: {Width} x {Height}")
        except Exception as Error:
            self.Logger.error(f"Failed to update size status: {Error}")
        
        # Trigger book grid layout recalculation (like original)
        if self.BookGrid:
            QTimer.singleShot(50, self.BookGrid.HandleResize)
    
    def closeEvent(self, Event) -> None:
        """Handle window close events"""
        try:
            self.Logger.info("Application closing")
            Event.accept()
            
        except Exception as Error:
            self.Logger.error(f"Error during application close: {Error}")
            Event.accept()  # Close anyway
    
    def GetBookGrid(self):
        """Get book grid reference (for external access)"""
        return self.BookGrid
    
    def GetFilterPanel(self):
        """Get filter panel reference (for external access)"""
        return self.FilterPanel


# Factory functions for compatibility
def CreateAndShowMainWindow(DatabasePath: str = "Assets/my_library.db"):
    """
    Create and display the main window with CustomWindow wrapper.
    Follows the original Andy.py pattern exactly.
    
    Args:
        DatabasePath: Path to SQLite database file
        
    Returns:
        CustomWindow wrapper instance
    """
    try:
        # Import CustomWindow here to avoid circular imports
        from Source.Interface.CustomWindow import CustomWindow
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(name)s - %(levelname)s: %(message)s'
        )
        
        # Create main window content (like original)
        MainWindowInstance = MainWindow(DatabasePath)
        
        # Wrap with CustomWindow (like original Andy.py)
        WindowWrapper = CustomWindow("Anderson's Library", MainWindowInstance)
        
        # Show maximized (like original)
        WindowWrapper.showMaximized()
        
        Logger = logging.getLogger("MainWindow")
        Logger.info("Anderson's Library Started with CustomWindow wrapper")
        
        return WindowWrapper
        
    except Exception as Error:
        logging.error(f"Failed to create main window: {Error}")
        raise


def RunApplication() -> int:
    """
    Run the complete Anderson's Library application (original pattern).
    
    Returns:
        Application exit code
    """
    try:
        from PySide6.QtWidgets import QApplication
        
        # Create QApplication
        App = QApplication.instance()
        if App is None:
            App = QApplication(sys.argv)
        
        # Set application properties
        App.setApplicationName("Anderson's Library")
        App.setApplicationVersion("2.0")
        App.setOrganizationName("Project Himalaya")
        App.setOrganizationDomain("BowersWorld.com")
        
        # Create and show main window
        WindowWrapper = CreateAndShowMainWindow()
        
        # Run the event loop
        return App.exec()
        
    except Exception as Error:
        logging.error(f"Application failed to run: {Error}")
        return 1


if __name__ == "__main__":
    sys.exit(RunApplication())