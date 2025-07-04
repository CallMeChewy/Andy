# File: BookGrid.py
# Path: Source/Interface/BookGrid.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  15:30PM
"""
Description: Anderson's Library Book Grid Component
Main book display area with responsive grid layout and hover effects.
Provides scalable book browsing interface with dynamic column calculation.

Purpose: Manages the visual presentation of books in a responsive grid format,
handling layout calculations, hover effects, and book selection events.
"""

import os
import logging
from typing import List, Optional, Callable
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QScrollArea, QGridLayout, QLabel, QHBoxLayout, QVBoxLayout,
    QSizePolicy, QSpacerItem, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QEvent
from PySide6.QtGui import QPixmap, QFont, QPen, QPainter

from ..Core.BookService import BookService
from ..Data.DatabaseModels import Book


class HoverHighlightWidget(QWidget):
    """
    Widget that highlights on hover and handles book selection clicks.
    Provides visual feedback and click handling for individual books.
    """
    
    def __init__(self, MainWindow, BookTitle: str, *args, **kwargs):
        """
        Initialize hover widget for a book.
        
        Args:
            MainWindow: Reference to main application window
            BookTitle: Title of the book this widget represents
        """
        super().__init__(*args, **kwargs)
        
        self.MainWindow = MainWindow
        self.BookTitle = BookTitle
        self.IsHovered = False
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
    
    def enterEvent(self, Event) -> None:
        """Handle mouse enter for hover highlight"""
        self.IsHovered = True
        self.update()
    
    def leaveEvent(self, Event) -> None:
        """Handle mouse leave to remove highlight"""
        self.IsHovered = False
        self.update()
    
    def mousePressEvent(self, Event) -> None:
        """Handle mouse click to select/open book"""
        if Event.button() == Qt.LeftButton and hasattr(self.MainWindow, 'OpenBook'):
            self.MainWindow.OpenBook(self.BookTitle)
    
    def paintEvent(self, Event) -> None:
        """Custom paint to show hover highlight"""
        super().paintEvent(Event)
        
        if self.IsHovered:
            Painter = QPainter(self)
            Painter.setPen(QPen(Qt.red, 8))
            Painter.drawRect(self.rect())


