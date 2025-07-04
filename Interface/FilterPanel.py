# File: FilterPanel.py
# Path: Source/Interface/FilterPanel.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  15:15PM
"""
Description: Anderson's Library Filter Panel Component
Left sidebar component with category/subject dropdowns and search functionality.
Provides clean separation between filtering UI and main book display.

Purpose: Encapsulates all filtering controls and their behavior, communicating
with BookService for data and main window for book selection events.
"""

from typing import Optional, Callable, List
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QLineEdit, QListView, QLabel
)
from PySide6.QtCore import Qt, QEvent, QStringListModel, QTimer
from PySide6.QtGui import QFont

from ..Core.BookService import BookService
from ..Data.DatabaseModels import Book


class ToolTipListView(QListView):
    """
    Enhanced QListView with tooltip support for long text items.
    Provides better user experience for dropdown menus with long names.
    """
    
    def __init__(self, Parent=None):
        """Initialize tooltip-enabled list view"""
        super().__init__(Parent)
        self.setMouseTracking(True)
    
    def viewportEvent(self, Event):
        """Handle viewport events to show tooltips for items"""
        if Event.type() == QEvent.ToolTip:
            Index = self.indexAt(Event.pos())
            if Index.isValid():
                from PySide6.QtWidgets import QToolTip
                QToolTip.showText(Event.globalPos(), Index.data(), self)
            else:
                from PySide6.QtWidgets import QToolTip
                QToolTip.hideText()
                Event.ignore()
            return True
        return super().viewportEvent(Event)


