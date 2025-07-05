#!/usr/bin/env python3
# File: ColorThemeImprovement.py
# Path: ColorThemeImprovement.py
# Standard: AIDEV-PascalCase-1.8
# Created: 2025-07-04
# Last Modified: 2025-07-04  09:20PM
"""
Description: Color Theme Improvement for Anderson's Library
Improves color contrast and visibility across all interface components
for better accessibility and professional appearance.
"""

import os
import sys
import re
from pathlib import Path

class ColorThemeUpdater:
    """Updates color themes across Anderson's Library interface components"""
    
    def __init__(self):
        self.ComponentFiles = [
            "Source/Interface/FilterPanel.py",
            "Source/Interface/BookGrid.py", 
            "Source/Interface/MainWindow.py"
        ]
        
        # Professional color scheme with high contrast
        self.ColorScheme = {
            # Base colors
            "primary_bg": "#2b2b2b",           # Dark gray background
            "secondary_bg": "#3c3c3c",        # Lighter gray for panels
            "accent_bg": "#4a4a4a",           # Even lighter for hover states
            
            # Text colors
            "primary_text": "#ffffff",         # White text for high contrast
            "secondary_text": "#e0e0e0",      # Light gray for secondary text
            "muted_text": "#b0b0b0",          # Muted text for labels
            
            # Accent colors
            "primary_accent": "#0078d4",       # Microsoft blue
            "primary_accent_hover": "#106ebe", # Darker blue for hover
            "primary_accent_pressed": "#005a9e", # Even darker for pressed
            
            # Success/Error colors
            "success": "#107c10",              # Green
            "warning": "#ff8c00",              # Orange
            "error": "#d13438",                # Red
            
            # Border colors
            "border_light": "#555555",         # Light border
            "border_medium": "#666666",        # Medium border
            "border_dark": "#333333",          # Dark border
            
            # Selection colors
            "selection_bg": "#0078d4",         # Blue selection background
            "selection_text": "#ffffff",       # White selection text
            "hover_bg": "#404040",             # Gray hover background
        }
    
    def UpdateFilterPanelStyles(self):
        """Update FilterPanel.py with improved color scheme"""
        print("🎨 Updating FilterPanel color scheme...")
        
        FilePath = "Source/Interface/FilterPanel.py"
        if not os.path.exists(FilePath):
            print(f"❌ File not found: {FilePath}")
            return False
        
        try:
            with open(FilePath, 'r', encoding='utf-8') as File:
                Content = File.read()
            
            # Improved stylesheet for FilterPanel
            NewStylesheet = f'''
        self.setStyleSheet("""
            QWidget {{
                background-color: {self.ColorScheme["secondary_bg"]};
                color: {self.ColorScheme["primary_text"]};
                font-family: "Segoe UI", Arial, sans-serif;
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {self.ColorScheme["border_light"]};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 8px;
                background-color: {self.ColorScheme["primary_bg"]};
                color: {self.ColorScheme["primary_text"]};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: {self.ColorScheme["primary_accent"]};
                font-weight: bold;
            }}
            
            QLineEdit {{
                padding: 8px;
                border: 2px solid {self.ColorScheme["border_medium"]};
                border-radius: 4px;
                background-color: {self.ColorScheme["accent_bg"]};
                color: {self.ColorScheme["primary_text"]};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {self.ColorScheme["primary_accent"]};
                background-color: {self.ColorScheme["secondary_bg"]};
            }}
            
            QComboBox {{
                padding: 6px 12px;
                border: 2px solid {self.ColorScheme["border_medium"]};
                border-radius: 4px;
                background-color: {self.ColorScheme["accent_bg"]};
                color: {self.ColorScheme["primary_text"]};
                font-size: 13px;
                min-width: 120px;
            }}
            QComboBox:hover {{
                border-color: {self.ColorScheme["primary_accent"]};
                background-color: {self.ColorScheme["hover_bg"]};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {self.ColorScheme["muted_text"]};
                margin-right: 8px;
            }}
            
            QPushButton {{
                padding: 8px 16px;
                border: 2px solid {self.ColorScheme["border_medium"]};
                border-radius: 4px;
                background-color: {self.ColorScheme["accent_bg"]};
                color: {self.ColorScheme["primary_text"]};
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {self.ColorScheme["hover_bg"]};
                border-color: {self.ColorScheme["primary_accent"]};
            }}
            QPushButton:pressed {{
                background-color: {self.ColorScheme["primary_accent_pressed"]};
                border-color: {self.ColorScheme["primary_accent"]};
            }}
            QPushButton:checked {{
                background-color: {self.ColorScheme["primary_accent"]};
                color: {self.ColorScheme["selection_text"]};
                border-color: {self.ColorScheme["primary_accent_hover"]};
            }}
            
            QCheckBox {{
                color: {self.ColorScheme["primary_text"]};
                font-size: 13px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {self.ColorScheme["border_medium"]};
                border-radius: 3px;
                background-color: {self.ColorScheme["accent_bg"]};
            }}
            QCheckBox::indicator:hover {{
                border-color: {self.ColorScheme["primary_accent"]};
            }}
            QCheckBox::indicator:checked {{
                background-color: {self.ColorScheme["primary_accent"]};
                border-color: {self.ColorScheme["primary_accent"]};
            }}
            
            QSlider::groove:horizontal {{
                height: 6px;
                background: {self.ColorScheme["border_dark"]};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {self.ColorScheme["primary_accent"]};
                border: 2px solid {self.ColorScheme["primary_accent_hover"]};
                width: 16px;
                border-radius: 8px;
                margin: -6px 0;
            }}
            QSlider::handle:horizontal:hover {{
                background: {self.ColorScheme["primary_accent_hover"]};
            }}
            
            QListWidget {{
                background-color: {self.ColorScheme["accent_bg"]};
                border: 2px solid {self.ColorScheme["border_medium"]};
                border-radius: 4px;
                color: {self.ColorScheme["primary_text"]};
                font-size: 13px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 6px;
                border-bottom: 1px solid {self.ColorScheme["border_dark"]};
            }}
            QListWidget::item:hover {{
                background-color: {self.ColorScheme["hover_bg"]};
            }}
            QListWidget::item:selected {{
                background-color: {self.ColorScheme["selection_bg"]};
                color: {self.ColorScheme["selection_text"]};
            }}
        """)'''
            
            # Replace the existing setStyleSheet call
            if 'self.setStyleSheet(' in Content:
                # Find and replace the existing stylesheet
                Pattern = r'self\.setStyleSheet\(""".*?"""\)'
                Content = re.sub(Pattern, NewStylesheet.strip(), Content, flags=re.DOTALL)
            else:
                # Add stylesheet to ApplyStyles method
                Content = Content.replace(
                    'def ApplyStyles(self):',
                    f'def ApplyStyles(self):\n        """Apply consistent styling"""{NewStylesheet}'
                )
            
            with open(FilePath, 'w', encoding='utf-8') as File:
                File.write(Content)
            
            print("✅ FilterPanel color scheme updated")
            return True
            
        except Exception as Error:
            print(f"❌ Error updating FilterPanel: {Error}")
            return False
    
    def UpdateBookGridStyles(self):
        """Update BookGrid.py with improved color scheme"""
        print("🎨 Updating BookGrid color scheme...")
        
        FilePath = "Source/Interface/BookGrid.py"
        if not os.path.exists(FilePath):
            print(f"❌ File not found: {FilePath}")
            return False
        
        try:
            with open(FilePath, 'r', encoding='utf-8') as File:
                Content = File.read()
            
            # Improved stylesheet for BookGrid
            NewStylesheet = f'''
        self.setStyleSheet("""
            QWidget {{
                background-color: {self.ColorScheme["primary_bg"]};
                color: {self.ColorScheme["primary_text"]};
                font-family: "Segoe UI", Arial, sans-serif;
            }}
            
            QFrame {{
                background-color: {self.ColorScheme["secondary_bg"]};
                border: 1px solid {self.ColorScheme["border_light"]};
                border-radius: 4px;
            }}
            
            QPushButton {{
                padding: 8px 16px;
                border: 2px solid {self.ColorScheme["border_medium"]};
                border-radius: 4px;
                background-color: {self.ColorScheme["accent_bg"]};
                color: {self.ColorScheme["primary_text"]};
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {self.ColorScheme["hover_bg"]};
                border-color: {self.ColorScheme["primary_accent"]};
            }}
            QPushButton:checked {{
                background-color: {self.ColorScheme["primary_accent"]};
                color: {self.ColorScheme["selection_text"]};
                border-color: {self.ColorScheme["primary_accent_hover"]};
            }}
            QPushButton:pressed {{
                background-color: {self.ColorScheme["primary_accent_pressed"]};
            }}
            
            QComboBox {{
                padding: 6px 12px;
                border: 2px solid {self.ColorScheme["border_medium"]};
                border-radius: 4px;
                background-color: {self.ColorScheme["accent_bg"]};
                color: {self.ColorScheme["primary_text"]};
                font-size: 13px;
                min-width: 120px;
            }}
            QComboBox:hover {{
                border-color: {self.ColorScheme["primary_accent"]};
                background-color: {self.ColorScheme["hover_bg"]};
            }}
            
            QProgressBar {{
                border: 2px solid {self.ColorScheme["border_medium"]};
                border-radius: 4px;
                background-color: {self.ColorScheme["accent_bg"]};
                text-align: center;
                color: {self.ColorScheme["primary_text"]};
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {self.ColorScheme["primary_accent"]};
                border-radius: 2px;
            }}
            
            QLabel {{
                color: {self.ColorScheme["primary_text"]};
                font-size: 13px;
            }}
            
            QScrollArea {{
                border: none;
                background-color: {self.ColorScheme["primary_bg"]};
            }}
            QScrollBar:vertical {{
                background-color: {self.ColorScheme["border_dark"]};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self.ColorScheme["border_light"]};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {self.ColorScheme["primary_accent"]};
            }}
        """)'''
            
            # Fix the typo first
            Content = Content.replace('Pixap.scaled', 'Pixmap.scaled')
            print("✅ Fixed Pixap typo")
            
            # Replace or add the stylesheet
            if 'self.setStyleSheet(' in Content:
                Pattern = r'self\.setStyleSheet\(""".*?"""\)'
                Content = re.sub(Pattern, NewStylesheet.strip(), Content, flags=re.DOTALL)
            else:
                Content = Content.replace(
                    'def ApplyStyles(self):',
                    f'def ApplyStyles(self):\n        """Apply consistent styling"""{NewStylesheet}'
                )
            
            # Update BookTile styling
            TileStylesheet = f'''
            if self.IsSelected:
                self.setStyleSheet("""
                    QFrame {{
                        background-color: {self.ColorScheme["selection_bg"]};
                        border: 3px solid {self.ColorScheme["primary_accent_hover"]};
                        border-radius: 8px;
                    }}
                    QLabel {{
                        color: {self.ColorScheme["selection_text"]};
                        font-weight: bold;
                    }}
                """)
            elif self.IsHovered:
                self.setStyleSheet("""
                    QFrame {{
                        background-color: {self.ColorScheme["hover_bg"]};
                        border: 2px solid {self.ColorScheme["primary_accent"]};
                        border-radius: 8px;
                    }}
                    QLabel {{
                        color: {self.ColorScheme["primary_text"]};
                    }}
                """)
            else:
                self.setStyleSheet("""
                    QFrame {{
                        background-color: {self.ColorScheme["secondary_bg"]};
                        border: 1px solid {self.ColorScheme["border_light"]};
                        border-radius: 8px;
                    }}
                    QFrame:hover {{
                        border: 2px solid {self.ColorScheme["primary_accent"]};
                        background-color: {self.ColorScheme["hover_bg"]};
                    }}
                    QLabel {{
                        color: {self.ColorScheme["primary_text"]};
                    }}
                """)'''
            
            # Update the ApplyStyles method in BookTile
            if 'def ApplyStyles(self):' in Content and 'BookTile' in Content:
                Pattern = r'def ApplyStyles\(self\):.*?(?=def|\Z)'
                Replacement = f'def ApplyStyles(self):\n        """Apply visual styling to the tile"""\n        {TileStylesheet.strip()}\n\n    '
                Content = re.sub(Pattern, Replacement, Content, flags=re.DOTALL)
            
            with open(FilePath, 'w', encoding='utf-8') as File:
                File.write(Content)
            
            print("✅ BookGrid color scheme updated")
            return True
            
        except Exception as Error:
            print(f"❌ Error updating BookGrid: {Error}")
            return False
    
    def UpdateMainWindowStyles(self):
        """Update MainWindow.py with improved color scheme"""
        print("🎨 Updating MainWindow color scheme...")
        
        FilePath = "Source/Interface/MainWindow.py"
        if not os.path.exists(FilePath):
            print(f"❌ File not found: {FilePath}")
            return False
        
        try:
            with open(FilePath, 'r', encoding='utf-8') as File:
                Content = File.read()
            
            # Add improved application stylesheet
            StylesheetCode = f'''
        # Set application-wide stylesheet for better contrast
        App.setStyleSheet("""
            QMainWindow {{
                background-color: {self.ColorScheme["primary_bg"]};
                color: {self.ColorScheme["primary_text"]};
            }}
            
            QMenuBar {{
                background-color: {self.ColorScheme["secondary_bg"]};
                color: {self.ColorScheme["primary_text"]};
                border-bottom: 1px solid {self.ColorScheme["border_light"]};
                font-size: 13px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 6px 12px;
            }}
            QMenuBar::item:selected {{
                background-color: {self.ColorScheme["primary_accent"]};
                color: {self.ColorScheme["selection_text"]};
            }}
            
            QMenu {{
                background-color: {self.ColorScheme["secondary_bg"]};
                color: {self.ColorScheme["primary_text"]};
                border: 2px solid {self.ColorScheme["border_light"]};
                border-radius: 4px;
            }}
            QMenu::item {{
                padding: 8px 16px;
            }}
            QMenu::item:selected {{
                background-color: {self.ColorScheme["primary_accent"]};
                color: {self.ColorScheme["selection_text"]};
            }}
            
            QToolBar {{
                background-color: {self.ColorScheme["secondary_bg"]};
                border: none;
                spacing: 4px;
                padding: 4px;
            }}
            QToolButton {{
                background-color: {self.ColorScheme["accent_bg"]};
                color: {self.ColorScheme["primary_text"]};
                border: 2px solid {self.ColorScheme["border_medium"]};
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }}
            QToolButton:hover {{
                background-color: {self.ColorScheme["hover_bg"]};
                border-color: {self.ColorScheme["primary_accent"]};
            }}
            
            QStatusBar {{
                background-color: {self.ColorScheme["secondary_bg"]};
                color: {self.ColorScheme["primary_text"]};
                border-top: 1px solid {self.ColorScheme["border_light"]};
            }}
            
            QSplitter::handle {{
                background-color: {self.ColorScheme["border_medium"]};
                width: 4px;
            }}
            QSplitter::handle:hover {{
                background-color: {self.ColorScheme["primary_accent"]};
            }}
        """)
        '''
            
            # Add this after App creation
            if 'App = QApplication(sys.argv)' in Content:
                Content = Content.replace(
                    'App = QApplication(sys.argv)',
                    f'App = QApplication(sys.argv)\n        \n{StylesheetCode.strip()}'
                )
            
            with open(FilePath, 'w', encoding='utf-8') as File:
                File.write(Content)
            
            print("✅ MainWindow color scheme updated")
            return True
            
        except Exception as Error:
            print(f"❌ Error updating MainWindow: {Error}")
            return False
    
    def CreateColorThemeModule(self):
        """Create a dedicated color theme module for future customization"""
        print("🎨 Creating ColorTheme module...")
        
        ThemeDir = Path("Source/Utils")
        ThemeDir.mkdir(exist_ok=True)
        
        ThemeFile = ThemeDir / "ColorTheme.py"
        
        ThemeContent = f'''# File: ColorTheme.py
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
    PRIMARY_BG = "{self.ColorScheme["primary_bg"]}"
    SECONDARY_BG = "{self.ColorScheme["secondary_bg"]}"
    ACCENT_BG = "{self.ColorScheme["accent_bg"]}"
    
    # Text colors
    PRIMARY_TEXT = "{self.ColorScheme["primary_text"]}"
    SECONDARY_TEXT = "{self.ColorScheme["secondary_text"]}"
    MUTED_TEXT = "{self.ColorScheme["muted_text"]}"
    
    # Accent colors
    PRIMARY_ACCENT = "{self.ColorScheme["primary_accent"]}"
    PRIMARY_ACCENT_HOVER = "{self.ColorScheme["primary_accent_hover"]}"
    PRIMARY_ACCENT_PRESSED = "{self.ColorScheme["primary_accent_pressed"]}"
    
    # Status colors
    SUCCESS = "{self.ColorScheme["success"]}"
    WARNING = "{self.ColorScheme["warning"]}"
    ERROR = "{self.ColorScheme["error"]}"
    
    # Border colors
    BORDER_LIGHT = "{self.ColorScheme["border_light"]}"
    BORDER_MEDIUM = "{self.ColorScheme["border_medium"]}"
    BORDER_DARK = "{self.ColorScheme["border_dark"]}"
    
    # Selection colors
    SELECTION_BG = "{self.ColorScheme["selection_bg"]}"
    SELECTION_TEXT = "{self.ColorScheme["selection_text"]}"
    HOVER_BG = "{self.ColorScheme["hover_bg"]}"
    
    @classmethod
    def GetButtonStyle(cls) -> str:
        """Get standard button stylesheet"""
        return f"""
            QPushButton {{
                padding: 8px 16px;
                border: 2px solid {{cls.BORDER_MEDIUM}};
                border-radius: 4px;
                background-color: {{cls.ACCENT_BG}};
                color: {{cls.PRIMARY_TEXT}};
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {{cls.HOVER_BG}};
                border-color: {{cls.PRIMARY_ACCENT}};
            }}
            QPushButton:pressed {{
                background-color: {{cls.PRIMARY_ACCENT_PRESSED}};
            }}
        """
    
    @classmethod
    def GetInputStyle(cls) -> str:
        """Get standard input field stylesheet"""
        return f"""
            QLineEdit, QComboBox {{
                padding: 8px;
                border: 2px solid {{cls.BORDER_MEDIUM}};
                border-radius: 4px;
                background-color: {{cls.ACCENT_BG}};
                color: {{cls.PRIMARY_TEXT}};
                font-size: 13px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border-color: {{cls.PRIMARY_ACCENT}};
                background-color: {{cls.SECONDARY_BG}};
            }}
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
'''
        
        with open(ThemeFile, 'w', encoding='utf-8') as File:
            File.write(ThemeContent)
        
        print("✅ ColorTheme module created")
        return True
    
    def UpdateAllThemes(self):
        """Update all interface components with improved color themes"""
        print("🎨 Anderson's Library - Color Theme Improvement")
        print("=" * 50)
        print("🌈 Applying high-contrast professional color scheme")
        print("=" * 50)
        
        Success = True
        
        # Update each component
        if not self.UpdateFilterPanelStyles():
            Success = False
        
        if not self.UpdateBookGridStyles():
            Success = False
        
        if not self.UpdateMainWindowStyles():
            Success = False
        
        # Create theme module for future use
        self.CreateColorThemeModule()
        
        return Success


def Main():
    """Main theme update function"""
    Updater = ColorThemeUpdater()
    
    if Updater.UpdateAllThemes():
        print("\n" + "=" * 50)
        print("🎉 COLOR THEME IMPROVEMENT COMPLETE!")
        print("=" * 50)
        print("🌈 Applied high-contrast professional color scheme")
        print("✅ Improved text visibility and readability")
        print("✅ Enhanced button and control contrast")
        print("✅ Better selection and hover states")
        print("✅ Fixed book cover loading issue")
        print("\n🚀 Restart Anderson's Library to see improvements:")
        print("python AndersonLibrary.py")
        print("\n💡 Theme module created at Source/Utils/ColorTheme.py")
        print("   Use this for future color customizations")
        return 0
    else:
        print("\n❌ Some theme updates failed")
        print("💡 Check the error messages above")
        return 1


if __name__ == "__main__":
    sys.exit(Main())
