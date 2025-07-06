# File: BookGrid.py
# Path: Source/Interface/BookGrid.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-05
# Last Modified: 2025-07-05  09:25PM
"""
Description: FIXED - Book Grid with Black Text on Light Backgrounds
Fixed text color for better readability on light purple/blue backgrounds.
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


class BookCard(QFrame):
    """Individual book card widget with thumbnail and title."""
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
        self.setFixedSize(200, 280)  # Standard card size
        self.setCursor(Qt.PointingHandCursor)
        
        # FIXED: Better card styling that works with blue gradient background
        self.setStyleSheet("""
            QFrame#BookCard {
                background-color: rgba(255, 255, 255, 220);
                border: 2px solid rgba(255, 255, 255, 100);
                border-radius: 8px;
                padding: 8px;
                margin: 5px;
            }
            QFrame#BookCard:hover {
                background-color: rgba(255, 255, 255, 240);
                border-color: rgba(255, 255, 255, 200);
            }
        """)
        
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
        Title = self.BookData.get('Title', self.BookData.get('title', 'Unknown Title'))
        if len(Title) > 40:
            Title = Title[:37] + "..."
        self.TitleLabel.setText(Title)
        
        # FIXED: Black text for title on card background
        TitleFont = QFont()
        TitleFont.setPointSize(9)
        TitleFont.setBold(True)
        self.TitleLabel.setFont(TitleFont)
        self.TitleLabel.setStyleSheet("color: #000000; background: transparent;")
        
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
        """Find the thumbnail path for this book."""
        # Handle different title field names
        Title = self.BookData.get('Title', self.BookData.get('title', ''))
        if not Title:
            return None
        
        # Check thumbnail directories (starting with correct location)
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
            # Handle different title field names
            Title = self.BookData.get('Title', self.BookData.get('title', ''))
            if Title:
                self.BookClicked.emit(Title)
                self.Logger.info(f"Book card clicked: {Title}")
        super().mousePressEvent(event)


class BookGrid(QWidget):
    """FIXED - Book Grid with proper text colors on light backgrounds."""
    BookClicked = Signal(str)  # Emits book title when clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.Logger = logging.getLogger(self.__class__.__name__)
        self.Books = []
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
        
        # FIXED: Transparent scroll area to show gradient background
        self.ScrollArea.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: rgba(255, 255, 255, 100);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(255, 255, 255, 200);
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(255, 255, 255, 255);
            }
        """)
        
        # Grid container
        self.GridContainer = QWidget()
        # FIXED: Transparent container to show gradient
        self.GridContainer.setStyleSheet("background-color: transparent;")
        
        self.GridLayout = QGridLayout(self.GridContainer)
        self.GridLayout.setSpacing(10)
        self.GridLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.ScrollArea.setWidget(self.GridContainer)
        self.MainLayout.addWidget(self.ScrollArea)
    
    def DisplayBooks(self, Books: List[Dict[str, Any]]):
        """Display the list of books in the grid."""
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
        """Create a book card widget."""
        Card = BookCard(BookData, self)
        Card.BookClicked.connect(self.BookClicked.emit)
        return Card
    
    def CreatePlaceholderCard(self) -> QFrame:
        """Create an invisible placeholder card to maintain grid alignment."""
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
        """FIXED - Show message with BLACK text on light background."""
        EmptyLabel = QLabel("No books found matching your criteria.")
        EmptyLabel.setAlignment(Qt.AlignCenter)
        
        # FIXED: Black text on semi-transparent light background for readability
        EmptyLabel.setStyleSheet("""
            QLabel {
                color: #000000;
                background-color: rgba(255, 255, 255, 180);
                font-size: 16px;
                font-weight: bold;
                padding: 20px;
                border-radius: 8px;
                border: 2px solid rgba(255, 255, 255, 100);
            }
        """)
        
        self.GridLayout.addWidget(EmptyLabel, 0, 0, 1, 3)  # Span 3 columns
    
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