"""
Collapsible Section Widget
Widget có thể collapse/expand để tiết kiệm không gian UI
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont

from utils import get_logger

logger = get_logger(__name__)


class CollapsibleSection(QWidget):
    """
    Widget section có thể collapse/expand

    Example:
        section = CollapsibleSection("Advanced Settings")
        section.setContent(your_widget)
    """

    def __init__(self, title: str = "", parent=None):
        """
        Khởi tạo Collapsible Section

        Args:
            title: Tiêu đề của section
            parent: Parent widget
        """
        super().__init__(parent)

        self.is_expanded = True
        self._content_height = 0

        self.setupUi(title)

    def setupUi(self, title: str):
        """Thiết lập UI"""

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Toggle button
        self.toggle_button = QPushButton(f"▼ {title}")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.clicked.connect(self.toggle)

        # Style toggle button
        self.toggle_button.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px;
                background-color: #2d2d2d;
                border: none;
                border-radius: 4px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3c3c3c;
            }
        """)

        main_layout.addWidget(self.toggle_button)

        # Content frame
        self.content_frame = QFrame()
        self.content_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(8, 8, 8, 8)

        main_layout.addWidget(self.content_frame)

        # Animation
        self.animation = QPropertyAnimation(self.content_frame, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def setContent(self, widget: QWidget):
        """
        Set nội dung của section

        Args:
            widget: Widget content
        """
        # Clear existing content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add new content
        self.content_layout.addWidget(widget)

        # Store content height
        widget.adjustSize()
        self._content_height = widget.sizeHint().height() + 16  # +padding

        # Set initial state
        if self.is_expanded:
            self.content_frame.setMaximumHeight(self._content_height)
        else:
            self.content_frame.setMaximumHeight(0)

    def toggle(self):
        """Toggle collapse/expand"""
        if self.toggle_button.isChecked():
            self.expand()
        else:
            self.collapse()

    def expand(self):
        """Expand section"""
        self.is_expanded = True
        self.toggle_button.setText(self.toggle_button.text().replace("▶", "▼"))

        self.animation.setStartValue(0)
        self.animation.setEndValue(self._content_height if self._content_height > 0 else 16777215)
        self.animation.start()

        logger.debug("Section expanded")

    def collapse(self):
        """Collapse section"""
        self.is_expanded = False
        self.toggle_button.setText(self.toggle_button.text().replace("▼", "▶"))

        self.animation.setStartValue(self.content_frame.height())
        self.animation.setEndValue(0)
        self.animation.start()

        logger.debug("Section collapsed")

    def setExpanded(self, expanded: bool):
        """
        Set expanded state programmatically

        Args:
            expanded: True để expand, False để collapse
        """
        self.toggle_button.setChecked(expanded)
        if expanded:
            self.expand()
        else:
            self.collapse()


# ===== EXPORT =====
__all__ = ['CollapsibleSection']
