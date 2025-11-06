"""
Video Player Widget Demo
Test the custom video player with various features
"""

import sys
import os
from pathlib import Path

# Suppress console encoding errors
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QFileDialog, QLabel,
    QMessageBox, QListWidget, QListWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt

from ui.widgets import VideoPlayerWidget
from utils import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


class VideoPlayerDemo(QMainWindow):
    """Demo window for video player widget"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Player Widget Demo")
        self.setGeometry(100, 100, 1200, 700)

        self.video_files = []  # List of video files
        self.setup_ui()

        logger.info("Video Player Demo initialized")

    def setup_ui(self):
        """Setup UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("Video Player Widget Demo")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Splitter for player and playlist
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Video player
        self.player = VideoPlayerWidget()

        # Connect signals
        self.player.video_loaded.connect(self.on_video_loaded)
        self.player.playback_started.connect(lambda: logger.info("▶ Playback started"))
        self.player.playback_paused.connect(lambda: logger.info("⏸ Playback paused"))
        self.player.playback_stopped.connect(lambda: logger.info("⏹ Playback stopped"))
        self.player.error_occurred.connect(self.on_error)

        splitter.addWidget(self.player)

        # Right panel - Playlist and controls
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Playlist label
        playlist_label = QLabel("Playlist")
        playlist_label.setStyleSheet("font-weight: bold; padding: 5px;")
        right_layout.addWidget(playlist_label)

        # Playlist
        self.playlist = QListWidget()
        self.playlist.itemDoubleClicked.connect(self.on_playlist_item_double_clicked)
        right_layout.addWidget(self.playlist)

        # Buttons
        btn_layout = QVBoxLayout()

        load_btn = QPushButton("Load Video File")
        load_btn.clicked.connect(self.load_video_file)
        btn_layout.addWidget(load_btn)

        scan_btn = QPushButton("Scan for Videos in outputs/")
        scan_btn.clicked.connect(self.scan_outputs_folder)
        btn_layout.addWidget(scan_btn)

        clear_btn = QPushButton("Clear Player")
        clear_btn.clicked.connect(self.clear_player)
        btn_layout.addWidget(clear_btn)

        test_btn = QPushButton("Test with Sample Video")
        test_btn.clicked.connect(self.test_with_sample)
        btn_layout.addWidget(test_btn)

        right_layout.addLayout(btn_layout)

        # Info panel
        info_label = QLabel("Keyboard Shortcuts")
        info_label.setStyleSheet("font-weight: bold; padding: 5px; margin-top: 10px;")
        right_layout.addWidget(info_label)

        shortcuts_text = """
Space: Play/Pause
F: Fullscreen
Esc: Exit Fullscreen
Left Arrow: Seek -5s
Right Arrow: Seek +5s
        """
        shortcuts_label = QLabel(shortcuts_text.strip())
        shortcuts_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 4px;")
        right_layout.addWidget(shortcuts_label)

        right_layout.addStretch()

        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter, 1)

        # Status bar
        self.statusBar().showMessage("Ready - Load a video to start")

    def load_video_file(self):
        """Load video file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.webm *.flv);;All Files (*.*)"
        )

        if file_path:
            self.player.load_video(file_path)
            self.add_to_playlist(file_path)

    def scan_outputs_folder(self):
        """Scan outputs folder for video files"""
        outputs_dir = Path("outputs")

        if not outputs_dir.exists():
            QMessageBox.information(
                self,
                "Info",
                "outputs/ folder not found.\n\n"
                "Please create the folder or use 'Load Video File' to select a video."
            )
            return

        # Find all video files
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
        video_files = []

        for ext in video_extensions:
            video_files.extend(outputs_dir.rglob(f"*{ext}"))

        if not video_files:
            QMessageBox.information(
                self,
                "No Videos Found",
                "No video files found in outputs/ folder."
            )
            return

        # Add to playlist
        self.playlist.clear()
        self.video_files = []

        for video_file in video_files:
            self.add_to_playlist(str(video_file))

        logger.info(f"Found {len(video_files)} video files in outputs/")
        self.statusBar().showMessage(f"Found {len(video_files)} videos in outputs/")

        # Load first video
        if self.video_files:
            self.player.load_video(self.video_files[0])

    def add_to_playlist(self, file_path: str):
        """Add video to playlist"""
        if file_path not in self.video_files:
            self.video_files.append(file_path)
            item = QListWidgetItem(Path(file_path).name)
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            item.setToolTip(file_path)
            self.playlist.addItem(item)

    def on_playlist_item_double_clicked(self, item: QListWidgetItem):
        """Handle playlist item double click"""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path:
            self.player.load_video(file_path)

    def clear_player(self):
        """Clear the player"""
        self.player.clear()
        self.statusBar().showMessage("Player cleared")

    def test_with_sample(self):
        """Test with a sample video URL or create a test pattern"""
        QMessageBox.information(
            self,
            "Test Sample",
            "To test the player:\n\n"
            "1. Use 'Load Video File' to select any video file on your computer\n"
            "2. Use 'Scan for Videos' to find videos in the outputs/ folder\n"
            "3. Generate videos using the main app, then come back here\n\n"
            "The player supports: MP4, AVI, MOV, MKV, WEBM, FLV"
        )

    def on_video_loaded(self, video_path: str):
        """Handle video loaded"""
        filename = Path(video_path).name
        self.statusBar().showMessage(f"Loaded: {filename}")
        logger.info(f"Video loaded: {filename}")

    def on_error(self, error_message: str):
        """Handle player error"""
        self.statusBar().showMessage(f"Error: {error_message}")
        logger.error(f"Player error: {error_message}")


def main():
    """Main function"""
    print("="*70)
    print("VIDEO PLAYER WIDGET DEMO")
    print("="*70)
    print()
    print("Features:")
    print("  - Load and play video files")
    print("  - Play/Pause/Stop controls")
    print("  - Progress slider with seeking")
    print("  - Volume control")
    print("  - Fullscreen mode (F key)")
    print("  - Download/Save video")
    print("  - Keyboard shortcuts (Space, F, Arrows)")
    print()
    print("="*70)
    print()

    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    demo = VideoPlayerDemo()
    demo.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
