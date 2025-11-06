"""
Demo file để test Settings Dialog
Chạy file này để xem Settings Dialog
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui import SettingsDialog
from ui.styles import DARK_THEME
from utils import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


def main():
    """Main function để chạy demo Settings Dialog"""

    logger.info("Starting Settings Dialog Demo...")

    # Tạo QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Settings Dialog Demo")
    app.setStyleSheet(DARK_THEME)

    # Tạo và hiển thị Settings Dialog
    dialog = SettingsDialog()

    # Connect signal
    dialog.settings_changed.connect(
        lambda: logger.info("Settings changed signal received")
    )

    # Show dialog
    result = dialog.exec()

    if result:
        logger.info("Settings saved successfully")
        print("\n✅ Settings saved!")
    else:
        logger.info("Settings dialog cancelled")
        print("\n❌ Settings cancelled")


if __name__ == '__main__':
    main()
