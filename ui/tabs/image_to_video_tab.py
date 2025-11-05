"""
Image to Video Tab
Animate static images into videos using Google Veo API
"""

from typing import Optional, Dict, Any, List
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QGroupBox, QListWidget,
    QListWidgetItem, QCheckBox, QFileDialog, QMessageBox,
    QScrollArea, QFrame, QSizePolicy, QRadioButton,
    QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QIcon

from config import settings
from config.user_settings import get_user_settings
from utils import get_logger
from ..styles import get_icon_text
from ..widgets import ImageDropArea, CollapsibleSection

logger = get_logger(__name__)


class ImageToVideoTab(QWidget):
    """
    Tab Image to Video - Animate static images

    Signals:
        generate_requested: Phát khi user click Generate
        add_to_queue_requested: Phát khi user click Add to Queue
    """

    # Signals
    generate_requested = pyqtSignal(dict)
    add_to_queue_requested = pyqtSignal(dict)

    # Animation presets
    ANIMATION_PRESETS = {
        'Camera Zoom In': 'Slow zoom in on the subject, cinematic camera movement',
        'Parallax Effect': 'Gentle parallax movement, subtle depth effect',
        'Subject Forward': 'Subject moves forward towards camera, dynamic motion',
        'Camera Rotation': 'Smooth camera rotation around subject, orbit movement',
        'Pan Left to Right': 'Slow pan from left to right, establishing shot',
        'Dolly Push': 'Camera pushes in, dramatic reveal',
        'Custom': ''  # User-defined
    }

    def __init__(self, parent=None):
        """Khởi tạo Image to Video Tab"""
        super().__init__(parent)

        self.user_settings = get_user_settings()
        self.reference_images: List[str] = []

        self.setupUi()
        self.connect_signals()

        logger.info("ImageToVideoTab initialized")

    def setupUi(self):
        """Thiết lập giao diện"""

        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Content widget
        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setSpacing(12)

        # ===== SECTION 1: IMAGE INPUT =====
        self.create_image_input_section(main_layout)

        # ===== SECTION 2: PROMPT & ANIMATION =====
        self.create_animation_section(main_layout)

        # ===== SECTION 3: REFERENCE IMAGES (Veo 3.1) =====
        self.create_reference_images_section(main_layout)

        # ===== SECTION 4: FIRST & LAST FRAME =====
        self.create_transition_section(main_layout)

        # ===== SECTION 5: MODEL & SETTINGS =====
        self.create_settings_section(main_layout)

        # ===== SECTION 6: ACTIONS =====
        self.create_actions_section(main_layout)

        # ===== SECTION 7: PREVIEW =====
        self.create_preview_section(main_layout)

        # Add stretch
        main_layout.addStretch()

        # Set scroll content
        scroll.setWidget(content_widget)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

    # ===== UI SECTIONS =====

    def create_image_input_section(self, parent_layout: QVBoxLayout):
        """Tạo Image Input Section"""

        group = QGroupBox(f"{get_icon_text('image')} Source Image")
        layout = QVBoxLayout(group)

        # Drag & Drop area
        self.image_drop_area = ImageDropArea()
        layout.addWidget(self.image_drop_area)

        # Buttons
        button_layout = QHBoxLayout()

        self.browse_btn = QPushButton(f"{get_icon_text('folder')} Browse Image")
        self.browse_btn.setObjectName("primaryButton")
        self.browse_btn.clicked.connect(self.browse_image)
        button_layout.addWidget(self.browse_btn)

        self.clear_btn = QPushButton(f"{get_icon_text('delete')} Clear")
        self.clear_btn.setObjectName("dangerButton")
        self.clear_btn.clicked.connect(self.clear_image)
        self.clear_btn.setEnabled(False)
        button_layout.addWidget(self.clear_btn)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        parent_layout.addWidget(group)

    def create_animation_section(self, parent_layout: QVBoxLayout):
        """Tạo Animation Section"""

        group = QGroupBox(f"{get_icon_text('video')} Animation & Motion")
        layout = QVBoxLayout(group)

        # Prompt input
        prompt_label = QLabel("Animation Description:")
        layout.addWidget(prompt_label)

        self.animation_prompt = QTextEdit()
        self.animation_prompt.setPlaceholderText(
            "Describe how you want the image to be animated...\n\n"
            "Example: Slow zoom into the subject with a gentle camera rotation"
        )
        self.animation_prompt.setMaximumHeight(100)
        layout.addWidget(self.animation_prompt)

        # Animation presets
        preset_label = QLabel("Animation Presets:")
        layout.addWidget(preset_label)

        # First row of presets
        preset_layout1 = QHBoxLayout()
        presets = list(self.ANIMATION_PRESETS.keys())

        for preset in presets[:4]:
            btn = QPushButton(preset)
            btn.setObjectName("secondaryButton")
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.clicked.connect(lambda checked, p=preset: self.apply_animation_preset(p))
            preset_layout1.addWidget(btn)

        layout.addLayout(preset_layout1)

        # Second row of presets
        preset_layout2 = QHBoxLayout()

        for preset in presets[4:]:
            btn = QPushButton(preset)
            btn.setObjectName("secondaryButton")
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.clicked.connect(lambda checked, p=preset: self.apply_animation_preset(p))
            preset_layout2.addWidget(btn)

        preset_layout2.addStretch()
        layout.addLayout(preset_layout2)

        parent_layout.addWidget(group)

    def create_reference_images_section(self, parent_layout: QVBoxLayout):
        """Tạo Reference Images Section (Veo 3.1)"""

        # Collapsible section
        self.reference_section = CollapsibleSection(
            f"{get_icon_text('image')} Reference Images (Veo 3.1 - Optional)"
        )

        # Content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Info
        info_label = QLabel(
            "Add up to 3 reference images for style/composition guidance.\n"
            "Requires Veo 3.1 model."
        )
        info_label.setStyleSheet("color: #a0a0a0; font-size: 9pt;")
        info_label.setWordWrap(True)
        content_layout.addWidget(info_label)

        # Reference list
        self.reference_list = QListWidget()
        self.reference_list.setMaximumHeight(150)
        content_layout.addWidget(self.reference_list)

        # Buttons
        ref_button_layout = QHBoxLayout()

        add_ref_btn = QPushButton(f"{get_icon_text('add')} Add Reference")
        add_ref_btn.setObjectName("secondaryButton")
        add_ref_btn.clicked.connect(self.add_reference_image_dialog)
        ref_button_layout.addWidget(add_ref_btn)

        remove_ref_btn = QPushButton(f"{get_icon_text('remove')} Remove")
        remove_ref_btn.setObjectName("dangerButton")
        remove_ref_btn.clicked.connect(self.remove_reference_image_selected)
        ref_button_layout.addWidget(remove_ref_btn)

        move_up_btn = QPushButton(f"{get_icon_text('arrow_up')} Up")
        move_up_btn.setObjectName("secondaryButton")
        move_up_btn.clicked.connect(self.move_reference_up)
        ref_button_layout.addWidget(move_up_btn)

        move_down_btn = QPushButton(f"{get_icon_text('arrow_down')} Down")
        move_down_btn.setObjectName("secondaryButton")
        move_down_btn.clicked.connect(self.move_reference_down)
        ref_button_layout.addWidget(move_down_btn)

        ref_button_layout.addStretch()

        content_layout.addLayout(ref_button_layout)

        # Set content
        self.reference_section.setContent(content)
        self.reference_section.setExpanded(False)

        parent_layout.addWidget(self.reference_section)

    def create_transition_section(self, parent_layout: QVBoxLayout):
        """Tạo First & Last Frame Section"""

        # Collapsible section
        self.transition_section = CollapsibleSection(
            f"{get_icon_text('video')} Transition Mode (First → Last Frame)"
        )

        # Content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Enable toggle
        self.enable_transition_checkbox = QCheckBox(
            "Enable transition mode (animate between two frames)"
        )
        content_layout.addWidget(self.enable_transition_checkbox)

        # Info
        info_label = QLabel(
            "First frame: Your uploaded image\n"
            "Last frame: Upload a second image to define the end state"
        )
        info_label.setStyleSheet("color: #a0a0a0; font-size: 9pt; margin-left: 20px;")
        content_layout.addWidget(info_label)

        # Last frame upload
        last_frame_layout = QHBoxLayout()
        last_frame_layout.addWidget(QLabel("Last Frame:"))

        self.last_frame_path_label = QLabel("No image selected")
        self.last_frame_path_label.setStyleSheet("color: #a0a0a0;")
        last_frame_layout.addWidget(self.last_frame_path_label)

        self.browse_last_frame_btn = QPushButton(f"{get_icon_text('folder')} Browse")
        self.browse_last_frame_btn.setObjectName("secondaryButton")
        self.browse_last_frame_btn.clicked.connect(self.browse_last_frame)
        self.browse_last_frame_btn.setEnabled(False)
        last_frame_layout.addWidget(self.browse_last_frame_btn)

        last_frame_layout.addStretch()

        content_layout.addLayout(last_frame_layout)

        # Connect checkbox
        self.enable_transition_checkbox.toggled.connect(
            self.browse_last_frame_btn.setEnabled
        )

        # Set content
        self.transition_section.setContent(content)
        self.transition_section.setExpanded(False)

        parent_layout.addWidget(self.transition_section)

    def create_settings_section(self, parent_layout: QVBoxLayout):
        """Tạo Settings Section"""

        group = QGroupBox(f"{get_icon_text('settings')} Generation Settings")
        layout = QVBoxLayout(group)

        # Model
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))

        self.model_display = QLabel(self.user_settings.get_default_model())
        self.model_display.setStyleSheet("color: #14ffec; font-weight: 600;")
        model_layout.addWidget(self.model_display)

        model_note = QLabel("(Change in sidebar →)")
        model_note.setStyleSheet("color: #a0a0a0; font-size: 8pt;")
        model_layout.addWidget(model_note)

        model_layout.addStretch()
        layout.addLayout(model_layout)

        # Duration
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration:"))

        self.duration_display = QLabel("5 seconds")
        self.duration_display.setStyleSheet("color: #e0e0e0;")
        duration_layout.addWidget(self.duration_display)

        duration_note = QLabel("(Change in sidebar →)")
        duration_note.setStyleSheet("color: #a0a0a0; font-size: 8pt;")
        duration_layout.addWidget(duration_note)

        duration_layout.addStretch()
        layout.addLayout(duration_layout)

        # Resolution
        resolution_label = QLabel("Output Resolution:")
        layout.addWidget(resolution_label)

        resolution_layout = QHBoxLayout()
        self.resolution_group = QButtonGroup()

        resolutions = ['720p', '1080p', '4K']
        for i, res in enumerate(resolutions):
            radio = QRadioButton(res)
            self.resolution_group.addButton(radio, i)
            resolution_layout.addWidget(radio)

            if res == self.user_settings.get_default_resolution():
                radio.setChecked(True)

        resolution_layout.addStretch()
        layout.addLayout(resolution_layout)

        parent_layout.addWidget(group)

    def create_actions_section(self, parent_layout: QVBoxLayout):
        """Tạo Actions Section"""

        layout = QHBoxLayout()

        # Generate Button
        self.generate_btn = QPushButton(f"{get_icon_text('play')} Generate Video")
        self.generate_btn.setObjectName("primaryButton")
        self.generate_btn.setMinimumHeight(50)
        self.generate_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.generate_btn.clicked.connect(self.on_generate_clicked)
        layout.addWidget(self.generate_btn, stretch=2)

        # Add to Queue
        self.queue_btn = QPushButton(f"{get_icon_text('add')} Add to Queue")
        self.queue_btn.setObjectName("secondaryButton")
        self.queue_btn.setMinimumHeight(50)
        self.queue_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.queue_btn.clicked.connect(self.on_add_to_queue_clicked)
        layout.addWidget(self.queue_btn, stretch=1)

        parent_layout.addLayout(layout)

    def create_preview_section(self, parent_layout: QVBoxLayout):
        """Tạo Preview Section"""

        group = QGroupBox(f"{get_icon_text('video')} Preview & Result")
        layout = QVBoxLayout(group)

        # Video player placeholder
        self.video_player = QLabel("Video preview will appear here")
        self.video_player.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_player.setMinimumHeight(250)
        self.video_player.setStyleSheet("""
            QLabel {
                background-color: #252525;
                border: 2px dashed #3c3c3c;
                border-radius: 8px;
                color: #a0a0a0;
                font-size: 12pt;
            }
        """)
        layout.addWidget(self.video_player)

        # Status
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #a0a0a0;")
        layout.addWidget(self.status_label)

        parent_layout.addWidget(group)

    # ===== SIGNAL CONNECTIONS =====

    def connect_signals(self):
        """Kết nối signals"""

        # Image drop area
        self.image_drop_area.image_dropped.connect(self.on_image_dropped)

        logger.debug("Signals connected")

    # ===== SLOT HANDLERS =====

    def on_image_dropped(self, file_path: str):
        """
        Handler khi image được drop

        Args:
            file_path: Path to dropped image
        """
        logger.info(f"Image dropped: {file_path}")

        # Enable clear button
        self.clear_btn.setEnabled(True)

        # Update status
        self.status_label.setText(f"✅ Image loaded: {Path(file_path).name}")

    def browse_image(self):
        """Browse for image file"""

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Source Image",
            "",
            "Images (*.jpg *.jpeg *.png *.bmp *.gif *.webp);;All Files (*)"
        )

        if file_path:
            self.image_drop_area.load_image(file_path)

    def clear_image(self):
        """Clear current image"""

        reply = QMessageBox.question(
            self,
            "Clear Image",
            "Are you sure you want to clear the current image?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.image_drop_area.clear_image()
            self.clear_btn.setEnabled(False)
            self.status_label.setText("")

            logger.info("Image cleared")

    def validate_image(self, file_path: str) -> bool:
        """
        Validate image file

        Args:
            file_path: Path to image

        Returns:
            bool: True if valid
        """
        return self.image_drop_area.validate_image(file_path)

    def apply_animation_preset(self, preset: str):
        """
        Apply animation preset

        Args:
            preset: Preset name
        """
        if preset not in self.ANIMATION_PRESETS:
            return

        preset_text = self.ANIMATION_PRESETS[preset]

        if preset == 'Custom':
            # Clear and let user type
            self.animation_prompt.clear()
        else:
            # Append preset to current text
            current_text = self.animation_prompt.toPlainText().strip()

            if current_text:
                new_text = f"{current_text}, {preset_text}"
            else:
                new_text = preset_text

            self.animation_prompt.setPlainText(new_text)

            # Move cursor to end
            cursor = self.animation_prompt.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.animation_prompt.setTextCursor(cursor)

        logger.info(f"Applied animation preset: {preset}")

    def add_reference_image_dialog(self):
        """Show dialog to add reference image"""

        if len(self.reference_images) >= 3:
            QMessageBox.warning(
                self,
                "Limit Reached",
                "Maximum 3 reference images allowed"
            )
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Reference Image",
            "",
            "Images (*.jpg *.jpeg *.png *.bmp *.gif *.webp);;All Files (*)"
        )

        if file_path:
            self.add_reference_image(file_path)

    def add_reference_image(self, file_path: str):
        """
        Add reference image

        Args:
            file_path: Path to reference image
        """
        if len(self.reference_images) >= 3:
            return

        # Validate
        if not self.validate_image(file_path):
            return

        # Add to list
        self.reference_images.append(file_path)

        # Add to UI
        item = QListWidgetItem(f"{get_icon_text('image')} {Path(file_path).name}")
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        self.reference_list.addItem(item)

        logger.info(f"Added reference image: {Path(file_path).name}")

    def remove_reference_image_selected(self):
        """Remove selected reference image"""

        current_row = self.reference_list.currentRow()

        if current_row >= 0:
            self.remove_reference_image(current_row)

    def remove_reference_image(self, index: int):
        """
        Remove reference image by index

        Args:
            index: Index in list
        """
        if 0 <= index < len(self.reference_images):
            removed = self.reference_images.pop(index)
            self.reference_list.takeItem(index)

            logger.info(f"Removed reference image: {Path(removed).name}")

    def move_reference_up(self):
        """Move selected reference image up"""

        current_row = self.reference_list.currentRow()

        if current_row > 0:
            # Swap in list
            self.reference_images[current_row], self.reference_images[current_row - 1] = \
                self.reference_images[current_row - 1], self.reference_images[current_row]

            # Swap in UI
            item = self.reference_list.takeItem(current_row)
            self.reference_list.insertItem(current_row - 1, item)
            self.reference_list.setCurrentRow(current_row - 1)

    def move_reference_down(self):
        """Move selected reference image down"""

        current_row = self.reference_list.currentRow()

        if 0 <= current_row < len(self.reference_images) - 1:
            # Swap in list
            self.reference_images[current_row], self.reference_images[current_row + 1] = \
                self.reference_images[current_row + 1], self.reference_images[current_row]

            # Swap in UI
            item = self.reference_list.takeItem(current_row)
            self.reference_list.insertItem(current_row + 1, item)
            self.reference_list.setCurrentRow(current_row + 1)

    def browse_last_frame(self):
        """Browse for last frame image"""

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Last Frame Image",
            "",
            "Images (*.jpg *.jpeg *.png *.bmp *.gif *.webp);;All Files (*)"
        )

        if file_path and self.validate_image(file_path):
            self.last_frame_path_label.setText(Path(file_path).name)
            self.last_frame_path_label.setStyleSheet("color: #14ffec;")

    def on_generate_clicked(self):
        """Handler cho Generate button"""

        # Validate
        if not self.validate_inputs():
            return

        # Get parameters
        params = self.get_generation_params()

        logger.info(f"Generate image-to-video requested: {params}")

        # Emit signal
        self.generate_requested.emit(params)

        # Update status
        self.status_label.setText("🎬 Starting generation...")

    def on_add_to_queue_clicked(self):
        """Handler cho Add to Queue button"""

        if not self.validate_inputs():
            return

        params = self.get_generation_params()

        logger.info(f"Add to queue requested: {params}")

        # Emit signal
        self.add_to_queue_requested.emit(params)

        QMessageBox.information(self, "Success", "Added to generation queue!")

    # ===== HELPER METHODS =====

    def validate_inputs(self) -> bool:
        """
        Validate inputs before generation

        Returns:
            bool: True if valid
        """
        # Check image
        if not self.image_drop_area.has_image():
            QMessageBox.warning(self, "Validation Error", "Please upload a source image")
            return False

        # Check animation prompt
        animation = self.animation_prompt.toPlainText().strip()
        if not animation:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please describe the animation or use a preset"
            )
            return False

        # Check transition mode
        if self.enable_transition_checkbox.isChecked():
            if self.last_frame_path_label.text() == "No image selected":
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "Please upload a last frame image for transition mode"
                )
                return False

        return True

    def get_generation_params(self) -> Dict[str, Any]:
        """
        Get generation parameters

        Returns:
            dict: Generation parameters
        """
        # Get resolution
        checked_button = self.resolution_group.checkedButton()
        resolution = checked_button.text() if checked_button else "1080p"

        params = {
            'type': 'image_to_video',
            'source_image': self.image_drop_area.get_image_path(),
            'animation_prompt': self.animation_prompt.toPlainText().strip(),
            'model': self.model_display.text(),
            'resolution': resolution,
            'reference_images': self.reference_images.copy(),
            'transition_mode': self.enable_transition_checkbox.isChecked(),
            'last_frame': self.last_frame_path_label.text() if self.enable_transition_checkbox.isChecked() else None
        }

        return params

    def update_model_display(self, model: str):
        """Update model display"""
        self.model_display.setText(model)

    def update_duration_display(self, duration: int):
        """Update duration display"""
        self.duration_display.setText(f"{duration} seconds")


# ===== EXPORT =====
__all__ = ['ImageToVideoTab']
