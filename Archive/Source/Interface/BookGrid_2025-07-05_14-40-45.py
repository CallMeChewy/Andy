# File: BookGrid.py
# Path: Source/Interface/BookGrid.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  01:34PM
"""
Description: Book Grid for Anderson's Library - Simple Working Version
Displays books in a responsive grid layout using standard Qt design.
"""

import logging
from typing import List, Optional
from PySide6.QtWidgets import (
    QScrollArea, QWidget, QGridLayout, QLabel, 
    QVBoxLayout, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap, QFont, QMouseEvent

from Source.Core.BookService import BookService


class BookCard(QFrame):
    """
    Individual book card widget.
    Displays book cover, title, and handles click events.
    """
    
    # Signal emitted when book is clicked
    BookClicked = Signal(str)  # Book title
    
    def __init__(self, Title: str, CoverPath: str = "", Parent=None):
        """
        Initialize book card.
        
        Args:
            Title: Book title
            CoverPath: Path to book cover image
            Parent: Parent widget
        """
        super().__init__(Parent)
        
        self.Title = Title
        self.CoverPath = CoverPath
        
        self._SetupUI()
        self._SetupStyles()
    
    def _SetupUI(self) -> None:
        """Create card layout"""
        Layout = QVBoxLayout(self)
        Layout.setContentsMargins(5, 5, 5, 5)
        Layout.setSpacing(5)
        
        # Book cover
        self.CoverLabel = QLabel()
        self.CoverLabel.setFixedSize(180, 240)
        self.CoverLabel.setAlignment(Qt.AlignCenter)
        self.CoverLabel.setStyleSheet("border: 1px solid #444; background-color: #333;")
        
        # Load cover image or show placeholder
        if self.CoverPath:
            Pixmap = QPixmap(self.CoverPath)
            if not Pixmap.isNull():
                ScaledPixmap = Pixmap.scaled(180, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.CoverLabel.setPixmap(ScaledPixmap)
            else:
                self.CoverLabel.setText("📖\nNo Cover")
        else:
            self.CoverLabel.setText("📖\nNo Cover")
        
        Layout.addWidget(self.CoverLabel)
        
        # Book title
        self.TitleLabel = QLabel(self.Title)
        self.TitleLabel.setWordWrap(True)
        self.TitleLabel.setAlignment(Qt.AlignCenter)
        self.TitleLabel.setMaximumWidth(180)
        
        TitleFont = QFont()
        TitleFont.setPointSize(10)
        self.TitleLabel.setFont(TitleFont)
        
        Layout.addWidget(self.TitleLabel)
        
        # Set fixed size for consistent grid
        self.setFixedSize(200, 300)
    
    def _SetupStyles(self) -> None:
        """Apply card styling"""
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
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
    
    def mousePressEvent(self, Event: QMouseEvent) -> None:
        """Handle mouse clicks"""
        if Event.button() == Qt.LeftButton:
            self.BookClicked.emit(self.Title)
        super().mousePressEvent(Event)


class BookGrid(QScrollArea):
    """
    Scrollable grid of book cards with responsive layout.
    """
    
    # Signals
    StatusUpdate = Signal(str)  # Status message
    
    def __init__(self, BookServiceInstance: BookService, Parent=None):
        """
        Initialize book grid.
        
        Args:
            BookServiceInstance: BookService for data operations
            Parent: Parent widget (optional)
        """
        super().__init__(Parent)
        
        # Store service reference
        self.BookService = BookServiceInstance
        self.Logger = logging.getLogger(__name__)
        
        # Grid parameters
        self.BaseWidth = 315
        self.ItemWidth = 230
        self.CurrentColumns = 0
        self.PreviousColumns = 0
        
        # Current books
        self.CurrentBooks: List[str] = []
        self.BookCards: List[BookCard] = []
        
        # Layout components
        self.ScrollWidget: Optional[QWidget] = None
        self.GridLayout: Optional[QGridLayout] = None
        
        # Resize timer for responsive layout
        self.ResizeTimer = QTimer()
        self.ResizeTimer.setSingleShot(True)
        self.ResizeTimer.timeout.connect(self._UpdateLayout)
        
        # Setup UI
        self._SetupScrollArea()
        self._SetupGridLayout()
        self._ShowEmptyState()
        
        self.Logger.info("BookGrid initialized")
    
    def _SetupScrollArea(self) -> None:
        """Configure scroll area"""
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create scroll widget
        self.ScrollWidget = QWidget()
        self.setWidget(self.ScrollWidget)
    
    def _SetupGridLayout(self) -> None:
        """Create grid layout"""
        self.GridLayout = QGridLayout(self.ScrollWidget)
        self.GridLayout.setContentsMargins(10, 10, 10, 10)
        self.GridLayout.setSpacing(10)
    
    def _ShowEmptyState(self) -> None:
        """Show empty state message"""
        # Clear existing layout
        self._ClearLayout()
        
        # Add empty state label
        EmptyLabel = QLabel("📚 Use search and filters to find books")
        EmptyLabel.setAlignment(Qt.AlignCenter)
        EmptyFont = QFont()
        EmptyFont.setPointSize(16)
        EmptyLabel.setFont(EmptyFont)
        
        self.GridLayout.addWidget(EmptyLabel, 0, 0)
        
        self.StatusUpdate.emit("Ready - Use search and filters to find books")
    
    def _ClearLayout(self) -> None:
        """Clear all widgets from layout"""
        while self.GridLayout.count():
            Child = self.GridLayout.takeAt(0)
            if Child.widget():
                Child.widget().deleteLater()
        
        self.BookCards.clear()
    
    def FilterBooks(self, SearchTerm: str = "", Category: str = "", Subject: str = "") -> None:
        """
        Filter and display books based on criteria.
        
        Args:
            SearchTerm: Text to search for
            Category: Category filter
            Subject: Subject filter
        """
        try:
            # Get books from service
            Books = self.BookService.SearchBooks(SearchTerm, Category, Subject)
            
            if not Books:
                if SearchTerm or Category or Subject:
                    self._ShowNoResults()
                else:
                    self._ShowEmptyState()
                return
            
            # Display books
            self._DisplayBooks(Books)
            
            # Update status
            self.StatusUpdate.emit(f"Found {len(Books)} books")
            
        except Exception as Error:
            self.Logger.error(f"Error filtering books: {Error}")
            self._ShowError(str(Error))
    
    def _ShowNoResults(self) -> None:
        """Show no results message"""
        self._ClearLayout()
        
        NoResultsLabel = QLabel("🔍 No books found\nTry different search terms")
        NoResultsLabel.setAlignment(Qt.AlignCenter)
        NoResultsFont = QFont()
        NoResultsFont.setPointSize(14)
        NoResultsLabel.setFont(NoResultsFont)
        
        self.GridLayout.addWidget(NoResultsLabel, 0, 0)
        
        self.StatusUpdate.emit("No books found")
    
    def _ShowError(self, ErrorMessage: str) -> None:
        """Show error message"""
        self._ClearLayout()
        
        ErrorLabel = QLabel(f"❌ Error loading books:\n{ErrorMessage}")
        ErrorLabel.setAlignment(Qt.AlignCenter)
        ErrorLabel.setStyleSheet("color: #ff4444;")
        
        self.GridLayout.addWidget(ErrorLabel, 0, 0)
        
        self.StatusUpdate.emit("Error loading books")
    
    def _DisplayBooks(self, Books: List[str]) -> None:
        """
        Display books in grid layout.
        
        Args:
            Books: List of book titles
        """
        self._ClearLayout()
        self.CurrentBooks = Books
        
        # Calculate columns
        self._UpdateColumnCount()
        
        # Create book cards
        Row = 0
        Column = 0
        
        for BookTitle in Books:
            # Create book card
            BookCard = BookCard(BookTitle)
            BookCard.BookClicked.connect(self._OnBookClicked)
            
            # Add to layout
            self.GridLayout.addWidget(BookCard, Row, Column)
            self.BookCards.append(BookCard)
            
            # Update position
            Column += 1
            if Column >= self.CurrentColumns:
                Column = 0
                Row += 1
        
        # Add stretch to fill remaining space
        self.GridLayout.setRowStretch(Row + 1, 1)
    
    def _UpdateColumnCount(self) -> None:
        """Calculate number of columns based on width"""
        AvailableWidth = self.width()
        self.PreviousColumns = self.CurrentColumns
        self.CurrentColumns = max(1, (AvailableWidth - self.BaseWidth) // self.ItemWidth)
    
    def _UpdateLayout(self) -> None:
        """Update layout if column count changed"""
        if self.PreviousColumns != self.CurrentColumns and self.CurrentBooks:
            self._DisplayBooks(self.CurrentBooks)
    
    def _OnBookClicked(self, BookTitle: str) -> None:
        """Handle book click events"""
        try:
            Success = self.BookService.OpenBook(BookTitle)
            if not Success:
                QMessageBox.warning(
                    self,
                    "Book Not Found", 
                    f"Could not open book: {BookTitle}\n\nThe PDF file may be missing."
                )
        except Exception as Error:
            self.Logger.error(f"Error opening book {BookTitle}: {Error}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error opening book: {Error}"
            )
    
    def RefreshLayout(self) -> None:
        """Refresh layout (called from MainWindow on resize)"""
        self.ResizeTimer.start(100)
    
    def resizeEvent(self, Event) -> None:
        """Handle resize events"""
        super().resizeEvent(Event)
        self._UpdateColumnCount()
        self.ResizeTimer.start(100)
        
        # Update status with current dimensions
        Width = self.width()
        Height = self.height()
        self.StatusUpdate.emit(f"{Width} x {Height}  C:{self.CurrentColumns}")
