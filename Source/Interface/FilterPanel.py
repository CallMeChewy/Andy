# File: FilterPanel.py
# Path: Source/Interface/FilterPanel.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  04:12PM
"""
Description: Filter Panel Component for Anderson's Library
Provides the left sidebar interface for searching and filtering books.
Includes text search, category filters, author filters, and advanced options.
"""

import logging
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QComboBox, QCheckBox,
                               QGroupBox, QScrollArea, QButtonGroup, QFrame,
                               QSlider, QSpinBox, QDateEdit, QListWidget,
                               QListWidgetItem, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QDate, QTimer
from PySide6.QtGui import QFont, QPalette, QIcon
from typing import List, Dict, Optional, Callable
from ..Data.DatabaseModels import SearchCriteria, CategoryInfo


class FilterPanel(QWidget):
    """
    Left sidebar panel providing search and filter functionality.
    Emits signals when search criteria changes to trigger book grid updates.
    """
    
    # Signals
    SearchRequested = Signal(object)  # SearchCriteria
    FiltersChanged = Signal(object)   # SearchCriteria
    ClearRequested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.SetupUI()
        self.SetupConnections()
        self.LoadInitialData()
        
        # Search debouncing
        self.SearchTimer = QTimer()
        self.SearchTimer.setSingleShot(True)
        self.SearchTimer.timeout.connect(self.OnSearchTimerTimeout)
        
        # Author filter debouncing for editable ComboBox
        self.AuthorTimer = QTimer()
        self.AuthorTimer.setSingleShot(True)
        self.AuthorTimer.timeout.connect(self.OnAuthorTimerTimeout)
        
        # Current filter state
        self.CurrentCriteria = SearchCriteria()
        
        logging.info("FilterPanel initialized")
    
    def SetupUI(self):
        """Create and arrange the filter panel interface"""
        self.setFixedWidth(320)
        self.setMinimumHeight(500)
        
        # Main layout
        MainLayout = QVBoxLayout(self)
        MainLayout.setContentsMargins(10, 10, 10, 10)
        MainLayout.setSpacing(15)
        
        # Header
        self.CreateHeaderSection(MainLayout)
        
        # Search section
        self.CreateSearchSection(MainLayout)
        
        # Quick filters
        self.CreateQuickFiltersSection(MainLayout)
        
        # Category filters
        self.CreateCategorySection(MainLayout)
        
        # Author filters  
        self.CreateAuthorSection(MainLayout)
        
        # Advanced filters
        self.CreateAdvancedSection(MainLayout)
        
        # Action buttons
        self.CreateActionSection(MainLayout)
        
        # Stretch to push everything to top
        MainLayout.addStretch()
        
        # Apply styling
        self.ApplyStyles()
    
    def CreateHeaderSection(self, Layout: QVBoxLayout):
        """Create the header with title and stats"""
        HeaderFrame = QFrame()
        HeaderLayout = QVBoxLayout(HeaderFrame)
        HeaderLayout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        TitleLabel = QLabel("📚 Library Filters")
        TitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        TitleFont = QFont()
        TitleFont.setPointSize(14)
        TitleFont.setBold(True)
        TitleLabel.setFont(TitleFont)
        HeaderLayout.addWidget(TitleLabel)
        
        # Stats label
        self.StatsLabel = QLabel("Loading...")
        self.StatsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.StatsLabel.setStyleSheet("color: #666; font-size: 11px;")
        HeaderLayout.addWidget(self.StatsLabel)
        
        Layout.addWidget(HeaderFrame)
    
    def CreateSearchSection(self, Layout: QVBoxLayout):
        """Create the text search section"""
        SearchGroup = QGroupBox("🔍 Search")
        SearchLayout = QVBoxLayout(SearchGroup)
        
        # Main search box
        self.SearchEdit = QLineEdit()
        self.SearchEdit.setPlaceholderText("Search titles, authors, subjects...")
        self.SearchEdit.setClearButtonEnabled(True)
        SearchLayout.addWidget(self.SearchEdit)
        
        # Search field options
        FieldsFrame = QFrame()
        FieldsLayout = QVBoxLayout(FieldsFrame)
        FieldsLayout.setContentsMargins(0, 0, 0, 0)
        FieldsLayout.setSpacing(5)
        
        self.SearchTitleCheck = QCheckBox("Search in titles")
        self.SearchTitleCheck.setChecked(True)
        FieldsLayout.addWidget(self.SearchTitleCheck)
        
        self.SearchAuthorCheck = QCheckBox("Search in authors")
        self.SearchAuthorCheck.setChecked(True)
        FieldsLayout.addWidget(self.SearchAuthorCheck)
        
        self.SearchSubjectCheck = QCheckBox("Search in subjects")
        self.SearchSubjectCheck.setChecked(True)
        FieldsLayout.addWidget(self.SearchSubjectCheck)
        
        self.SearchKeywordsCheck = QCheckBox("Search in keywords")
        self.SearchKeywordsCheck.setChecked(True)
        FieldsLayout.addWidget(self.SearchKeywordsCheck)
        
        self.SearchDescriptionCheck = QCheckBox("Search in descriptions")
        self.SearchDescriptionCheck.setChecked(False)
        FieldsLayout.addWidget(self.SearchDescriptionCheck)
        
        SearchLayout.addWidget(FieldsFrame)
        Layout.addWidget(SearchGroup)
    
    def CreateQuickFiltersSection(self, Layout: QVBoxLayout):
        """Create quick filter buttons"""
        QuickGroup = QGroupBox("⚡ Quick Filters")
        QuickLayout = QVBoxLayout(QuickGroup)
        
        # Row 1
        Row1Layout = QHBoxLayout()
        self.RecentlyAddedBtn = QPushButton("Recent")
        self.RecentlyAddedBtn.setCheckable(True)
        self.HighRatedBtn = QPushButton("★★★★+")
        self.HighRatedBtn.setCheckable(True)
        Row1Layout.addWidget(self.RecentlyAddedBtn)
        Row1Layout.addWidget(self.HighRatedBtn)
        QuickLayout.addLayout(Row1Layout)
        
        # Row 2
        Row2Layout = QHBoxLayout()
        self.UnreadBtn = QPushButton("Unread")
        self.UnreadBtn.setCheckable(True)
        self.LargeFilesBtn = QPushButton("Large Files")
        self.LargeFilesBtn.setCheckable(True)
        Row2Layout.addWidget(self.UnreadBtn)
        Row2Layout.addWidget(self.LargeFilesBtn)
        QuickLayout.addLayout(Row2Layout)
        
        Layout.addWidget(QuickGroup)
    
    def CreateCategorySection(self, Layout: QVBoxLayout):
        """Create category filter section"""
        CategoryGroup = QGroupBox("📂 Categories")
        CategoryLayout = QVBoxLayout(CategoryGroup)
        
        # Category dropdown
        self.CategoryCombo = QComboBox()
        self.CategoryCombo.addItem("All Categories", "")
        CategoryLayout.addWidget(self.CategoryCombo)
        
        # Category list for multiple selection
        self.CategoryList = QListWidget()
        self.CategoryList.setMaximumHeight(120)
        self.CategoryList.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        CategoryLayout.addWidget(self.CategoryList)
        
        # Show/hide multiple selection
        self.MultipleCategoriesCheck = QCheckBox("Multiple selection")
        self.MultipleCategoriesCheck.toggled.connect(self.OnMultipleCategoriesToggled)
        CategoryLayout.addWidget(self.MultipleCategoriesCheck)
        
        # Initially hide the list
        self.CategoryList.hide()
        
        Layout.addWidget(CategoryGroup)
    
    def CreateAuthorSection(self, Layout: QVBoxLayout):
        """Create author filter section"""
        AuthorGroup = QGroupBox("👤 Authors")
        AuthorLayout = QVBoxLayout(AuthorGroup)
        
        # Author dropdown
        self.AuthorCombo = QComboBox()
        self.AuthorCombo.addItem("All Authors", "")
        self.AuthorCombo.setEditable(True)
        self.AuthorCombo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        AuthorLayout.addWidget(self.AuthorCombo)
        
        # Popular authors quick buttons
        self.PopularAuthorsFrame = QFrame()
        self.PopularAuthorsLayout = QVBoxLayout(self.PopularAuthorsFrame)
        self.PopularAuthorsLayout.setContentsMargins(0, 0, 0, 0)
        AuthorLayout.addWidget(self.PopularAuthorsFrame)
        
        Layout.addWidget(AuthorGroup)
    
    def CreateAdvancedSection(self, Layout: QVBoxLayout):
        """Create advanced filters section"""
        AdvancedGroup = QGroupBox("⚙️ Advanced")
        AdvancedLayout = QVBoxLayout(AdvancedGroup)
        
        # Make it collapsible
        AdvancedGroup.setCheckable(True)
        AdvancedGroup.setChecked(False)
        
        # Rating filter
        RatingFrame = QFrame()
        RatingLayout = QHBoxLayout(RatingFrame)
        RatingLayout.addWidget(QLabel("Rating:"))
        
        self.MinRatingSlider = QSlider(Qt.Orientation.Horizontal)
        self.MinRatingSlider.setRange(0, 5)
        self.MinRatingSlider.setValue(0)
        RatingLayout.addWidget(self.MinRatingSlider)
        
        self.RatingLabel = QLabel("0-5")
        RatingLayout.addWidget(self.RatingLabel)
        AdvancedLayout.addWidget(RatingFrame)
        
        # Page count filter
        PageFrame = QFrame()
        PageLayout = QHBoxLayout(PageFrame)
        PageLayout.addWidget(QLabel("Pages:"))
        
        self.MinPagesSpinBox = QSpinBox()
        self.MinPagesSpinBox.setRange(0, 9999)
        self.MinPagesSpinBox.setSpecialValueText("Any")
        PageLayout.addWidget(self.MinPagesSpinBox)
        
        PageLayout.addWidget(QLabel("to"))
        
        self.MaxPagesSpinBox = QSpinBox()
        self.MaxPagesSpinBox.setRange(0, 9999)
        self.MaxPagesSpinBox.setValue(9999)
        self.MaxPagesSpinBox.setSpecialValueText("Any")
        PageLayout.addWidget(self.MaxPagesSpinBox)
        AdvancedLayout.addWidget(PageFrame)
        
        # Date filter
        DateFrame = QFrame()
        DateLayout = QVBoxLayout(DateFrame)
        DateLayout.addWidget(QLabel("Date Added:"))
        
        DateRangeLayout = QHBoxLayout()
        self.DateFromEdit = QDateEdit()
        self.DateFromEdit.setDate(QDate.currentDate().addYears(-1))
        self.DateFromEdit.setCalendarPopup(True)
        DateRangeLayout.addWidget(self.DateFromEdit)
        
        DateRangeLayout.addWidget(QLabel("to"))
        
        self.DateToEdit = QDateEdit()
        self.DateToEdit.setDate(QDate.currentDate())
        self.DateToEdit.setCalendarPopup(True)
        DateRangeLayout.addWidget(self.DateToEdit)
        
        DateLayout.addLayout(DateRangeLayout)
        
        self.DateFilterCheck = QCheckBox("Enable date filter")
        self.DateFilterCheck.toggled.connect(self.OnDateFilterToggled)
        DateLayout.addWidget(self.DateFilterCheck)
        AdvancedLayout.addWidget(DateFrame)
        
        # File format filter
        FormatFrame = QFrame()
        FormatLayout = QVBoxLayout(FormatFrame)
        FormatLayout.addWidget(QLabel("File Format:"))
        
        self.PdfCheck = QCheckBox("PDF")
        self.PdfCheck.setChecked(True)
        FormatLayout.addWidget(self.PdfCheck)
        
        self.EpubCheck = QCheckBox("EPUB")
        FormatLayout.addWidget(self.EpubCheck)
        
        self.MobiCheck = QCheckBox("MOBI")
        FormatLayout.addWidget(self.MobiCheck)
        AdvancedLayout.addWidget(FormatFrame)
        
        # Initially disable date controls
        self.OnDateFilterToggled(False)
        
        Layout.addWidget(AdvancedGroup)
    
    def CreateActionSection(self, Layout: QVBoxLayout):
        """Create action buttons"""
        ActionFrame = QFrame()
        ActionLayout = QVBoxLayout(ActionFrame)
        ActionLayout.setSpacing(10)
        
        # Search button
        self.SearchButton = QPushButton("🔍 Search")
        self.SearchButton.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        ActionLayout.addWidget(self.SearchButton)
        
        # Clear button
        self.ClearButton = QPushButton("🗑️ Clear All")
        self.ClearButton.setStyleSheet("""
            QPushButton {
                background-color: #FF5722;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #D84315;
            }
        """)
        ActionLayout.addWidget(self.ClearButton)
        
        # Results count
        self.ResultsLabel = QLabel("Ready to search")
        self.ResultsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ResultsLabel.setStyleSheet("color: #666; font-size: 11px; margin-top: 5px;")
        ActionLayout.addWidget(self.ResultsLabel)
        
        Layout.addWidget(ActionFrame)
    
    def SetupConnections(self):
        """Connect signals and slots"""
        # Search text with debouncing
        self.SearchEdit.textChanged.connect(self.OnSearchTextChanged)
        
        # Search field checkboxes
        self.SearchTitleCheck.toggled.connect(self.OnFiltersChanged)
        self.SearchAuthorCheck.toggled.connect(self.OnFiltersChanged)
        self.SearchSubjectCheck.toggled.connect(self.OnFiltersChanged)
        self.SearchKeywordsCheck.toggled.connect(self.OnFiltersChanged)
        self.SearchDescriptionCheck.toggled.connect(self.OnFiltersChanged)
        
        # Quick filters
        self.RecentlyAddedBtn.toggled.connect(self.OnFiltersChanged)
        self.HighRatedBtn.toggled.connect(self.OnFiltersChanged)
        self.UnreadBtn.toggled.connect(self.OnFiltersChanged)
        self.LargeFilesBtn.toggled.connect(self.OnFiltersChanged)
        
        # Category filters
        self.CategoryCombo.currentTextChanged.connect(self.OnFiltersChanged)
        self.CategoryList.itemSelectionChanged.connect(self.OnFiltersChanged)
        
        # Author filter - use both signals for editable ComboBox
        self.AuthorCombo.currentIndexChanged.connect(self.OnFiltersChanged)
        self.AuthorCombo.editTextChanged.connect(self.OnAuthorTextChanged)
        
        # Advanced filters
        self.MinRatingSlider.valueChanged.connect(self.OnRatingChanged)
        self.MinPagesSpinBox.valueChanged.connect(self.OnFiltersChanged)
        self.MaxPagesSpinBox.valueChanged.connect(self.OnFiltersChanged)
        self.DateFromEdit.dateChanged.connect(self.OnFiltersChanged)
        self.DateToEdit.dateChanged.connect(self.OnFiltersChanged)
        self.PdfCheck.toggled.connect(self.OnFiltersChanged)
        self.EpubCheck.toggled.connect(self.OnFiltersChanged)
        self.MobiCheck.toggled.connect(self.OnFiltersChanged)
        
        # Action buttons
        self.SearchButton.clicked.connect(self.OnSearchClicked)
        self.ClearButton.clicked.connect(self.OnClearClicked)
    
    def ApplyStyles(self):
        """Apply consistent styling"""
        # Use CustomWindow inherited styling with minimal overrides
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                margin-top: 10px;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    
    def LoadInitialData(self):
        """Load initial filter data"""
        # This will be called by the main window to populate categories and authors
        pass
    
    def UpdateCategories(self, Categories: List[CategoryInfo]):
        """Update the category filter options"""
        # Clear existing
        self.CategoryCombo.clear()
        self.CategoryList.clear()
        
        # Add "All Categories" option
        self.CategoryCombo.addItem("All Categories", "")
        
        # Add categories
        for Category in Categories:
            DisplayName = Category.GetDisplayName()
            self.CategoryCombo.addItem(DisplayName, Category.Name)
            
            ListItem = QListWidgetItem(DisplayName)
            ListItem.setData(Qt.ItemDataRole.UserRole, Category.Name)
            self.CategoryList.addItem(ListItem)
    
    def UpdateAuthors(self, Authors: List[str]):
        """Update the author filter options"""
        # Clear existing
        self.AuthorCombo.clear()
        
        # Add "All Authors" option
        self.AuthorCombo.addItem("All Authors", "")
        
        # Add authors
        for Author in Authors:
            self.AuthorCombo.addItem(Author, Author)
        
        # Update popular authors buttons
        self.UpdatePopularAuthors(Authors[:6])  # Top 6 authors
    
    def UpdatePopularAuthors(self, Authors: List[str]):
        """Update popular author quick buttons"""
        # Clear existing buttons
        for i in reversed(range(self.PopularAuthorsLayout.count())):
            child = self.PopularAuthorsLayout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        # Add new buttons
        for Author in Authors:
            AuthorBtn = QPushButton(Author)
            AuthorBtn.setCheckable(True)
            AuthorBtn.setMaximumHeight(25)
            AuthorBtn.clicked.connect(lambda checked, a=Author: self.OnPopularAuthorClicked(a))
            self.PopularAuthorsLayout.addWidget(AuthorBtn)
    
    def UpdateStats(self, TotalBooks: int, FilteredBooks: int):
        """Update the stats display"""
        if FilteredBooks == TotalBooks:
            self.StatsLabel.setText(f"{TotalBooks} books total")
        else:
            self.StatsLabel.setText(f"{FilteredBooks} of {TotalBooks} books")
        
        self.ResultsLabel.setText(f"Showing {FilteredBooks} books")
    
    def GetCurrentCriteria(self) -> SearchCriteria:
        """Build and return current search criteria"""
        Criteria = SearchCriteria()
        
        # Text search
        Criteria.SearchText = self.SearchEdit.text().strip()
        Criteria.SearchTitle = self.SearchTitleCheck.isChecked()
        Criteria.SearchAuthor = self.SearchAuthorCheck.isChecked()
        Criteria.SearchSubject = self.SearchSubjectCheck.isChecked()
        Criteria.SearchKeywords = self.SearchKeywordsCheck.isChecked()
        Criteria.SearchDescription = self.SearchDescriptionCheck.isChecked()
        
        # Categories
        if self.MultipleCategoriesCheck.isChecked():
            # Multiple selection from list
            SelectedItems = self.CategoryList.selectedItems()
            Criteria.Categories = [item.data(Qt.ItemDataRole.UserRole) for item in SelectedItems 
                                 if item.data(Qt.ItemDataRole.UserRole)]
        else:
            # Single selection from combo
            CurrentCategory = self.CategoryCombo.currentData()
            if CurrentCategory:  # Skip empty category (All Categories option)
                Criteria.Categories = [CurrentCategory]
        
        # Author - handle both selection and typed text for editable ComboBox
        CurrentAuthor = self.AuthorCombo.currentData()
        CurrentAuthorText = self.AuthorCombo.currentText().strip()
        CurrentAuthorIndex = self.AuthorCombo.currentIndex()
        
        # For editable ComboBox, we need to handle both data and text
        AuthorToUse = None
        
        if CurrentAuthor and CurrentAuthor.strip():
            # User selected from dropdown - use the data
            AuthorToUse = CurrentAuthor.strip()
        elif CurrentAuthorText and CurrentAuthorText != "All Authors":
            # User typed something - check if it matches an existing author
            for i in range(self.AuthorCombo.count()):
                if self.AuthorCombo.itemText(i).strip().lower() == CurrentAuthorText.lower():
                    AuthorToUse = self.AuthorCombo.itemData(i)
                    break
            
            # If no exact match found, use the typed text as-is (user might be filtering by partial author name)
            if not AuthorToUse and CurrentAuthorText:
                AuthorToUse = CurrentAuthorText
        
        if AuthorToUse:
            Criteria.Authors = [AuthorToUse]
        
        # Quick filters
        if self.RecentlyAddedBtn.isChecked():
            Criteria.DateAddedFrom = QDate.currentDate().addDays(-30).toString("yyyy-MM-dd")
        
        if self.HighRatedBtn.isChecked():
            Criteria.MinRating = 4
        
        if self.UnreadBtn.isChecked():
            Criteria.ReadStatuses = ["Unread"]
        
        if self.LargeFilesBtn.isChecked():
            Criteria.MinFileSize = 50 * 1024 * 1024  # 50 MB
        
        # Advanced filters
        if self.MinRatingSlider.value() > 0:
            Criteria.MinRating = max(Criteria.MinRating, self.MinRatingSlider.value())
        
        if self.MinPagesSpinBox.value() > 0:
            Criteria.MinPageCount = self.MinPagesSpinBox.value()
        
        if self.MaxPagesSpinBox.value() < 9999:
            Criteria.MaxPageCount = self.MaxPagesSpinBox.value()
        
        # Date filter
        if self.DateFilterCheck.isChecked():
            Criteria.DateAddedFrom = self.DateFromEdit.date().toString("yyyy-MM-dd")
            Criteria.DateAddedTo = self.DateToEdit.date().toString("yyyy-MM-dd")
        
        # File formats
        FileFormats = []
        if self.PdfCheck.isChecked():
            FileFormats.append("PDF")
        if self.EpubCheck.isChecked():
            FileFormats.append("EPUB")
        if self.MobiCheck.isChecked():
            FileFormats.append("MOBI")
        Criteria.FileFormats = FileFormats
        
        self.CurrentCriteria = Criteria
        return Criteria
    
    def ClearFilters(self):
        """Clear all filters and reset to defaults"""
        # Search
        self.SearchEdit.clear()
        self.SearchTitleCheck.setChecked(True)
        self.SearchAuthorCheck.setChecked(True)
        self.SearchSubjectCheck.setChecked(True)
        self.SearchKeywordsCheck.setChecked(True)
        self.SearchDescriptionCheck.setChecked(False)
        
        # Quick filters
        self.RecentlyAddedBtn.setChecked(False)
        self.HighRatedBtn.setChecked(False)
        self.UnreadBtn.setChecked(False)
        self.LargeFilesBtn.setChecked(False)
        
        # Categories
        self.CategoryCombo.setCurrentIndex(0)
        self.CategoryList.clearSelection()
        self.MultipleCategoriesCheck.setChecked(False)
        
        # Authors
        self.AuthorCombo.setCurrentIndex(0)
        
        # Clear popular author buttons
        for i in range(self.PopularAuthorsLayout.count()):
            widget = self.PopularAuthorsLayout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setChecked(False)
        
        # Advanced
        self.MinRatingSlider.setValue(0)
        self.MinPagesSpinBox.setValue(0)
        self.MaxPagesSpinBox.setValue(9999)
        self.DateFilterCheck.setChecked(False)
        self.PdfCheck.setChecked(True)
        self.EpubCheck.setChecked(False)
        self.MobiCheck.setChecked(False)
        
        logging.info("All filters cleared")
    
    # Event handlers
    def OnSearchTextChanged(self):
        """Handle search text changes with debouncing"""
        self.SearchTimer.stop()
        self.SearchTimer.start(500)  # 500ms delay
    
    def OnSearchTimerTimeout(self):
        """Handle search timer timeout"""
        self.OnFiltersChanged()
    
    def OnAuthorTextChanged(self):
        """Handle author text changes with debouncing"""
        self.AuthorTimer.stop()
        self.AuthorTimer.start(500)  # 500ms delay
    
    def OnAuthorTimerTimeout(self):
        """Handle author timer timeout"""
        self.OnFiltersChanged()
    
    def OnFiltersChanged(self):
        """Handle any filter change"""
        Criteria = self.GetCurrentCriteria()
        self.FiltersChanged.emit(Criteria)
    
    def OnSearchClicked(self):
        """Handle search button click"""
        Criteria = self.GetCurrentCriteria()
        self.SearchRequested.emit(Criteria)
        logging.info(f"Search requested: {Criteria.GetSummary()}")
    
    def OnClearClicked(self):
        """Handle clear button click"""
        self.ClearFilters()
        self.ClearRequested.emit()
        logging.info("Filters cleared")
    
    def OnMultipleCategoriesToggled(self, Checked: bool):
        """Handle multiple categories checkbox toggle"""
        if Checked:
            self.CategoryCombo.hide()
            self.CategoryList.show()
        else:
            self.CategoryCombo.show()
            self.CategoryList.hide()
            self.CategoryList.clearSelection()
        self.OnFiltersChanged()
    
    def OnRatingChanged(self, Value: int):
        """Handle rating slider change"""
        self.RatingLabel.setText(f"{Value}-5")
        self.OnFiltersChanged()
    
    def OnDateFilterToggled(self, Checked: bool):
        """Handle date filter checkbox toggle"""
        self.DateFromEdit.setEnabled(Checked)
        self.DateToEdit.setEnabled(Checked)
        if Checked:
            self.OnFiltersChanged()
    
    def OnPopularAuthorClicked(self, Author: str):
        """Handle popular author button click"""
        # Set the author in the combo box
        Index = self.AuthorCombo.findData(Author)
        if Index >= 0:
            self.AuthorCombo.setCurrentIndex(Index)
        self.OnFiltersChanged()