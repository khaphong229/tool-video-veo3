"""
Demo file để test Text to Video Tab
Chạy file này để xem Text to Video Tab
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from ui.tabs import TextToVideoTab
from ui.styles import DARK_THEME
from utils import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


def main():
    """Main function để chạy demo Text to Video Tab"""

    logger.info("Starting Text to Video Tab Demo...")

    # Tạo QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Text to Video Tab - Demo")
    app.setStyleSheet(DARK_THEME)

    # Tạo window
    window = QMainWindow()
    window.setWindowTitle("Text to Video Tab Demo")
    window.setGeometry(100, 100, 1000, 900)

    # Create Text to Video Tab
    tab = TextToVideoTab()

    # Connect signals
    def on_generate(params):
        logger.info(f"Generate requested: {params}")
        print("\n" + "="*60)
        print("GENERATE VIDEO REQUESTED")
        print("="*60)
        print(f"Prompt: {params['prompt']}")
        print(f"Model: {params['model']}")
        print(f"Aspect Ratio: {params['aspect_ratio']}")
        print(f"Duration: {params['duration']} seconds")
        print(f"Resolution: {params['resolution']}")
        print(f"Seed: {params['seed']}")
        print(f"Audio: {params['enable_audio']}")
        print("="*60 + "\n")

    def on_queue(params):
        logger.info(f"Added to queue: {params}")
        print("\n✅ Added to queue!")

    def on_template_saved(template):
        logger.info(f"Template saved: {template['name']}")
        print(f"\n💾 Template saved: {template['name']}")

    tab.generate_requested.connect(on_generate)
    tab.add_to_queue_requested.connect(on_queue)
    tab.template_saved.connect(on_template_saved)

    # Set as central widget
    window.setCentralWidget(tab)

    # Show window
    window.show()

    logger.info("Text to Video Tab demo displayed")

    # Run event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
