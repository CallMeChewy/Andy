# File: ColorTheme.py
# Path: Source/Utils/ColorTheme.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  09:20PM
"""
Description: Color Theme Management for Anderson's Library
Centralized color theme definitions and utilities for consistent styling
across all interface components.
"""

class AndersonLibraryTheme:
    """Professional color theme for Anderson's Library"""
    
    # Base colors
    PRIMARY_BG = "#2b2b2b"
    SECONDARY_BG = "#3c3c3c"
    ACCENT_BG = "#4a4a4a"
    
    # Text colors
    PRIMARY_TEXT = "#ffffff"
    SECONDARY_TEXT = "#e0e0e0"
    MUTED_TEXT = "#b0b0b0"
    
    # Accent colors
    PRIMARY_ACCENT = "#0078d4"
    PRIMARY_ACCENT_HOVER = "#106ebe"
    PRIMARY_ACCENT_PRESSED = "#005a9e"
    
    # Status colors
    SUCCESS = "#107c10"
    WARNING = "#ff8c00"
    ERROR = "#d13438"
    
    # Border colors
    BORDER_LIGHT = "#555555"
    BORDER_MEDIUM = "#666666"
    BORDER_DARK = "#333333"
    
    # Selection colors
    SELECTION_BG = "#0078d4"
    SELECTION_TEXT = "#ffffff"
    HOVER_BG = "#404040"
    
    @classmethod
    def GetButtonStyle(cls) -> str:
        """Get standard button stylesheet"""
        return f"""
            QPushButton {
                padding: 8px 16px;
                border: 2px solid {cls.BORDER_MEDIUM};
                border-radius: 4px;
                background-color: {cls.ACCENT_BG};
                color: {cls.PRIMARY_TEXT};
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: {cls.HOVER_BG};
                border-color: {cls.PRIMARY_ACCENT};
            }
            QPushButton:pressed {
                background-color: {cls.PRIMARY_ACCENT_PRESSED};
            }
        """
    
    @classmethod
    def GetInputStyle(cls) -> str:
        """Get standard input field stylesheet"""
        return f"""
            QLineEdit, QComboBox {
                padding: 8px;
                border: 2px solid {cls.BORDER_MEDIUM};
                border-radius: 4px;
                background-color: {cls.ACCENT_BG};
                color: {cls.PRIMARY_TEXT};
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: {cls.PRIMARY_ACCENT};
                background-color: {cls.SECONDARY_BG};
            }
        """


# Alternative theme variants for future use
class LightTheme:
    """Light theme variant"""
    PRIMARY_BG = "#ffffff"
    SECONDARY_BG = "#f5f5f5"
    PRIMARY_TEXT = "#000000"
    PRIMARY_ACCENT = "#0078d4"
    # ... etc


class HighContrastTheme:
    """High contrast theme for accessibility"""
    PRIMARY_BG = "#000000"
    SECONDARY_BG = "#1a1a1a"
    PRIMARY_TEXT = "#ffffff"
    PRIMARY_ACCENT = "#00ff00"
    # ... etc
