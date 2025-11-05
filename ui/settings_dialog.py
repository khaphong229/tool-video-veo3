"""
Settings Dialog cho ứng dụng Veo3 Video Generator
Cho phép người dùng cấu hình API, default settings, templates, và advanced options
"""

from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QSpinBox, QSlider, QCheckBox, QListWidget, QListWidgetItem,
    QGroupBox, QFileDialog, QMessageBox, QTextEdit,
    QDialogButtonBox, QFormLayout, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont

from config import settings
from config.user_settings import get_user_settings, UserSettingsManager
from core import create_client, VeoAPIClient
from utils import get_logger
from .styles import get_icon_text

logger = get_logger(__name__)


class ConnectionTestThread(QThread):
    """Thread để test API connection"""
    test_complete = pyqtSignal(bool, str)

    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key

    def run(self):
        try:
            import asyncio
            client = create_client(self.api_key)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            is_connected = loop.run_until_complete(client.test_connection())
            loop.close()

            if is_connected:
                self.test_complete.emit(True, "Kết nối thành công!")
            else:
                self.test_complete.emit(False, "Không thể kết nối")

        except Exception as e:
            self.test_complete.emit(False, f"Lỗi: {str(e)}")


class SettingsDialog(QDialog):
    """
    Dialog để cấu hình settings của ứng dụng

    Signals:
        settings_changed: Phát khi settings được thay đổi
    """

    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        """Khởi tạo Settings Dialog"""
        super().__init__(parent)

        self.settings_manager = get_user_settings()
        self.test_thread: Optional[ConnectionTestThread] = None

        self.setupUi()
        self.load_settings()

        logger.info("Settings Dialog đã được khởi tạo")

    def setupUi(self):
        """Thiết lập giao diện"""

        self.setWindowTitle(f"{get_icon_text('settings')} Settings")
        self.setMinimumSize(700, 600)
        self.resize(800, 650)

        # Main layout
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Application Settings")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Create tabs
        self.create_api_tab()
        self.create_defaults_tab()
        self.create_templates_tab()
        self.create_advanced_tab()

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )

        button_box.button(QDialogButtonBox.StandardButton.Ok).setText("OK")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancel")
        button_box.button(QDialogButtonBox.StandardButton.Apply).setText("Apply")
        button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).setText("Reset to Defaults")

        button_box.accepted.connect(self.accept_settings)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
        button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self.reset_to_defaults)

        layout.addWidget(button_box)

    # ===== TAB 1: API CONFIGURATION =====

    def create_api_tab(self):
        """Tạo tab API Configuration"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # API Key Group
        api_group = QGroupBox(f"{get_icon_text('api')} API Key Configuration")
        api_layout = QFormLayout(api_group)

        # API Key input
        api_key_container = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter your Google AI API Key")
        api_key_container.addWidget(self.api_key_input)

        # Toggle visibility
        self.show_api_key_btn = QPushButton(get_icon_text('user'))
        self.show_api_key_btn.setMaximumWidth(40)
        self.show_api_key_btn.setObjectName("secondaryButton")
        self.show_api_key_btn.clicked.connect(self.toggle_api_key_visibility)
        api_key_container.addWidget(self.show_api_key_btn)

        api_layout.addRow("API Key:", api_key_container)

        # Test Connection button
        self.test_connection_btn = QPushButton(f"{get_icon_text('refresh')} Test Connection")
        self.test_connection_btn.setObjectName("primaryButton")
        self.test_connection_btn.clicked.connect(self.test_api_connection)
        api_layout.addRow("", self.test_connection_btn)

        # Connection status
        self.connection_status_label = QLabel("Status: Not tested")
        api_layout.addRow("Connection Status:", self.connection_status_label)

        # Last test date
        self.last_test_label = QLabel("Never")
        api_layout.addRow("Last Test:", self.last_test_label)

        layout.addWidget(api_group)

        # Model Availability Group
        model_group = QGroupBox(f"{get_icon_text('database')} Available Models")
        model_layout = QVBoxLayout(model_group)

        self.model_list = QListWidget()
        self.model_list.setMaximumHeight(200)
        model_layout.addWidget(self.model_list)

        refresh_models_btn = QPushButton(f"{get_icon_text('refresh')} Refresh Models")
        refresh_models_btn.setObjectName("secondaryButton")
        refresh_models_btn.clicked.connect(self.refresh_models)
        model_layout.addWidget(refresh_models_btn)

        layout.addWidget(model_group)

        # Instructions
        info_label = QLabel(
            "💡 Tip: Get your API key from Google AI Studio\n"
            "https://makersuite.google.com/app/apikey"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #a0a0a0; padding: 10px;")
        layout.addWidget(info_label)

        layout.addStretch()

        self.tabs.addTab(tab, f"{get_icon_text('api')} API Configuration")

    # ===== TAB 2: DEFAULT SETTINGS =====

    def create_defaults_tab(self):
        """Tạo tab Default Settings"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Video Settings Group
        video_group = QGroupBox(f"{get_icon_text('video')} Default Video Settings")
        video_layout = QFormLayout(video_group)

        # Model
        self.default_model_combo = QComboBox()
        self.default_model_combo.addItems(settings.AVAILABLE_MODELS)
        video_layout.addRow("Default Model:", self.default_model_combo)

        # Resolution
        self.default_resolution_combo = QComboBox()
        self.default_resolution_combo.addItems(list(settings.RESOLUTIONS.keys()))
        video_layout.addRow("Default Resolution:", self.default_resolution_combo)

        # Aspect Ratio
        self.default_aspect_ratio_combo = QComboBox()
        self.default_aspect_ratio_combo.addItems(list(settings.ASPECT_RATIOS.keys()))
        video_layout.addRow("Default Aspect Ratio:", self.default_aspect_ratio_combo)

        # Duration with slider
        duration_container = QHBoxLayout()
        self.default_duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.default_duration_slider.setMinimum(settings.VIDEO_DURATION_RANGE['min'])
        self.default_duration_slider.setMaximum(settings.VIDEO_DURATION_RANGE['max'])
        self.default_duration_slider.setValue(settings.VIDEO_DURATION_RANGE['default'])
        self.default_duration_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.default_duration_slider.setTickInterval(5)

        self.duration_value_label = QLabel(f"{settings.VIDEO_DURATION_RANGE['default']} sec")
        self.default_duration_slider.valueChanged.connect(
            lambda v: self.duration_value_label.setText(f"{v} sec")
        )

        duration_container.addWidget(self.default_duration_slider)
        duration_container.addWidget(self.duration_value_label)

        video_layout.addRow("Default Duration:", duration_container)

        # FPS
        self.default_fps_combo = QComboBox()
        self.default_fps_combo.addItems([str(fps) for fps in settings.FPS_OPTIONS])
        video_layout.addRow("Default FPS:", self.default_fps_combo)

        layout.addWidget(video_group)

        # Paths Group
        paths_group = QGroupBox(f"{get_icon_text('folder')} Output Directories")
        paths_layout = QFormLayout(paths_group)

        # Output Directory
        output_container = QHBoxLayout()
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setReadOnly(True)
        output_container.addWidget(self.output_dir_input)

        browse_output_btn = QPushButton(f"{get_icon_text('folder')} Browse")
        browse_output_btn.setObjectName("secondaryButton")
        browse_output_btn.clicked.connect(self.browse_output_directory)
        output_container.addWidget(browse_output_btn)

        paths_layout.addRow("Output Directory:", output_container)

        # Temp Directory
        temp_container = QHBoxLayout()
        self.temp_dir_input = QLineEdit()
        self.temp_dir_input.setReadOnly(True)
        temp_container.addWidget(self.temp_dir_input)

        browse_temp_btn = QPushButton(f"{get_icon_text('folder')} Browse")
        browse_temp_btn.setObjectName("secondaryButton")
        browse_temp_btn.clicked.connect(self.browse_temp_directory)
        temp_container.addWidget(browse_temp_btn)

        paths_layout.addRow("Temp Directory:", temp_container)

        layout.addWidget(paths_group)

        layout.addStretch()

        self.tabs.addTab(tab, f"{get_icon_text('settings')} Default Settings")

    # ===== TAB 3: TEMPLATES =====

    def create_templates_tab(self):
        """Tạo tab Templates"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Template List
        list_group = QGroupBox(f"{get_icon_text('bookmark')} Saved Templates")
        list_layout = QVBoxLayout(list_group)

        self.template_list = QListWidget()
        list_layout.addWidget(self.template_list)

        # Buttons
        button_layout = QHBoxLayout()

        add_template_btn = QPushButton(f"{get_icon_text('add')} Add Template")
        add_template_btn.setObjectName("primaryButton")
        add_template_btn.clicked.connect(self.add_template)
        button_layout.addWidget(add_template_btn)

        edit_template_btn = QPushButton(f"{get_icon_text('edit')} Edit")
        edit_template_btn.setObjectName("secondaryButton")
        edit_template_btn.clicked.connect(self.edit_template)
        button_layout.addWidget(edit_template_btn)

        delete_template_btn = QPushButton(f"{get_icon_text('delete')} Delete")
        delete_template_btn.setObjectName("dangerButton")
        delete_template_btn.clicked.connect(self.delete_template)
        button_layout.addWidget(delete_template_btn)

        list_layout.addLayout(button_layout)

        layout.addWidget(list_group)

        # Template Preview
        preview_group = QGroupBox(f"{get_icon_text('search')} Template Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.template_preview = QTextEdit()
        self.template_preview.setReadOnly(True)
        self.template_preview.setMaximumHeight(150)
        self.template_preview.setPlaceholderText("Select a template to preview")
        preview_layout.addWidget(self.template_preview)

        layout.addWidget(preview_group)

        # Connect selection changed
        self.template_list.currentItemChanged.connect(self.on_template_selected)

        self.tabs.addTab(tab, f"{get_icon_text('bookmark')} Templates")

    # ===== TAB 4: ADVANCED =====

    def create_advanced_tab(self):
        """Tạo tab Advanced Settings"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Generation Settings
        gen_group = QGroupBox(f"{get_icon_text('settings')} Generation Settings")
        gen_layout = QFormLayout(gen_group)

        # Max Concurrent
        self.max_concurrent_spin = QSpinBox()
        self.max_concurrent_spin.setMinimum(1)
        self.max_concurrent_spin.setMaximum(10)
        self.max_concurrent_spin.setValue(3)
        gen_layout.addRow("Max Concurrent Generations:", self.max_concurrent_spin)

        # Auto Retry
        self.auto_retry_checkbox = QCheckBox("Enable automatic retry on failure")
        self.auto_retry_checkbox.setChecked(True)
        gen_layout.addRow("", self.auto_retry_checkbox)

        # Retry Count
        self.retry_count_spin = QSpinBox()
        self.retry_count_spin.setMinimum(1)
        self.retry_count_spin.setMaximum(10)
        self.retry_count_spin.setValue(3)
        gen_layout.addRow("Retry Count:", self.retry_count_spin)

        layout.addWidget(gen_group)

        # Logging Settings
        log_group = QGroupBox(f"{get_icon_text('log')} Logging Settings")
        log_layout = QFormLayout(log_group)

        # Enable Logging
        self.enable_logging_checkbox = QCheckBox("Enable application logging")
        self.enable_logging_checkbox.setChecked(True)
        log_layout.addRow("", self.enable_logging_checkbox)

        # Log Level
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
        self.log_level_combo.setCurrentText('INFO')
        log_layout.addRow("Log Level:", self.log_level_combo)

        layout.addWidget(log_group)

        # UI Settings
        ui_group = QGroupBox(f"{get_icon_text('search')} UI Preferences")
        ui_layout = QFormLayout(ui_group)

        # Dark Theme
        self.dark_theme_checkbox = QCheckBox("Use dark theme")
        self.dark_theme_checkbox.setChecked(True)
        ui_layout.addRow("", self.dark_theme_checkbox)

        # Auto Save
        self.auto_save_checkbox = QCheckBox("Auto-save projects")
        self.auto_save_checkbox.setChecked(True)
        ui_layout.addRow("", self.auto_save_checkbox)

        # Auto Save Interval
        self.auto_save_interval_spin = QSpinBox()
        self.auto_save_interval_spin.setMinimum(60)
        self.auto_save_interval_spin.setMaximum(3600)
        self.auto_save_interval_spin.setValue(300)
        self.auto_save_interval_spin.setSuffix(" seconds")
        ui_layout.addRow("Auto-save Interval:", self.auto_save_interval_spin)

        # Show Notifications
        self.notifications_checkbox = QCheckBox("Show desktop notifications")
        self.notifications_checkbox.setChecked(True)
        ui_layout.addRow("", self.notifications_checkbox)

        layout.addWidget(ui_group)

        # Maintenance
        maint_group = QGroupBox(f"{get_icon_text('delete')} Maintenance")
        maint_layout = QVBoxLayout(maint_group)

        clear_cache_btn = QPushButton(f"{get_icon_text('delete')} Clear Cache")
        clear_cache_btn.setObjectName("dangerButton")
        clear_cache_btn.clicked.connect(self.clear_cache)
        maint_layout.addWidget(clear_cache_btn)

        clear_logs_btn = QPushButton(f"{get_icon_text('delete')} Clear Logs")
        clear_logs_btn.setObjectName("dangerButton")
        clear_logs_btn.clicked.connect(self.clear_logs)
        maint_layout.addWidget(clear_logs_btn)

        layout.addWidget(maint_group)

        layout.addStretch()

        self.tabs.addTab(tab, f"{get_icon_text('settings')} Advanced")

    # ===== LOAD / SAVE SETTINGS =====

    def load_settings(self):
        """Load settings từ UserSettingsManager"""
        try:
            # API Tab
            self.api_key_input.setText(self.settings_manager.get_api_key())

            last_test = self.settings_manager.get('api.last_test_date')
            if last_test:
                self.last_test_label.setText(last_test)

            status = self.settings_manager.get('api.connection_status', 'not_tested')
            self.update_connection_status(status)

            # Load available models
            self.load_available_models()

            # Defaults Tab
            self.default_model_combo.setCurrentText(self.settings_manager.get_default_model())
            self.default_resolution_combo.setCurrentText(self.settings_manager.get_default_resolution())
            self.default_aspect_ratio_combo.setCurrentText(self.settings_manager.get_default_aspect_ratio())
            self.default_duration_slider.setValue(self.settings_manager.get_default_duration())
            self.default_fps_combo.setCurrentText(str(self.settings_manager.get('defaults.fps', settings.DEFAULT_FPS)))

            self.output_dir_input.setText(self.settings_manager.get_output_directory())
            self.temp_dir_input.setText(self.settings_manager.get('defaults.temp_directory', str(settings.TEMP_DIR)))

            # Templates Tab
            self.load_templates()

            # Advanced Tab
            self.max_concurrent_spin.setValue(self.settings_manager.get_max_concurrent())
            self.auto_retry_checkbox.setChecked(self.settings_manager.get_auto_retry())
            self.retry_count_spin.setValue(self.settings_manager.get('advanced.retry_count', 3))
            self.enable_logging_checkbox.setChecked(self.settings_manager.get('advanced.enable_logging', True))
            self.log_level_combo.setCurrentText(self.settings_manager.get('advanced.log_level', 'INFO'))
            self.dark_theme_checkbox.setChecked(self.settings_manager.get('advanced.dark_theme', True))
            self.auto_save_checkbox.setChecked(self.settings_manager.get('advanced.auto_save_project', True))
            self.auto_save_interval_spin.setValue(self.settings_manager.get('advanced.auto_save_interval', 300))
            self.notifications_checkbox.setChecked(self.settings_manager.get('advanced.show_notifications', True))

            logger.info("Đã load settings vào dialog")

        except Exception as e:
            logger.error(f"Lỗi khi load settings: {e}")
            QMessageBox.warning(self, "Warning", f"Could not load some settings:\n{str(e)}")

    def save_settings(self) -> bool:
        """
        Lưu settings từ UI vào UserSettingsManager

        Returns:
            bool: True nếu thành công
        """
        try:
            # Validate trước khi save
            if not self.validate_settings():
                return False

            # API
            self.settings_manager.set_api_key(self.api_key_input.text().strip())

            # Defaults
            self.settings_manager.set_default_model(self.default_model_combo.currentText())
            self.settings_manager.set_default_resolution(self.default_resolution_combo.currentText())
            self.settings_manager.set_default_aspect_ratio(self.default_aspect_ratio_combo.currentText())
            self.settings_manager.set_default_duration(self.default_duration_slider.value())
            self.settings_manager.set('defaults.fps', int(self.default_fps_combo.currentText()))
            self.settings_manager.set_output_directory(self.output_dir_input.text())
            self.settings_manager.set('defaults.temp_directory', self.temp_dir_input.text())

            # Advanced
            self.settings_manager.set('advanced.max_concurrent_generations', self.max_concurrent_spin.value())
            self.settings_manager.set('advanced.auto_retry_failed', self.auto_retry_checkbox.isChecked())
            self.settings_manager.set('advanced.retry_count', self.retry_count_spin.value())
            self.settings_manager.set('advanced.enable_logging', self.enable_logging_checkbox.isChecked())
            self.settings_manager.set('advanced.log_level', self.log_level_combo.currentText())
            self.settings_manager.set('advanced.dark_theme', self.dark_theme_checkbox.isChecked())
            self.settings_manager.set('advanced.auto_save_project', self.auto_save_checkbox.isChecked())
            self.settings_manager.set('advanced.auto_save_interval', self.auto_save_interval_spin.value())
            self.settings_manager.set('advanced.show_notifications', self.notifications_checkbox.isChecked())

            # Save to file
            success = self.settings_manager.save_settings()

            if success:
                logger.info("Đã lưu settings thành công")
                self.settings_changed.emit()
                return True
            else:
                QMessageBox.critical(self, "Error", "Could not save settings to file")
                return False

        except Exception as e:
            logger.error(f"Lỗi khi save settings: {e}")
            QMessageBox.critical(self, "Error", f"Error saving settings:\n{str(e)}")
            return False

    def validate_settings(self) -> bool:
        """
        Validate settings trước khi save

        Returns:
            bool: True nếu valid
        """
        # Validate API key (nếu có)
        api_key = self.api_key_input.text().strip()
        if api_key and len(api_key) < 20:
            QMessageBox.warning(
                self,
                "Validation Error",
                "API Key appears to be invalid (too short)"
            )
            self.tabs.setCurrentIndex(0)  # Switch to API tab
            return False

        # Validate output directory
        output_dir = self.output_dir_input.text()
        if not output_dir:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Output directory cannot be empty"
            )
            self.tabs.setCurrentIndex(1)  # Switch to Defaults tab
            return False

        # All validations passed
        return True

    # ===== API TAB METHODS =====

    def toggle_api_key_visibility(self):
        """Toggle hiển thị/ẩn API key"""
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_api_key_btn.setText("🔒")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_api_key_btn.setText(get_icon_text('user'))

    def test_api_connection(self):
        """Test API connection"""
        api_key = self.api_key_input.text().strip()

        if not api_key:
            QMessageBox.warning(self, "Warning", "Please enter an API key first")
            return

        # Disable button
        self.test_connection_btn.setEnabled(False)
        self.test_connection_btn.setText("Testing...")
        self.connection_status_label.setText("Status: Testing...")

        # Start test thread
        self.test_thread = ConnectionTestThread(api_key)
        self.test_thread.test_complete.connect(self.on_test_complete)
        self.test_thread.finished.connect(lambda: self.test_connection_btn.setEnabled(True))
        self.test_thread.start()

    def on_test_complete(self, success: bool, message: str):
        """Callback khi test connection hoàn tất"""
        self.test_connection_btn.setText(f"{get_icon_text('refresh')} Test Connection")

        if success:
            status = "connected"
            self.connection_status_label.setText(f"Status: {get_icon_text('success')} {message}")
            self.connection_status_label.setStyleSheet("color: #66bb6a;")
            QMessageBox.information(self, "Success", message)
        else:
            status = "failed"
            self.connection_status_label.setText(f"Status: {get_icon_text('error')} {message}")
            self.connection_status_label.setStyleSheet("color: #d32f2f;")
            QMessageBox.warning(self, "Connection Failed", message)

        # Update test date
        test_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_test_label.setText(test_date)

        # Save status
        self.settings_manager.set_connection_status(status, test_date)

    def update_connection_status(self, status: str):
        """Update connection status display"""
        if status == 'connected':
            self.connection_status_label.setText(f"Status: {get_icon_text('success')} Connected")
            self.connection_status_label.setStyleSheet("color: #66bb6a;")
        elif status == 'failed':
            self.connection_status_label.setText(f"Status: {get_icon_text('error')} Failed")
            self.connection_status_label.setStyleSheet("color: #d32f2f;")
        else:
            self.connection_status_label.setText("Status: Not tested")
            self.connection_status_label.setStyleSheet("color: #a0a0a0;")

    def load_available_models(self):
        """Load available models into list"""
        self.model_list.clear()
        models = settings.AVAILABLE_MODELS

        for model in models:
            item = QListWidgetItem(f"{get_icon_text('video')} {model}")
            self.model_list.addItem(item)

    def refresh_models(self):
        """Refresh models list from API"""
        # TODO: Implement actual API call to get models
        self.load_available_models()
        QMessageBox.information(self, "Info", "Models list refreshed")

    # ===== DEFAULTS TAB METHODS =====

    def browse_output_directory(self):
        """Browse output directory"""
        current_dir = self.output_dir_input.text() or str(settings.OUTPUT_DIR)
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            current_dir
        )

        if directory:
            self.output_dir_input.setText(directory)

    def browse_temp_directory(self):
        """Browse temp directory"""
        current_dir = self.temp_dir_input.text() or str(settings.TEMP_DIR)
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Temp Directory",
            current_dir
        )

        if directory:
            self.temp_dir_input.setText(directory)

    # ===== TEMPLATES TAB METHODS =====

    def load_templates(self):
        """Load templates into list"""
        self.template_list.clear()
        templates = self.settings_manager.get_templates()

        for template in templates:
            name = template.get('name', 'Unnamed Template')
            item = QListWidgetItem(f"{get_icon_text('bookmark')} {name}")
            item.setData(Qt.ItemDataRole.UserRole, template)
            self.template_list.addItem(item)

    def on_template_selected(self, current, previous):
        """Callback khi template được chọn"""
        if current:
            template = current.data(Qt.ItemDataRole.UserRole)
            preview = f"Name: {template.get('name', 'N/A')}\n"
            preview += f"Style: {template.get('base_style', 'N/A')}\n"
            preview += f"Category: {template.get('category', 'N/A')}\n"
            preview += f"Tags: {', '.join(template.get('tags', []))}\n"
            self.template_preview.setText(preview)
        else:
            self.template_preview.clear()

    def add_template(self):
        """Add new template"""
        # TODO: Implement template editor dialog
        QMessageBox.information(self, "Info", "Template editor will be implemented")

    def edit_template(self):
        """Edit selected template"""
        current = self.template_list.currentItem()
        if not current:
            QMessageBox.warning(self, "Warning", "Please select a template to edit")
            return

        # TODO: Implement template editor dialog
        QMessageBox.information(self, "Info", "Template editor will be implemented")

    def delete_template(self):
        """Delete selected template"""
        current_row = self.template_list.currentRow()

        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a template to delete")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this template?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.settings_manager.delete_template(current_row)
            self.load_templates()
            logger.info(f"Deleted template at index {current_row}")

    # ===== ADVANCED TAB METHODS =====

    def clear_cache(self):
        """Clear application cache"""
        reply = QMessageBox.question(
            self,
            "Confirm",
            "Are you sure you want to clear the cache?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # TODO: Implement cache clearing
            import shutil
            try:
                if settings.TEMP_DIR.exists():
                    shutil.rmtree(settings.TEMP_DIR)
                    settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)

                QMessageBox.information(self, "Success", "Cache cleared successfully")
                logger.info("Cache cleared")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not clear cache:\n{str(e)}")

    def clear_logs(self):
        """Clear application logs"""
        reply = QMessageBox.question(
            self,
            "Confirm",
            "Are you sure you want to clear all logs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            from utils import clear_logs
            if clear_logs():
                QMessageBox.information(self, "Success", "Logs cleared successfully")
            else:
                QMessageBox.warning(self, "Warning", "Could not clear all logs")

    # ===== DIALOG BUTTON HANDLERS =====

    def accept_settings(self):
        """OK button clicked - save and close"""
        if self.save_settings():
            self.accept()

    def apply_settings(self):
        """Apply button clicked - save without closing"""
        if self.save_settings():
            QMessageBox.information(self, "Success", "Settings saved successfully")

    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Are you sure you want to reset all settings to defaults?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.settings_manager.reset_to_defaults()
            self.load_settings()
            QMessageBox.information(self, "Success", "Settings reset to defaults")
            logger.info("Settings reset to defaults")


# ===== EXPORT =====
__all__ = ['SettingsDialog']
