# File: FilterPanel.py
# Path: Source/Interface/FilterPanel.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  01:34PM
"""
Description: Enhanced Filter Panel with Category-Filtered Subjects and Icons
Features category-filtered subjects, flat label backgrounds, and Assets/ icons.
"""

import logging
from typing import Optional, List
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QComboBox, 
    QLabel, QFrame, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap

from Source.Core.BookService import BookService
from Source.Data.DatabaseModels import SearchCriteria


class FilterPanel(QWidget):
    """
    Enhanced filter panel with category-filtered subjects and icons.
    """
    
    # Signals
    SearchRequested = Signal(object)  # SearchCriteria object
    FilterChanged = Signal(object)    # SearchCriteria object  
    BookSelected = Signal(str)        # Book title (for compatibility)
    
    def __init__(self, BookServiceInstance: BookService, Parent=None):
        """Initialize enhanced filter panel."""
        super().__init__(Parent)
        
        self.BookService = BookServiceInstance
        self.Logger = logging.getLogger(__name__)
        
        # UI Components
        self.SearchLineEdit: Optional[QLineEdit] = None
        self.CategoryComboBox: Optional[QComboBox] = None
        self.SubjectComboBox: Optional[QComboBox] = None
        
        # Data storage
        self.AllCategories: List = []
        self.AllSubjects: List = []
        self.CategorySubjectsMap: dict = {}  # category_id -> [subjects]
        
        # Search timer
        self.SearchTimer = QTimer()
        self.SearchTimer.setSingleShot(True)
        self.SearchTimer.timeout.connect(self._PerformSearch)
        
        # Setup
        self._SetupUI()
        self._LoadInitialData()
        self._ConnectSignals()
        
        self.Logger.info("Enhanced FilterPanel initialized")
    
    def _SetupUI(self) -> None:
        """Create enhanced UI with flat labels and icons"""
        # Main layout
        Layout = QVBoxLayout(self)
        Layout.setContentsMargins(15, 15, 15, 15)
        Layout.setSpacing(15)
        
        # Title with icon
        TitleLayout = QHBoxLayout()
        
        # Title icon
        TitleIcon = QLabel()
        IconPath = Path("Assets/icon.png")
        if IconPath.exists():
            Pixmap = QPixmap(str(IconPath))
            ScaledPixmap = Pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            TitleIcon.setPixmap(ScaledPixmap)
        else:
            TitleIcon.setText("📚")
        
        TitleLabel = QLabel(" Options")
        TitleFont = QFont()
        TitleFont.setPointSize(14)
        TitleFont.setBold(True)
        TitleLabel.setFont(TitleFont)
        
        TitleLayout.addWidget(TitleIcon)
        TitleLayout.addWidget(TitleLabel)
        TitleLayout.addStretch()
        
        Layout.addLayout(TitleLayout)
        
        # Separator
        Separator = QFrame()
        Separator.setFrameShape(QFrame.HLine)
        Layout.addWidget(Separator)
        
        # Category section with icon
        CategoryLayout = QHBoxLayout()
        CategoryIconLabel = QLabel()
        CategoryIconLabel.setText("🗂️")  # Folder icon
        CategoryIconLabel.setFixedWidth(20)
        
        CategoryTextLabel = QLabel("Category:")
        CategoryTextLabel.setStyleSheet("""
            QLabel {
                background-color: rgba(50, 100, 150, 180);
                color: #ffffff;
                padding: 4px 8px;
                border-radius: 3px;
                font-weight: bold;
            }
        """)
        
        CategoryLayout.addWidget(CategoryIconLabel)
        CategoryLayout.addWidget(CategoryTextLabel)
        CategoryLayout.addStretch()
        Layout.addLayout(CategoryLayout)
        
        self.CategoryComboBox = QComboBox()
        self.CategoryComboBox.addItem("All Categories")
        Layout.addWidget(self.CategoryComboBox)
        
        # Subject section with icon  
        SubjectLayout = QHBoxLayout()
        SubjectIconLabel = QLabel()
        SubjectIconLabel.setText("📋")  # List icon
        SubjectIconLabel.setFixedWidth(20)
        
        SubjectTextLabel = QLabel("Subject:")
        SubjectTextLabel.setStyleSheet("""
            QLabel {
                background-color: rgba(50, 100, 150, 180);
                color: #ffffff;
                padding: 4px 8px;
                border-radius: 3px;
                font-weight: bold;
            }
        """)
        
        SubjectLayout.addWidget(SubjectIconLabel)
        SubjectLayout.addWidget(SubjectTextLabel)
        SubjectLayout.addStretch()
        Layout.addLayout(SubjectLayout)
        
        self.SubjectComboBox = QComboBox()
        self.SubjectComboBox.addItem("All Subjects")
        Layout.addWidget(self.SubjectComboBox)
        
        # Search section with icon
        SearchLayout = QHBoxLayout()
        SearchIconLabel = QLabel()
        SearchIconLabel.setText("🔍")  # Search icon
        SearchIconLabel.setFixedWidth(20)
        
        SearchTextLabel = QLabel("Search:")
        SearchTextLabel.setStyleSheet("""
            QLabel {
                background-color: rgba(50, 100, 150, 180);
                color: #ffffff;
                padding: 4px 8px;
                border-radius: 3px;
                font-weight: bold;
            }
        """)
        
        SearchLayout.addWidget(SearchIconLabel)
        SearchLayout.addWidget(SearchTextLabel)
        SearchLayout.addStretch()
        Layout.addLayout(SearchLayout)
        
        self.SearchLineEdit = QLineEdit()
        self.SearchLineEdit.setPlaceholderText("Type Something Here")
        Layout.addWidget(self.SearchLineEdit)
        
        # Add stretch
        Layout.addStretch()
        
        # Set fixed width and apply enhanced styling
        self.setFixedWidth(320)
        self._ApplyEnhancedStyling()
    
    def _ApplyEnhancedStyling(self) -> None:
        """Apply enhanced styling with flat backgrounds and custom dropdown arrows"""
        self.setStyleSheet("""
            /* Combo box styling with custom arrow */
            QComboBox {
                padding: 8px;
                border: 2px solid #555;
                border-radius: 4px;
                background-color: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                font-size: 12px;
                min-height: 20px;
            }
            
            QComboBox:hover {
                border-color: #0078d4;
                background-color: rgba(255, 255, 255, 0.15);
            }
            
            QComboBox:focus {
                border-color: #ffffff;
                background-color: rgba(255, 255, 255, 0.2);
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QComboBox::down-arrow {
                image: url(Assets/arrow.png);
                width: 12px;
                height: 12px;
            }
            
            QComboBox QAbstractItemView {
                border: 2px solid #555;
                border-radius: 4px;
                background-color: rgba(20, 40, 60, 240);
                color: #ffffff;
                selection-background-color: #ff4444;
                selection-color: #ffffff;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #ff4444;
                color: #ffffff;
            }
            
            /* Search box styling */
            QLineEdit {
                padding: 8px;
                border: 2px solid #555;
                border-radius: 4px;
                background-color: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                font-size: 12px;
            }
            
            QLineEdit:focus {
                border-color: #ffffff;
                background-color: rgba(255, 255, 255, 0.2);
            }
            
            QLineEdit::placeholder {
                color: #cccccc;
                font-style: italic;
            }
        """)
    
    def _LoadInitialData(self) -> None:
        """Load categories and build category->subjects mapping"""
        try:
            # Load all categories
            self.AllCategories = self.BookService.Database.GetAllCategories()
            for Category in self.AllCategories:
                self.CategoryComboBox.addItem(Category.Name)
            
            # Load all subjects and build category mapping
            self.AllSubjects = self.BookService.Database.GetAllSubjects()
            
            # Build category ID to subjects mapping
            self.CategorySubjectsMap = {}
            for Subject in self.AllSubjects:
                CategoryId = getattr(Subject, 'CategoryId', None)
                if CategoryId:
                    if CategoryId not in self.CategorySubjectsMap:
                        self.CategorySubjectsMap[CategoryId] = []
                    self.CategorySubjectsMap[CategoryId].append(Subject)
            
            # Initially load all subjects
            self._LoadAllSubjects()
            
            self.Logger.info(f"Loaded {len(self.AllCategories)} categories, {len(self.AllSubjects)} subjects")
            
        except Exception as Error:
            self.Logger.error(f"Data loading error: {Error}")
            # Fallback data
            self.CategoryComboBox.addItem("Programming Languages")
            self.CategoryComboBox.addItem("Computer Science")
            self.SubjectComboBox.addItem("Python")
            self.SubjectComboBox.addItem("Programming")
    
    def _LoadAllSubjects(self) -> None:
        """Load all subjects into subjects dropdown"""
        self.SubjectComboBox.clear()
        self.SubjectComboBox.addItem("All Subjects")
        
        for Subject in self.AllSubjects:
            self.SubjectComboBox.addItem(Subject.Name)
    
    def _LoadSubjectsForCategory(self, CategoryName: str) -> None:
        """Load subjects filtered by category"""
        self.SubjectComboBox.clear()
        self.SubjectComboBox.addItem("All Subjects")
        
        if CategoryName == "All Categories":
            # Load all subjects
            self._LoadAllSubjects()
            return
        
        # Find category ID
        CategoryId = None
        for Category in self.AllCategories:
            if Category.Name == CategoryName:
                CategoryId = Category.Id
                break
        
        if CategoryId and CategoryId in self.CategorySubjectsMap:
            # Load subjects for this category
            CategorySubjects = self.CategorySubjectsMap[CategoryId]
            for Subject in CategorySubjects:
                self.SubjectComboBox.addItem(Subject.Name)
            
            self.Logger.debug(f"Loaded {len(CategorySubjects)} subjects for category '{CategoryName}'")
        else:
            self.Logger.debug(f"No subjects found for category '{CategoryName}'")
    
    def _ConnectSignals(self) -> None:
        """Connect UI signals with enhanced category->subject filtering"""
        # Search with debouncing
        self.SearchLineEdit.textChanged.connect(self._OnSearchTextChanged)
        
        # Category changes should filter subjects
        self.CategoryComboBox.currentTextChanged.connect(self._OnCategoryChanged)
        
        # Subject changes 
        self.SubjectComboBox.currentTextChanged.connect(self._OnSubjectChanged)
    
    def _OnCategoryChanged(self, CategoryText: str) -> None:
        """Handle category changes - filter subjects and clear search"""
        # Filter subjects by selected category
        self._LoadSubjectsForCategory(CategoryText)
        
        # Clear search when category changes
        if CategoryText != "All Categories":
            self.SearchLineEdit.clear()
        
        # Emit filter change
        self._EmitFilterChange()
    
    def _OnSubjectChanged(self, SubjectText: str) -> None:
        """Handle subject changes - clear search"""
        # Clear search when subject is selected
        if SubjectText != "All Subjects":
            self.SearchLineEdit.clear()
        
        # Emit filter change
        self._EmitFilterChange()
    
    def _OnSearchTextChanged(self, SearchText: str) -> None:
        """Handle search with category/subject clearing"""
        self.SearchTimer.stop()
        
        if len(SearchText) > 1:
            # Clear dropdowns when searching
            self.CategoryComboBox.setCurrentText("All Categories")
            self.SubjectComboBox.setCurrentText("All Subjects")
            self.SearchTimer.start(400)
        elif len(SearchText) == 0:
            self._PerformSearch()
    
    def _PerformSearch(self) -> None:
        """Perform search"""
        SearchText = self.SearchLineEdit.text().strip()
        Criteria = SearchCriteria()
        if SearchText:
            Criteria.SearchTerm = SearchText
        self.SearchRequested.emit(Criteria)
    
    def _EmitFilterChange(self) -> None:
        """Emit filter change with current selections"""
        Category = self.CategoryComboBox.currentText()
        Subject = self.SubjectComboBox.currentText()
        
        Criteria = SearchCriteria()
        if Category != "All Categories":
            Criteria.Categories = [Category]
        if Subject != "All Subjects":
            Criteria.Subjects = [Subject]
        
        # Only emit if we have actual filters
        if not Criteria.IsEmpty():
            self.FilterChanged.emit(Criteria)
        
        self.Logger.debug(f"Filter changed: Category='{Category}', Subject='{Subject}'")
    
    def GetCurrentCriteria(self) -> SearchCriteria:
        """Get current search criteria"""
        Criteria = SearchCriteria()
        
        SearchText = self.SearchLineEdit.text().strip()
        if SearchText:
            Criteria.SearchTerm = SearchText
        
        Category = self.CategoryComboBox.currentText()
        if Category != "All Categories":
            Criteria.Categories = [Category]
        
        Subject = self.SubjectComboBox.currentText()
        if Subject != "All Subjects":
            Criteria.Subjects = [Subject]
        
        return Criteria
