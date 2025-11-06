"""
File chính để khởi chạy ứng dụng Google Veo Video Generator
Tạo giao diện PyQt6 và quản lý luồng chương trình
"""

import sys
import asyncio
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox,
    QSpinBox, QGroupBox, QMessageBox, QFileDialog, QProgressBar,
    QTabWidget, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon

from config import settings
from core import create_client, VeoAPIClient
from utils import get_logger, setup_logging

# Khởi tạo logger
logger = get_logger(__name__)


class ConnectionTestThread(QThread):
    """
    Thread để test kết nối API không chặn UI
    """
    # Signal để gửi kết quả về main thread
    connection_result = pyqtSignal(bool, str)

    def __init__(self, api_client: VeoAPIClient):
        super().__init__()
        self.api_client = api_client

    def run(self):
        """Chạy test connection trong thread riêng"""
        try:
            # Tạo event loop mới cho thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Test connection
            is_connected = loop.run_until_complete(
                self.api_client.test_connection()
            )

            if is_connected:
                self.connection_result.emit(True, "Kết nối thành công!")
            else:
                self.connection_result.emit(False, "Không thể kết nối đến API")

            loop.close()

        except Exception as e:
            self.connection_result.emit(False, f"Lỗi: {str(e)}")


class ModelListThread(QThread):
    """
    Thread để lấy danh sách models không chặn UI
    """
    # Signal để gửi danh sách models về main thread
    models_loaded = pyqtSignal(list)

    def __init__(self, api_client: VeoAPIClient):
        super().__init__()
        self.api_client = api_client

    def run(self):
        """Lấy danh sách models trong thread riêng"""
        try:
            # Tạo event loop mới
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Lấy danh sách models
            models = loop.run_until_complete(
                self.api_client.list_models()
            )

            self.models_loaded.emit(models)
            loop.close()

        except Exception as e:
            logger.error(f"Lỗi khi lấy danh sách models: {e}")
            self.models_loaded.emit([])


class VideoGenerationThread(QThread):
    """
    Thread để tạo video không chặn UI
    """
    # Signals
    generation_started = pyqtSignal()
    generation_progress = pyqtSignal(int, str)  # progress, message
    generation_completed = pyqtSignal(dict)  # result dict
    generation_error = pyqtSignal(str)

    def __init__(self, api_client: VeoAPIClient, params: dict):
        super().__init__()
        self.api_client = api_client
        self.params = params

    def run(self):
        """Tạo video trong thread riêng"""
        try:
            self.generation_started.emit()

            # Tạo event loop mới
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Tạo video
            result = loop.run_until_complete(
                self.api_client.generate_video(**self.params)
            )

            self.generation_completed.emit(result)
            loop.close()

        except Exception as e:
            logger.error(f"Lỗi khi tạo video: {e}")
            self.generation_error.emit(str(e))


