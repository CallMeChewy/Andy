# File: MainWindow.py
# Path: Source/Interface/MainWindow.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04 06:35PM
"""
Description: Main Application Window for Anderson's Library
Orchestrates the Filter Panel and Book Grid components to create the complete
library management interface. Handles application-level concerns and user interactions.
"""

import sys
import logging
import os
import subprocess
import platform
from PySide6.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QSizePolicy, QMenu,
                               QWidget, QMenuBar, QStatusBar, QToolBar, 
                               QMessageBox, QProgressBar, QLabel, QSplitter,
                               QDialog, QTextEdit, QPushButton, QFileDialog)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSettings, QSize
from PySide6.QtGui import QIcon, QPixmap, QFont, QKeySequence, QShortcut, QAction
from typing import List, Optional, Dict, Any
import traceback

from .CustomWindow import CustomWindow
from .FilterPanel import FilterPanel
from .BookGrid import BookGrid
from ..Core.DatabaseManager import DatabaseManager
from ..Core.BookService import BookService
from ..Data.DatabaseModels import BookRecord, SearchResult, SearchCriteria, CategoryInfo, LibraryStatistics


class LoadingWorker(QThread):
    """
    Background worker for loading books and performing database operations.
    Prevents the UI from freezing during long operations.
    """
    
    # Signals
    BooksLoaded = Signal(object)        # SearchResult
    StatisticsLoaded = Signal(object)   # LibraryStatistics
    Error = Signal(str)                 # Error message
    Progress = Signal(int, str)         # Progress value, status message
    
    def __init__(self, BookService: BookService, SearchCriteria: Optional[SearchCriteria] = None):
        super().__init__()
        self.BookService = BookService
        self.SearchCriteria = SearchCriteria
        self.Operation = "load_books"
        
    def SetOperation(self, Operation: str):
        """Set the operation to perform"""
        self.Operation = Operation
    
    def run(self):
        """Execute the background operation"""
        try:
            if self.Operation == "load_books":
                self.LoadBooks()
            elif self.Operation == "load_statistics":
                self.LoadStatistics()
            elif self.Operation == "refresh_database":
                self.RefreshDatabase()
                
        except Exception as Error:
            logging.error(f"Worker error: {Error}")
            self.Error.emit(str(Error))
    
    def LoadBooks(self):
        """Load books based on search criteria"""
        try:
            self.Progress.emit(10, "Connecting to database...")
            
            if self.SearchCriteria and not self.SearchCriteria.IsEmpty():
                self.Progress.emit(30, "Searching books...")
                Result = self.BookService.SearchBooks(self.SearchCriteria)
            else:
                self.Progress.emit(30, "Loading all books...")
                Result = self.BookService.GetAllBooks()
            
            self.Progress.emit(90, "Processing results...")
            self.BooksLoaded.emit(Result)
            self.Progress.emit(100, "Complete")
            
        except Exception as Error:
            self.Error.emit(f"Error loading books: {Error}")
    
    def LoadStatistics(self):
        """Load library statistics"""
        try:
            self.Progress.emit(20, "Calculating statistics...")
            Stats = self.BookService.GetLibraryStatistics()
            self.StatisticsLoaded.emit(Stats)
            self.Progress.emit(100, "Statistics loaded")
            
        except Exception as Error:
            self.Error.emit(f"Error loading statistics: {Error}")
    
    def RefreshDatabase(self):
        """Refresh database and reload books"""
        try:
            self.Progress.emit(20, "Refreshing database...")
            # This could include operations like updating file paths, 
            # recalculating statistics, cleaning up orphaned records, etc.
            self.Progress.emit(60, "Reloading books...")
            Result = self.BookService.GetAllBooks()
            self.BooksLoaded.emit(Result)
            self.Progress.emit(100, "Database refreshed")
            
        except Exception as Error:
            self.Error.emit(f"Error refreshing database: {Error}")


