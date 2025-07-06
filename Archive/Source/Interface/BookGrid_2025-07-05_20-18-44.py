# File: BookGrid.py
# Path: Source/Interface/BookGrid.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  07:55PM
"""
Description: BookGrid with PySide6 Signal Compatibility
Fixed import to use PySide6.QtCore.Signal instead of pyqtSignal.
Implements proper 5-column max layout with left justification and placeholder cards.
"""

import logging
import os
from typing import List, Optional, Callable
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QMessageBox, QSizePolicy
)
from PySide6.QtCore import QTimer, Signal, Qt, QSize  # ✅ FIXED: Signal instead of pyqtSignal
from PySide6.QtGui import QPixmap, QFont

from Source.Core.BookService import BookService
from Source.Data.DatabaseModels import Book


class BookCard(QFrame):
    """Individual book card widget with cover and title"""
    
    # ✅ FIXED: Use Signal instead of pyqtSignal for PySide6
    BookClicked = Signal(str)  # Emits book title when clicked
    
    def __init__(self, Book: Book, parent=None):
        """
        Initialize book card.
        
        Args:
            Book: Book data object
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.Book = Book
        self.Logger = logging.getLogger(__name__)
        
        # Set card properties
        self.setFixedSize(180, 240)  # Standard card size
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            BookCard {
                background-color: rgba(255, 255, 255, 230);
                border: 2px solid rgba(0, 0, 0, 100);
                border-radius: 8px;
                margin: 2px;
            }
            BookCard:hover {
                background-color: rgba(255, 255, 255, 255);
                border: 2px solid rgba(0, 100, 200, 200);
            }
        """)
        
        # Create layout
        Layout = QVBoxLayout(self)
        Layout.setContentsMargins(5, 5, 5, 5)
        Layout.setSpacing(3)
        
        # Book cover image
        self.CoverLabel = QLabel()
        self.CoverLabel.setFixedSize(170, 200)
        self.CoverLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.CoverLabel.setStyleSheet("border: 1px solid gray; background-color: white;")
        Layout.addWidget(self.CoverLabel)
        
        # Book title
        self.TitleLabel = QLabel(Book.Title)
        self.TitleLabel.setFont(QFont("Arial", 8))
        self.TitleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.TitleLabel.setWordWrap(True)
        self.TitleLabel.setMaximumHeight(30)
        self.TitleLabel.setStyleSheet("border: none; color: black;")
        Layout.addWidget(self.TitleLabel)
        
        # Load cover image
        self._LoadCoverImage()
        
        # Make clickable
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def _LoadCoverImage(self) -> None:
        """Load book cover image"""
        try:
            # Try to load thumbnail
            ThumbnailPath = Path("Assets/Thumbnails") / f"{self.Book.Title}.jpg"
            
            if ThumbnailPath.exists():
                Pixmap = QPixmap(str(ThumbnailPath))
                if not Pixmap.isNull():
                    # Scale image to fit
                    ScaledPixmap = Pixmap.scaled(
                        165, 195, 
                        Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.CoverLabel.setPixmap(ScaledPixmap)
                    return
            
            # Fallback to placeholder
            self.CoverLabel.setText("No Cover\nAvailable")
            self.CoverLabel.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0; color: gray;")
            
        except Exception as Error:
            self.Logger.error(f"Failed to load cover for '{self.Book.Title}': {Error}")
            self.CoverLabel.setText("Error Loading\nCover")
    
    def mousePressEvent(self, Event) -> None:
        """Handle mouse clicks"""
        if Event.button() == Qt.MouseButton.LeftButton:
            self.BookClicked.emit(self.Book.Title)
        super().mousePressEvent(Event)


class PlaceholderCard(QFrame):
    """Invisible placeholder card to fill grid rows"""
    
    def __init__(self, parent=None):
        """Initialize invisible placeholder"""
        super().__init__(parent)
        
        # Same size as BookCard but invisible
        self.setFixedSize(180, 240)
        self.setStyleSheet("background-color: transparent; border: none;")
        
        # Make sure it doesn't interfere with layout
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)


