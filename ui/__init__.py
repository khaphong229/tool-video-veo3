"""
Module UI chứa các components giao diện tùy chỉnh
Có thể thêm các widget và dialog tùy chỉnh vào đây
"""

from .main_window import MainWindow
from .settings_dialog import SettingsDialog
from .styles import DARK_THEME, ICONS, get_icon_text, get_accent_color

__all__ = [
    'MainWindow',
    'SettingsDialog',
    'DARK_THEME',
    'ICONS',
    'get_icon_text',
    'get_accent_color'
]
