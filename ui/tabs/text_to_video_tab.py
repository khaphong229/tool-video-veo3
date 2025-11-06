"""
Text to Video Tab
Tab chính để tạo video từ text prompts
"""

from typing import Optional, Dict, Any
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QGroupBox, QSpinBox,
    QCheckBox, QRadioButton, QButtonGroup, QSlider,
    QProgressBar, QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor

from config import settings
from config.user_settings import get_user_settings
from utils import get_logger
from ..styles import get_icon_text
from ..widgets import CollapsibleSection

logger = get_logger(__name__)


class TextToVideoTab(QWidget):
    """
    Tab Text to Video - Core feature

    Signals:
        generate_requested: Phát khi user click Generate (params: dict)
        add_to_queue_requested: Phát khi user click Add to Queue
        template_saved: Phát khi template được save
    """

    # Signals
    generate_requested = pyqtSignal(dict)  # generation parameters
    add_to_queue_requested = pyqtSignal(dict)
    template_saved = pyqtSignal(dict)

    # Style presets
    STYLE_PRESETS = {
        'Cinematic': 'cinematic, dramatic lighting, film grain, depth of field, professional cinematography',
        'Anime': 'anime style, vibrant colors, detailed animation, studio quality',
        'Realistic': 'photorealistic, high detail, natural lighting, 8k quality',
        'Abstract': 'abstract art, surreal, artistic, creative, unique perspective',
        'Vintage': 'vintage film, retro, nostalgic, film grain, classic',
        'Sci-Fi': 'science fiction, futuristic, high-tech, neon lights, cyberpunk',
        'Fantasy': 'fantasy, magical, ethereal, enchanting, mystical',
        'Documentary': 'documentary style, natural, authentic, raw footage'
    }

    def __init__(self, parent=None):
        """Khởi tạo Text to Video Tab"""
        super().__init__(parent)

        self.user_settings = get_user_settings()
        self.current_template = None
        self.is_generating = False

        self.setupUi()
        self.connect_signals()

        logger.info("TextToVideoTab initialized")

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

        # ===== SECTION 1: PROMPT INPUT =====
        self.create_prompt_section(main_layout)

        # ===== SECTION 2: ADVANCED SETTINGS (Collapsible) =====
        self.create_advanced_section(main_layout)

        # ===== SECTION 3: MODEL & OUTPUT =====
        self.create_model_output_section(main_layout)

        # ===== SECTION 4: ACTIONS =====
        self.create_actions_section(main_layout)

        # ===== SECTION 5: PREVIEW / RESULT =====
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

    def create_prompt_section(self, parent_layout: QVBoxLayout):
        """Tạo Prompt Input Section"""

        group = QGroupBox(f"{get_icon_text('edit')} Prompt")
        layout = QVBoxLayout(group)

        # Main prompt
        prompt_label = QLabel("Describe your video:")
        layout.addWidget(prompt_label)

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText(
            "Example: A serene mountain landscape at sunset, "
            "with golden light reflecting off a calm lake, "
            "surrounded by pine trees, cinematic camera movement"
        )
        self.prompt_input.setMinimumHeight(120)
        self.prompt_input.setMaximumHeight(200)
        self.prompt_input.textChanged.connect(self.update_char_count)
        layout.addWidget(self.prompt_input)

        # Character counter
        self.char_counter = QLabel("0 / 2000 characters")
        self.char_counter.setStyleSheet("color: #a0a0a0; font-size: 8pt;")
        self.char_counter.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.char_counter)

        # Quick style buttons
        style_label = QLabel("Quick Styles:")
        layout.addWidget(style_label)

        style_buttons_layout = QHBoxLayout()
        style_buttons_layout.setSpacing(6)

        for style_name in self.STYLE_PRESETS.keys():
            btn = QPushButton(style_name)
            btn.setObjectName("secondaryButton")
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.clicked.connect(lambda checked, s=style_name: self.apply_style_preset(s))
            style_buttons_layout.addWidget(btn)

            # Wrap after 4 buttons
            if style_name == 'Abstract':
                layout.addLayout(style_buttons_layout)
                style_buttons_layout = QHBoxLayout()
                style_buttons_layout.setSpacing(6)

        # Add remaining buttons
        if style_buttons_layout.count() > 0:
            layout.addLayout(style_buttons_layout)

        # Use Template button
        template_btn_layout = QHBoxLayout()
        self.use_template_btn = QPushButton(f"{get_icon_text('bookmark')} Use Template")
        self.use_template_btn.setObjectName("secondaryButton")
        self.use_template_btn.clicked.connect(self.show_template_picker)
        template_btn_layout.addWidget(self.use_template_btn)
        template_btn_layout.addStretch()

        layout.addLayout(template_btn_layout)

        parent_layout.addWidget(group)

    def create_advanced_section(self, parent_layout: QVBoxLayout):
        """Tạo Advanced Settings Section (Collapsible)"""

        # Collapsible section
        self.advanced_section = CollapsibleSection(f"{get_icon_text('settings')} Advanced Settings")

        # Content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Negative Prompt
        neg_label = QLabel("Negative Prompt (what to avoid):")
        content_layout.addWidget(neg_label)

        self.negative_prompt_input = QTextEdit()
        self.negative_prompt_input.setPlaceholderText(
            "Example: blurry, low quality, distorted, watermark, text, logos"
        )
        self.negative_prompt_input.setMaximumHeight(80)
        content_layout.addWidget(self.negative_prompt_input)

        # Seed
        seed_layout = QHBoxLayout()
        seed_label = QLabel("Seed (optional):")
        seed_layout.addWidget(seed_label)

        self.seed_spin = QSpinBox()
        self.seed_spin.setMinimum(0)
        self.seed_spin.setMaximum(999999999)
        self.seed_spin.setValue(0)
        self.seed_spin.setSpecialValueText("Random")
        seed_layout.addWidget(self.seed_spin)

        random_seed_btn = QPushButton(f"{get_icon_text('refresh')} Random")
        random_seed_btn.setObjectName("secondaryButton")
        random_seed_btn.clicked.connect(self.randomize_seed)
        seed_layout.addWidget(random_seed_btn)

        seed_layout.addStretch()
        content_layout.addLayout(seed_layout)

        # Enable Audio
        self.enable_audio_checkbox = QCheckBox("Enable audio generation (if supported)")
        content_layout.addWidget(self.enable_audio_checkbox)

        # Set content
        self.advanced_section.setContent(content)

        # Start collapsed
        self.advanced_section.setExpanded(False)

        parent_layout.addWidget(self.advanced_section)

    def create_model_output_section(self, parent_layout: QVBoxLayout):
        """Tạo Model & Output Settings Section"""

        group = QGroupBox(f"{get_icon_text('video')} Model & Output Settings")
        layout = QVBoxLayout(group)

        # Model Selection
        model_layout = QHBoxLayout()
        model_label = QLabel("Model:")
        model_layout.addWidget(model_label)

        # Note: Model selection is in sidebar, this is display only
        self.model_display = QLabel(self.user_settings.get_default_model())
        self.model_display.setStyleSheet("color: #14ffec; font-weight: 600;")
        model_layout.addWidget(self.model_display)

        model_note = QLabel("(Change in sidebar →)")
        model_note.setStyleSheet("color: #a0a0a0; font-size: 8pt;")
        model_layout.addWidget(model_note)

        model_layout.addStretch()
        layout.addLayout(model_layout)

        # Aspect Ratio
        aspect_label = QLabel("Aspect Ratio:")
        layout.addWidget(aspect_label)

        aspect_layout = QHBoxLayout()
        self.aspect_ratio_group = QButtonGroup()

        aspect_ratios = [
            ('16:9', '16:9 (Landscape)'),
            ('9:16', '9:16 (Portrait)'),
            ('1:1', '1:1 (Square)'),
            ('4:3', '4:3 (Classic)'),
        ]

        for i, (value, label) in enumerate(aspect_ratios):
            radio = QRadioButton(label)
            self.aspect_ratio_group.addButton(radio, i)
            aspect_layout.addWidget(radio)

            if value == self.user_settings.get_default_aspect_ratio():
                radio.setChecked(True)

        layout.addLayout(aspect_layout)

        # Duration
        duration_label = QLabel("Duration:")
        layout.addWidget(duration_label)

        duration_layout = QHBoxLayout()

        self.duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.duration_slider.setMinimum(settings.VIDEO_DURATION_RANGE['min'])
        self.duration_slider.setMaximum(settings.VIDEO_DURATION_RANGE['max'])
        self.duration_slider.setValue(self.user_settings.get_default_duration())
        self.duration_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.duration_slider.setTickInterval(5)
        duration_layout.addWidget(self.duration_slider)

        self.duration_value_label = QLabel(f"{self.user_settings.get_default_duration()} sec")
        self.duration_value_label.setMinimumWidth(60)
        self.duration_slider.valueChanged.connect(
            lambda v: self.duration_value_label.setText(f"{v} sec")
        )
        duration_layout.addWidget(self.duration_value_label)

        layout.addLayout(duration_layout)

        # Resolution
        resolution_label = QLabel("Resolution:")
        layout.addWidget(resolution_label)

        resolution_layout = QHBoxLayout()
        self.resolution_group = QButtonGroup()

        resolutions = ['480p', '720p', '1080p', '4K']
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

        # Generate Video Button (Primary)
        self.generate_btn = QPushButton(f"{get_icon_text('play')} Generate Video")
        self.generate_btn.setObjectName("primaryButton")
        self.generate_btn.setMinimumHeight(50)
        self.generate_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.generate_btn.clicked.connect(self.on_generate_clicked)
        layout.addWidget(self.generate_btn, stretch=2)

        # Add to Queue Button
        self.queue_btn = QPushButton(f"{get_icon_text('add')} Add to Queue")
        self.queue_btn.setObjectName("secondaryButton")
        self.queue_btn.setMinimumHeight(50)
        self.queue_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.queue_btn.clicked.connect(self.on_add_to_queue_clicked)
        layout.addWidget(self.queue_btn, stretch=1)

        # Save as Template Button
        self.save_template_btn = QPushButton(f"{get_icon_text('save')} Save as Template")
        self.save_template_btn.setObjectName("secondaryButton")
        self.save_template_btn.setMinimumHeight(50)
        self.save_template_btn.clicked.connect(self.save_as_template)
        layout.addWidget(self.save_template_btn, stretch=1)

        parent_layout.addLayout(layout)

    def create_preview_section(self, parent_layout: QVBoxLayout):
        """Tạo Preview / Result Section"""

        group = QGroupBox(f"{get_icon_text('video')} Preview & Result")
        layout = QVBoxLayout(group)

        # Video player placeholder
        self.video_player = QLabel("No video generated yet")
        self.video_player.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_player.setMinimumHeight(300)
        self.video_player.setStyleSheet("""
            QLabel {
                background-color: #252525;
                border: 2px dashed #3c3c3c;
                border-radius: 8px;
                color: #a0a0a0;
                font-size: 14pt;
            }
        """)
        layout.addWidget(self.video_player)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Status text
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #a0a0a0;")
        layout.addWidget(self.status_label)

        # Action buttons (hidden initially)
        result_buttons_layout = QHBoxLayout()

        self.download_btn = QPushButton(f"{get_icon_text('download')} Download Video")
        self.download_btn.setObjectName("primaryButton")
        self.download_btn.setVisible(False)
        self.download_btn.clicked.connect(self.on_download_clicked)
        result_buttons_layout.addWidget(self.download_btn)

        self.open_folder_btn = QPushButton(f"{get_icon_text('folder')} Open Folder")
        self.open_folder_btn.setObjectName("secondaryButton")
        self.open_folder_btn.setVisible(False)
        self.open_folder_btn.clicked.connect(self.on_open_folder_clicked)
        result_buttons_layout.addWidget(self.open_folder_btn)

        result_buttons_layout.addStretch()

        layout.addLayout(result_buttons_layout)

        parent_layout.addWidget(group)

    # ===== SIGNAL CONNECTIONS =====

    def connect_signals(self):
        """Kết nối signals"""
        logger.debug("Connecting signals for TextToVideoTab")

    # ===== SLOT HANDLERS =====

    def update_char_count(self):
        """Update character counter"""
        text = self.prompt_input.toPlainText()
        count = len(text)
        max_chars = 2000

        self.char_counter.setText(f"{count} / {max_chars} characters")

        # Change color if over limit
        if count > max_chars:
            self.char_counter.setStyleSheet("color: #d32f2f; font-size: 8pt;")
        elif count > max_chars * 0.9:
            self.char_counter.setStyleSheet("color: #ffa726; font-size: 8pt;")
        else:
            self.char_counter.setStyleSheet("color: #a0a0a0; font-size: 8pt;")

    def apply_style_preset(self, style: str):
        """
        Apply style preset to prompt

        Args:
            style: Style name
        """
        if style not in self.STYLE_PRESETS:
            logger.warning(f"Unknown style: {style}")
            return

        current_text = self.prompt_input.toPlainText().strip()
        style_text = self.STYLE_PRESETS[style]

        # Append style to current text
        if current_text:
            new_text = f"{current_text}, {style_text}"
        else:
            new_text = style_text

        self.prompt_input.setPlainText(new_text)

        # Move cursor to end
        cursor = self.prompt_input.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.prompt_input.setTextCursor(cursor)

        logger.info(f"Applied style preset: {style}")

    def show_template_picker(self):
        """Show template picker dialog"""
        from PyQt6.QtWidgets import QInputDialog

        templates = self.user_settings.get_templates()

        if not templates:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "No Templates",
                "You don't have any saved templates yet.\n\n"
                "Create one by clicking 'Save as Template' after configuring your settings."
            )
            return

        # Show template picker
        template_names = [t.get('name', 'Unnamed') for t in templates]

        name, ok = QInputDialog.getItem(
            self,
            "Select Template",
            "Choose a template to load:",
            template_names,
            0,
            False
        )

        if ok and name:
            index = template_names.index(name)
            self.load_template(index)

    def load_template(self, template_id: int):
        """
        Load template by ID

        Args:
            template_id: Index of template in templates list
        """
        templates = self.user_settings.get_templates()

        if 0 <= template_id < len(templates):
            template = templates[template_id]

            # Load template data
            self.prompt_input.setPlainText(template.get('base_style', ''))
            # TODO: Load other template settings

            self.current_template = template
            logger.info(f"Loaded template: {template.get('name', 'Unnamed')}")

    def save_as_template(self):
        """Save current settings as template"""
        from PyQt6.QtWidgets import QInputDialog, QMessageBox

        # Get template name
        name, ok = QInputDialog.getText(
            self,
            "Save Template",
            "Enter template name:"
        )

        if not ok or not name:
            return

        # Create template
        template = {
            'name': name,
            'base_style': self.prompt_input.toPlainText(),
            'negative_prompt': self.negative_prompt_input.toPlainText(),
            'category': 'user',
            'tags': [],
            'settings': {
                'aspect_ratio': self.get_selected_aspect_ratio(),
                'duration': self.duration_slider.value(),
                'resolution': self.get_selected_resolution(),
                'enable_audio': self.enable_audio_checkbox.isChecked()
            }
        }

        # Save to settings
        self.user_settings.add_template(template)
        self.user_settings.save_settings()

        # Emit signal
        self.template_saved.emit(template)

        QMessageBox.information(
            self,
            "Success",
            f"Template '{name}' saved successfully!"
        )

        logger.info(f"Saved template: {name}")

    def randomize_seed(self):
        """Generate random seed"""
        import random
        seed = random.randint(1, 999999999)
        self.seed_spin.setValue(seed)

    def on_generate_clicked(self):
        """Handler cho Generate Video button"""

        # Validate
        if not self.validate_inputs():
            return

        # Get parameters
        params = self.get_generation_params()

        logger.info(f"Generate requested with params: {params}")

        # Emit signal
        self.generate_requested.emit(params)

        # Start mock generation (for demo)
        self.start_generation_simulation()

    def on_add_to_queue_clicked(self):
        """Handler cho Add to Queue button"""

        if not self.validate_inputs():
            return

        params = self.get_generation_params()

        logger.info(f"Add to queue requested: {params}")

        # Emit signal
        self.add_to_queue_requested.emit(params)

        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Success", "Added to generation queue!")

    def on_download_clicked(self):
        """Handler cho Download button"""
        logger.info("Download clicked")
        # TODO: Implement download

    def on_open_folder_clicked(self):
        """Handler cho Open Folder button"""
        logger.info("Open folder clicked")
        # TODO: Implement open folder

    # ===== HELPER METHODS =====

    def validate_inputs(self) -> bool:
        """
        Validate inputs before generation

        Returns:
            bool: True if valid
        """
        from PyQt6.QtWidgets import QMessageBox

        # Check prompt
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Validation Error", "Please enter a prompt")
            return False

        if len(prompt) > 2000:
            QMessageBox.warning(self, "Validation Error", "Prompt is too long (max 2000 characters)")
            return False

        return True

    def get_generation_params(self) -> Dict[str, Any]:
        """
        Get generation parameters từ UI

        Returns:
            dict: Generation parameters
        """
        seed = self.seed_spin.value()
        if seed == 0:
            seed = None  # Random

        return {
            'prompt': self.prompt_input.toPlainText().strip(),
            'negative_prompt': self.negative_prompt_input.toPlainText().strip(),
            'model': self.model_display.text(),
            'aspect_ratio': self.get_selected_aspect_ratio(),
            'duration': self.duration_slider.value(),
            'resolution': self.get_selected_resolution(),
            'seed': seed,
            'enable_audio': self.enable_audio_checkbox.isChecked()
        }

    def get_selected_aspect_ratio(self) -> str:
        """Get selected aspect ratio"""
        checked_button = self.aspect_ratio_group.checkedButton()
        if checked_button:
            return checked_button.text().split(' ')[0]  # "16:9 (Landscape)" -> "16:9"
        return "16:9"

    def get_selected_resolution(self) -> str:
        """Get selected resolution"""
        checked_button = self.resolution_group.checkedButton()
        if checked_button:
            return checked_button.text()
        return "1080p"

    def update_progress(self, progress: int, status: str):
        """
        Update progress bar và status

        Args:
            progress: Progress percentage (0-100)
            status: Status message
        """
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)

        logger.debug(f"Progress: {progress}% - {status}")

    def start_generation_simulation(self):
        """Start mock generation (for demo/testing)"""

        # Disable generate button
        self.generate_btn.setEnabled(False)
        self.is_generating = True

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Initializing...")

        # Hide result buttons
        self.download_btn.setVisible(False)
        self.open_folder_btn.setVisible(False)

        # Simulate progress
        self.simulation_progress = 0
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self.update_simulation)
        self.simulation_timer.start(100)  # Update every 100ms

        logger.info("Started generation simulation")

    def update_simulation(self):
        """Update simulation progress"""
        self.simulation_progress += 1

        # Update progress in stages
        if self.simulation_progress < 20:
            self.update_progress(self.simulation_progress * 5, "Preparing...")
        elif self.simulation_progress < 50:
            progress = 20 + (self.simulation_progress - 20)
            self.update_progress(progress, "Generating frames...")
        elif self.simulation_progress < 80:
            progress = 50 + (self.simulation_progress - 50)
            self.update_progress(progress, "Rendering video...")
        elif self.simulation_progress < 100:
            progress = 80 + (self.simulation_progress - 80)
            self.update_progress(progress, "Finalizing...")
        else:
            # Complete
            self.simulation_timer.stop()
            self.complete_generation_simulation()

    def complete_generation_simulation(self):
        """Complete generation simulation"""

        self.update_progress(100, "Complete!")

        # Show result
        self.video_player.setText(f"{get_icon_text('success')} Video Generated Successfully!")
        self.video_player.setStyleSheet("""
            QLabel {
                background-color: #0d7377;
                border: 2px solid #14ffec;
                border-radius: 8px;
                color: #ffffff;
                font-size: 14pt;
                font-weight: 600;
            }
        """)

        # Show result buttons
        QTimer.singleShot(500, lambda: self.download_btn.setVisible(True))
        QTimer.singleShot(600, lambda: self.open_folder_btn.setVisible(True))

        # Re-enable generate button
        self.generate_btn.setEnabled(True)
        self.is_generating = False

        logger.info("Generation simulation completed")

    def update_model_display(self, model: str):
        """
        Update model display label

        Args:
            model: Model name
        """
        self.model_display.setText(model)


# ===== EXPORT =====
__all__ = ['TextToVideoTab']
