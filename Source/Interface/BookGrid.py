# File: BookGrid.py
# Path: Source/Interface/BookGrid.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  04:12PM
"""
Description: Book Grid Display Component for Anderson's Library
Provides the main scrollable grid display of books with covers, titles, and metadata.
Supports multiple view modes, sorting, and selection.
"""

import logging
import os
import subprocess
import platform
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
                               QFrame, QLabel, QPushButton, QComboBox, QButtonGroup,
                               QGridLayout, QSizePolicy, QMenu, QToolButton, 
                               QProgressBar, QStackedWidget, QTextEdit, QGroupBox,
                               QApplication)
from PySide6.QtCore import Qt, Signal, QSize, QThread, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap, QFont, QPainter, QPen, QBrush, QIcon, QAction, QCursor
from typing import List, Optional, Dict, Callable
from ..Data.DatabaseModels import BookRecord, SearchResult, SearchCriteria


class BookTile(QFrame):
    """
    Individual book tile widget showing cover, title, author, and metadata.
    Supports different display modes and provides interactive features.
    """
    
    # Signals
    BookSelected = Signal(object)      # BookRecord
    BookDoubleClicked = Signal(object) # BookRecord
    BookRightClicked = Signal(object, object) # BookRecord, QPoint
    
    def __init__(self, Book: BookRecord, ViewMode: str = "grid", parent=None):
        super().__init__(parent)
        self.Book = Book
        self.ViewMode = ViewMode
        self.IsSelected = False
        self.IsHovered = False
        
        self.SetupUI()
        self.LoadBookCover()
        self.ApplyStyles()
        
        # Animation for hover effects
        self.HoverAnimation = QPropertyAnimation(self, b"geometry")
        self.HoverAnimation.setDuration(200)
        self.HoverAnimation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def SetupUI(self):
        """Create the tile interface based on view mode"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if self.ViewMode == "grid":
            self.SetupGridMode()
        elif self.ViewMode == "list":
            self.SetupListMode()
        elif self.ViewMode == "detail":
            self.SetupDetailMode()
        else:
            self.SetupGridMode()  # Default
    
    def SetupGridMode(self):
        """Setup grid tile layout (vertical with cover on top)"""
        self.setFixedSize(180, 280)
        
        Layout = QVBoxLayout(self)
        Layout.setContentsMargins(8, 8, 8, 8)
        Layout.setSpacing(8)
        
        # Cover image
        self.CoverLabel = QLabel()
        self.CoverLabel.setFixedSize(164, 220)
        self.CoverLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.CoverLabel.setStyleSheet("""
            QLabel {
                border: 1px solid #ddd;
                background-color: #f9f9f9;
                border-radius: 4px;
            }
        """)
        Layout.addWidget(self.CoverLabel)
        
        # Title (truncated)
        self.TitleLabel = QLabel(self.Book.GetDisplayTitle())
        self.TitleLabel.setWordWrap(True)
        self.TitleLabel.setMaximumHeight(32)
        self.TitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        TitleFont = QFont()
        TitleFont.setPointSize(9)
        TitleFont.setBold(True)
        self.TitleLabel.setFont(TitleFont)
        Layout.addWidget(self.TitleLabel)
        
        # Author (truncated)
        self.AuthorLabel = QLabel(self.Book.GetDisplayAuthor())
        self.AuthorLabel.setWordWrap(True)
        self.AuthorLabel.setMaximumHeight(20)
        self.AuthorLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.AuthorLabel.setStyleSheet("color: #666; font-size: 8pt;")
        Layout.addWidget(self.AuthorLabel)
    
    def SetupListMode(self):
        """Setup list tile layout (horizontal with cover on left)"""
        self.setFixedHeight(80)
        self.setMinimumWidth(400)
        
        Layout = QHBoxLayout(self)
        Layout.setContentsMargins(8, 8, 8, 8)
        Layout.setSpacing(12)
        
        # Cover image (smaller)
        self.CoverLabel = QLabel()
        self.CoverLabel.setFixedSize(50, 64)
        self.CoverLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.CoverLabel.setStyleSheet("""
            QLabel {
                border: 1px solid #ddd;
                background-color: #f9f9f9;
                border-radius: 2px;
            }
        """)
        Layout.addWidget(self.CoverLabel)
        
        # Text content
        TextLayout = QVBoxLayout()
        TextLayout.setSpacing(4)
        
        # Title
        self.TitleLabel = QLabel(self.Book.Title)
        TitleFont = QFont()
        TitleFont.setPointSize(11)
        TitleFont.setBold(True)
        self.TitleLabel.setFont(TitleFont)
        TextLayout.addWidget(self.TitleLabel)
        
        # Author and metadata
        self.AuthorLabel = QLabel(f"by {self.Book.Author}")
        self.AuthorLabel.setStyleSheet("color: #666;")
        TextLayout.addWidget(self.AuthorLabel)
        
        # Additional info
        InfoText = f"{self.Book.Category}"
        if self.Book.PageCount > 0:
            InfoText += f" • {self.Book.PageCount} pages"
        if self.Book.FileSize > 0:
            InfoText += f" • {self.Book.GetFileSizeFormatted()}"
        
        self.InfoLabel = QLabel(InfoText)
        self.InfoLabel.setStyleSheet("color: #888; font-size: 9pt;")
        TextLayout.addWidget(self.InfoLabel)
        
        Layout.addLayout(TextLayout)
        Layout.addStretch()
        
        # Rating and status
        StatusLayout = QVBoxLayout()
        StatusLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        if self.Book.Rating > 0:
            RatingLabel = QLabel("★" * self.Book.Rating)
            RatingLabel.setStyleSheet("color: #ffc107;")
            StatusLayout.addWidget(RatingLabel)
        
        StatusLabel = QLabel(self.Book.ReadStatus)
        StatusLabel.setStyleSheet("color: #666; font-size: 8pt;")
        StatusLayout.addWidget(StatusLabel)
        
        Layout.addLayout(StatusLayout)
    
    def SetupDetailMode(self):
        """Setup detailed tile layout (large with full metadata)"""
        self.setFixedHeight(120)
        self.setMinimumWidth(600)
        
        Layout = QHBoxLayout(self)
        Layout.setContentsMargins(12, 12, 12, 12)
        Layout.setSpacing(16)
        
        # Cover image
        self.CoverLabel = QLabel()
        self.CoverLabel.setFixedSize(75, 96)
        self.CoverLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.CoverLabel.setStyleSheet("""
            QLabel {
                border: 1px solid #ddd;
                background-color: #f9f9f9;
                border-radius: 4px;
            }
        """)
        Layout.addWidget(self.CoverLabel)
        
        # Main content
        ContentLayout = QVBoxLayout()
        ContentLayout.setSpacing(6)
        
        # Title and author
        self.TitleLabel = QLabel(self.Book.Title)
        TitleFont = QFont()
        TitleFont.setPointSize(12)
        TitleFont.setBold(True)
        self.TitleLabel.setFont(TitleFont)
        ContentLayout.addWidget(self.TitleLabel)
        
        self.AuthorLabel = QLabel(f"by {self.Book.Author}")
        AuthorFont = QFont()
        AuthorFont.setPointSize(10)
        self.AuthorLabel.setFont(AuthorFont)
        self.AuthorLabel.setStyleSheet("color: #666;")
        ContentLayout.addWidget(self.AuthorLabel)
        
        # Description or subject
        DescText = self.Book.Description if self.Book.Description else self.Book.Subject
        if DescText and len(DescText) > 150:
            DescText = DescText[:147] + "..."
        
        if DescText:
            self.DescLabel = QLabel(DescText)
            self.DescLabel.setWordWrap(True)
            self.DescLabel.setStyleSheet("color: #444; font-size: 9pt;")
            ContentLayout.addWidget(self.DescLabel)
        
        Layout.addLayout(ContentLayout)
        
        # Metadata column
        MetaLayout = QVBoxLayout()
        MetaLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        MetaLayout.setSpacing(4)
        
        # Category and pages
        if self.Book.Category:
            CategoryLabel = QLabel(f"📂 {self.Book.Category}")
            CategoryLabel.setStyleSheet("color: #666; font-size: 9pt;")
            MetaLayout.addWidget(CategoryLabel)
        
        if self.Book.PageCount > 0:
            PagesLabel = QLabel(f"📄 {self.Book.PageCount} pages")
            PagesLabel.setStyleSheet("color: #666; font-size: 9pt;")
            MetaLayout.addWidget(PagesLabel)
        
        # File size and format
        FileSizeLabel = QLabel(f"💾 {self.Book.GetFileSizeFormatted()}")
        FileSizeLabel.setStyleSheet("color: #666; font-size: 9pt;")
        MetaLayout.addWidget(FileSizeLabel)
        
        # Rating
        if self.Book.Rating > 0:
            RatingLabel = QLabel(f"⭐ {self.Book.Rating}/5")
            RatingLabel.setStyleSheet("color: #ffc107; font-size: 9pt;")
            MetaLayout.addWidget(RatingLabel)
        
        # Date added
        if self.Book.DateAdded:
            DateLabel = QLabel(f"📅 {self.Book.DateAdded[:10]}")
            DateLabel.setStyleSheet("color: #666; font-size: 8pt;")
            MetaLayout.addWidget(DateLabel)
        
        Layout.addLayout(MetaLayout)
    
    def LoadBookCover(self):
        """Load and display book cover image"""
        try:
            # Try to load thumbnail first
            CoverPath = None
            if self.Book.ThumbnailPath and os.path.exists(self.Book.ThumbnailPath):
                CoverPath = self.Book.ThumbnailPath
            
            # Try default cover locations
            if not CoverPath:
                PossiblePaths = [
                    f"Assets/Covers/{self.Book.FileName}.jpg",
                    f"Assets/Covers/{self.Book.FileName}.png",
                    f"Data/Covers/{self.Book.FileName}.jpg",
                    f"Data/Covers/{self.Book.FileName}.png"
                ]
                
                for Path in PossiblePaths:
                    if os.path.exists(Path):
                        CoverPath = Path
                        break
            
            if CoverPath:
                Pixmap = QPixmap(CoverPath)
                if not Pixmap.isNull():
                    # Scale to fit the label
                    ScaledPixmap = Pixmap.scaled(
                        self.CoverLabel.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.CoverLabel.setPixmap(ScaledPixmap)
                    return
            
            # Use default cover
            self.SetDefaultCover()
            
        except Exception as Error:
            logging.warning(f"Error loading cover for {self.Book.Title}: {Error}")
            self.SetDefaultCover()
    
    def SetDefaultCover(self):
        """Set a default cover image"""
        try:
            # Try to load default cover
            DefaultPaths = [
                "Assets/default_cover.png",
                "Assets/book_placeholder.png"
            ]
            
            for Path in DefaultPaths:
                if os.path.exists(Path):
                    Pixmap = QPixmap(Path)
                    if not Pixmap.isNull():
                        ScaledPixmap = Pixmap.scaled(
                            self.CoverLabel.size(),
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        self.CoverLabel.setPixmap(ScaledPixmap)
                        return
            
            # Generate text-based cover
            self.GenerateTextCover()
            
        except Exception as Error:
            logging.warning(f"Error setting default cover: {Error}")
            self.GenerateTextCover()
    
    def GenerateTextCover(self):
        """Generate a text-based cover"""
        try:
            Size = self.CoverLabel.size()
            Pixmap = QPixmap(Size)
            Pixmap.fill(Qt.GlobalColor.lightGray)
            
            Painter = QPainter(Pixmap)
            Painter.setPen(QPen(Qt.GlobalColor.darkGray, 2))
            
            # Draw border
            Painter.drawRect(2, 2, Size.width()-4, Size.height()-4)
            
            # Draw title text
            TitleFont = QFont()
            TitleFont.setPointSize(8)
            TitleFont.setBold(True)
            Painter.setFont(TitleFont)
            
            # Wrap title text
            Title = self.Book.Title if len(self.Book.Title) <= 40 else self.Book.Title[:37] + "..."
            TitleRect = Painter.fontMetrics().boundingRect(10, 10, Size.width()-20, Size.height()-20, 
                                                         Qt.TextFlag.TextWordWrap, Title)
            
            Painter.drawText(10, 30, Size.width()-20, Size.height()-40, 
                           Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignCenter, Title)
            
            # Draw author
            if self.Book.Author:
                AuthorFont = QFont()
                AuthorFont.setPointSize(6)
                Painter.setFont(AuthorFont)
                
                Author = self.Book.Author if len(self.Book.Author) <= 30 else self.Book.Author[:27] + "..."
                Painter.drawText(10, Size.height()-30, Size.width()-20, 25, 
                               Qt.AlignmentFlag.AlignCenter, f"by {Author}")
            
            Painter.end()
            self.CoverLabel.setPixmap(Pixmap)
            
        except Exception as Error:
            logging.error(f"Error generating text cover: {Error}")
            # Last resort - just set text
            self.CoverLabel.setText("📖\nNo Cover")
            self.CoverLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def ApplyStyles(self):
        """Apply visual styling to the tile"""
        if self.IsSelected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #e3f2fd;
                    border: 2px solid #2196f3;
                    border-radius: 6px;
                }
            """)
        elif self.IsHovered:
            self.setStyleSheet("""
                QFrame {
                    background-color: #f5f5f5;
                    border: 1px solid #ccc;
                    border-radius: 6px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                }
                QFrame:hover {
                    border: 1px solid #bbb;
                    background-color: #fafafa;
                }
            """)
    
    def SetSelected(self, Selected: bool):
        """Set tile selection state"""
        self.IsSelected = Selected
        self.ApplyStyles()
    
    def SetHovered(self, Hovered: bool):
        """Set tile hover state"""
        self.IsHovered = Hovered
        self.ApplyStyles()
    
    # Event handlers
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.BookSelected.emit(self.Book)
        elif event.button() == Qt.MouseButton.RightButton:
            self.BookRightClicked.emit(self.Book, event.globalPosition().toPoint())
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.BookDoubleClicked.emit(self.Book)
        super().mouseDoubleClickEvent(event)
    
    def enterEvent(self, event):
        """Handle mouse enter"""
        self.SetHovered(True)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave"""
        self.SetHovered(False)
        super().leaveEvent(event)


class BookGrid(QWidget):
    """
    Main book grid widget that displays a collection of BookTile widgets.
    Supports different view modes, sorting, and virtual scrolling for performance.
    """
    
    # Signals
    BookSelected = Signal(object)       # BookRecord
    BookOpened = Signal(object)         # BookRecord
    SelectionChanged = Signal(list)     # List[BookRecord]
    ViewModeChanged = Signal(str)       # View mode
    SortChanged = Signal(str, str)      # Sort field, sort order
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.Books = []
        self.FilteredBooks = []
        self.SelectedBooks = []
        self.ViewMode = "grid"
        self.SortField = "Title"
        self.SortOrder = "ASC"
        self.BookTiles = []
        
        self.SetupUI()
        self.SetupConnections()
        
        logging.info("BookGrid initialized")
    
    def SetupUI(self):
        """Create the book grid interface"""
        Layout = QVBoxLayout(self)
        Layout.setContentsMargins(0, 0, 0, 0)
        Layout.setSpacing(0)
        
        # Toolbar
        self.CreateToolbar(Layout)
        
        # Main scroll area
        self.ScrollArea = QScrollArea()
        self.ScrollArea.setWidgetResizable(True)
        self.ScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Grid container
        self.GridContainer = QWidget()
        self.GridLayout = QGridLayout(self.GridContainer)
        self.GridLayout.setSpacing(10)
        self.GridLayout.setContentsMargins(15, 15, 15, 15)
        
        self.ScrollArea.setWidget(self.GridContainer)
        Layout.addWidget(self.ScrollArea)
        
        # Status bar
        self.CreateStatusBar(Layout)
        
        # Apply initial styling
        self.ApplyStyles()
    
    def CreateToolbar(self, Layout: QVBoxLayout):
        """Create the toolbar with view options and sorting"""
        ToolbarFrame = QFrame()
        ToolbarFrame.setFrameStyle(QFrame.Shape.StyledPanel)
        ToolbarFrame.setFixedHeight(50)
        ToolbarLayout = QHBoxLayout(ToolbarFrame)
        ToolbarLayout.setContentsMargins(15, 8, 15, 8)
        
        # View mode buttons
        ViewLabel = QLabel("View:")
        ToolbarLayout.addWidget(ViewLabel)
        
        self.ViewButtonGroup = QButtonGroup()
        
        self.GridViewBtn = QPushButton("⊞ Grid")
        self.GridViewBtn.setCheckable(True)
        self.GridViewBtn.setChecked(True)
        self.ViewButtonGroup.addButton(self.GridViewBtn, 0)
        ToolbarLayout.addWidget(self.GridViewBtn)
        
        self.ListViewBtn = QPushButton("☰ List")
        self.ListViewBtn.setCheckable(True)
        self.ViewButtonGroup.addButton(self.ListViewBtn, 1)
        ToolbarLayout.addWidget(self.ListViewBtn)
        
        self.DetailViewBtn = QPushButton("📄 Detail")
        self.DetailViewBtn.setCheckable(True)
        self.ViewButtonGroup.addButton(self.DetailViewBtn, 2)
        ToolbarLayout.addWidget(self.DetailViewBtn)
        
        ToolbarLayout.addWidget(QFrame())  # Separator
        
        # Sort options
        SortLabel = QLabel("Sort by:")
        ToolbarLayout.addWidget(SortLabel)
        
        self.SortCombo = QComboBox()
        self.SortCombo.addItems([
            "Title", "Author", "Category", "Date Added", 
            "File Size", "Page Count", "Rating", "Last Accessed"
        ])
        ToolbarLayout.addWidget(self.SortCombo)
        
        self.SortOrderBtn = QPushButton("↑ A-Z")
        self.SortOrderBtn.setCheckable(True)
        self.SortOrderBtn.setToolTip("Toggle sort order")
        ToolbarLayout.addWidget(self.SortOrderBtn)
        
        ToolbarLayout.addStretch()
        
        # Selection info
        self.SelectionLabel = QLabel("No selection")
        self.SelectionLabel.setStyleSheet("color: #666;")
        ToolbarLayout.addWidget(self.SelectionLabel)
        
        Layout.addWidget(ToolbarFrame)
    
    def CreateStatusBar(self, Layout: QVBoxLayout):
        """Create status bar showing book count and loading state"""
        self.StatusFrame = QFrame()
        self.StatusFrame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.StatusFrame.setFixedHeight(30)
        StatusLayout = QHBoxLayout(self.StatusFrame)
        StatusLayout.setContentsMargins(15, 5, 15, 5)
        
        self.StatusLabel = QLabel("Ready")
        StatusLayout.addWidget(self.StatusLabel)
        
        StatusLayout.addStretch()
        
        # Loading progress bar
        self.ProgressBar = QProgressBar()
        self.ProgressBar.setVisible(False)
        self.ProgressBar.setMaximumWidth(200)
        StatusLayout.addWidget(self.ProgressBar)
        
        Layout.addWidget(self.StatusFrame)
    
    def SetupConnections(self):
        """Connect signals and slots"""
        # View mode buttons
        self.ViewButtonGroup.buttonClicked.connect(self.OnViewModeChanged)
        
        # Sort controls
        self.SortCombo.currentTextChanged.connect(self.OnSortFieldChanged)
        self.SortOrderBtn.clicked.connect(self.OnSortOrderToggled)
    
    def ApplyStyles(self):
        """Apply consistent styling"""
        self.setStyleSheet("""
            QFrame {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
            }
            QPushButton {
                padding: 6px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #fff;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton:checked {
                background-color: #2196f3;
                color: white;
                border-color: #1976d2;
            }
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #fff;
                min-width: 100px;
            }
        """)
    
    def SetBooks(self, Books: List[BookRecord]):
        """Set the list of books to display"""
        self.Books = Books.copy()
        self.FilteredBooks = Books.copy()
        self.ApplySorting()
        self.RefreshDisplay()
        
        logging.info(f"BookGrid updated with {len(Books)} books")
    
    def UpdateBooks(self, SearchResult: SearchResult):
        """Update books from search result"""
        self.Books = SearchResult.Books.copy()
        self.FilteredBooks = SearchResult.Books.copy()
        self.ApplySorting()
        self.RefreshDisplay()
        
        # Update status
        if SearchResult.Success:
            self.StatusLabel.setText(SearchResult.GetResultSummary())
        else:
            self.StatusLabel.setText(f"Error: {SearchResult.ErrorMessage}")
    
    def ClearBooks(self):
        """Clear all books"""
        self.Books.clear()
        self.FilteredBooks.clear()
        self.SelectedBooks.clear()
        self.ClearTiles()
        self.StatusLabel.setText("No books to display")
    
    def ClearTiles(self):
        """Clear all book tiles from the grid"""
        for Tile in self.BookTiles:
            Tile.deleteLater()
        self.BookTiles.clear()
        
        # Clear the grid layout
        while self.GridLayout.count():
            child = self.GridLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def RefreshDisplay(self):
        """Refresh the book display"""
        self.ClearTiles()
        
        if not self.FilteredBooks:
            self.ShowEmptyState()
            return
        
        self.ShowLoadingState()
        
        # Use QTimer to prevent UI freezing
        QTimer.singleShot(10, self.CreateBookTiles)
    
    def CreateBookTiles(self):
        """Create book tiles for current books"""
        try:
            self.ProgressBar.setVisible(True)
            self.ProgressBar.setMaximum(len(self.FilteredBooks))
            self.ProgressBar.setValue(0)
            
            if self.ViewMode == "grid":
                self.CreateGridTiles()
            elif self.ViewMode == "list":
                self.CreateListTiles()
            elif self.ViewMode == "detail":
                self.CreateDetailTiles()
            
            self.ProgressBar.setVisible(False)
            self.UpdateSelectionDisplay()
            
        except Exception as Error:
            logging.error(f"Error creating book tiles: {Error}")
            self.ProgressBar.setVisible(False)
            self.StatusLabel.setText("Error displaying books")
    
    def CreateGridTiles(self):
        """Create tiles in grid layout"""
        ColumnsPerRow = max(1, (self.ScrollArea.width() - 50) // 200)
        
        for Index, Book in enumerate(self.FilteredBooks):
            Row = Index // ColumnsPerRow
            Col = Index % ColumnsPerRow
            
            Tile = BookTile(Book, "grid")
            self.ConnectTileSignals(Tile)
            
            self.GridLayout.addWidget(Tile, Row, Col)
            self.BookTiles.append(Tile)
            
            self.ProgressBar.setValue(Index + 1)
            
            # Process events to prevent freezing
            if Index % 10 == 0:
                QApplication.processEvents()
    
    def CreateListTiles(self):
        """Create tiles in list layout"""
        for Index, Book in enumerate(self.FilteredBooks):
            Tile = BookTile(Book, "list")
            self.ConnectTileSignals(Tile)
            
            self.GridLayout.addWidget(Tile, Index, 0)
            self.BookTiles.append(Tile)
            
            self.ProgressBar.setValue(Index + 1)
            
            if Index % 5 == 0:
                QApplication.processEvents()
    
    def CreateDetailTiles(self):
        """Create tiles in detail layout"""
        for Index, Book in enumerate(self.FilteredBooks):
            Tile = BookTile(Book, "detail")
            self.ConnectTileSignals(Tile)
            
            self.GridLayout.addWidget(Tile, Index, 0)
            self.BookTiles.append(Tile)
            
            self.ProgressBar.setValue(Index + 1)
            
            if Index % 3 == 0:
                QApplication.processEvents()
    
    def ConnectTileSignals(self, Tile: BookTile):
        """Connect signals from book tile"""
        Tile.BookSelected.connect(self.OnBookSelected)
        Tile.BookDoubleClicked.connect(self.OnBookDoubleClicked)
        Tile.BookRightClicked.connect(self.OnBookRightClicked)
    
    def ShowEmptyState(self):
        """Show empty state message"""
        EmptyLabel = QLabel("📚\n\nNo books found\n\nTry adjusting your search filters")
        EmptyLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        EmptyLabel.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14pt;
                padding: 50px;
            }
        """)
        self.GridLayout.addWidget(EmptyLabel, 0, 0)
    
    def ShowLoadingState(self):
        """Show loading state"""
        self.StatusLabel.setText("Loading books...")
    
    def ApplySorting(self):
        """Apply current sorting to filtered books"""
        if not self.FilteredBooks:
            return
        
        try:
            Reverse = (self.SortOrder == "DESC")
            
            if self.SortField == "Title":
                self.FilteredBooks.sort(key=lambda b: b.Title.lower(), reverse=Reverse)
            elif self.SortField == "Author":
                self.FilteredBooks.sort(key=lambda b: b.Author.lower(), reverse=Reverse)
            elif self.SortField == "Category":
                self.FilteredBooks.sort(key=lambda b: b.Category.lower(), reverse=Reverse)
            elif self.SortField == "Date Added":
                self.FilteredBooks.sort(key=lambda b: b.DateAdded, reverse=Reverse)
            elif self.SortField == "File Size":
                self.FilteredBooks.sort(key=lambda b: b.FileSize, reverse=Reverse)
            elif self.SortField == "Page Count":
                self.FilteredBooks.sort(key=lambda b: b.PageCount, reverse=Reverse)
            elif self.SortField == "Rating":
                self.FilteredBooks.sort(key=lambda b: b.Rating, reverse=Reverse)
            elif self.SortField == "Last Accessed":
                self.FilteredBooks.sort(key=lambda b: b.LastAccessed or "", reverse=Reverse)
            
            logging.info(f"Books sorted by {self.SortField} ({self.SortOrder})")
            
        except Exception as Error:
            logging.error(f"Error sorting books: {Error}")
    
    def UpdateSelectionDisplay(self):
        """Update selection display"""
        Count = len(self.SelectedBooks)
        if Count == 0:
            self.SelectionLabel.setText("No selection")
        elif Count == 1:
            self.SelectionLabel.setText("1 book selected")
        else:
            self.SelectionLabel.setText(f"{Count} books selected")
    
    # Event handlers
    def OnViewModeChanged(self, Button):
        """Handle view mode change"""
        ButtonId = self.ViewButtonGroup.id(Button)
        
        if ButtonId == 0:
            self.ViewMode = "grid"
        elif ButtonId == 1:
            self.ViewMode = "list"
        elif ButtonId == 2:
            self.ViewMode = "detail"
        
        self.RefreshDisplay()
        self.ViewModeChanged.emit(self.ViewMode)
        logging.info(f"View mode changed to: {self.ViewMode}")
    
    def OnSortFieldChanged(self, Field: str):
        """Handle sort field change"""
        self.SortField = Field
        self.ApplySorting()
        self.RefreshDisplay()
        self.SortChanged.emit(self.SortField, self.SortOrder)
    
    def OnSortOrderToggled(self):
        """Handle sort order toggle"""
        if self.SortOrder == "ASC":
            self.SortOrder = "DESC"
            self.SortOrderBtn.setText("↓ Z-A")
        else:
            self.SortOrder = "ASC"
            self.SortOrderBtn.setText("↑ A-Z")
        
        self.ApplySorting()
        self.RefreshDisplay()
        self.SortChanged.emit(self.SortField, self.SortOrder)
    
    def OnBookSelected(self, Book: BookRecord):
        """Handle book selection"""
        # Toggle selection
        if Book in self.SelectedBooks:
            self.SelectedBooks.remove(Book)
        else:
            self.SelectedBooks.append(Book)
        
        # Update tile selection states
        for Tile in self.BookTiles:
            Tile.SetSelected(Tile.Book in self.SelectedBooks)
        
        self.UpdateSelectionDisplay()
        self.BookSelected.emit(Book)
        self.SelectionChanged.emit(self.SelectedBooks.copy())
    
    def OnBookDoubleClicked(self, Book: BookRecord):
        """Handle book double click"""
        self.BookOpened.emit(Book)
        logging.info(f"Book opened: {Book.Title}")
    
    def OnBookRightClicked(self, Book: BookRecord, Position):
        """Handle book right click"""
        # Create context menu
        Menu = QMenu(self)
        
        OpenAction = Menu.addAction("📖 Open Book")
        OpenAction.triggered.connect(lambda: self.BookOpened.emit(Book))
        
        Menu.addSeparator()
        
        PropertiesAction = Menu.addAction("ℹ️ Properties")
        PropertiesAction.triggered.connect(lambda: self.ShowBookProperties(Book))
        
        Menu.exec(Position)
    
    def ShowBookProperties(self, Book: BookRecord):
        """Show book properties dialog"""
        # This would open a properties dialog
        # For now, just log the action
        logging.info(f"Show properties for: {Book.Title}")
    
    def resizeEvent(self, event):
        """Handle resize to adjust grid columns"""
        super().resizeEvent(event)
        if self.ViewMode == "grid":
            # Refresh grid layout on resize
            QTimer.singleShot(100, self.RefreshDisplay)