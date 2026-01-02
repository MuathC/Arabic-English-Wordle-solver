from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

def get_language_ui_config(language: str):
    return {
        "ar": {
            "layout_direction": Qt.LayoutDirection.RightToLeft,
            "font": QFont("Cairo", 16, QFont.Weight.Bold)  # Or use Amiri/Tajawal if Cairo isn't installed
        },
        "default": {
            "layout_direction": Qt.LayoutDirection.LeftToRight,
            "font": QFont("Arial", 12)
        }
    }.get(language, {
        "layout_direction": Qt.LayoutDirection.LeftToRight,
        "font": QFont("Arial", 12,QFont.Weight.Medium)
    })