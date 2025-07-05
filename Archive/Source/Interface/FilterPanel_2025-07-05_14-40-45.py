# File: FilterPanel.py
# Path: Source/Interface/FilterPanel.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  01:34PM
"""
Description: Filter Panel for Anderson's Library - Simple Working Version
Provides search and filter controls using standard Qt design.
"""

import logging
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QComboBox, 
    QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

from Source.Core.BookService import BookService


class FilterPanel(QWidget):
    """
    Simple filter panel with search and category selection.
    Emits signals when filters change to update the book grid.
    """
    
    # Signals for communication with BookGrid
    SearchRequested = Signal(str)  # Search term
    FilterChanged = Signal(str, str)  # Category, Subject
    
    def __init__(self, BookServiceInstance: BookService, Parent=None):
        """
        Initialize filter panel.
        
        Args:
            BookServiceInstance: BookService for data operations
            Parent: Parent widget (optional)
        """
        super().__init__(Parent)
        
        # Store service reference
        self.BookService = BookServiceInstance
        self.Logger = logging.getLogger(__name__)
        
        # UI Components
        self.SearchLineEdit: Optional[QLineEdit] = None
        self.CategoryComboBox: Optional[QComboBox] = None
        self.SubjectComboBox: Optional[QComboBox] = None
        
        # Setup UI
        self._SetupUI()
        self._LoadInitialData()
        self._ConnectSignals()
        
        self.Logger.info("FilterPanel initialized")
    
    def _SetupUI(self) -> None:
        """Create the user interface"""
        # Main layout
        Layout = QVBoxLayout(self)
        Layout.setContentsMargins(15, 15, 15, 15)
        Layout.setSpacing(10)
        
        # Title
        TitleLabel = QLabel("📚 Options")
        TitleFont = QFont()
        TitleFont.setPointSize(14)
        TitleFont.setBold(True)
        TitleLabel.setFont(TitleFont)
        TitleLabel.setAlignment(Qt.AlignCenter)
        Layout.addWidget(TitleLabel)
        
        # Separator
        Separator = QFrame()
        Separator.setFrameShape(QFrame.HLine)
        Layout.addWidget(Separator)
        
        # Category selection
        Layout.addWidget(QLabel("Category:"))
        self.CategoryComboBox = QComboBox()
        self.CategoryComboBox.addItem("All Categories")
        Layout.addWidget(self.CategoryComboBox)
        
        # Subject selection  
        Layout.addWidget(QLabel("Subject:"))
        self.SubjectComboBox = QComboBox()
        self.SubjectComboBox.addItem("All Subjects")
        Layout.addWidget(self.SubjectComboBox)
        
        # Search
        Layout.addWidget(QLabel("Search:"))
        self.SearchLineEdit = QLineEdit()
        self.SearchLineEdit.setPlaceholderText("Type Something Here")
        Layout.addWidget(self.SearchLineEdit)
        
        # Add stretch to push everything to top
        Layout.addStretch()
        
        # Set fixed width
        self.setFixedWidth(320)
    
    def _LoadInitialData(self) -> None:
        """Load categories and subjects from database"""
        try:
            # Get categories from BookService
            Categories = self.BookService.GetCategories()
            for Category in Categories:
                self.CategoryComboBox.addItem(Category)
            
            # Get subjects from BookService  
            Subjects = self.BookService.GetSubjects()
            for Subject in Subjects:
                self.SubjectComboBox.addItem(Subject)
                
            self.Logger.info("Filter data loaded successfully")
            
        except Exception as Error:
            self.Logger.error(f"Failed to load filter data: {Error}")
    
    def _ConnectSignals(self) -> None:
        """Connect UI signals to handlers"""
        # Search as user types
        self.SearchLineEdit.textChanged.connect(self._OnSearchChanged)
        
        # Filter changes
        self.CategoryComboBox.currentTextChanged.connect(self._OnFilterChanged)
        self.SubjectComboBox.currentTextChanged.connect(self._OnFilterChanged)
    
    def _OnSearchChanged(self, SearchText: str) -> None:
        """Handle search text changes"""
        # Emit search signal
        self.SearchRequested.emit(SearchText)
    
    def _OnFilterChanged(self) -> None:
        """Handle filter changes"""
        Category = self.CategoryComboBox.currentText()
        Subject = self.SubjectComboBox.currentText()
        
        # Convert "All" selections to empty strings
        if Category == "All Categories":
            Category = ""
        if Subject == "All Subjects":
            Subject = ""
        
        # Emit filter change signal
        self.FilterChanged.emit(Category, Subject)