class FilterPanel(QWidget):
    """
    Filter panel component providing category, subject, and search controls.
    Manages filter state and communicates changes to BookService.
    """
    
    def __init__(self, BookServiceInstance: BookService, Parent=None):
        """
        Initialize filter panel with book service dependency.
        
        Args:
            BookServiceInstance: BookService instance for data operations
            Parent: Parent widget
        """
        super().__init__(Parent)
        
        self.BookService = BookServiceInstance
        self.Logger = logging.getLogger(__name__)
        
        # UI Components
        self.CategoryComboBox: Optional[QComboBox] = None
        self.SubjectComboBox: Optional[QComboBox] = None
        self.BookComboBox: Optional[QComboBox] = None
        self.SearchLineEdit: Optional[QLineEdit] = None
        self.SearchListView: Optional[QListView] = None
        self.SearchModel: Optional[QStringListModel] = None
        
        # Search debounce timer
        self.SearchTimer = QTimer()
        self.SearchTimer.setSingleShot(True)
        self.SearchTimer.timeout.connect(self._PerformSearch)
        
        # Event callbacks
        self.OnBookSelected: Optional[Callable[[str], None]] = None
        
        # Filter placeholders
        self.Placeholders = [
            "Select a Category",
            "Select a Subject", 
            "Select a Book Title",
            "Type Something Here"
        ]
        
        self._SetupUserInterface()
        self._ConnectEvents()
        self._PopulateCategories()
        
        self.Logger.info("FilterPanel initialized successfully")
    
    def _SetupUserInterface(self) -> None:
        """Create and layout UI components"""
        # Set fixed width to match original design
        self.setFixedWidth(300)
        
        # Main layout
        self.MainLayout = QVBoxLayout(self)
        self.MainLayout.setContentsMargins(0, 0, 0, 0)
        
        # Create heading
        self._CreateHeading()
        
        # Create font for controls
        ControlFont = QFont()
        ControlFont.setPointSize(12)
        
        # Create category dropdown
        self.CategoryComboBox = self._CreateComboBox(ControlFont, 0)
        self.MainLayout.addWidget(self.CategoryComboBox)
        
        # Create subject dropdown
        self.SubjectComboBox = self._CreateComboBox(ControlFont, 1)
        self.MainLayout.addWidget(self.SubjectComboBox)
        
        # Create book title dropdown
        self.BookComboBox = self._CreateComboBox(ControlFont, 2)
        self.MainLayout.addWidget(self.BookComboBox)
        
        # Create search input
        self.SearchLineEdit = self._CreateSearchInput(ControlFont)
        self.MainLayout.addWidget(self.SearchLineEdit)
        
        # Create search results list
        self.SearchListView = self._CreateSearchList(ControlFont)
        self.MainLayout.addWidget(self.SearchListView)
        
        self.Logger.info("FilterPanel UI setup complete")
    
    def _CreateHeading(self) -> None:
        """Create the options heading label"""
        HeadingFont = QFont("Arial", 12)
        Heading = QLabel("- - - O p t i o n s - - -", alignment=Qt.AlignmentFlag.AlignHCenter)
        Heading.setFont(HeadingFont)
        Heading.setStyleSheet("color: #FCC419")
        Heading.setObjectName("heading")
        self.MainLayout.addWidget(Heading)
    
    def _CreateComboBox(self, Font: QFont, PlaceholderIndex: int) -> QComboBox:
        """
        Create styled combo box with tooltip support.
        
        Args:
            Font: Font to apply to combo box
            PlaceholderIndex: Index of placeholder text
            
        Returns:
            Configured QComboBox
        """
        ComboBox = QComboBox()
        ComboBox.setMaxVisibleItems(30)
        ComboBox.setFont(Font)
        
        # Create custom view with tooltip support
        ListView = ToolTipListView()
        ListView.setFont(Font)
        ListView.setStyleSheet("QListView::item { height: 18px; }")
        ListView.setTextElideMode(Qt.ElideRight)
        ComboBox.setView(ListView)
        
        # Set placeholder
        self._ResetComboBox(ComboBox, PlaceholderIndex)
        
        return ComboBox
    
    def _CreateSearchInput(self, Font: QFont) -> QLineEdit:
        """
        Create search input with proper styling and behavior.
        
        Args:
            Font: Font to apply to line edit
            
        Returns:
            Configured QLineEdit
        """
        LineEdit = QLineEdit()
        LineEdit.setMinimumHeight(18)
        LineEdit.setFont(Font)
        LineEdit.setText(self.Placeholders[3])  # "Type Something Here"
        LineEdit.installEventFilter(self)
        
        return LineEdit
    
    def _CreateSearchList(self, Font: QFont) -> QListView:
        """
        Create search results list view.
        
        Args:
            Font: Font to apply to list view
            
        Returns:
            Configured QListView
        """
        ListView = ToolTipListView()
        ListView.setFont(Font)
        
        # Create and set model
        self.SearchModel = QStringListModel()
        ListView.setModel(self.SearchModel)
        
        # Make it expand to fill remaining space
        from PySide6.QtWidgets import QSizePolicy
        ListView.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        return ListView
    
    def _ConnectEvents(self) -> None:
        """Connect UI events to handler methods"""
        if self.CategoryComboBox:
            self.CategoryComboBox.currentTextChanged.connect(self._OnCategoryChanged)
        
        if self.SubjectComboBox:
            self.SubjectComboBox.currentTextChanged.connect(self._OnSubjectChanged)
        
        if self.BookComboBox:
            self.BookComboBox.currentTextChanged.connect(self._OnBookChanged)
        
        if self.SearchLineEdit:
            self.SearchLineEdit.textChanged.connect(self._OnSearchTextChanged)
        
        if self.SearchListView:
            self.SearchListView.clicked.connect(self._OnSearchItemClicked)
    
    # =================================================================
    # DATA POPULATION METHODS
    # =================================================================
    
    def _PopulateCategories(self) -> None:
        """Populate category combo box with available categories"""
        try:
            CategoryNames = self.BookService.GetCategoryNames()
            
            if self.CategoryComboBox:
                self.CategoryComboBox.blockSignals(True)
                
                # Clear and add placeholder
                self.CategoryComboBox.clear()
                self.CategoryComboBox.addItem(self.Placeholders[0])
                
                # Add categories with tooltips
                for CategoryName in CategoryNames:
                    self.CategoryComboBox.addItem(CategoryName)
                    ItemIndex = self.CategoryComboBox.count() - 1
                    self.CategoryComboBox.setItemData(ItemIndex, CategoryName, Qt.ToolTipRole)
                
                self.CategoryComboBox.blockSignals(False)
                
            self.Logger.info(f"Populated {len(CategoryNames)} categories")
            
        except Exception as Error:
            self.Logger.error(f"Failed to populate categories: {Error}")
    
    def _PopulateSubjects(self) -> None:
        """Populate subject combo box based on selected category"""
        try:
            SubjectNames = self.BookService.GetSubjectNamesForCurrentCategory()
            
            if self.SubjectComboBox:
                self.SubjectComboBox.blockSignals(True)
                
                # Clear and add placeholder
                self.SubjectComboBox.clear()
                self.SubjectComboBox.addItem(self.Placeholders[1])
                
                # Add subjects with tooltips
                for SubjectName in SubjectNames:
                    self.SubjectComboBox.addItem(SubjectName)
                    ItemIndex = self.SubjectComboBox.count() - 1
                    self.SubjectComboBox.setItemData(ItemIndex, SubjectName, Qt.ToolTipRole)
                
                self.SubjectComboBox.blockSignals(False)
                
            self.Logger.info(f"Populated {len(SubjectNames)} subjects")
            
        except Exception as Error:
            self.Logger.error(f"Failed to populate subjects: {Error}")
    
    def _PopulateBooks(self) -> None:
        """Populate book combo box based on current filters"""
        try:
            CurrentBooks = self.BookService.GetCurrentBooks()
            BookTitles = [Book.Title for Book in CurrentBooks]
            
            if self.BookComboBox:
                self.BookComboBox.blockSignals(True)
                
                # Clear and add placeholder
                self.BookComboBox.clear()
                self.BookComboBox.addItem(self.Placeholders[2])
                
                # Add book titles with tooltips
                for BookTitle in BookTitles:
                    self.BookComboBox.addItem(BookTitle)
                    ItemIndex = self.BookComboBox.count() - 1
                    self.BookComboBox.setItemData(ItemIndex, BookTitle, Qt.ToolTipRole)
                
                self.BookComboBox.blockSignals(False)
                
            self.Logger.info(f"Populated {len(BookTitles)} books")
            
        except Exception as Error:
            self.Logger.error(f"Failed to populate books: {Error}")
    
    # =================================================================
    # EVENT HANDLERS
    # =================================================================
    
    def _OnCategoryChanged(self, CategoryName: str) -> None:
        """
        Handle category selection change.
        
        Args:
            CategoryName: Selected category name
        """
        if CategoryName == self.Placeholders[0]:
            # Placeholder selected - clear filter
            self.BookService.SetCurrentCategory(None)
        else:
            # Valid category selected
            self.BookService.SetCurrentCategory(CategoryName)
        
        # Reset dependent dropdowns
        self._ResetComboBox(self.SubjectComboBox, 1)
        self._ResetComboBox(self.BookComboBox, 2)
        
        # Clear search
        self._ClearSearch()
        
        # Populate subjects for new category
        if CategoryName != self.Placeholders[0]:
            self._PopulateSubjects()
    
    def _OnSubjectChanged(self, SubjectName: str) -> None:
        """
        Handle subject selection change.
        
        Args:
            SubjectName: Selected subject name
        """
        if SubjectName == self.Placeholders[1]:
            # Placeholder selected - clear filter
            self.BookService.SetCurrentSubject(None)
        else:
            # Valid subject selected
            self.BookService.SetCurrentSubject(SubjectName)
        
        # Reset book dropdown
        self._ResetComboBox(self.BookComboBox, 2)
        
        # Clear search
        self._ClearSearch()
        
        # Populate books for current filters
        if SubjectName != self.Placeholders[1]:
            self._PopulateBooks()
    
    def _OnBookChanged(self, BookTitle: str) -> None:
        """
        Handle book selection from dropdown.
        
        Args:
            BookTitle: Selected book title
        """
        if BookTitle != self.Placeholders[2] and self.OnBookSelected:
            self.OnBookSelected(BookTitle)
    
    def _OnSearchTextChanged(self, SearchText: str) -> None:
        """
        Handle search text changes with debouncing.
        
        Args:
            SearchText: Current search text
        """
        # Reset search timer for debouncing
        self.SearchTimer.stop()
        
        if len(SearchText) > 1 and SearchText != self.Placeholders[3]:
            # Start timer for delayed search
            self.SearchTimer.start(300)  # 300ms delay
        else:
            # Clear search results immediately for short text
            if self.SearchModel:
                self.SearchModel.setStringList([])
    
    def _PerformSearch(self) -> None:
        """Perform the actual search operation"""
        SearchText = self.SearchLineEdit.text() if self.SearchLineEdit else ""
        
        if len(SearchText) > 1:
            # Clear other filters when searching
            self._ResetComboBox(self.CategoryComboBox, 0)
            self._ResetComboBox(self.SubjectComboBox, 1) 
            self._ResetComboBox(self.BookComboBox, 2)
            
            # Perform search
            SearchResults = self.BookService.SearchBooks(SearchText)
            BookTitles = [Book.Title for Book in SearchResults]
            
            # Update search results list
            if self.SearchModel:
                self.SearchModel.setStringList(BookTitles)
    
    def _OnSearchItemClicked(self, Index) -> None:
        """
        Handle click on search result item.
        
        Args:
            Index: Model index of clicked item
        """
        BookTitle = Index.data()
        if BookTitle and self.OnBookSelected:
            self.OnBookSelected(BookTitle)
    
    # =================================================================
    # UTILITY METHODS
    # =================================================================
    
    def _ResetComboBox(self, ComboBox: Optional[QComboBox], PlaceholderIndex: int) -> None:
        """
        Reset combo box to placeholder state.
        
        Args:
            ComboBox: Combo box to reset
            PlaceholderIndex: Index of placeholder text
        """
        if ComboBox:
            ComboBox.blockSignals(True)
            ComboBox.clear()
            ComboBox.addItem(self.Placeholders[PlaceholderIndex])
            ComboBox.setCurrentIndex(0)
            ComboBox.blockSignals(False)
    
    def _ClearSearch(self) -> None:
        """Clear search input and results"""
        if self.SearchLineEdit:
            self.SearchLineEdit.clear()
            self.SearchLineEdit.setText(self.Placeholders[3])
        
        if self.SearchModel:
            self.SearchModel.setStringList([])
        
        self.BookService.ClearSearch()
    
    def eventFilter(self, Source, Event) -> bool:
        """
        Handle events for search input focus management.
        
        Args:
            Source: Event source object
            Event: Event object
            
        Returns:
            True if event was handled, False otherwise
        """
        if Source is self.SearchLineEdit and Event.type() == QEvent.FocusIn:
            # Clear other selections when search is focused
            self._ResetComboBox(self.CategoryComboBox, 0)
            self._ResetComboBox(self.SubjectComboBox, 1)
            self._ResetComboBox(self.BookComboBox, 2)
            
            # Clear placeholder text
            if self.SearchLineEdit.text() == self.Placeholders[3]:
                self.SearchLineEdit.setText("")
        
        return super().eventFilter(Source, Event)
    
    # =================================================================
    # PUBLIC INTERFACE
    # =================================================================
    
    def SetEventHandlers(self, OnBookSelected: Optional[Callable[[str], None]] = None) -> None:
        """
        Set event handlers for external communication.
        
        Args:
            OnBookSelected: Called when a book is selected for opening
        """
        if OnBookSelected:
            self.OnBookSelected = OnBookSelected
    
    def RefreshData(self) -> None:
        """Refresh all dropdown data from database"""
        self.BookService.RefreshCache()
        self._PopulateCategories()
        
        # Reset all dropdowns to placeholder state
        self._ResetComboBox(self.CategoryComboBox, 0)
        self._ResetComboBox(self.SubjectComboBox, 1)
        self._ResetComboBox(self.BookComboBox, 2)
        self._ClearSearch()
    
    def GetCurrentFilterState(self) -> dict:
        """
        Get current filter state for external use.
        
        Returns:
            Dictionary with current filter values
        """
        return {
            'Category': self.CategoryComboBox.currentText() if self.CategoryComboBox else "",
            'Subject': self.SubjectComboBox.currentText() if self.SubjectComboBox else "",
            'Book': self.BookComboBox.currentText() if self.BookComboBox else "",
            'SearchTerm': self.SearchLineEdit.text() if self.SearchLineEdit else ""
        }