class BookCard(QWidget):
    """
    Individual book card widget displaying cover image and title.
    Encapsulates the visual representation of a single book.
    """
    
    def __init__(self, BookData: Book, MainWindow, Parent=None):
        """
        Initialize book card with book data.
        
        Args:
            BookData: Book object with metadata
            MainWindow: Reference to main application window
            Parent: Parent widget
        """
        super().__init__(Parent)
        
        self.BookData = BookData
        self.MainWindow = MainWindow
        self.Logger = logging.getLogger(__name__)
        
        self._SetupCard()
    
    def _SetupCard(self) -> None:
        """Create and layout card components"""
        # Create hover-enabled container
        self.HoverWidget = HoverHighlightWidget(self.MainWindow, self.BookData.Title)
        
        # Main layout for the card
        CardLayout = QVBoxLayout(self)
        CardLayout.setContentsMargins(0, 0, 0, 0)
        CardLayout.addWidget(self.HoverWidget)
        
        # Content layout inside hover widget
        ContentLayout = QHBoxLayout(self.HoverWidget)
        ContentLayout.setContentsMargins(3, 3, 5, 5)
        
        # Create image label
        self.ImageLabel = self._CreateImageLabel()
        ContentLayout.addWidget(self.ImageLabel)
        
        # Create description label
        self.DescriptionLabel = self._CreateDescriptionLabel()
        ContentLayout.addWidget(self.DescriptionLabel)
    
    def _CreateImageLabel(self) -> QLabel:
        """
        Create image label with book cover or placeholder.
        
        Returns:
            QLabel with book cover image
        """
        ImageLabel = QLabel()
        
        # Try to load cover image
        CoverPath = self.BookData.GetCoverImagePath()
        Pixmap = QPixmap(CoverPath)
        
        if Pixmap.isNull():
            # Fallback: try different path or show error text
            AlternatePath = os.path.join("Covers", f"{Path(self.BookData.FileName).stem}.png")
            Pixmap = QPixmap(AlternatePath)
            
            if Pixmap.isNull():
                ImageLabel.setText("No Cover")
                ImageLabel.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
                ImageLabel.setAlignment(Qt.AlignCenter)
            else:
                # Scale the image to appropriate size
                ScaledPixmap = Pixmap.scaled(105, 135, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                ImageLabel.setPixmap(ScaledPixmap)
        else:
            # Scale the image to appropriate size (60% of original 175x225)
            ScaledPixmap = Pixmap.scaled(105, 135, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            ImageLabel.setPixmap(ScaledPixmap)
        
        return ImageLabel
    
    def _CreateDescriptionLabel(self) -> QLabel:
        """
        Create description label with book title and metadata.
        
        Returns:
            QLabel with book information
        """
        DescriptionLabel = QLabel()
        
        # Set font
        Font = QFont("Arial", 11)
        DescriptionLabel.setFont(Font)
        
        # Create description text
        DisplayText = self._FormatBookDescription()
        DescriptionLabel.setText(DisplayText)
        
        # Configure label properties
        DescriptionLabel.setWordWrap(True)
        DescriptionLabel.setFixedSize(105, 135)  # Match image size
        DescriptionLabel.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        return DescriptionLabel
    
    def _FormatBookDescription(self) -> str:
        """
        Format book information for display.
        
        Returns:
            Formatted description string
        """
        Lines = []
        
        # Book title (primary)
        Title = self.BookData.GetDisplayTitle()
        if len(Title) > 50:
            Title = Title[:47] + "..."
        Lines.append(f"<b>{Title}</b>")
        
        # Category and subject information
        if self.BookData.CategoryName or self.BookData.SubjectName:
            CategoryInfo = self.BookData.GetCategorySubjectDisplay()
            if len(CategoryInfo) > 40:
                CategoryInfo = CategoryInfo[:37] + "..."
            Lines.append(f"<i>{CategoryInfo}</i>")
        
        # File information
        if self.BookData.FileSizeMB:
            FileSizeText = self.BookData.GetFileSizeDisplay()
            Lines.append(f"Size: {FileSizeText}")
        
        # File status
        if not self.BookData.FileExists():
            Lines.append("<span style='color: red;'>⚠ File Missing</span>")
        
        return "<br>".join(Lines)


class BookGrid(QScrollArea):
    """
    Scrollable grid container for displaying books with responsive layout.
    Manages grid column calculation and book card positioning.
    """
    
    def __init__(self, BookServiceInstance: BookService, Parent=None):
        """
        Initialize book grid with book service dependency.
        
        Args:
            BookServiceInstance: BookService for data operations
            Parent: Parent widget
        """
        super().__init__(Parent)
        
        self.BookService = BookServiceInstance
        self.Logger = logging.getLogger(__name__)
        
        # Grid layout parameters (matching original design)
        self.BaseWidth = 315      # Base width before grid starts
        self.ItemWidth = 230      # Width per grid item
        self.CurrentColumns = 0   # Current number of columns
        self.PreviousColumns = 0  # Previous column count for change detection
        
        # Current book data
        self.CurrentBooks: List[Book] = []
        
        # Layout components
        self.ScrollWidget: Optional[QWidget] = None
        self.GridLayout: Optional[QGridLayout] = None
        
        # Update timer for responsive layout
        self.ResizeTimer = QTimer()
        self.ResizeTimer.setSingleShot(True)
        self.ResizeTimer.timeout.connect(self._UpdateLayoutIfNeeded)
        
        # Event callbacks
        self.OnBookOpened: Optional[Callable[[str], None]] = None
        
        self._SetupScrollArea()
        self._SetupGridLayout()
        
        self.Logger.info("BookGrid initialized successfully")
    
    def _SetupScrollArea(self) -> None:
        """Configure scroll area properties"""
        # Create scroll widget
        self.ScrollWidget = QWidget()
        self.setWidget(self.ScrollWidget)
        self.setWidgetResizable(True)
        
        # Configure scroll area
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Enable mouse tracking
        self.setMouseTracking(True)
    
    def _SetupGridLayout(self) -> None:
        """Create and configure grid layout"""
        self.GridLayout = QGridLayout(self.ScrollWidget)
        self.GridLayout.setContentsMargins(0, 0, 0, 0)
        self.GridLayout.setSpacing(10)  # Add some spacing between cards
    
    def UpdateBooks(self, Books: List[Book]) -> None:
        """
        Update grid with new book list.
        
        Args:
            Books: List of books to display
        """
        self.CurrentBooks = Books
        self._RebuildGrid()
        
        self.Logger.info(f"BookGrid updated with {len(Books)} books")
    
    def _RebuildGrid(self) -> None:
        """Clear and rebuild the entire grid layout"""
        if not self.GridLayout:
            return
        
        # Clear existing widgets
        self._ClearGrid()
        
        # Calculate current column count
        self._UpdateColumnCount()
        
        # Add book cards to grid
        for Index, BookData in enumerate(self.CurrentBooks):
            BookCard = self._CreateBookCard(BookData)
            
            if self.CurrentColumns > 0:
                Row = Index // self.CurrentColumns
                Column = Index % self.CurrentColumns
                self.GridLayout.addWidget(BookCard, Row, Column)
        
        # Add spacers to push content to top-left
        self._AddGridSpacers()
    
    def _CreateBookCard(self, BookData: Book) -> BookCard:
        """
        Create book card widget for grid.
        
        Args:
            BookData: Book data for the card
            
        Returns:
            BookCard widget
        """
        # Create main window reference (placeholder - will be set by parent)
        MainWindowRef = self.parent()
        while MainWindowRef and not hasattr(MainWindowRef, 'OpenBook'):
            MainWindowRef = MainWindowRef.parent()
        
        BookCardWidget = BookCard(BookData, MainWindowRef)
        return BookCardWidget
    
    def _ClearGrid(self) -> None:
        """Remove all widgets from grid layout"""
        if not self.GridLayout:
            return
        
        while self.GridLayout.count():
            Child = self.GridLayout.takeAt(0)
            if Child.widget():
                Child.widget().setParent(None)
    
    def _AddGridSpacers(self) -> None:
        """Add spacer items to push content to top-left"""
        if not self.GridLayout or not self.CurrentBooks or self.CurrentColumns <= 0:
            return
        
        LastIndex = len(self.CurrentBooks) - 1
        LastRow = LastIndex // self.CurrentColumns
        LastColumn = LastIndex % self.CurrentColumns
        
        # Add horizontal spacer
        HorizontalSpacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.GridLayout.addItem(HorizontalSpacer, LastRow, LastColumn + 1)
        
        # Add vertical spacer
        VerticalSpacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.GridLayout.addItem(VerticalSpacer, LastRow + 1, LastColumn)
    
    def _UpdateColumnCount(self) -> None:
        """Calculate number of columns based on current width"""
        AvailableWidth = self.width()
        self.PreviousColumns = self.CurrentColumns
        self.CurrentColumns = max(1, (AvailableWidth - self.BaseWidth) // self.ItemWidth)
        
        # Emit status update if parent supports it
        self._UpdateStatusMessage()
    
    def _UpdateLayoutIfNeeded(self) -> None:
        """Update layout only if column count changed"""
        if self.PreviousColumns != self.CurrentColumns:
            self._RebuildGrid()
    
    def _UpdateStatusMessage(self) -> None:
        """Update status bar with grid information"""
        # Try to find status bar in parent hierarchy
        StatusBar = None
        Parent = self.parent()
        
        while Parent:
            if hasattr(Parent, 'statusBar'):
                StatusBar = Parent.statusBar()
                break
            elif hasattr(Parent, 'get_status_bar'):
                StatusBar = Parent.get_status_bar()
                break
            Parent = Parent.parent()
        
        if StatusBar:
            Width = self.width()
            Height = self.height()
            Message = f"{Width} x {Height}  C:{self.CurrentColumns}"
            StatusBar.showMessage(Message)
    
    # =================================================================
    # EVENT HANDLING
    # =================================================================
    
    def resizeEvent(self, Event) -> None:
        """Handle resize events with debounced layout updates"""
        super().resizeEvent(Event)
        
        # Update column count
        self._UpdateColumnCount()
        
        # Start/restart timer for debounced layout update
        self.ResizeTimer.start(100)  # 100ms delay
        
        # Update status immediately
        self._UpdateStatusMessage()
    
    def OpenBook(self, BookTitle: str) -> None:
        """
        Handle book opening request from card widgets.
        
        Args:
            BookTitle: Title of book to open
        """
        try:
            Success = self.BookService.OpenBook(BookTitle)
            
            if not Success:
                # Show error message
                QMessageBox.warning(
                    self,
                    "Book Not Found",
                    f"Could not open book: {BookTitle}\n\nThe PDF file may be missing or moved."
                )
            else:
                # Notify external handlers
                if self.OnBookOpened:
                    self.OnBookOpened(BookTitle)
                    
        except Exception as Error:
            self.Logger.error(f"Failed to open book '{BookTitle}': {Error}")
            QMessageBox.critical(
                self,
                "Error Opening Book", 
                f"An error occurred while opening the book:\n\n{Error}"
            )
    
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
        self._RebuildGrid()
    
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
            'Rows': (len(self.CurrentBooks) + self.CurrentColumns - 1) // self.CurrentColumns if self.CurrentColumns > 0 else 0,
            'GridWidth': self.width(),
            'GridHeight': self.height(),
            'ItemWidth': self.ItemWidth,
            'BaseWidth': self.BaseWidth
        }
