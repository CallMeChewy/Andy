# File: FilterPanel.py
# Path: Source/Interface/FilterPanel.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  07:55PM
"""
Description: FilterPanel with PySide6 Signal Compatibility
Fixed import to use PySide6.QtCore.Signal instead of pyqtSignal.
Implements correct workflow: Category selection → Subject population → Book display.
"""

import logging
from typing import Optional, Callable, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QFrame
)
from PySide6.QtCore import QTimer, Signal  # ✅ FIXED: Signal instead of pyqtSignal
from PySide6.QtGui import QFont

from Source.Core.BookService import BookService
from Source.Data.DatabaseModels import SearchCriteria


class FilterPanel(QWidget):
    """
    Enhanced filter panel with proper category/subject coordination.
    Uses simple BookService interface without direct database access.
    """
    
    # ✅ FIXED: Use Signal instead of pyqtSignal for PySide6
    FilterChanged = Signal(SearchCriteria)  # Category/Subject filters
    SearchRequested = Signal(SearchCriteria)  # Search queries
    StatusUpdate = Signal(str)  # Status messages
    
    def __init__(self, BookService: BookService, parent=None):
        """
        Initialize filter panel with proper event coordination.
        
        Args:
            BookService: Service for database operations
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Core dependencies
        self.BookService = BookService
        self.Logger = logging.getLogger(__name__)
        
        # State tracking
        self.IgnoreSignals = False  # Prevent recursive updates
        self.CurrentCategory = ""
        self.CurrentSubject = ""
        
        # Search timer for debouncing
        self.SearchTimer = QTimer()
        self.SearchTimer.setSingleShot(True)
        self.SearchTimer.timeout.connect(self._PerformSearch)
        
        # UI Components (will be created in _CreateUI)
        self.CategoryComboBox = None
        self.SubjectComboBox = None
        self.SearchLineEdit = None
        
        # Build interface
        self._CreateUI()
        self._LoadInitialData()
        self._ConnectSignals()
        
        self.Logger.info("FilterPanel initialized successfully")
    
    def _CreateUI(self) -> None:
        """Create the user interface"""
        Layout = QVBoxLayout(self)
        Layout.setContentsMargins(10, 10, 10, 10)
        Layout.setSpacing(10)
        
        # Title
        TitleLabel = QLabel("--- Options ---")
        TitleLabel.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        TitleLabel.setStyleSheet("color: white; background-color: transparent;")
        Layout.addWidget(TitleLabel)
        
        # Category selection
        CategoryLabel = QLabel("Category:")
        CategoryLabel.setStyleSheet("color: white; font-weight: bold;")
        Layout.addWidget(CategoryLabel)
        
        self.CategoryComboBox = QComboBox()
        self.CategoryComboBox.addItem("All Categories")  # Default placeholder
        self.CategoryComboBox.setMinimumHeight(25)
        Layout.addWidget(self.CategoryComboBox)
        
        # Subject selection  
        SubjectLabel = QLabel("Subject:")
        SubjectLabel.setStyleSheet("color: white; font-weight: bold;")
        Layout.addWidget(SubjectLabel)
        
        self.SubjectComboBox = QComboBox()
        self.SubjectComboBox.addItem("All Subjects")  # Default placeholder
        self.SubjectComboBox.setMinimumHeight(25)
        self.SubjectComboBox.setEnabled(False)  # Disabled until category selected
        Layout.addWidget(self.SubjectComboBox)
        
        # Search
        SearchLabel = QLabel("Search:")
        SearchLabel.setStyleSheet("color: white; font-weight: bold;")
        Layout.addWidget(SearchLabel)
        
        self.SearchLineEdit = QLineEdit()
        self.SearchLineEdit.setPlaceholderText("Type Something Here")
        self.SearchLineEdit.setMinimumHeight(25)
        Layout.addWidget(self.SearchLineEdit)
        
        # Add stretch to push everything to top
        Layout.addStretch()
        
        # Set panel styling
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 50, 100, 180);
                border-right: 2px solid rgba(255, 255, 255, 100);
            }
            QComboBox, QLineEdit {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid rgba(0, 0, 0, 100);
                border-radius: 3px;
                padding: 3px;
            }
            QComboBox:disabled {
                background-color: rgba(200, 200, 200, 100);
                color: gray;
            }
        """)
        
        # Set fixed width
        self.setFixedWidth(320)
    
    def _LoadInitialData(self) -> None:
        """Load categories from database using BookService methods"""
        try:
            # ✅ FIXED: Use BookService methods instead of accessing Database directly
            Categories = self.BookService.GetCategories()
            
            # Populate category dropdown
            self.IgnoreSignals = True  # Prevent events during loading
            for Category in Categories:
                self.CategoryComboBox.addItem(Category)
            self.IgnoreSignals = False
            
            self.Logger.info(f"Loaded {len(Categories)} categories")
            
        except Exception as Error:
            self.Logger.error(f"Data loading error: {Error}")
    
    def _ConnectSignals(self) -> None:
        """Connect UI signals to handlers"""
        # Category selection triggers subject loading
        self.CategoryComboBox.currentTextChanged.connect(self._OnCategoryChanged)
        
        # Subject selection triggers book display
        self.SubjectComboBox.currentTextChanged.connect(self._OnSubjectChanged)
        
        # Search as user types (with debouncing)
        self.SearchLineEdit.textChanged.connect(self._OnSearchChanged)
    
    def _OnCategoryChanged(self, CategoryText: str) -> None:
        """
        Handle category selection changes.
        Loads subjects for selected category and enables subject dropdown.
        """
        if self.IgnoreSignals:
            return
            
        self.Logger.debug(f"Category changed to: '{CategoryText}'")
        
        # Clear search when category changes
        if self.SearchLineEdit.text().strip():
            self.IgnoreSignals = True
            self.SearchLineEdit.clear()
            self.IgnoreSignals = False
        
        # Update current category
        self.CurrentCategory = CategoryText if CategoryText != "All Categories" else ""
        
        # Load subjects for this category
        self._LoadSubjectsForCategory(CategoryText)
        
        # Reset subject selection
        self.CurrentSubject = ""
        
        # If "All Categories" selected, disable subject dropdown
        if CategoryText == "All Categories":
            self.SubjectComboBox.setEnabled(False)
            # Don't emit filter - user needs to select a specific category
        else:
            self.SubjectComboBox.setEnabled(True)
            # Don't emit filter yet - wait for subject selection
    
    def _LoadSubjectsForCategory(self, CategoryText: str) -> None:
        """
        Load subjects for the selected category.
        
        Args:
            CategoryText: Selected category name
        """
        try:
            # Clear existing subjects
            self.IgnoreSignals = True
            self.SubjectComboBox.clear()
            self.SubjectComboBox.addItem("All Subjects")
            
            # ✅ FIXED: Use BookService method instead of database access
            if CategoryText and CategoryText != "All Categories":
                Subjects = self.BookService.GetSubjectsForCategory(CategoryText)
                for Subject in Subjects:
                    self.SubjectComboBox.addItem(Subject)
                    
                self.Logger.debug(f"Loaded {len(Subjects)} subjects for category '{CategoryText}'")
            
            self.IgnoreSignals = False
            
        except Exception as Error:
            self.IgnoreSignals = False
            self.Logger.error(f"Failed to load subjects for category '{CategoryText}': {Error}")
    
    def _OnSubjectChanged(self, SubjectText: str) -> None:
        """
        Handle subject selection changes.
        Emits filter to display books for selected category/subject.
        """
        if self.IgnoreSignals:
            return
            
        self.Logger.debug(f"Subject changed to: '{SubjectText}'")
        
        # Update current subject
        self.CurrentSubject = SubjectText if SubjectText != "All Subjects" else ""
        
        # Only emit filter if we have a valid category and subject
        if self.CurrentCategory and self.CurrentSubject:
            Criteria = SearchCriteria()
            Criteria.Categories = [self.CurrentCategory]
            Criteria.Subjects = [self.CurrentSubject]
            
            self.FilterChanged.emit(Criteria)
            self.StatusUpdate.emit(f"Showing books: {self.CurrentCategory} → {self.CurrentSubject}")
            
        elif self.CurrentCategory and SubjectText == "All Subjects":
            # Show all books in category
            Criteria = SearchCriteria()
            Criteria.Categories = [self.CurrentCategory]
            
            self.FilterChanged.emit(Criteria)
            self.StatusUpdate.emit(f"Showing all books in: {self.CurrentCategory}")
    
    def _OnSearchChanged(self, SearchText: str) -> None:
        """
        Handle search text changes.
        Clears category/subject selections and shows search results.
        """
        if self.IgnoreSignals:
            return
            
        self.SearchTimer.stop()
        
        if len(SearchText.strip()) > 1:
            # Clear dropdowns when searching
            self.IgnoreSignals = True
            self.CategoryComboBox.setCurrentText("All Categories")
            self.SubjectComboBox.clear()
            self.SubjectComboBox.addItem("All Subjects")
            self.SubjectComboBox.setEnabled(False)
            self.IgnoreSignals = False
            
            # Reset state
            self.CurrentCategory = ""
            self.CurrentSubject = ""
            
            # Start search timer (debounced)
            self.SearchTimer.start(400)
            self.StatusUpdate.emit(f"Searching for: {SearchText.strip()}")
            
        elif len(SearchText.strip()) == 0:
            # Search cleared - reset to initial state
            self._ResetToInitialState()
    
    def _PerformSearch(self) -> None:
        """Perform search with current search text"""
        SearchText = self.SearchLineEdit.text().strip()
        
        if SearchText:
            Criteria = SearchCriteria()
            Criteria.SearchTerm = SearchText
            
            self.SearchRequested.emit(Criteria)
            self.Logger.debug(f"Search performed: '{SearchText}'")
    
    def _ResetToInitialState(self) -> None:
        """Reset panel to initial state (no selections)"""
        self.IgnoreSignals = True
        
        # Reset dropdowns
        self.CategoryComboBox.setCurrentText("All Categories")
        self.SubjectComboBox.clear()
        self.SubjectComboBox.addItem("All Subjects")
        self.SubjectComboBox.setEnabled(False)
        
        # Reset state
        self.CurrentCategory = ""
        self.CurrentSubject = ""
        
        self.IgnoreSignals = False
        
        # Clear grid
        EmptyCriteria = SearchCriteria()
        self.FilterChanged.emit(EmptyCriteria)
        self.StatusUpdate.emit("Select a category to begin")
    
    def GetCurrentCriteria(self) -> SearchCriteria:
        """
        Get current search criteria.
        
        Returns:
            SearchCriteria object with current filters
        """
        Criteria = SearchCriteria()
        
        # Search term takes priority
        SearchText = self.SearchLineEdit.text().strip()
        if SearchText:
            Criteria.SearchTerm = SearchText
            return Criteria
        
        # Otherwise use category/subject filters
        if self.CurrentCategory:
            Criteria.Categories = [self.CurrentCategory]
        if self.CurrentSubject:
            Criteria.Subjects = [self.CurrentSubject]
        
        return Criteria
    
    def RefreshData(self) -> None:
        """Refresh filter data from database"""
        self._LoadInitialData()
        self._ResetToInitialState()
        self.Logger.info("Filter data refreshed")