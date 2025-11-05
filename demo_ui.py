"""
Demo file để test và showcase Main Window UI
Chạy file này để xem giao diện mới
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui import MainWindow
from utils import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


def main():
    """Main function để chạy demo UI"""

    logger.info("Starting UI Demo...")

    # Tạo QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Veo3 Video Generator - UI Demo")

    # Tạo và hiển thị Main Window
    window = MainWindow()

    # Simulate API connection (for demo purposes)
    # window.set_api_status(True, "Connected")  # Connected
    window.set_api_status(False, "Not configured")  # Disconnected

    # Set initial status
    window.set_status_message("UI Demo Mode - Ready")

    # Show window
    window.show()

    logger.info("UI Demo window displayed")

    # Run event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