class MainWindow(QMainWindow):
    """
    Cửa sổ chính của ứng dụng
    """

    def __init__(self):
        super().__init__()
        self.api_client: Optional[VeoAPIClient] = None
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """Khởi tạo giao diện người dùng"""

        # Thiết lập cửa sổ
        self.setWindowTitle(settings.APP_TITLE)
        self.setGeometry(100, 100, settings.WINDOW_SIZE['width'], settings.WINDOW_SIZE['height'])
        self.setMinimumSize(settings.WINDOW_SIZE['min_width'], settings.WINDOW_SIZE['min_height'])

        # Widget chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout chính
        main_layout = QVBoxLayout(central_widget)

        # ===== TAB WIDGET =====
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Tab 1: Tạo video
        self.video_generation_tab = self.create_video_generation_tab()
        self.tabs.addTab(self.video_generation_tab, "Tạo Video")

        # Tab 2: Cài đặt
        self.settings_tab = self.create_settings_tab()
        self.tabs.addTab(self.settings_tab, "Cài đặt")

        # Tab 3: Logs
        self.logs_tab = self.create_logs_tab()
        self.tabs.addTab(self.logs_tab, "Logs")

        # ===== STATUS BAR =====
        self.statusBar().showMessage("Sẵn sàng")

        logger.info("Đã khởi tạo giao diện")

    def create_video_generation_tab(self) -> QWidget:
        """Tạo tab tạo video"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # ===== PROMPT INPUT =====
        prompt_group = QGroupBox("Mô tả Video")
        prompt_layout = QVBoxLayout(prompt_group)

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText(
            "Nhập mô tả chi tiết cho video của bạn...\n\n"
            "Ví dụ: A beautiful sunset over the ocean with waves crashing on the beach"
        )
        self.prompt_input.setMinimumHeight(100)
        prompt_layout.addWidget(self.prompt_input)

        layout.addWidget(prompt_group)

        # ===== VIDEO SETTINGS =====
        settings_group = QGroupBox("Cài đặt Video")
        settings_layout = QVBoxLayout(settings_group)

        # Model selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(settings.AVAILABLE_MODELS)
        model_layout.addWidget(self.model_combo)
        settings_layout.addLayout(model_layout)

        # Resolution
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel("Độ phân giải:"))
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(list(settings.RESOLUTIONS.keys()))
        self.resolution_combo.setCurrentText(settings.DEFAULT_RESOLUTION)
        resolution_layout.addWidget(self.resolution_combo)
        settings_layout.addLayout(resolution_layout)

        # Aspect ratio
        aspect_layout = QHBoxLayout()
        aspect_layout.addWidget(QLabel("Tỷ lệ khung hình:"))
        self.aspect_ratio_combo = QComboBox()
        self.aspect_ratio_combo.addItems(list(settings.ASPECT_RATIOS.keys()))
        self.aspect_ratio_combo.setCurrentText(settings.DEFAULT_ASPECT_RATIO)
        aspect_layout.addWidget(self.aspect_ratio_combo)
        settings_layout.addLayout(aspect_layout)

        # Duration
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Độ dài (giây):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setMinimum(settings.VIDEO_DURATION_RANGE['min'])
        self.duration_spin.setMaximum(settings.VIDEO_DURATION_RANGE['max'])
        self.duration_spin.setValue(settings.VIDEO_DURATION_RANGE['default'])
        duration_layout.addWidget(self.duration_spin)
        settings_layout.addLayout(duration_layout)

        layout.addWidget(settings_group)

        # ===== PROGRESS BAR =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # ===== BUTTONS =====
        button_layout = QHBoxLayout()

        self.generate_btn = QPushButton("Tạo Video")
        self.generate_btn.clicked.connect(self.generate_video)
        self.generate_btn.setMinimumHeight(40)
        button_layout.addWidget(self.generate_btn)

        self.cancel_btn = QPushButton("Hủy")
        self.cancel_btn.clicked.connect(self.cancel_generation)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setMinimumHeight(40)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        # ===== OUTPUT LOG =====
        output_group = QGroupBox("Kết quả")
        output_layout = QVBoxLayout(output_group)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        output_layout.addWidget(self.output_text)

        layout.addWidget(output_group)

        return tab

    def create_settings_tab(self) -> QWidget:
        """Tạo tab cài đặt"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # ===== API KEY =====
        api_group = QGroupBox("Cấu hình API")
        api_layout = QVBoxLayout(api_group)

        # API Key input
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Nhập Google AI API Key")
        key_layout.addWidget(self.api_key_input)

        # Show/Hide button
        self.show_key_btn = QPushButton("👁")
        self.show_key_btn.setMaximumWidth(40)
        self.show_key_btn.clicked.connect(self.toggle_api_key_visibility)
        key_layout.addWidget(self.show_key_btn)

        api_layout.addLayout(key_layout)

        # Test connection button
        self.test_connection_btn = QPushButton("Test Kết nối")
        self.test_connection_btn.clicked.connect(self.test_connection)
        api_layout.addWidget(self.test_connection_btn)

        # Save API key button
        self.save_key_btn = QPushButton("Lưu API Key")
        self.save_key_btn.clicked.connect(self.save_api_key)
        api_layout.addWidget(self.save_key_btn)

        layout.addWidget(api_group)

        # ===== PATHS =====
        paths_group = QGroupBox("Đường dẫn")
        paths_layout = QVBoxLayout(paths_group)

        # Output folder
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Thư mục lưu video:"))
        self.output_path_label = QLabel(str(settings.OUTPUT_DIR))
        output_layout.addWidget(self.output_path_label)
        self.browse_output_btn = QPushButton("Chọn")
        self.browse_output_btn.clicked.connect(self.browse_output_folder)
        output_layout.addWidget(self.browse_output_btn)
        paths_layout.addLayout(output_layout)

        layout.addWidget(paths_group)

        # Spacer
        layout.addStretch()

        return tab

    def create_logs_tab(self) -> QWidget:
        """Tạo tab hiển thị logs"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Log viewer
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setFont(QFont("Courier New", 9))
        layout.addWidget(self.log_viewer)

        # Buttons
        button_layout = QHBoxLayout()

        self.refresh_log_btn = QPushButton("Làm mới")
        self.refresh_log_btn.clicked.connect(self.refresh_logs)
        button_layout.addWidget(self.refresh_log_btn)

        self.clear_log_btn = QPushButton("Xóa Logs")
        self.clear_log_btn.clicked.connect(self.clear_logs)
        button_layout.addWidget(self.clear_log_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        return tab

    def load_settings(self):
        """Tải cài đặt từ file"""
        # Load API key
        if settings.validate_api_key():
            self.api_key_input.setText(settings.GOOGLE_API_KEY)
            self.initialize_api_client()

    def initialize_api_client(self):
        """Khởi tạo API client"""
        try:
            api_key = self.api_key_input.text().strip()

            if not api_key:
                return

            self.api_client = create_client(api_key)
            self.statusBar().showMessage("Đã kết nối API client")
            logger.info("Đã khởi tạo API client")

            # Load models
            self.load_models()

        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo API client: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể khởi tạo API client:\n{str(e)}")

    def load_models(self):
        """Tải danh sách models từ API"""
        if not self.api_client:
            return

        self.statusBar().showMessage("Đang tải danh sách models...")

        # Tạo thread để load models
        self.model_thread = ModelListThread(self.api_client)
        self.model_thread.models_loaded.connect(self.on_models_loaded)
        self.model_thread.start()

    def on_models_loaded(self, models: list):
        """Callback khi models được tải"""
        if models:
            self.model_combo.clear()
            self.model_combo.addItems(models)
            self.statusBar().showMessage(f"Đã tải {len(models)} model(s)")
        else:
            self.statusBar().showMessage("Không thể tải danh sách models")

    def toggle_api_key_visibility(self):
        """Toggle hiển thị/ẩn API key"""
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_key_btn.setText("🔒")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_btn.setText("👁")

    def test_connection(self):
        """Test kết nối với API"""
        api_key = self.api_key_input.text().strip()

        if not api_key:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập API key!")
            return

        try:
            # Khởi tạo client tạm
            temp_client = create_client(api_key)

            self.statusBar().showMessage("Đang kiểm tra kết nối...")
            self.test_connection_btn.setEnabled(False)

            # Tạo thread để test connection
            self.test_thread = ConnectionTestThread(temp_client)
            self.test_thread.connection_result.connect(self.on_connection_tested)
            self.test_thread.finished.connect(
                lambda: self.test_connection_btn.setEnabled(True)
            )
            self.test_thread.start()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi test kết nối:\n{str(e)}")
            self.test_connection_btn.setEnabled(True)

    def on_connection_tested(self, success: bool, message: str):
        """Callback khi test connection hoàn tất"""
        self.statusBar().showMessage(message)

        if success:
            QMessageBox.information(self, "Thành công", message)
            self.initialize_api_client()
        else:
            QMessageBox.warning(self, "Thất bại", message)

    def save_api_key(self):
        """Lưu API key vào file .env"""
        api_key = self.api_key_input.text().strip()

        if not api_key:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập API key!")
            return

        try:
            env_file = settings.BASE_DIR / '.env'

            # Đọc file .env hiện tại
            env_content = ""
            if env_file.exists():
                env_content = env_file.read_text()

            # Cập nhật hoặc thêm GOOGLE_API_KEY
            if 'GOOGLE_API_KEY=' in env_content:
                # Replace existing key
                lines = env_content.split('\n')
                new_lines = []
                for line in lines:
                    if line.startswith('GOOGLE_API_KEY='):
                        new_lines.append(f'GOOGLE_API_KEY={api_key}')
                    else:
                        new_lines.append(line)
                env_content = '\n'.join(new_lines)
            else:
                # Add new key
                env_content += f'\nGOOGLE_API_KEY={api_key}\n'

            # Ghi vào file
            env_file.write_text(env_content)

            QMessageBox.information(self, "Thành công", "Đã lưu API key!")
            logger.info("Đã lưu API key vào .env")

        except Exception as e:
            logger.error(f"Lỗi khi lưu API key: {e}")
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu API key:\n{str(e)}")

    def browse_output_folder(self):
        """Chọn thư mục lưu video"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Chọn thư mục lưu video",
            str(settings.OUTPUT_DIR)
        )

        if folder:
            self.output_path_label.setText(folder)
            logger.info(f"Đã chọn thư mục output: {folder}")

    def generate_video(self):
        """Bắt đầu tạo video"""
        if not self.api_client:
            QMessageBox.warning(
                self,
                "Cảnh báo",
                "Vui lòng cấu hình API key trước!"
            )
            self.tabs.setCurrentIndex(1)  # Chuyển sang tab settings
            return

        prompt = self.prompt_input.toPlainText().strip()

        if not prompt:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập mô tả video!")
            return

        # Chuẩn bị parameters
        params = {
            'prompt': prompt,
            'model': self.model_combo.currentText(),
            'duration': self.duration_spin.value(),
            'resolution': self.resolution_combo.currentText(),
            'aspect_ratio': self.aspect_ratio_combo.currentText()
        }

        # Disable controls
        self.generate_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Log
        self.output_text.append(f"\n{'='*50}")
        self.output_text.append(f"Đang tạo video...")
        self.output_text.append(f"Model: {params['model']}")
        self.output_text.append(f"Prompt: {params['prompt']}")
        self.output_text.append(f"{'='*50}\n")

        # Tạo thread để generate video
        self.generation_thread = VideoGenerationThread(self.api_client, params)
        self.generation_thread.generation_started.connect(self.on_generation_started)
        self.generation_thread.generation_completed.connect(self.on_generation_completed)
        self.generation_thread.generation_error.connect(self.on_generation_error)
        self.generation_thread.finished.connect(self.on_generation_finished)
        self.generation_thread.start()

    def on_generation_started(self):
        """Callback khi bắt đầu generate"""
        self.statusBar().showMessage("Đang tạo video...")
        self.progress_bar.setValue(10)

    def on_generation_completed(self, result: dict):
        """Callback khi generate hoàn tất"""
        self.progress_bar.setValue(100)

        if result['status'] == 'success':
            self.output_text.append(f"✅ Tạo video thành công!")
            self.output_text.append(f"Đường dẫn: {result['video_path']}")
            QMessageBox.information(
                self,
                "Thành công",
                f"Video đã được tạo!\n\nĐường dẫn: {result['video_path']}"
            )
        else:
            self.output_text.append(f"ℹ️ {result['message']}")
            QMessageBox.information(self, "Thông báo", result['message'])

    def on_generation_error(self, error: str):
        """Callback khi có lỗi"""
        self.output_text.append(f"❌ Lỗi: {error}")
        QMessageBox.critical(self, "Lỗi", f"Lỗi khi tạo video:\n{error}")

    def on_generation_finished(self):
        """Callback khi thread kết thúc"""
        self.generate_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Sẵn sàng")

    def cancel_generation(self):
        """Hủy quá trình tạo video"""
        # TODO: Implement cancellation logic
        if hasattr(self, 'generation_thread') and self.generation_thread.isRunning():
            self.generation_thread.terminate()
            self.output_text.append("⚠️ Đã hủy tạo video")
            self.statusBar().showMessage("Đã hủy")

    def refresh_logs(self):
        """Làm mới và hiển thị logs"""
        try:
            if settings.LOG_FILE_PATH.exists():
                with open(settings.LOG_FILE_PATH, 'r', encoding='utf-8') as f:
                    # Đọc 1000 dòng cuối
                    lines = f.readlines()
                    self.log_viewer.setText(''.join(lines[-1000:]))

                    # Scroll to bottom
                    self.log_viewer.verticalScrollBar().setValue(
                        self.log_viewer.verticalScrollBar().maximum()
                    )
        except Exception as e:
            self.log_viewer.setText(f"Lỗi khi đọc log: {e}")

    def clear_logs(self):
        """Xóa logs"""
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc muốn xóa tất cả logs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            from utils import clear_logs
            if clear_logs():
                self.log_viewer.clear()
                QMessageBox.information(self, "Thành công", "Đã xóa logs!")


def main():
    """Hàm main để khởi chạy ứng dụng"""

    # Thiết lập logging
    setup_logging()
    logger.info(f"Khởi động {settings.APP_TITLE} v{settings.APP_VERSION}")

    # Tạo ứng dụng Qt
    app = QApplication(sys.argv)

    # Cấu hình ứng dụng
    app.setApplicationName(settings.APP_TITLE)
    app.setApplicationVersion(settings.APP_VERSION)

    # Tạo và hiển thị cửa sổ chính
    window = MainWindow()
    window.show()

    logger.info("Ứng dụng đã khởi động")

    # Chạy event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
