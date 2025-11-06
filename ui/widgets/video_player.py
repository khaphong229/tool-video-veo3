"""
Video Player Widget - Custom video player with controls
"""

import os
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSlider, QLabel, QStyle, QFileDialog, QMessageBox,
    QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut, QPalette, QColor
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

from utils import get_logger

logger = get_logger(__name__)


class VideoPlayerWidget(QWidget):
    """
    Custom video player widget with full controls

    Features:
    - Play/Pause/Stop controls
    - Progress slider with seeking
    - Volume control
    - Fullscreen mode
    - Download button
    - Keyboard shortcuts
    - Loading indicator
    - Error handling

    Signals:
        video_loaded: Emitted when video is loaded (video_path)
        playback_started: Emitted when playback starts
        playback_paused: Emitted when playback pauses
        playback_stopped: Emitted when playback stops
        error_occurred: Emitted when error occurs (error_message)
    """

    # Signals
    video_loaded = pyqtSignal(str)
    playback_started = pyqtSignal()
    playback_paused = pyqtSignal()
    playback_stopped = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # State
        self.current_video_path: Optional[str] = None
        self.is_fullscreen = False
        self.normal_geometry = None
        self.is_seeking = False  # Flag to prevent feedback loop

        # Setup UI
        self.setup_ui()
        self.setup_shortcuts()

        logger.info("VideoPlayerWidget initialized")

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Video widget container
        video_container = QFrame()
        video_container.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        video_container.setStyleSheet("background-color: black;")
        video_container_layout = QVBoxLayout(video_container)
        video_container_layout.setContentsMargins(0, 0, 0, 0)

        # Video display
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(640, 360)
        video_container_layout.addWidget(self.video_widget)

        # Loading indicator (overlay)
        self.loading_label = QLabel("Loading...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 180);
                font-size: 16px;
                padding: 20px;
                border-radius: 8px;
            }
        """)
        self.loading_label.hide()

        # Position loading label at center (using absolute positioning)
        video_container_layout.addWidget(self.loading_label)
        video_container_layout.setAlignment(self.loading_label, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(video_container, 1)

        # Media player setup
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)

        # Connect media player signals
        self.media_player.playbackStateChanged.connect(self.on_state_changed)
        self.media_player.durationChanged.connect(self.on_duration_changed)
        self.media_player.positionChanged.connect(self.on_position_changed)
        self.media_player.errorOccurred.connect(self.on_error_occurred)

        # Control bar
        control_bar = self.create_control_bar()
        layout.addWidget(control_bar)

    def create_control_bar(self) -> QWidget:
        """Create the control bar with buttons and sliders"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.StyledPanel)
        widget.setMaximumHeight(80)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)

        # Progress slider
        progress_layout = QHBoxLayout()

        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 0)
        self.progress_slider.sliderMoved.connect(self.on_slider_moved)
        self.progress_slider.sliderPressed.connect(self.on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self.on_slider_released)

        progress_layout.addWidget(self.progress_slider)
        layout.addLayout(progress_layout)

        # Bottom controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        # Play/Pause button
        self.play_pause_btn = QPushButton()
        self.play_pause_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_pause_btn.setToolTip("Play (Space)")
        self.play_pause_btn.setFixedSize(40, 40)
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        controls_layout.addWidget(self.play_pause_btn)

        # Stop button
        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stop_btn.setToolTip("Stop")
        self.stop_btn.setFixedSize(40, 40)
        self.stop_btn.clicked.connect(self.stop)
        controls_layout.addWidget(self.stop_btn)

        # Time label
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setMinimumWidth(120)
        self.time_label.setStyleSheet("font-size: 12px; padding: 0 10px;")
        controls_layout.addWidget(self.time_label)

        controls_layout.addStretch()

        # Volume controls
        volume_icon = QLabel("🔊")
        volume_icon.setStyleSheet("font-size: 16px;")
        controls_layout.addWidget(volume_icon)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.setToolTip("Volume")
        self.volume_slider.valueChanged.connect(self.set_volume)
        controls_layout.addWidget(self.volume_slider)

        # Set initial volume
        self.set_volume(70)

        controls_layout.addSpacing(10)

        # Download button
        self.download_btn = QPushButton("Download")
        self.download_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.download_btn.setToolTip("Download video")
        self.download_btn.clicked.connect(self.download_video)
        self.download_btn.setEnabled(False)
        controls_layout.addWidget(self.download_btn)

        # Fullscreen button
        self.fullscreen_btn = QPushButton()
        self.fullscreen_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton))
        self.fullscreen_btn.setToolTip("Fullscreen (F)")
        self.fullscreen_btn.setFixedSize(40, 40)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        controls_layout.addWidget(self.fullscreen_btn)

        layout.addLayout(controls_layout)

        return widget

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Space - Play/Pause
        play_pause_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        play_pause_shortcut.activated.connect(self.toggle_play_pause)

        # F - Fullscreen
        fullscreen_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F), self)
        fullscreen_shortcut.activated.connect(self.toggle_fullscreen)

        # Escape - Exit fullscreen
        escape_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        escape_shortcut.activated.connect(self.exit_fullscreen)

        # Left/Right arrows - Seek
        seek_back_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        seek_back_shortcut.activated.connect(lambda: self.seek_relative(-5000))

        seek_forward_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        seek_forward_shortcut.activated.connect(lambda: self.seek_relative(5000))

        logger.debug("Keyboard shortcuts configured")

    def load_video(self, video_path: str):
        """
        Load a video file

        Args:
            video_path: Path to video file
        """
        if not os.path.exists(video_path):
            error_msg = f"Video file not found: {video_path}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            return

        logger.info(f"Loading video: {video_path}")
        self.current_video_path = video_path

        # Show loading indicator
        self.loading_label.show()
        self.loading_label.setText("Loading video...")

        # Load video
        url = QUrl.fromLocalFile(video_path)
        self.media_player.setSource(url)

        # Enable download button
        self.download_btn.setEnabled(True)

        # Auto-play
        QTimer.singleShot(100, self.play)

        self.video_loaded.emit(video_path)
        logger.info(f"Video loaded: {Path(video_path).name}")

    def play(self):
        """Start playback"""
        self.media_player.play()
        logger.debug("Playback started")

    def pause(self):
        """Pause playback"""
        self.media_player.pause()
        logger.debug("Playback paused")

    def stop(self):
        """Stop playback"""
        self.media_player.stop()
        self.progress_slider.setValue(0)
        self.time_label.setText("00:00 / 00:00")
        logger.debug("Playback stopped")

    def toggle_play_pause(self):
        """Toggle between play and pause"""
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.pause()
        else:
            self.play()

    def seek(self, position: int):
        """
        Seek to position

        Args:
            position: Position in milliseconds
        """
        self.media_player.setPosition(position)
        logger.debug(f"Seeked to position: {position}ms")

    def seek_relative(self, offset: int):
        """
        Seek relative to current position

        Args:
            offset: Offset in milliseconds (negative for backward)
        """
        current_pos = self.media_player.position()
        new_pos = max(0, min(current_pos + offset, self.media_player.duration()))
        self.seek(new_pos)

    def on_slider_pressed(self):
        """Handle slider press - start seeking"""
        self.is_seeking = True

    def on_slider_moved(self, position: int):
        """Handle slider movement during seeking"""
        if self.is_seeking:
            # Update time label during seeking
            self.update_time_label(position, self.media_player.duration())

    def on_slider_released(self):
        """Handle slider release - perform seek"""
        self.is_seeking = False
        position = self.progress_slider.value()
        self.seek(position)

    def set_volume(self, volume: int):
        """
        Set volume level

        Args:
            volume: Volume level (0-100)
        """
        # Convert to 0.0-1.0 range
        volume_linear = volume / 100.0
        self.audio_output.setVolume(volume_linear)
        logger.debug(f"Volume set to: {volume}%")

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()

    def enter_fullscreen(self):
        """Enter fullscreen mode"""
        if not self.is_fullscreen:
            self.normal_geometry = self.geometry()
            self.video_widget.setParent(None)
            self.video_widget.showFullScreen()
            self.is_fullscreen = True
            self.fullscreen_btn.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarNormalButton)
            )
            logger.info("Entered fullscreen mode")

    def exit_fullscreen(self):
        """Exit fullscreen mode"""
        if self.is_fullscreen:
            self.video_widget.showNormal()
            # Re-add to layout
            layout = self.layout()
            if layout:
                video_container = layout.itemAt(0).widget()
                if isinstance(video_container, QFrame):
                    video_container.layout().insertWidget(0, self.video_widget)

            self.is_fullscreen = False
            self.fullscreen_btn.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton)
            )
            logger.info("Exited fullscreen mode")

    def download_video(self):
        """Download/Save video to chosen location"""
        if not self.current_video_path:
            QMessageBox.warning(self, "Warning", "No video loaded")
            return

        # Ask for save location
        source_path = Path(self.current_video_path)
        default_name = source_path.name

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Video",
            default_name,
            f"Video Files (*{source_path.suffix})"
        )

        if save_path:
            try:
                import shutil
                shutil.copy2(self.current_video_path, save_path)
                logger.info(f"Video saved to: {save_path}")
                QMessageBox.information(
                    self,
                    "Success",
                    f"Video saved to:\n{save_path}"
                )
            except Exception as e:
                error_msg = f"Failed to save video: {str(e)}"
                logger.error(error_msg)
                QMessageBox.critical(self, "Error", error_msg)

    def on_state_changed(self, state: QMediaPlayer.PlaybackState):
        """
        Handle playback state changes

        Args:
            state: New playback state
        """
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_pause_btn.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
            )
            self.play_pause_btn.setToolTip("Pause (Space)")
            self.loading_label.hide()
            self.playback_started.emit()
            logger.debug("State: Playing")

        elif state == QMediaPlayer.PlaybackState.PausedState:
            self.play_pause_btn.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )
            self.play_pause_btn.setToolTip("Play (Space)")
            self.playback_paused.emit()
            logger.debug("State: Paused")

        elif state == QMediaPlayer.PlaybackState.StoppedState:
            self.play_pause_btn.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )
            self.play_pause_btn.setToolTip("Play (Space)")
            self.loading_label.hide()
            self.playback_stopped.emit()
            logger.debug("State: Stopped")

    def on_duration_changed(self, duration: int):
        """
        Handle duration change

        Args:
            duration: Video duration in milliseconds
        """
        self.progress_slider.setRange(0, duration)
        self.update_time_label(0, duration)
        logger.debug(f"Duration: {duration}ms ({self.format_time(duration)})")

    def on_position_changed(self, position: int):
        """
        Handle position change

        Args:
            position: Current position in milliseconds
        """
        # Only update slider if not seeking
        if not self.is_seeking:
            self.progress_slider.setValue(position)
            self.update_time_label(position, self.media_player.duration())

    def on_error_occurred(self, error: QMediaPlayer.Error, error_string: str):
        """
        Handle media player errors

        Args:
            error: Error code
            error_string: Error description
        """
        logger.error(f"Media player error: {error_string}")
        self.loading_label.hide()

        error_msg = f"Playback error: {error_string}"
        self.error_occurred.emit(error_msg)

        QMessageBox.critical(
            self,
            "Playback Error",
            f"An error occurred during playback:\n\n{error_string}"
        )

    def update_time_label(self, position: int, duration: int):
        """
        Update time label

        Args:
            position: Current position in milliseconds
            duration: Total duration in milliseconds
        """
        pos_str = self.format_time(position)
        dur_str = self.format_time(duration)
        self.time_label.setText(f"{pos_str} / {dur_str}")

    @staticmethod
    def format_time(milliseconds: int) -> str:
        """
        Format time from milliseconds to MM:SS or HH:MM:SS

        Args:
            milliseconds: Time in milliseconds

        Returns:
            Formatted time string
        """
        seconds = milliseconds // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        hours = minutes // 60
        minutes = minutes % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    def clear(self):
        """Clear the player and reset state"""
        self.stop()
        self.media_player.setSource(QUrl())
        self.current_video_path = None
        self.download_btn.setEnabled(False)
        self.time_label.setText("00:00 / 00:00")
        self.progress_slider.setValue(0)
        logger.info("Player cleared")

    def closeEvent(self, event):
        """Handle widget close event"""
        # Exit fullscreen if active
        if self.is_fullscreen:
            self.exit_fullscreen()

        # Stop playback
        self.stop()

        super().closeEvent(event)

    def get_current_video_path(self) -> Optional[str]:
        """Get current video path"""
        return self.current_video_path

    def is_playing(self) -> bool:
        """Check if video is currently playing"""
        return self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def is_paused(self) -> bool:
        """Check if video is paused"""
        return self.media_player.playbackState() == QMediaPlayer.PlaybackState.PausedState

    def is_stopped(self) -> bool:
        """Check if video is stopped"""
        return self.media_player.playbackState() == QMediaPlayer.PlaybackState.StoppedState

    def get_duration(self) -> int:
        """Get video duration in milliseconds"""
        return self.media_player.duration()

    def get_position(self) -> int:
        """Get current position in milliseconds"""
        return self.media_player.position()


# Export
__all__ = ['VideoPlayerWidget']
