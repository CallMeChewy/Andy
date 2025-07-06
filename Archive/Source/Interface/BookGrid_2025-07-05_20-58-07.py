# File: BookGrid.py
# Path: Source/Interface/BookGrid.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  08:30PM
"""
Description: Enhanced Book Grid Interface with Image Display
Displays books in a grid layout with thumbnails and improved visual design.
"""

import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, 
    QFrame, QLabel, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QPixmap, QFont, QPainter, QPen, QBrush

from Source.Utils.ColorTheme import ColorTheme


class BookCard(QFrame):
    """
    Individual book card widget with thumbnail and title.
    """
    BookClicked = Signal(str)  # Emits book title when clicked
    
    def __init__(self, BookData: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.BookData = BookData
        self.Logger = logging.getLogger(self.__class__.__name__)
        self.SetupUI()
        self.LoadThumbnail()
    
    def SetupUI(self):
        """Setup the card UI layout."""
        self.setObjectName("BookCard")
        self.setProperty("class", "BookCard")
        self.setFixedSize(200, 280)  # Standard card size
        self.setCursor(Qt.PointingHandCursor)
        
        # Main layout
        Layout = QVBoxLayout(self)
        Layout.setContentsMargins(8, 8, 8, 8)
        Layout.setSpacing(5)
        
        # Thumbnail area
        self.ThumbnailLabel = QLabel()
        self.ThumbnailLabel.setFixedSize(180, 220)
        self.ThumbnailLabel.setAlignment(Qt.AlignCenter)
        self.ThumbnailLabel.setStyleSheet("""
            QLabel {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
        """)
        Layout.addWidget(self.ThumbnailLabel)
        
        # Title label
        self.TitleLabel = QLabel()
        self.TitleLabel.setWordWrap(True)
        self.TitleLabel.setAlignment(Qt.AlignCenter)
        self.TitleLabel.setMaximumHeight(45)
        
        # Set title with truncation
        Title = self.BookData.get('Title', 'Unknown Title')
        if len(Title) > 40:
            Title = Title[:37] + "..."
        self.TitleLabel.setText(Title)
        
        # Title font
        TitleFont = QFont()
        TitleFont.setPointSize(9)
        TitleFont.setBold(True)
        self.TitleLabel.setFont(TitleFont)
        
        Layout.addWidget(self.TitleLabel)
        
    def LoadThumbnail(self):
        """Load book thumbnail image."""
        try:
            # Try to find thumbnail
            ThumbnailPath = self.FindThumbnailPath()
            
            if ThumbnailPath and os.path.exists(ThumbnailPath):
                # Load actual thumbnail
                Pixmap = QPixmap(ThumbnailPath)
                if not Pixmap.isNull():
                    # Scale to fit while maintaining aspect ratio
                    ScaledPixmap = Pixmap.scaled(
                        180, 220, 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.ThumbnailLabel.setPixmap(ScaledPixmap)
                    return
            
            # If no thumbnail found, create a placeholder
            self.CreatePlaceholder()
            
        except Exception as Error:
            self.Logger.warning(f"Failed to load thumbnail for {self.BookData.get('Title', 'Unknown')}: {Error}")
            self.CreatePlaceholder()
    
    def FindThumbnailPath(self) -> Optional[str]:
        """
        Find the thumbnail path for this book.
        
        Returns:
            Path to thumbnail file or None if not found
        """
        Title = self.BookData.get('Title', '')
        if not Title:
            return None
        
        # Common thumbnail directories to check (starting with actual location)
        ThumbnailDirs = [
            'Data/Thumbs',           # Actual thumbnail location
            'Assets/Thumbnails',
            'Assets/Images', 
            'Thumbnails',
            'Images'
        ]
        
        # Common thumbnail extensions
        Extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        
        for ThumbnailDir in ThumbnailDirs:
            if os.path.exists(ThumbnailDir):
                for Extension in Extensions:
                    # Try exact title match
                    ThumbnailPath = os.path.join(ThumbnailDir, f"{Title}{Extension}")
                    if os.path.exists(ThumbnailPath):
                        return ThumbnailPath
                    
                    # Try lowercase
                    ThumbnailPath = os.path.join(ThumbnailDir, f"{Title.lower()}{Extension}")
                    if os.path.exists(ThumbnailPath):
                        return ThumbnailPath
        
        return None
    
    def CreatePlaceholder(self):
        """Create a placeholder image for books without thumbnails."""
        # Create a simple placeholder pixmap
        Pixmap = QPixmap(180, 220)
        Pixmap.fill(Qt.white)
        
        # Draw placeholder content
        Painter = QPainter(Pixmap)
        Painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw border
        Pen = QPen(Qt.gray, 2)
        Painter.setPen(Pen)
        Painter.drawRect(2, 2, 176, 216)
        
        # Draw book icon (simple rectangle with lines)
        Painter.setBrush(QBrush(Qt.lightGray))
        Painter.drawRect(50, 60, 80, 100)
        
        # Draw "lines" on the book
        Painter.setPen(QPen(Qt.darkGray, 1))
        for i in range(5):
            y = 80 + (i * 15)
            Painter.drawLine(60, y, 120, y)
        
        # Draw book emoji/icon
        Font = QFont()
        Font.setPointSize(24)
        Painter.setFont(Font)
        Painter.setPen(QPen(Qt.darkBlue))
        Painter.drawText(75, 45, "📚")
        
        # Draw "No Image" text
        Font.setPointSize(10)
        Painter.setFont(Font)
        Painter.setPen(QPen(Qt.gray))
        Painter.drawText(65, 190, "No Image")
        
        Painter.end()
        
        self.ThumbnailLabel.setPixmap(Pixmap)
    
    def mousePressEvent(self, event):
        """Handle mouse click on book card."""
        if event.button() == Qt.LeftButton:
            Title = self.BookData.get('Title', '')
            if Title:
                self.BookClicked.emit(Title)
                self.Logger.info(f"Book card clicked: {Title}")
        super().mousePressEvent(event)


class BookGrid(QWidget):
    """
    Enhanced grid layout for displaying book cards with thumbnails.
    """
    BookClicked = Signal(str)  # Emits book title when clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.Logger = logging.getLogger(self.__class__.__name__)
        self.Books = []
        self.ColorTheme = ColorTheme()
        self.MaxColumns = 5  # Maximum columns in grid
        self.SetupUI()
        self.Logger.info("BookGrid initialized successfully")
    
    def SetupUI(self):
        """Setup the grid UI components."""
        # Main layout
        self.MainLayout = QVBoxLayout(self)
        self.MainLayout.setContentsMargins(10, 10, 10, 10)
        
        # Scroll area
        self.ScrollArea = QScrollArea()
        self.ScrollArea.setWidgetResizable(True)
        self.ScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.ScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Grid container
        self.GridContainer = QWidget()
        self.GridLayout = QGridLayout(self.GridContainer)
        self.GridLayout.setSpacing(10)
        self.GridLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.ScrollArea.setWidget(self.GridContainer)
        self.MainLayout.addWidget(self.ScrollArea)
        
        # Apply theme
        self.ApplyTheme()
    
    def ApplyTheme(self):
        """Apply the color theme to the grid."""
        StyleSheet = self.ColorTheme.GetStyleSheet("Professional")
        self.setStyleSheet(StyleSheet)
    
    def DisplayBooks(self, Books: List[Dict[str, Any]]):
        """
        Display the list of books in the grid.
        
        Args:
            Books: List of book dictionaries to display
        """
        try:
            self.ClearGrid()
            self.Books = Books
            
            if not Books:
                self.ShowEmptyMessage()
                return
            
            # Calculate number of columns based on container width
            ContainerWidth = self.ScrollArea.viewport().width()
            CardWidth = 220  # Card width + margin
            NumColumns = min(max(ContainerWidth // CardWidth, 1), self.MaxColumns)
            
            # Add book cards to grid
            for Index, Book in enumerate(Books):
                Row = Index // NumColumns
                Col = Index % NumColumns
                
                BookCard = self.CreateBookCard(Book)
                self.GridLayout.addWidget(BookCard, Row, Col)
            
            # Add placeholder cards to fill the last row if needed
            TotalBooks = len(Books)
            LastRowBooks = TotalBooks % NumColumns
            if LastRowBooks > 0:
                PlaceholdersNeeded = NumColumns - LastRowBooks
                for i in range(PlaceholdersNeeded):
                    PlaceholderCard = self.CreatePlaceholderCard()
                    Row = TotalBooks // NumColumns
                    Col = LastRowBooks + i
                    self.GridLayout.addWidget(PlaceholderCard, Row, Col)
            
            self.Logger.info(f"Displayed {len(Books)} books in {NumColumns} columns")
            
        except Exception as Error:
            self.Logger.error(f"Failed to display books: {Error}")
    
    def CreateBookCard(self, BookData: Dict[str, Any]) -> BookCard:
        """
        Create a book card widget.
        
        Args:
            BookData: Dictionary containing book information
            
        Returns:
            BookCard widget
        """
        Card = BookCard(BookData, self)
        Card.BookClicked.connect(self.BookClicked.emit)
        return Card
    
    def CreatePlaceholderCard(self) -> QFrame:
        """
        Create an invisible placeholder card to maintain grid alignment.
        
        Returns:
            Invisible placeholder frame
        """
        Placeholder = QFrame()
        Placeholder.setFixedSize(200, 280)
        Placeholder.setStyleSheet("background: transparent; border: none;")
        return Placeholder
    
    def ClearGrid(self):
        """Clear all items from the grid."""
        while self.GridLayout.count():
            Child = self.GridLayout.takeAt(0)
            if Child.widget():
                Child.widget().deleteLater()
    
    def ShowEmptyMessage(self):
        """Show message when no books are found."""
        EmptyLabel = QLabel("No books found matching your criteria.")
        EmptyLabel.setAlignment(Qt.AlignCenter)
        EmptyLabel.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                padding: 50px;
            }
        """)
        self.GridLayout.addWidget(EmptyLabel, 0, 0)
    
    def resizeEvent(self, event):
        """Handle window resize to adjust grid columns."""
        super().resizeEvent(event)
        
        # Use a timer to avoid excessive recalculation during resize
        if hasattr(self, 'ResizeTimer'):
            self.ResizeTimer.stop()
        else:
            self.ResizeTimer = QTimer()
            self.ResizeTimer.setSingleShot(True)
            self.ResizeTimer.timeout.connect(self.RefreshGrid)
        
        self.ResizeTimer.start(100)  # 100ms delay
    
    def RefreshGrid(self):
        """Refresh the grid layout with current books."""
        if self.Books:
            self.DisplayBooks(self.Books)