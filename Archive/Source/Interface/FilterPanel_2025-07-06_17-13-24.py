# File: FilterPanel.py
# Path: Source/Interface/FilterPanel.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-06
# Last Modified: 2025-07-06  11:26AM
"""
Description: Fixed Filter Panel with Improved Contrast
Enhanced sidebar with black text on light areas for better readability.
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QLineEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon

from Source.Core.BookService import BookService


class FilterPanel(QFrame):
    """
    Fixed filter panel with improved contrast and styling.
    
    Fixes applied:
    - Enhanced contrast for light purple areas
    - Black text on light backgrounds for readability
    - Better dropdown styling
    - Improved icon loading
    """
    
    # Signal emitted when filters change
    FiltersChanged = Signal(dict)
    
    def __init__(self, BookService: BookService):
        super().__init__()
        
        self.Logger = logging.getLogger(__name__)
        self.BookService = BookService
        
        # Current filter state
        self.CurrentFilters = {
            "Category": "",
            "Subject": "",
            "SearchText": ""
        }
        
        # UI Components
        self.CategoryCombo: Optional[QComboBox] = None
        self.SubjectCombo: Optional[QComboBox] = None
        self.SearchBox: Optional[QLineEdit] = None
        
        # Initialize UI
        self._SetupUI()
        self._LoadFilterData()
        self._ConnectSignals()
        
        self.Logger.info("Filter panel initialized with enhanced contrast")
    
    def _SetupUI(self) -> None:
        """Setup the filter panel user interface with improved styling"""
        # Set object name for CSS targeting
        self.setObjectName("FilterPanel")
        
        # ✅ Fixed: Enhanced frame styling for better contrast
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setLineWidth(2)
        
        # Create main layout
        MainLayout = QVBoxLayout(self)
        MainLayout.setContentsMargins(15, 15, 15, 15)
        MainLayout.setSpacing(15)
        
        # ✅ Create header with improved styling
        self._CreateHeader(MainLayout)
        
        # ✅ Create filter sections with enhanced contrast
        self._CreateCategorySection(MainLayout)
        self._CreateSubjectSection(MainLayout)
        self._CreateSearchSection(MainLayout)
        
        # Add flexible spacer
        MainLayout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )
        
        # ✅ Apply enhanced local styling
        self._ApplyLocalStyling()
    
    def _CreateHeader(self, Layout: QVBoxLayout) -> None:
        """Create the header section with enhanced styling"""
        # Header frame with better contrast
        HeaderFrame = QFrame()
        HeaderFrame.setFrameStyle(QFrame.Box)
        HeaderFrame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.15);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        HeaderLayout = QVBoxLayout(HeaderFrame)
        HeaderLayout.setContentsMargins(10, 10, 10, 10)
        
        # ✅ Title with better contrast
        TitleLabel = QLabel("--- Options ---")
        TitleLabel.setAlignment(Qt.AlignCenter)
        TitleLabel.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 18px;
                font-weight: bold;
                background-color: transparent;
                border: none;
                padding: 5px;
            }
        """)
        HeaderLayout.addWidget(TitleLabel)
        
        Layout.addWidget(HeaderFrame)
    
    def _CreateCategorySection(self, Layout: QVBoxLayout) -> None:
        """Create category filter section with enhanced contrast"""
        # ✅ Section frame with light background for contrast
        SectionFrame = QFrame()
        SectionFrame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.4);
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
        SectionLayout = QVBoxLayout(SectionFrame)
        SectionLayout.setContentsMargins(10, 10, 10, 10)
        SectionLayout.setSpacing(8)
        
        # ✅ Label with black text for light background
        CategoryLabel = QLabel("Category:")
        CategoryLabel.setStyleSheet("""
            QLabel {
                color: #000000;  /* Black text for light background */
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
                border: none;
                padding: 2px;
            }
        """)
        SectionLayout.addWidget(CategoryLabel)
        
        # ✅ ComboBox with enhanced styling
        self.CategoryCombo = QComboBox()
        self.CategoryCombo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.95);
                color: #000000;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
                font-weight: bold;
                min-height: 20px;
            }
            
            QComboBox:hover {
                border: 2px solid #FFC107;
                background-color: #FFFFFF;
            }
            
            QComboBox::drop-down {
                border: none;
                background-color: transparent;
                width: 25px;
            }
            
            QComboBox::down-arrow {
                image: url(Assets/arrow.png);
                width: 14px;
                height: 14px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #2E3B4E;
                color: #FFFFFF;
                selection-background-color: #4CAF50;
                border: 2px solid #4CAF50;
                border-radius: 5px;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 8px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #4CAF50;
                color: #FFFFFF;
            }
        """)
        SectionLayout.addWidget(self.CategoryCombo)
        
        Layout.addWidget(SectionFrame)
    
    def _CreateSubjectSection(self, Layout: QVBoxLayout) -> None:
        """Create subject filter section with enhanced contrast"""
        # ✅ Section frame with light background
        SectionFrame = QFrame()
        SectionFrame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.4);
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
        SectionLayout = QVBoxLayout(SectionFrame)
        SectionLayout.setContentsMargins(10, 10, 10, 10)
        SectionLayout.setSpacing(8)
        
        # ✅ Label with black text
        SubjectLabel = QLabel("Subject:")
        SubjectLabel.setStyleSheet("""
            QLabel {
                color: #000000;  /* Black text for light background */
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
                border: none;
                padding: 2px;
            }
        """)
        SectionLayout.addWidget(SubjectLabel)
        
        # ✅ ComboBox with enhanced styling
        self.SubjectCombo = QComboBox()
        self.SubjectCombo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.95);
                color: #000000;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
                font-weight: bold;
                min-height: 20px;
            }
            
            QComboBox:hover {
                border: 2px solid #FFC107;
                background-color: #FFFFFF;
            }
            
            QComboBox::drop-down {
                border: none;
                background-color: transparent;
                width: 25px;
            }
            
            QComboBox::down-arrow {
                image: url(Assets/arrow.png);
                width: 14px;
                height: 14px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #2E3B4E;
                color: #FFFFFF;
                selection-background-color: #4CAF50;
                border: 2px solid #4CAF50;
                border-radius: 5px;
            }
            
            QComboBox QAbstractItemView::item {
                padding: 8px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #4CAF50;
                color: #FFFFFF;
            }
        """)
        SectionLayout.addWidget(self.SubjectCombo)
        
        Layout.addWidget(SectionFrame)
    
    def _CreateSearchSection(self, Layout: QVBoxLayout) -> None:
        """Create search section with enhanced contrast"""
        # ✅ Section frame with light background
        SectionFrame = QFrame()
        SectionFrame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.4);
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
        SectionLayout = QVBoxLayout(SectionFrame)
        SectionLayout.setContentsMargins(10, 10, 10, 10)
        SectionLayout.setSpacing(8)
        
        # ✅ Label with black text
        SearchLabel = QLabel("Search:")
        SearchLabel.setStyleSheet("""
            QLabel {
                color: #000000;  /* Black text for light background */
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
                border: none;
                padding: 2px;
            }
        """)
        SectionLayout.addWidget(SearchLabel)
        
        # ✅ Search box with enhanced styling
        self.SearchBox = QLineEdit()
        self.SearchBox.setPlaceholderText("Type Something Here")
        self.SearchBox.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.95);
                color: #000000;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                padding: 10px;
                font-size: 13px;
                min-height: 20px;
            }
            
            QLineEdit:hover {
                border: 2px solid #FFC107;
                background-color: #FFFFFF;
            }
            
            QLineEdit:focus {
                border: 2px solid #FFC107;
                background-color: #FFFFFF;
                outline: none;
            }
            
            QLineEdit::placeholder {
                color: #666666;
                font-style: italic;
            }
        """)
        SectionLayout.addWidget(self.SearchBox)
        
        Layout.addWidget(SectionFrame)
    
    def _ApplyLocalStyling(self) -> None:
        """Apply enhanced local styling to the filter panel"""
        self.setStyleSheet("""
            QFrame#FilterPanel {
                background-color: rgba(255, 255, 255, 0.05);
                border-right: 3px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                margin: 5px;
            }
        """)
    
    def _LoadFilterData(self) -> None:
        """Load categories and subjects from the database"""
        try:
            if self.BookService:
                # Load categories
                Categories = self.BookService.GetAllCategories()
                self.CategoryCombo.addItem("All Categories")
                for Category in Categories:
                    self.CategoryCombo.addItem(Category)
                
                # Load subjects
                Subjects = self.BookService.GetAllSubjects()
                self.SubjectCombo.addItem("All Subjects")
                for Subject in Subjects:
                    self.SubjectCombo.addItem(Subject)
                
                self.Logger.info(f"Loaded {len(Categories)} categories and {len(Subjects)} subjects")
            
        except Exception as Error:
            self.Logger.error(f"Failed to load filter data: {Error}")
    
    def _ConnectSignals(self) -> None:
        """Connect UI signals to handlers"""
        try:
            # Connect combo box changes
            self.CategoryCombo.currentTextChanged.connect(self._OnCategoryChanged)
            self.SubjectCombo.currentTextChanged.connect(self._OnSubjectChanged)
            
            # Connect search box with delay for better performance
            self.SearchBox.textChanged.connect(self._OnSearchTextChanged)
            
            self.Logger.info("Filter panel signals connected")
            
        except Exception as Error:
            self.Logger.error(f"Failed to connect signals: {Error}")
    
    def _OnCategoryChanged(self, CategoryText: str) -> None:
        """Handle category selection change"""
        try:
            self.CurrentFilters["Category"] = CategoryText if CategoryText != "All Categories" else ""
            self._EmitFiltersChanged()
            
        except Exception as Error:
            self.Logger.error(f"Failed to handle category change: {Error}")
    
    def _OnSubjectChanged(self, SubjectText: str) -> None:
        """Handle subject selection change"""
        try:
            self.CurrentFilters["Subject"] = SubjectText if SubjectText != "All Subjects" else ""
            self._EmitFiltersChanged()
            
        except Exception as Error:
            self.Logger.error(f"Failed to handle subject change: {Error}")
    
    def _OnSearchTextChanged(self, SearchText: str) -> None:
        """Handle search text change with debouncing"""
        try:
            self.CurrentFilters["SearchText"] = SearchText.strip()
            
            # Use timer for debouncing to avoid too many updates while typing
            if hasattr(self, '_SearchTimer'):
                self._SearchTimer.stop()
            
            self._SearchTimer = QTimer()
            self._SearchTimer.timeout.connect(self._EmitFiltersChanged)
            self._SearchTimer.setSingleShot(True)
            self._SearchTimer.start(300)  # 300ms delay
            
        except Exception as Error:
            self.Logger.error(f"Failed to handle search text change: {Error}")
    
    def _EmitFiltersChanged(self) -> None:
        """Emit the filters changed signal"""
        try:
            self.FiltersChanged.emit(self.CurrentFilters.copy())
            self.Logger.debug(f"Filters changed: {self.CurrentFilters}")
            
        except Exception as Error:
            self.Logger.error(f"Failed to emit filters changed: {Error}")
    
    def ResetFilters(self) -> None:
        """Reset all filters to default values"""
        try:
            self.CategoryCombo.setCurrentIndex(0)  # "All Categories"
            self.SubjectCombo.setCurrentIndex(0)   # "All Subjects"  
            self.SearchBox.clear()
            
            self.CurrentFilters = {
                "Category": "",
                "Subject": "",
                "SearchText": ""
            }
            
            self._EmitFiltersChanged()
            self.Logger.info("Filters reset to defaults")
            
        except Exception as Error:
            self.Logger.error(f"Failed to reset filters: {Error}")
    
    def GetCurrentFilters(self) -> Dict[str, str]:
        """Get the current filter values"""
        return self.CurrentFilters.copy()