class AndersonMainWindow(CustomWindow):
    """
    Main application window for Anderson's Library.
    Inherits from CustomWindow for consistent BowersWorld styling and behavior.
    """
    
    def __init__(self):
        super().__init__("Anderson's Library - Professional Edition")
        
        # Initialize services
        self.DatabaseManager = None
        self.BookService = None
        self.LoadingWorker = None
        
        # Application state
        self.CurrentBooks = []
        self.CurrentCriteria = SearchCriteria()
        self.LibraryStats = None
        
        # Initialize the UI
        self.InitializeApplication()
        self.SetupMainWindow()
        self.CreateMenuSystem()
        self.CreateToolbar()
        self.CreateMainInterface()
        self.CreateStatusBar()
        self.SetupConnections()
        self.LoadSettings()
        
        # Start loading data
        self.StartDataLoading()
        
        logging.info("Anderson's Library main window initialized")
    
    def InitializeApplication(self):
        """Initialize database and services"""
        try:
            # Initialize database
            DatabasePath = "Assets/my_library.db"
            if not os.path.exists(DatabasePath):
                # Try alternate paths
                AlternatePaths = [
                    "Data/my_library.db",
                    "Data/Databases/my_library.db",
                    "my_library.db"
                ]
                
                for Path in AlternatePaths:
                    if os.path.exists(Path):
                        DatabasePath = Path
                        break
                else:
                    raise FileNotFoundError("Database file not found")
            
            self.DatabaseManager = DatabaseManager(DatabasePath)
            self.BookService = BookService(self.DatabaseManager)
            
            logging.info(f"Database initialized: {DatabasePath}")
            
        except Exception as Error:
            logging.error(f"Failed to initialize application: {Error}")
            QMessageBox.critical(self, "Initialization Error", 
                               f"Failed to initialize Anderson's Library:\n{Error}")
            sys.exit(1)
    
    def SetupMainWindow(self):
        """Configure the main window properties"""
        self.setWindowTitle("🏔️ Anderson's Library - Professional Edition")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Try to load application icon
        IconPaths = [
            "Assets/icon.png",
            "Assets/library.png", 
            "Assets/BowersWorld.png"
        ]
        
        for IconPath in IconPaths:
            if os.path.exists(IconPath):
                self.setWindowIcon(QIcon(IconPath))
                break
    
    def CreateMenuSystem(self):
        """Create the application menu system"""
        MenuBar = self.menuBar()
        
        # File menu
        FileMenu = MenuBar.addMenu("&File")
        
        OpenAction = QAction("&Open Book...", self)
        OpenAction.setShortcut(QKeySequence.StandardKey.Open)
        OpenAction.setStatusTip("Open a book file")
        OpenAction.triggered.connect(self.OnOpenBook)
        FileMenu.addAction(OpenAction)
        
        FileMenu.addSeparator()
        
        RefreshAction = QAction("&Refresh Library", self)
        RefreshAction.setShortcut(QKeySequence("F5"))
        RefreshAction.setStatusTip("Refresh the library database")
        RefreshAction.triggered.connect(self.OnRefreshLibrary)
        FileMenu.addAction(RefreshAction)
        
        FileMenu.addSeparator()
        
        ExitAction = QAction("E&xit", self)
        ExitAction.setShortcut(QKeySequence.StandardKey.Quit)
        ExitAction.setStatusTip("Exit Anderson's Library")
        ExitAction.triggered.connect(self.close)
        FileMenu.addAction(ExitAction)
        
        # View menu
        self.ViewMenu = MenuBar.addMenu("&View")
        
        GridViewAction = QAction("&Grid View", self)
        GridViewAction.setShortcut(QKeySequence("Ctrl+1"))
        GridViewAction.setCheckable(True)
        GridViewAction.setChecked(True)
        GridViewAction.triggered.connect(lambda: self.SetViewMode("grid"))
        self.ViewMenu.addAction(GridViewAction)
        
        ListViewAction = QAction("&List View", self)
        ListViewAction.setShortcut(QKeySequence("Ctrl+2"))
        ListViewAction.setCheckable(True)
        ListViewAction.triggered.connect(lambda: self.SetViewMode("list"))
        self.ViewMenu.addAction(ListViewAction)
        
        DetailViewAction = QAction("&Detail View", self)
        DetailViewAction.setShortcut(QKeySequence("Ctrl+3"))
        DetailViewAction.setCheckable(True)
        DetailViewAction.triggered.connect(lambda: self.SetViewMode("detail"))
        self.ViewMenu.addAction(DetailViewAction)
        
        # Tools menu
        ToolsMenu = MenuBar.addMenu("&Tools")
        
        StatsAction = QAction("Library &Statistics", self)
        StatsAction.setStatusTip("Show library statistics")
        StatsAction.triggered.connect(self.OnShowStatistics)
        ToolsMenu.addAction(StatsAction)
        
        SettingsAction = QAction("&Settings...", self)
        SettingsAction.setStatusTip("Open application settings")
        SettingsAction.triggered.connect(self.OnShowSettings)
        ToolsMenu.addAction(SettingsAction)
        
        # Help menu
        HelpMenu = MenuBar.addMenu("&Help")
        
        AboutAction = QAction("&About Anderson's Library", self)
        AboutAction.setStatusTip("About this application")
        AboutAction.triggered.connect(self.OnShowAbout)
        HelpMenu.addAction(AboutAction)
    
    def CreateToolbar(self):
        """Create the main toolbar"""
        self.MainToolbar = self.addToolBar("Main")
        self.MainToolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        
        # Refresh action
        RefreshAction = QAction("🔄 Refresh", self)
        RefreshAction.setToolTip("Refresh library")
        RefreshAction.triggered.connect(self.OnRefreshLibrary)
        self.MainToolbar.addAction(RefreshAction)
        
        self.MainToolbar.addSeparator()
        
        # Statistics action
        StatsAction = QAction("📊 Statistics", self)
        StatsAction.setToolTip("Show library statistics")
        StatsAction.triggered.connect(self.OnShowStatistics)
        self.MainToolbar.addAction(StatsAction)
        
        self.MainToolbar.addSeparator()
        
        # Add spacer
        Spacer = QWidget()
        Spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.MainToolbar.addWidget(Spacer)
        
        # Logo/branding
        LogoLabel = QLabel("📚 Anderson's Library")
        LogoFont = QFont()
        LogoFont.setPointSize(12)
        LogoFont.setBold(True)
        LogoLabel.setFont(LogoFont)
        LogoLabel.setStyleSheet("color: #2196F3; margin-right: 10px;")
        self.MainToolbar.addWidget(LogoLabel)
    
    def CreateMainInterface(self):
        """Create the main interface with filter panel and book grid"""
        # Central widget
        CentralWidget = QWidget()
        self.setCentralWidget(CentralWidget)
        
        # Main layout
        MainLayout = QHBoxLayout(CentralWidget)
        MainLayout.setContentsMargins(0, 0, 0, 0)
        MainLayout.setSpacing(0)
        
        # Create splitter for resizable panels
        self.MainSplitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Filter panel
        self.FilterPanel = FilterPanel()
        self.MainSplitter.addWidget(self.FilterPanel)
        
        # Book grid
        self.BookGrid = BookGrid()
        self.MainSplitter.addWidget(self.BookGrid)
        
        # Set splitter proportions
        self.MainSplitter.setStretchFactor(0, 0)  # Filter panel fixed width
        self.MainSplitter.setStretchFactor(1, 1)  # Book grid expandable
        self.MainSplitter.setSizes([280, 1120])    # Initial sizes
        
        MainLayout.addWidget(self.MainSplitter)
    
    def CreateStatusBar(self):
        """Create the status bar"""
        self.StatusBar = self.statusBar()
        
        # Main status label
        self.StatusLabel = QLabel("Ready")
        self.StatusBar.addWidget(self.StatusLabel)
        
        # Progress bar for operations
        self.ProgressBar = QProgressBar()
        self.ProgressBar.setVisible(False)
        self.ProgressBar.setMaximumWidth(200)
        self.StatusBar.addPermanentWidget(self.ProgressBar)
        
        # Database status
        self.DatabaseStatusLabel = QLabel("Database: Connected")
        self.DatabaseStatusLabel.setStyleSheet("color: green;")
        self.StatusBar.addPermanentWidget(self.DatabaseStatusLabel)
    
    def SetupConnections(self):
        """Connect signals between components"""
        # Filter panel connections
        self.FilterPanel.SearchRequested.connect(self.OnSearchRequested)
        self.FilterPanel.FiltersChanged.connect(self.OnFiltersChanged)
        self.FilterPanel.ClearRequested.connect(self.OnClearFilters)
        
        # Book grid connections
        self.BookGrid.BookSelected.connect(self.OnBookSelected)
        self.BookGrid.BookOpened.connect(self.OnBookOpened)
        self.BookGrid.SelectionChanged.connect(self.OnSelectionChanged)
        self.BookGrid.ViewModeChanged.connect(self.OnViewModeChanged)
        self.BookGrid.SortChanged.connect(self.OnSortChanged)
    
    def LoadSettings(self):
        """Load application settings"""
        try:
            Settings = QSettings("BowersWorld", "AndersonLibrary")
            
            # Window geometry
            if Settings.contains("geometry"):
                self.restoreGeometry(Settings.value("geometry"))
            
            # Splitter state
            if Settings.contains("splitter"):
                self.MainSplitter.restoreState(Settings.value("splitter"))
            
            # View mode
            ViewMode = Settings.value("viewMode", "grid")
            self.SetViewMode(ViewMode)
            
            logging.info("Settings loaded")
            
        except Exception as Error:
            logging.warning(f"Error loading settings: {Error}")
    
    def SaveSettings(self):
        """Save application settings"""
        try:
            Settings = QSettings("BowersWorld", "AndersonLibrary")
            
            Settings.setValue("geometry", self.saveGeometry())
            Settings.setValue("splitter", self.MainSplitter.saveState())
            Settings.setValue("viewMode", self.BookGrid.ViewMode)
            
            logging.info("Settings saved")
            
        except Exception as Error:
            logging.warning(f"Error saving settings: {Error}")
    
    def StartDataLoading(self):
        """Start loading initial data"""
        self.SetLoadingState(True, "Initializing library...")
        
        # Load initial books
        self.LoadBooks()
        
        # Load filter data in background
        QTimer.singleShot(100, self.LoadFilterData)
    
    def LoadBooks(self, Criteria: Optional[SearchCriteria] = None):
        """Load books with optional search criteria"""
        if self.LoadingWorker and self.LoadingWorker.isRunning():
            return  # Already loading
        
        self.CurrentCriteria = Criteria or SearchCriteria()
        
        self.LoadingWorker = LoadingWorker(self.BookService, self.CurrentCriteria)
        self.LoadingWorker.BooksLoaded.connect(self.OnBooksLoaded)
        self.LoadingWorker.Error.connect(self.OnLoadingError)
        self.LoadingWorker.Progress.connect(self.OnLoadingProgress)
        self.LoadingWorker.finished.connect(self.OnLoadingFinished)
        
        self.SetLoadingState(True, "Loading books...")
        self.LoadingWorker.start()
    
    def LoadFilterData(self):
        """Load data for filter dropdowns"""
        try:
            # Load categories
            Categories = self.BookService.GetAllCategories()
            self.FilterPanel.UpdateCategories(Categories)
            
            # Load authors
            Authors = self.BookService.GetAuthors()
            if Authors:
                self.FilterPanel.UpdateAuthors(Authors)
            
            logging.info("Filter data loaded")
            
        except Exception as Error:
            logging.error(f"Error loading filter data: {Error}")
    
    def SetLoadingState(self, Loading: bool, Message: str = ""):
        """Set the loading state of the interface"""
        if Loading:
            self.ProgressBar.setVisible(True)
            self.ProgressBar.setValue(0)
            self.StatusLabel.setText(Message)
            self.setCursor(Qt.CursorShape.WaitCursor)
        else:
            self.ProgressBar.setVisible(False)
            self.setCursor(Qt.CursorShape.ArrowCursor)
            if not Message:
                Message = "Ready"
            self.StatusLabel.setText(Message)
    
    def SetViewMode(self, Mode: str):
        """Set the book grid view mode"""
        if not self.ViewMenu:
            return

        # Update menu checkmarks
        for Action in self.ViewMenu.actions():
            Action.setChecked(False)
            if Action.text().lower().startswith(f"&{Mode}"):
                Action.setChecked(True)
        
        # Update book grid
        self.BookGrid.ViewMode = Mode
        self.BookGrid.RefreshDisplay()
    
    # Event handlers
    def OnSearchRequested(self, Criteria: SearchCriteria):
        """Handle search request from filter panel"""
        logging.info(f"Search requested: {Criteria.GetSummary()}")
        self.LoadBooks(Criteria)
    
    def OnFiltersChanged(self, Criteria: SearchCriteria):
        """Handle filter changes (with debouncing)"""
        # Auto-search with a slight delay
        QTimer.singleShot(300, lambda: self.LoadBooks(Criteria))
    
    def OnClearFilters(self):
        """Handle clear filters request"""
        self.LoadBooks()
    
    def OnBooksLoaded(self, Result: SearchResult):
        """Handle books loaded from worker"""
        if not Result.Success:
            self.OnLoadingError(Result.ErrorMessage)
            return

        self.CurrentBooks = Result.Books
        self.BookGrid.UpdateBooks(Result)
        
        # Update filter panel stats
        self.FilterPanel.UpdateStats(len(self.CurrentBooks), len(Result.Books))
        
        Message = f"Loaded {len(Result.Books)} books"
        if Result.SearchTime > 0:
            Message += f" in {Result.SearchTime:.2f}s"
        
        self.SetLoadingState(False, Message)
        logging.info(f"Books loaded: {len(Result.Books)}")
    
    def OnLoadingError(self, ErrorMessage: str):
        """Handle loading error"""
        self.SetLoadingState(False, f"Error: {ErrorMessage}")
        QMessageBox.warning(self, "Loading Error", f"Failed to load books:\n{ErrorMessage}")
        logging.error(f"Loading error: {ErrorMessage}")
    
    def OnLoadingProgress(self, Value: int, Message: str):
        """Handle loading progress update"""
        self.ProgressBar.setValue(Value)
        self.StatusLabel.setText(Message)
    
    def OnLoadingFinished(self):
        """Handle loading worker finished"""
        if self.LoadingWorker:
            self.LoadingWorker.deleteLater()
            self.LoadingWorker = None
    
    def OnBookSelected(self, Book: BookRecord):
        """Handle book selection"""
        self.StatusLabel.setText(f"Selected: {Book.Title}")
    
    def OnBookOpened(self, Book: BookRecord):
        """Handle book opening"""
        self.OpenBook(Book)
    
    def OnSelectionChanged(self, SelectedBooks: List[BookRecord]):
        """Handle selection change"""
        Count = len(SelectedBooks)
        if Count == 0:
            self.StatusLabel.setText("Ready")
        elif Count == 1:
            self.StatusLabel.setText(f"Selected: {SelectedBooks[0].Title}")
        else:
            self.StatusLabel.setText(f"Selected {Count} books")
    
    def OnViewModeChanged(self, Mode: str):
        """Handle view mode change"""
        logging.info(f"View mode changed to: {Mode}")
    
    def OnSortChanged(self, Field: str, Order: str):
        """Handle sort change"""
        logging.info(f"Sort changed: {Field} {Order}")
    
    # Menu actions
    def OnOpenBook(self):
        """Handle open book menu action"""
        FilePath, _ = QFileDialog.getOpenFileName(
            self, "Open Book File", "", 
            "Book Files (*.pdf *.epub *.mobi *.txt);;All Files (*.*)"
        )
        
        if FilePath:
            # This would add the book to the library
            logging.info(f"Open book file: {FilePath}")
    
    def OnRefreshLibrary(self):
        """Handle refresh library action"""
        self.LoadBooks()
        self.LoadFilterData()
    
    def OnShowStatistics(self):
        """Show library statistics dialog"""
        if self.LoadingWorker and self.LoadingWorker.isRunning():
            QMessageBox.information(self, "Busy", "Please wait for the current operation to complete.")
            return

        if not self.LibraryStats:
            # Load statistics in background
            self.LoadingWorker = LoadingWorker(self.BookService)
            self.LoadingWorker.SetOperation("load_statistics")
            self.LoadingWorker.StatisticsLoaded.connect(self.DisplayStatistics)
            self.LoadingWorker.Error.connect(self.OnLoadingError)
            self.LoadingWorker.Progress.connect(self.OnLoadingProgress)
            self.LoadingWorker.finished.connect(self.OnLoadingFinished)
            self.SetLoadingState(True, "Loading statistics...")
            self.LoadingWorker.start()
        else:
            self.DisplayStatistics(self.LibraryStats)
    
    def DisplayStatistics(self, Stats: LibraryStatistics):
        """Display statistics dialog"""
        self.LibraryStats = Stats
        
        Dialog = QDialog(self)
        Dialog.setWindowTitle("Library Statistics")
        Dialog.setModal(True)
        Dialog.resize(400, 300)
        
        Layout = QVBoxLayout(Dialog)
        
        StatsText = QTextEdit()
        StatsText.setReadOnly(True)
        StatsText.setPlainText(f"""
📚 Anderson's Library Statistics

Total Books: {Stats.TotalBooks}
Total Size: {Stats.GetFormattedTotalSize()}
Total Authors: {Stats.TotalAuthors}
Total Categories: {Stats.TotalCategories}

Average Rating: {Stats.AverageRating:.1f}/5
Rated Books: {Stats.RatedBooks}

Books Added This Month: {Stats.BooksAddedThisMonth}
Books Added This Year: {Stats.BooksAddedThisYear}

Missing Files: {Stats.MissingFiles}
Books with Thumbnails: {Stats.BooksWithThumbnails}

File Type Breakdown:
{chr(10).join([f"  {fmt}: {count}" for fmt, count in Stats.FileTypeCounts.items()])}
        """)
        Layout.addWidget(StatsText)
        
        CloseBtn = QPushButton("Close")
        CloseBtn.clicked.connect(Dialog.accept)
        Layout.addWidget(CloseBtn)
        
        Dialog.exec()
    
    def OnShowSettings(self):
        """Show settings dialog"""
        QMessageBox.information(self, "Settings", "Settings dialog not yet implemented")
    
    def OnShowAbout(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Anderson's Library", 
                         """
<h3>🏔️ Anderson's Library - Professional Edition</h3>
<p><b>Digital Library Management System</b></p>
<p>🎯 Project Himalaya - BowersWorld.com</p>
<p>⚡ Modular Architecture - Design Standard v1.8</p>
<br>
<p>A professional-grade library management application built with modern Python architecture.</p>
<p>© 2025 Herb Bowers - BowersWorld.com</p>
                         """)
    
    def OpenBook(self, Book: BookRecord):
        """Open a book file with the system default application"""
        try:
            if not Book.FileExists():
                QMessageBox.warning(self, "File Not Found", 
                                  f"The book file was not found:\n{Book.FilePath}")
                return
            
            FilePath = Book.GetFullPath()
            
            # Open with system default application
            if platform.system() == "Windows":
                os.startfile(FilePath)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", FilePath])
            else:  # Linux
                subprocess.call(["xdg-open", FilePath])
            
            # Update last accessed time
            self.BookService.UpdateLastAccessed(Book.Id)
            
            logging.info(f"Opened book: {Book.Title}")
            
        except Exception as Error:
            logging.error(f"Error opening book: {Error}")
            QMessageBox.critical(self, "Error Opening Book", 
                               f"Failed to open book:\n{Error}")
    
    # Window event handlers
    def closeEvent(self, event):
        """Handle window close event"""
        self.SaveSettings()
        
        # Clean up workers
        if self.LoadingWorker and self.LoadingWorker.isRunning():
            self.LoadingWorker.quit()
            if not self.LoadingWorker.wait(3000):  # Wait up to 3 seconds
                logging.warning("Worker thread did not terminate gracefully.")
                self.LoadingWorker.terminate() # Force terminate if necessary
                self.LoadingWorker.wait() # Wait again after termination
        
        super().closeEvent(event)


