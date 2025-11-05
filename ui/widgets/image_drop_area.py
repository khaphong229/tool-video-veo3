"""
Image Drop Area Widget
Drag-and-drop area for uploading images với preview
"""

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QPainter

from utils import get_logger
from ..styles import get_icon_text

logger = get_logger(__name__)


class ImageDropArea(QWidget):
    """
    Widget drag-and-drop cho images với preview

    Signals:
        image_dropped: Phát khi image được drop (file_path: str)
    """

    # Signals
    image_dropped = pyqtSignal(str)  # file_path

    # Supported formats
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

    def __init__(self, parent=None):
        """Khởi tạo Image Drop Area"""
        super().__init__(parent)

        self.current_image_path: Optional[Path] = None
        self.pixmap: Optional[QPixmap] = None

        self.setupUi()

        # Enable drag and drop
        self.setAcceptDrops(True)

        logger.debug("ImageDropArea initialized")

    def setupUi(self):
        """Thiết lập UI"""

        # Main layout
        layout = QVBoxLayout(self)

        # Preview label
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(400, 300)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #252525;
                border: 2px dashed #3c3c3c;
                border-radius: 8px;
                color: #a0a0a0;
                font-size: 12pt;
            }
        """)
        self.preview_label.setText(
            f"{get_icon_text('image')} Drag & Drop Image Here\n\n"
            "or click Browse button below\n\n"
            f"Supported: {', '.join(self.SUPPORTED_FORMATS)}"
        )

        layout.addWidget(self.preview_label)

        # Info label
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("color: #a0a0a0; font-size: 9pt;")
        layout.addWidget(self.info_label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # Change border color
            self.preview_label.setStyleSheet("""
                QLabel {
                    background-color: #252525;
                    border: 2px dashed #14ffec;
                    border-radius: 8px;
                    color: #14ffec;
                    font-size: 12pt;
                }
            """)

    def dragLeaveEvent(self, event):
        """Handle drag leave"""
        # Reset border
        if not self.current_image_path:
            self.preview_label.setStyleSheet("""
                QLabel {
                    background-color: #252525;
                    border: 2px dashed #3c3c3c;
                    border-radius: 8px;
                    color: #a0a0a0;
                    font-size: 12pt;
                }
            """)

    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        urls = event.mimeData().urls()

        if urls:
            file_path = urls[0].toLocalFile()
            self.load_image(file_path)

            # Reset border
            self.preview_label.setStyleSheet("""
                QLabel {
                    background-color: #252525;
                    border: 2px solid #3c3c3c;
                    border-radius: 8px;
                }
            """)

    def load_image(self, file_path: str) -> bool:
        """
        Load image from file path

        Args:
            file_path: Path to image file

        Returns:
            bool: True if loaded successfully
        """
        try:
            path = Path(file_path)

            # Validate
            if not self.validate_image(str(path)):
                return False

            # Load pixmap
            self.pixmap = QPixmap(str(path))

            if self.pixmap.isNull():
                logger.error(f"Failed to load image: {path}")
                self.show_error("Failed to load image")
                return False

            # Store path
            self.current_image_path = path

            # Display preview
            self.display_preview()

            # Update info
            self.update_info()

            # Emit signal
            self.image_dropped.emit(str(path))

            logger.info(f"Image loaded: {path.name}")

            return True

        except Exception as e:
            logger.error(f"Error loading image: {e}")
            self.show_error(f"Error: {str(e)}")
            return False

    def validate_image(self, file_path: str) -> bool:
        """
        Validate image file

        Args:
            file_path: Path to image

        Returns:
            bool: True if valid
        """
        path = Path(file_path)

        # Check existence
        if not path.exists():
            self.show_error("File does not exist")
            return False

        # Check format
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            self.show_error(
                f"Unsupported format: {path.suffix}\n"
                f"Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            )
            return False

        # Check file size
        file_size = path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            self.show_error(
                f"File too large: {file_size / 1024 / 1024:.1f} MB\n"
                f"Max size: {self.MAX_FILE_SIZE / 1024 / 1024:.0f} MB"
            )
            return False

        return True

    def display_preview(self):
        """Display image preview"""
        if not self.pixmap:
            return

        # Scale to fit while maintaining aspect ratio
        scaled_pixmap = self.pixmap.scaled(
            self.preview_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.preview_label.setPixmap(scaled_pixmap)

        # Update stylesheet
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                border: 2px solid #3c3c3c;
                border-radius: 8px;
            }
        """)

    def update_info(self):
        """Update info label"""
        if not self.current_image_path or not self.pixmap:
            self.info_label.setText("")
            return

        # Get info
        width = self.pixmap.width()
        height = self.pixmap.height()
        file_size = self.current_image_path.stat().st_size
        format_name = self.current_image_path.suffix.upper()[1:]

        # Format size
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / 1024 / 1024:.1f} MB"

        # Update label
        info_text = (
            f"📸 {self.current_image_path.name}  |  "
            f"📐 {width} × {height}  |  "
            f"💾 {size_str}  |  "
            f"📄 {format_name}"
        )

        self.info_label.setText(info_text)

    def show_error(self, message: str):
        """Show error message"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Image Validation Error", message)

    def clear_image(self):
        """Clear current image"""
        self.current_image_path = None
        self.pixmap = None

        # Reset preview
        self.preview_label.setPixmap(QPixmap())
        self.preview_label.setText(
            f"{get_icon_text('image')} Drag & Drop Image Here\n\n"
            "or click Browse button below\n\n"
            f"Supported: {', '.join(self.SUPPORTED_FORMATS)}"
        )
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #252525;
                border: 2px dashed #3c3c3c;
                border-radius: 8px;
                color: #a0a0a0;
                font-size: 12pt;
            }
        """)

        # Clear info
        self.info_label.setText("")

        logger.debug("Image cleared")

    def get_image_path(self) -> Optional[str]:
        """
        Get current image path

        Returns:
            str: Image path or None
        """
        return str(self.current_image_path) if self.current_image_path else None

    def get_image_dimensions(self) -> tuple:
        """
        Get image dimensions

        Returns:
            tuple: (width, height) or (0, 0)
        """
        if self.pixmap:
            return (self.pixmap.width(), self.pixmap.height())
        return (0, 0)

    def has_image(self) -> bool:
        """Check if image is loaded"""
        return self.current_image_path is not None and self.pixmap is not None


# ===== EXPORT =====
__all__ = ['ImageDropArea']
