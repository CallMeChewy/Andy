# File: BookGrid.py
# Path: Source/Interface/BookGrid.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  01:34PM
"""
Description: Fixed Responsive Book Grid
Uses all available real estate with no column limits.
"""

import logging
from typing import List, Optional
from pathlib import Path
from PySide6.QtWidgets import (
    QScrollArea, QWidget, QGridLayout, QLabel, 
    QVBoxLayout, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap, QFont, QMouseEvent

from Source.Core.BookService import BookService
from Source.Data.DatabaseModels import SearchCriteria, Book


class BookCard(QFrame):
    """Book card for responsive layout"""
    
    BookClicked = Signal(str)
    
    def __init__(self, BookData: Book, Parent=None):
        super().__init__(Parent)
        self.BookData = BookData
        self.Title = BookData.Title
        self._SetupUI()
        self._SetupStyles()
    
    def _SetupUI(self) -> None:
        Layout = QVBoxLayout(self)
        Layout.setContentsMargins(5, 5, 5, 5)
        Layout.setSpacing(5)
        
        # Cover for responsive layout
        self.CoverLabel = QLabel()
        self.CoverLabel.setFixedSize(160, 210)
        self.CoverLabel.setAlignment(Qt.AlignCenter)
        self.CoverLabel.setStyleSheet("border: 1px solid #444; background-color: #333;")
        
        # Try to load cover
        CoverLoaded = False
        if hasattr(self.BookData, 'ThumbnailPath') and self.BookData.ThumbnailPath:
            ThumbnailPath = Path(self.BookData.ThumbnailPath)
            if ThumbnailPath.exists():
                Pixmap = QPixmap(str(ThumbnailPath))
                if not Pixmap.isNull():
                    ScaledPixmap = Pixmap.scaled(160, 210, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.CoverLabel.setPixmap(ScaledPixmap)
                    CoverLoaded = True
        
        if not CoverLoaded:
            # Try standard paths
            for CoverPath in [Path("Data/Covers") / f"{self.Title}.jpg", 
                             Path("Data/Thumbs") / f"{self.Title}.jpg",
                             Path("Assets/library") / f"{self.Title}.jpg"]:
                if CoverPath.exists():
                    Pixmap = QPixmap(str(CoverPath))
                    if not Pixmap.isNull():
                        ScaledPixmap = Pixmap.scaled(160, 210, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.CoverLabel.setPixmap(ScaledPixmap)
                        CoverLoaded = True
                        break
        
        if not CoverLoaded:
            self.CoverLabel.setText("📖\nNo Cover")
            Font = QFont()
            Font.setPointSize(14)
            self.CoverLabel.setFont(Font)
        
        Layout.addWidget(self.CoverLabel)
        
        # Title
        self.TitleLabel = QLabel(self.Title)
        self.TitleLabel.setWordWrap(True)
        self.TitleLabel.setAlignment(Qt.AlignCenter)
        self.TitleLabel.setMaximumWidth(160)
        self.TitleLabel.setMaximumHeight(40)
        
        TitleFont = QFont()
        TitleFont.setPointSize(9)
        TitleFont.setBold(True)
        self.TitleLabel.setFont(TitleFont)
        Layout.addWidget(self.TitleLabel)
        
        # Author
        if hasattr(self.BookData, 'Author') and self.BookData.Author:
            self.AuthorLabel = QLabel(self.BookData.Author)
            self.AuthorLabel.setWordWrap(True)
            self.AuthorLabel.setAlignment(Qt.AlignCenter)
            self.AuthorLabel.setMaximumWidth(160)
            self.AuthorLabel.setMaximumHeight(25)
            
            AuthorFont = QFont()
            AuthorFont.setPointSize(7)
            self.AuthorLabel.setFont(AuthorFont)
            self.AuthorLabel.setStyleSheet("color: #cccccc;")
            Layout.addWidget(self.AuthorLabel)
        
        self.setFixedSize(180, 280)
    
    def _SetupStyles(self) -> None:
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            BookCard {
                border: 2px solid transparent;
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 0.1);
            }
            BookCard:hover {
                border: 2px solid #ff4444;
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.setMouseTracking(True)
    
    def mousePressEvent(self, Event: QMouseEvent) -> None:
        if Event.button() == Qt.LeftButton:
            self.BookClicked.emit(self.Title)
        super().mousePressEvent(Event)


class BlankCard(QFrame):
    """Blank placeholder card for left-justified layout"""
    
    def __init__(self, Parent=None):
        super().__init__(Parent)
        self.setFixedSize(180, 280)
        self.setStyleSheet("background-color: transparent; border: none;")


class BookGrid(QScrollArea):
    """Fully responsive book grid using all available space"""
    
    StatusUpdate = Signal(str)
    
    def __init__(self, BookServiceInstance: BookService, Parent=None):
        super().__init__(Parent)
        
        self.BookService = BookServiceInstance
        self.Logger = logging.getLogger(__name__)
        
        # Responsive layout parameters (NO MAX LIMIT)
        self.FilterPanelWidth = 320
        self.CardWidth = 180
        self.CardSpacing = 20
        self.ColumnWidth = 200  # Card + spacing
        
        self.CurrentColumns = 0
        self.PreviousColumns = 0
        self.CurrentBooks: List[Book] = []
        self.BookCards = []
        
        self.ScrollWidget: Optional[QWidget] = None
        self.GridLayout: Optional[QGridLayout] = None
        
        self.ResizeTimer = QTimer()
        self.ResizeTimer.setSingleShot(True)
        self.ResizeTimer.timeout.connect(self._UpdateLayout)
        
        self._SetupScrollArea()
        self._SetupGridLayout()
        self._ShowEmptyState()
        
        self.Logger.info("Fully responsive BookGrid initialized")
    
    def _SetupScrollArea(self) -> None:
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.ScrollWidget = QWidget()
        self.setWidget(self.ScrollWidget)
    
    def _SetupGridLayout(self) -> None:
        self.GridLayout = QGridLayout(self.ScrollWidget)
        self.GridLayout.setContentsMargins(10, 10, 10, 10)
        self.GridLayout.setSpacing(10)
        # Left-align the grid
        self.GridLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    
    def _UpdateColumnCount(self) -> None:
        """Calculate columns using ALL available space (no max limit)"""
        MainWindow = self.window()
        TotalWidth = MainWindow.width() if MainWindow else 1920
        
        # Available width = Total - FilterPanel - margins/scrollbar
        AvailableWidth = TotalWidth - self.FilterPanelWidth - 40
        
        # Calculate columns (minimum 1, NO MAXIMUM)
        ColumnsFloat = AvailableWidth / self.ColumnWidth
        
        self.PreviousColumns = self.CurrentColumns
        self.CurrentColumns = max(1, int(ColumnsFloat))  # NO MAX LIMIT
        
        self.Logger.debug(f"Responsive calculation: Width={TotalWidth}, Available={AvailableWidth}, Columns={self.CurrentColumns}")
    
    def _ShowEmptyState(self) -> None:
        """Show empty state - no books selected"""
        self._ClearLayout()
        EmptyLabel = QLabel("📚 Select a category and subject to view books")
        EmptyLabel.setAlignment(Qt.AlignCenter)
        Font = QFont()
        Font.setPointSize(16)
        EmptyLabel.setFont(Font)
        # Span all possible columns
        self.GridLayout.addWidget(EmptyLabel, 0, 0, 1, 10)  # Span 10 columns
        self.StatusUpdate.emit("Ready - Select category and subject to browse books")
    
    def ClearGrid(self) -> None:
        """Clear the grid (called when category changes or search clears)"""
        self._ShowEmptyState()
    
    def _ClearLayout(self) -> None:
        while self.GridLayout.count():
            Child = self.GridLayout.takeAt(0)
            if Child.widget():
                Child.widget().deleteLater()
        self.BookCards.clear()
    
    def FilterBooks(self, Criteria: SearchCriteria) -> None:
        """Display books with responsive layout and blank filling"""
        try:
            self.Logger.debug(f"FilterBooks called with criteria: SearchTerm='{Criteria.SearchTerm}', Categories={Criteria.Categories}, Subjects={Criteria.Subjects}")
            
            SearchResult = self.BookService.SearchBooks(Criteria)
            
            if not SearchResult.Success:
                self._ShowError(SearchResult.ErrorMessage or "Search failed")
                return
            
            Books = SearchResult.Books
            self.Logger.debug(f"Search returned {len(Books)} books")
            
            if not Books:
                self._ShowNoResults()
                return
            
            self._DisplayBooksLeftJustified(Books)
            self.StatusUpdate.emit(f"Found {len(Books)} books")
            
        except Exception as Error:
            self.Logger.error(f"Error filtering books: {Error}")
            self._ShowError(str(Error))
    
    def _ShowNoResults(self) -> None:
        self._ClearLayout()
        Label = QLabel("🔍 No books found\nTry different search terms or filters")
        Label.setAlignment(Qt.AlignCenter)
        Font = QFont()
        Font.setPointSize(14)
        Label.setFont(Font)
        self.GridLayout.addWidget(Label, 0, 0, 1, 10)  # Span 10 columns
        self.StatusUpdate.emit("No books found")
    
    def _ShowError(self, ErrorMessage: str) -> None:
        self._ClearLayout()
        Label = QLabel(f"❌ Error:\n{ErrorMessage}")
        Label.setAlignment(Qt.AlignCenter)
        Label.setStyleSheet("color: #ff4444;")
        self.GridLayout.addWidget(Label, 0, 0, 1, 10)  # Span 10 columns
        self.StatusUpdate.emit("Error loading books")
    
    def _DisplayBooksLeftJustified(self, Books: List[Book]) -> None:
        """Display books with left-justified layout and blank filling"""
        self._ClearLayout()
        self.CurrentBooks = Books
        self._UpdateColumnCount()
        
        Row = 0
        Column = 0
        
        # Add book cards
        for BookData in Books:
            Card = BookCard(BookData)
            Card.BookClicked.connect(self._OnBookClicked)
            
            self.GridLayout.addWidget(Card, Row, Column)
            self.BookCards.append(Card)
            
            Column += 1
            if Column >= self.CurrentColumns:
                Column = 0
                Row += 1
        
        # Fill remaining slots in the last row with blank cards
        if Column > 0:  # If we're in the middle of a row
            while Column < self.CurrentColumns:
                BlankCardWidget = BlankCard()
                self.GridLayout.addWidget(BlankCardWidget, Row, Column)
                Column += 1
        
        # Add stretch to push everything to top
        self.GridLayout.setRowStretch(Row + 1, 1)
        
        self.Logger.debug(f"Displayed {len(Books)} books in {Row + 1} rows, {self.CurrentColumns} columns")
    
    def _UpdateLayout(self) -> None:
        if self.PreviousColumns != self.CurrentColumns and self.CurrentBooks:
            self._DisplayBooksLeftJustified(self.CurrentBooks)
    
    def _OnBookClicked(self, BookTitle: str) -> None:
        try:
            Success = self.BookService.OpenBook(BookTitle)
            if not Success:
                QMessageBox.warning(self, "Book Not Found", 
                    f"Could not open: {BookTitle}\n\nFile may be missing.")
        except Exception as Error:
            self.Logger.error(f"Error opening {BookTitle}: {Error}")
            QMessageBox.critical(self, "Error", f"Error: {Error}")
    
    def RefreshLayout(self) -> None:
        self.ResizeTimer.start(100)
    
    def resizeEvent(self, Event) -> None:
        super().resizeEvent(Event)
        self._UpdateColumnCount()
        self.ResizeTimer.start(100)
        
        Width = self.width()
        Height = self.height()
        self.StatusUpdate.emit(f"{Width} x {Height}  C:{self.CurrentColumns}")
