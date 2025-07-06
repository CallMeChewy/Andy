# File: BookGrid.py
# Path: Source/Interface/BookGrid.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-06
# Last Modified: 2025-07-06  11:26AM
"""
Description: Fixed Book Grid with Proper PySide6 Imports
Enhanced book display grid with proper imports and resize handling.
"""

import logging
import math
from typing import List, Dict, Optional
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame, QLabel,
    QPushButton, QGridLayout, QSizePolicy, QApplication
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import QPixmap, QFont, QPainter, QBrush, QColor

from Source.Core.BookService import BookService


class BookCard(QFrame):
    """
    Individual book card widget with enhanced styling.
    """
    
    BookClicked = Signal(dict)
    
    def __init__(self, BookData: dict):
        super().__init__()
        
        self.BookData = BookData
        self.Logger = logging.getLogger(__name__)
        
        # Set up the card
        self._SetupCard()
        self._LoadBookCover()
    
    def _SetupCard(self) -> None:
        """Setup the book card layout and styling"""
        # Set fixed size for consistent grid
        self.setFixedSize(180, 280)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setLineWidth(2)
        
        # Create layout
        Layout = QVBoxLayout(self)
        Layout.setContentsMargins(8, 8, 8, 8)
        Layout.setSpacing(5)
        
        # Cover image label
        self.CoverLabel = QLabel()
        self.CoverLabel.setAlignment(Qt.AlignCenter)
        self.CoverLabel.setMinimumSize(160, 200)
        self.CoverLabel.setMaximumSize(160, 200)
        self.CoverLabel.setStyleSheet("""
            QLabel {
                border: 2px solid #4CAF50;
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.9);
                padding: 2px;
            }
        """)
        Layout.addWidget(self.CoverLabel)
        
        # Title label
        Title = self.BookData.get('Title', 'Unknown Title')
        self.TitleLabel = QLabel(Title[:25] + "..." if len(Title) > 25 else Title)
        self.TitleLabel.setAlignment(Qt.AlignCenter)
        self.TitleLabel.setWordWrap(True)
        self.TitleLabel.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 12px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 0.7);
                border-radius: 4px;
                padding: 4px;
            }
        """)
        Layout.addWidget(self.TitleLabel)
        
        # Set hover effects
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }
            QFrame:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border: 3px solid #FFC107;
            }
        """)
    
    def _LoadBookCover(self) -> None:
        """Load and display the book cover"""
        try:
            # Try to load cover from BLOB data first
            if 'CoverImage' in self.BookData and self.BookData['CoverImage']:
                Pixmap = QPixmap()
                if Pixmap.loadFromData(self.BookData['CoverImage']):
                    # Scale to fit the label
                    ScaledPixmap = Pixmap.scaled(
                        156, 196, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    self.CoverLabel.setPixmap(ScaledPixmap)
                    return
            
            # Fallback to file-based cover
            CoverPath = Path(f"Data/Covers/{self.BookData.get('ID', 0)}.jpg")
            if CoverPath.exists():
                Pixmap = QPixmap(str(CoverPath))
                ScaledPixmap = Pixmap.scaled(
                    156, 196, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.CoverLabel.setPixmap(ScaledPixmap)
                return
            
            # No cover found - use placeholder
            self._CreatePlaceholder()
            
        except Exception as Error:
            self.Logger.error(f"Failed to load cover for book {self.BookData.get('ID', 'Unknown')}: {Error}")
            self._CreatePlaceholder()
    
    def _CreatePlaceholder(self) -> None:
        """Create a placeholder image for books without covers"""
        Placeholder = QPixmap(156, 196)
        Placeholder.fill(QColor("#E0E0E0"))
        
        # Draw placeholder text
        Painter = QPainter(Placeholder)
        Painter.setPen(QColor("#757575"))
        Font = QFont("Arial", 12, QFont.Bold)
        Painter.setFont(Font)
        Painter.drawText(Placeholder.rect(), Qt.AlignCenter, "No Cover\nAvailable")
        Painter.end()
        
        self.CoverLabel.setPixmap(Placeholder)
    
    def mousePressEvent(self, event):
        """Handle mouse click on book card"""
        if event.button() == Qt.LeftButton:
            self.BookClicked.emit(self.BookData)
        super().mousePressEvent(event)


class BookGrid(QWidget):
    """
    Fixed book grid with proper PySide6 imports and enhanced functionality.
    
    Fixes applied:
    - Proper PySide6 Signal imports
    - Enhanced resize handling
    - Better grid calculations
    - Improved performance
    """
    
    BookSelected = Signal(dict)
    
    def __init__(self, BookService: BookService):
        super().__init__()
        
        self.Logger = logging.getLogger(__name__)
        self.BookService = BookService
        
        # Current state
        self.CurrentBooks: List[Dict] = []
        self.CurrentFilters: Dict = {}
        self.BookCards: List[BookCard] = []
        
        # Layout settings
        self.ColumnsCount = 4
        self.CardWidth = 180
        self.CardHeight = 280
        
        # Initialize UI
        self._SetupUI()
        self._LoadAllBooks()
        
        self.Logger.info("Book grid initialized with fixes")
    
    def _SetupUI(self) -> None:
        """Setup the book grid user interface"""
        # Main layout
        MainLayout = QVBoxLayout(self)
        MainLayout.setContentsMargins(10, 10, 10, 10)
        MainLayout.setSpacing(5)
        
        # Create scroll area
        self.ScrollArea = QScrollArea()
        self.ScrollArea.setWidgetResizable(True)
        self.ScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        MainLayout.addWidget(self.ScrollArea)
        
        # Create scrollable content widget
        self.ContentWidget = QWidget()
        self.ScrollArea.setWidget(self.ContentWidget)
        
        # Create grid layout for book cards
        self.GridLayout = QGridLayout(self.ContentWidget)
        self.GridLayout.setSpacing(15)
        self.GridLayout.setContentsMargins(20, 20, 20, 20)
        
        # Apply styling
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            QScrollBar:vertical {
                background-color: rgba(255, 255, 255, 0.1);
                width: 16px;
                border-radius: 8px;
                margin: 0;
            }
            
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                min-height: 30px;
                margin: 2px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: rgba(255, 255, 255, 0.5);
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
    
    def _LoadAllBooks(self) -> None:
        """Load all books from the database"""
        try:
            if self.BookService:
                self.CurrentBooks = self.BookService.GetAllBooks()
                self._UpdateDisplay()
                self.Logger.info(f"Loaded {len(self.CurrentBooks)} books")
            
        except Exception as Error:
            self.Logger.error(f"Failed to load books: {Error}")
    
    def _UpdateDisplay(self) -> None:
        """Update the book grid display"""
        try:
            # Clear existing cards
            self._ClearGrid()
            
            # Calculate columns based on available width
            self._CalculateColumns()
            
            # Add book cards to grid
            Row, Col = 0, 0
            for BookData in self.CurrentBooks:
                Card = BookCard(BookData)
                Card.BookClicked.connect(self._OnBookSelected)
                
                self.GridLayout.addWidget(Card, Row, Col)
                self.BookCards.append(Card)
                
                Col += 1
                if Col >= self.ColumnsCount:
                    Col = 0
                    Row += 1
            
            # Add stretch to center the grid
            self.GridLayout.setRowStretch(Row + 1, 1)
            
            # Process events to update display
            QApplication.processEvents()
            
            self.Logger.debug(f"Display updated with {len(self.CurrentBooks)} books in {self.ColumnsCount} columns")
            
        except Exception as Error:
            self.Logger.error(f"Failed to update display: {Error}")
    
    def _ClearGrid(self) -> None:
        """Clear all widgets from the grid"""
        try:
            # Remove all book cards
            for Card in self.BookCards:
                self.GridLayout.removeWidget(Card)
                Card.deleteLater()
            
            self.BookCards.clear()
            
        except Exception as Error:
            self.Logger.error(f"Failed to clear grid: {Error}")
    
    def _CalculateColumns(self) -> None:
        """Calculate optimal number of columns based on available width"""
        try:
            AvailableWidth = self.ScrollArea.viewport().width()
            
            # Account for margins and spacing
            UsableWidth = AvailableWidth - 40  # 20px margin on each side
            
            # Calculate number of columns
            ColumnsCount = max(1, UsableWidth // (self.CardWidth + 15))  # 15px spacing
            
            # Limit to reasonable range
            self.ColumnsCount = min(max(ColumnsCount, 2), 8)
            
            self.Logger.debug(f"Calculated {self.ColumnsCount} columns for width {AvailableWidth}")
            
        except Exception as Error:
            self.Logger.error(f"Failed to calculate columns: {Error}")
            self.ColumnsCount = 4  # Fallback
    
    def _OnBookSelected(self, BookData: dict) -> None:
        """Handle book selection"""
        try:
            self.BookSelected.emit(BookData)
            self.Logger.info(f"Book selected: {BookData.get('Title', 'Unknown')}")
            
            # Open PDF if available
            if self.BookService:
                self.BookService.OpenBook(BookData.get('ID', 0))
            
        except Exception as Error:
            self.Logger.error(f"Failed to handle book selection: {Error}")
    
    def ApplyFilters(self, Filters: dict) -> None:
        """Apply filters to the book display"""
        try:
            self.CurrentFilters = Filters.copy()
            
            if self.BookService:
                # Get filtered books from service
                FilteredBooks = self.BookService.FilterBooks(
                    Category=Filters.get('Category', ''),
                    Subject=Filters.get('Subject', ''),
                    SearchText=Filters.get('SearchText', '')
                )
                
                self.CurrentBooks = FilteredBooks
                self._UpdateDisplay()
                
                self.Logger.info(f"Applied filters: {len(FilteredBooks)} books match criteria")
            
        except Exception as Error:
            self.Logger.error(f"Failed to apply filters: {Error}")
    
    def HandleResize(self) -> None:
        """Handle window resize events"""
        try:
            # Recalculate columns and update display
            OldColumns = self.ColumnsCount
            self._CalculateColumns()
            
            # Only update if column count changed
            if OldColumns != self.ColumnsCount:
                self._UpdateDisplay()
                self.Logger.debug(f"Resize handled: columns changed from {OldColumns} to {self.ColumnsCount}")
            
        except Exception as Error:
            self.Logger.error(f"Failed to handle resize: {Error}")
    
    def resizeEvent(self, event):
        """Handle widget resize events"""
        super().resizeEvent(event)
        
        # Use timer to avoid too many updates during resizing
        if hasattr(self, '_ResizeTimer'):
            self._ResizeTimer.stop()
        
        self._ResizeTimer = QTimer()
        self._ResizeTimer.timeout.connect(self.HandleResize)
        self._ResizeTimer.setSingleShot(True)
        self._ResizeTimer.start(100)  # 100ms delay
    
    def GetBookCount(self) -> int:
        """Get the current number of displayed books"""
        return len(self.CurrentBooks)
    
    def RefreshDisplay(self) -> None:
        """Refresh the entire display"""
        try:
            self._LoadAllBooks()
            self.Logger.info("Book grid display refreshed")
            
        except Exception as Error:
            self.Logger.error(f"Failed to refresh display: {Error}")