def RunApplication() -> int:
    """
    Main entry point for the Anderson's Library application.
    Creates and runs the QApplication with proper error handling.
    """
    try:
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('anderson_library.log'),
                logging.StreamHandler()
            ]
        )
        
        # Create application
        App = QApplication(sys.argv)
        
# Set application-wide stylesheet for better contrast
        App.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            
            QMenuBar {
                background-color: #3c3c3c;
                color: #ffffff;
                border-bottom: 1px solid #555555;
                font-size: 13px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
            }
            QMenuBar::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            
            QMenu {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 4px;
            }
            QMenu::item {
                padding: 8px 16px;
            }
            QMenu::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            
            QToolBar {
                background-color: #3c3c3c;
                border: none;
                spacing: 4px;
                padding: 4px;
            }
            QToolButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 2px solid #666666;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #404040;
                border-color: #0078d4;
            }
            
            QStatusBar {
                background-color: #3c3c3c;
                color: #ffffff;
                border-top: 1px solid #555555;
            }
            
            QSplitter::handle {
                background-color: #666666;
                width: 4px;
            }
            QSplitter::handle:hover {
                background-color: #0078d4;
            }
        """)
        App.setApplicationName("Anderson's Library")
        App.setApplicationVersion("1.0.0")
        App.setOrganizationName("BowersWorld")
        App.setOrganizationDomain("bowersworld.com")
        
        # Print startup message
        print("🏔️ Anderson's Library - Professional Edition")
        print("=" * 50)
        print("📚 Digital Library Management System")
        print("🎯 Project Himalaya - BowersWorld.com")
        print("⚡ Modular Architecture - Design Standard v1.8")
        print("=" * 50)
        
        # Create and show main window
        MainWindow = AndersonMainWindow()
        MainWindow.show()
        
        # Run application
        return App.exec()
        
    except Exception as Error:
        logging.critical(f"Application startup failed: {Error}")
        logging.critical(traceback.format_exc())
        
        if 'App' in locals():
            QMessageBox.critical(None, "Startup Error", 
                               f"Anderson's Library failed to start:\n{Error}")
        else:
            print(f"CRITICAL ERROR: {Error}")
            traceback.print_exc()
        
        return 1


if __name__ == "__main__":
    sys.exit(RunApplication())