class BookGrid(QWidget):
    """
    Main book display grid with simple interface compatibility.
    Works with plain List[Book] instead of SearchResult objects.
    Supports max 5 columns and uses placeholders to prevent centering.
    """
    
    # ✅ FIXED: Use Signal instead of pyqtSignal for PySide6
    StatusUpdate = Signal(str)
    BookOpened = Signal(str)
    
    def __init__(self, BookService: BookService, parent=None):
        """
        Initialize book grid.
        
        Args:
            BookService: Service for database operations
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Core dependencies
        self.BookService = BookService
        self.Logger = logging.getLogger(__name__)
        
        # Grid configuration
        self.MaxColumns = 5  # Maximum books per row
        self.CurrentColumns = 1
        self.CurrentBooks = []
        self.BookCards = []
        self.PlaceholderCards = []
        
        # Layout calculation
        self.CardWidth = 185  # BookCard width + margin
        self.BaseWidth = 50   # Minimum margin for layout
        
        # Resize timer for debouncing
        self.ResizeTimer = QTimer()
        self.ResizeTimer.setSingleShot(True)
        self.ResizeTimer.timeout.connect(self._UpdateLayout)
        
        # Event handlers
        self.OnBookOpened: Optional[Callable[[str], None]] = None
        
        # Create UI
        self._CreateUI()
        
        self.Logger.info("BookGrid initialized successfully")
    
    def _CreateUI(self) -> None:
        """Create the grid user interface"""
        # Main layout
        MainLayout = QVBoxLayout(self)
        MainLayout.setContentsMargins(10, 10, 10, 10)
        MainLayout.setSpacing(0)
        
        # Create scroll area
        self.ScrollArea = QScrollArea()
        self.ScrollArea.setWidgetResizable(True)
        self.ScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.ScrollArea.setStyleSheet("""
            QScrollArea {
                background-color: rgba(0, 50, 100, 50);
                border: none;
            }
            QScrollBar:vertical {
                background-color: rgba(255, 255, 255, 100);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(0, 100, 200, 200);
                border-radius: 6px;
                min-height: 20px;
            }
        """)
        MainLayout.addWidget(self.ScrollArea)
        
        # Create scrollable content widget
        self.ContentWidget = QWidget()
        self.ContentWidget.setStyleSheet("background-color: transparent;")
        self.ScrollArea.setWidget(self.ContentWidget)
        
        # Create grid layout for books
        self.GridLayout = QGridLayout(self.ContentWidget)
        self.GridLayout.setContentsMargins(10, 10, 10, 10)
        self.GridLayout.setSpacing(10)
        self.GridLayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    
    def DisplayBooks(self, Books: List[Book]) -> None:
        """
        ✅ FIXED: Accept plain List[Book] instead of SearchResult objects.
        Display list of books in grid with proper left justification.
        
        Args:
            Books: List of book objects to display
        """
        try:
            # Clear existing display
            self._ClearGrid()
            
            # Store current books
            self.CurrentBooks = Books
            
            if not Books:
                # Show "no books" message
                self._ShowEmptyMessage()
                return
            
            # Calculate optimal columns
            self._UpdateColumnCount()
            
            # Create book cards
            self._CreateBookCards()
            
            # Add placeholder cards to fill remaining positions
            self._AddPlaceholderCards()
            
            # Update status
            self.StatusUpdate.emit(f"Displaying {len(Books)} books in {self.CurrentColumns} columns")
            self.Logger.info(f"Displayed {len(Books)} books")
            
        except Exception as Error:
            self.Logger.error(f"Failed to display books: {Error}")
            self._ShowErrorMessage(str(Error))
    
    def _ClearGrid(self) -> None:
        """Clear all widgets from grid"""
        # Remove all book cards
        for Card in self.BookCards:
            self.GridLayout.removeWidget(Card)
            Card.deleteLater()
        self.BookCards.clear()
        
        # Remove all placeholder cards
        for Placeholder in self.PlaceholderCards:
            self.GridLayout.removeWidget(Placeholder)
            Placeholder.deleteLater()
        self.PlaceholderCards.clear()
        
        # Clear any remaining widgets
        while self.GridLayout.count():
            Child = self.GridLayout.takeAt(0)
            if Child.widget():
                Child.widget().deleteLater()
    
    def _UpdateColumnCount(self) -> None:
        """Calculate optimal number of columns based on width"""
        AvailableWidth = self.width() - 40  # Account for margins and scrollbar
        
        if AvailableWidth > 0:
            PossibleColumns = max(1, AvailableWidth // self.CardWidth)
            self.CurrentColumns = min(PossibleColumns, self.MaxColumns)
        else:
            self.CurrentColumns = 1
            
        self.Logger.debug(f"Updated columns: {self.CurrentColumns} (width: {AvailableWidth})")
    
    def _CreateBookCards(self) -> None:
        """Create book cards and place them in grid"""
        Row = 0
        Column = 0
        
        for Book in self.CurrentBooks:
            # Create book card
            BookCard = BookCard(Book)
            BookCard.BookClicked.connect(self._OnBookClicked)
            
            # Add to grid
            self.GridLayout.addWidget(BookCard, Row, Column)
            self.BookCards.append(BookCard)
            
            # Update position
            Column += 1
            if Column >= self.CurrentColumns:
                Column = 0
                Row += 1
    
    def _AddPlaceholderCards(self) -> None:
        """Add invisible placeholder cards to fill remaining grid positions"""
        if not self.CurrentBooks:
            return
            
        # Calculate last row position
        LastRow = (len(self.CurrentBooks) - 1) // self.CurrentColumns
        LastColumn = (len(self.CurrentBooks) - 1) % self.CurrentColumns
        
        # Add placeholders to fill the last row
        for Column in range(LastColumn + 1, self.CurrentColumns):
            Placeholder = PlaceholderCard()
            self.GridLayout.addWidget(Placeholder, LastRow, Column)
            self.PlaceholderCards.append(Placeholder)
            
        self.Logger.debug(f"Added {len(self.PlaceholderCards)} placeholder cards")
    
    def _ShowEmptyMessage(self) -> None:
        """Show message when no books to display"""
        MessageLabel = QLabel("No books found matching your criteria")
        MessageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        MessageLabel.setFont(QFont("Arial", 14))
        MessageLabel.setStyleSheet("color: white; padding: 50px;")
        
        self.GridLayout.addWidget(MessageLabel, 0, 0, 1, self.MaxColumns)
    
    def _ShowErrorMessage(self, ErrorText: str) -> None:
        """Show error message"""
        MessageLabel = QLabel(f"Error loading books:\n{ErrorText}")
        MessageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        MessageLabel.setFont(QFont("Arial", 12))
        MessageLabel.setStyleSheet("color: red; padding: 50px;")
        
        self.GridLayout.addWidget(MessageLabel, 0, 0, 1, self.MaxColumns)
    
    def _OnBookClicked(self, BookTitle: str) -> None:
        """
        Handle book click events.
        
        Args:
            BookTitle: Title of clicked book
        """
        try:
            Success = self.BookService.OpenBook(BookTitle)
            
            if not Success:
                QMessageBox.warning(
                    self,
                    "Book Not Found",
                    f"Could not open book: {BookTitle}\n\nThe PDF file may be missing or moved."
                )
            else:
                # Notify external handlers
                self.BookOpened.emit(BookTitle)
                if self.OnBookOpened:
                    self.OnBookOpened(BookTitle)
                    
        except Exception as Error:
            self.Logger.error(f"Failed to open book '{BookTitle}': {Error}")
            QMessageBox.critical(
                self,
                "Error Opening Book", 
                f"An error occurred while opening the book:\n\n{Error}"
            )
    
    def _UpdateLayout(self) -> None:
        """Update layout after resize"""
        if self.CurrentBooks:
            OldColumns = self.CurrentColumns
            self._UpdateColumnCount()
            
            # Only rebuild if column count changed
            if OldColumns != self.CurrentColumns:
                self.DisplayBooks(self.CurrentBooks)
    
    def resizeEvent(self, Event) -> None:
        """Handle resize events with debouncing"""
        super().resizeEvent(Event)
        
        # Start resize timer (debounced)
        self.ResizeTimer.start(150)
        
        # Update status with current dimensions
        Width = self.width()
        Height = self.height()
        self.StatusUpdate.emit(f"{Width} x {Height}  C:{self.CurrentColumns}")
    
    # =================================================================
    # PUBLIC INTERFACE
    # =================================================================
    
    def SetEventHandlers(self, OnBookOpened: Optional[Callable[[str], None]] = None) -> None:
        """
        Set event handlers for external communication.
        
        Args:
            OnBookOpened: Called when a book is successfully opened
        """
        if OnBookOpened:
            self.OnBookOpened = OnBookOpened
    
    def RefreshLayout(self) -> None:
        """Force refresh of grid layout"""
        self._UpdateColumnCount()
        if self.CurrentBooks:
            self.DisplayBooks(self.CurrentBooks)
    
    def GetCurrentBooks(self) -> List[Book]:
        """
        Get currently displayed books.
        
        Returns:
            List of books currently shown in grid
        """
        return self.CurrentBooks.copy()
    
    def GetGridStatistics(self) -> dict:
        """
        Get grid layout statistics.
        
        Returns:
            Dictionary with grid metrics
        """
        return {
            'BookCount': len(self.CurrentBooks),
            'Columns': self.CurrentColumns,
            'MaxColumns': self.MaxColumns,
            'Rows': (len(self.CurrentBooks) + self.CurrentColumns - 1) // self.CurrentColumns if self.CurrentColumns > 0 else 0,
            'PlaceholderCount': len(self.PlaceholderCards),
            'GridWidth': self.width(),
            'GridHeight': self.height(),
            'CardWidth': self.CardWidth
        }