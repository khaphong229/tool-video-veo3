"""
Main Window cho ứng dụng Veo3 Video Generator
Giao diện chính với menu bar, toolbar, tabs, sidebar, và status bar
"""

from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QMenu, QToolBar, QStatusBar,
    QDockWidget, QLabel, QPushButton, QComboBox,
    QGroupBox, QSpinBox, QListWidget, QMessageBox,
    QSplitter, QFrame
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QIcon, QFont

from config import settings
from utils import get_logger
from .styles import DARK_THEME, ICONS, get_icon_text

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """
    Cửa sổ chính của ứng dụng Veo3 Video Generator

    Signals:
        api_status_changed: Phát khi trạng thái API thay đổi
        project_changed: Phát khi project được chọn thay đổi
    """

    # Custom signals
    api_status_changed = pyqtSignal(bool, str)  # connected, message
    project_changed = pyqtSignal(int)  # project_id

    def __init__(self, parent=None):
        """Khởi tạo Main Window"""
        super().__init__(parent)

        # State variables
        self.current_project_id: Optional[int] = None
        self.api_connected: bool = False

        # Setup UI
        self.setupUi()
        self.apply_theme()

        logger.info("Main Window đã được khởi tạo")

    def setupUi(self):
        """Thiết lập giao diện người dùng"""

        # Window properties
        self.setWindowTitle(f"{settings.APP_TITLE} v{settings.APP_VERSION}")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)

        # Create components
        self.createMenuBar()
        self.createToolBar()
        self.createCentralWidget()
        self.createSidebar()
        self.createStatusBar()

        # Connect signals
        self.connect_signals()

    def apply_theme(self):
        """Áp dụng dark theme"""
        self.setStyleSheet(DARK_THEME)
        logger.info("Đã áp dụng dark theme")

    # ===== MENU BAR =====

    def createMenuBar(self):
        """Tạo menu bar"""
        menubar = self.menuBar()

        # ===== FILE MENU =====
        file_menu = menubar.addMenu(f"{get_icon_text('folder')} File")

        # New Project
        new_project_action = QAction(f"{get_icon_text('new_project')} New Project", self)
        new_project_action.setShortcut("Ctrl+N")
        new_project_action.setStatusTip("Create a new video project")
        new_project_action.triggered.connect(self.on_new_project)
        file_menu.addAction(new_project_action)

        # Open Project
        open_project_action = QAction(f"{get_icon_text('open_project')} Open Project", self)
        open_project_action.setShortcut("Ctrl+O")
        open_project_action.setStatusTip("Open an existing project")
        open_project_action.triggered.connect(self.on_open_project)
        file_menu.addAction(open_project_action)

        file_menu.addSeparator()

        # Save
        save_action = QAction(f"{get_icon_text('save')} Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Save current project")
        save_action.triggered.connect(self.on_save_project)
        file_menu.addAction(save_action)

        # Save As
        save_as_action = QAction(f"{get_icon_text('save_as')} Save As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.on_save_project_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # Export
        export_action = QAction(f"{get_icon_text('export')} Export Video", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.on_export_video)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        # Exit
        exit_action = QAction(f"{get_icon_text('close')} Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # ===== EDIT MENU =====
        edit_menu = menubar.addMenu(f"{get_icon_text('edit')} Edit")

        undo_action = QAction(f"{get_icon_text('undo')} Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)

        redo_action = QAction(f"{get_icon_text('redo')} Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        copy_action = QAction(f"{get_icon_text('copy')} Copy", self)
        copy_action.setShortcut("Ctrl+C")
        edit_menu.addAction(copy_action)

        paste_action = QAction(f"{get_icon_text('paste')} Paste", self)
        paste_action.setShortcut("Ctrl+V")
        edit_menu.addAction(paste_action)

        # ===== VIEW MENU =====
        view_menu = menubar.addMenu(f"{get_icon_text('search')} View")

        # Toggle Sidebar
        toggle_sidebar_action = QAction("Toggle Sidebar", self)
        toggle_sidebar_action.setShortcut("Ctrl+B")
        toggle_sidebar_action.setCheckable(True)
        toggle_sidebar_action.setChecked(True)
        toggle_sidebar_action.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(toggle_sidebar_action)

        view_menu.addSeparator()

        # Zoom
        zoom_in_action = QAction(f"{get_icon_text('zoom_in')} Zoom In", self)
        zoom_in_action.setShortcut("Ctrl++")
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction(f"{get_icon_text('zoom_out')} Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        view_menu.addAction(zoom_out_action)

        # ===== HELP MENU =====
        help_menu = menubar.addMenu(f"{get_icon_text('help')} Help")

        documentation_action = QAction(f"{get_icon_text('file')} Documentation", self)
        documentation_action.setShortcut("F1")
        documentation_action.triggered.connect(self.on_show_documentation)
        help_menu.addAction(documentation_action)

        help_menu.addSeparator()

        about_action = QAction(f"{get_icon_text('about')} About", self)
        about_action.triggered.connect(self.on_show_about)
        help_menu.addAction(about_action)

        logger.debug("Menu bar đã được tạo")

    # ===== TOOLBAR =====

    def createToolBar(self):
        """Tạo toolbar với quick actions"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # New Project
        new_project_btn = QAction(f"{get_icon_text('new_project')} New", self)
        new_project_btn.setStatusTip("Create new project")
        new_project_btn.triggered.connect(self.on_new_project)
        toolbar.addAction(new_project_btn)

        # Open Project
        open_project_btn = QAction(f"{get_icon_text('open_project')} Open", self)
        open_project_btn.triggered.connect(self.on_open_project)
        toolbar.addAction(open_project_btn)

        # Save
        save_btn = QAction(f"{get_icon_text('save')} Save", self)
        save_btn.triggered.connect(self.on_save_project)
        toolbar.addAction(save_btn)

        toolbar.addSeparator()

        # Settings
        settings_btn = QAction(f"{get_icon_text('settings')} Settings", self)
        settings_btn.setStatusTip("Open settings")
        settings_btn.triggered.connect(self.on_open_settings)
        toolbar.addAction(settings_btn)

        # Refresh
        refresh_btn = QAction(f"{get_icon_text('refresh')} Refresh", self)
        refresh_btn.setStatusTip("Refresh data")
        refresh_btn.triggered.connect(self.on_refresh)
        toolbar.addAction(refresh_btn)

        toolbar.addSeparator()

        # API Status indicator (will be updated dynamically)
        self.api_status_action = QAction(f"{get_icon_text('api')} API: Disconnected", self)
        self.api_status_action.setEnabled(False)
        toolbar.addAction(self.api_status_action)

        logger.debug("Toolbar đã được tạo")

    # ===== CENTRAL WIDGET & TABS =====

    def createCentralWidget(self):
        """Tạo central widget với tab widget"""

        # Main container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setDocumentMode(True)
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # Create tabs
        self.setupTabs()

        layout.addWidget(self.tabs)

        logger.debug("Central widget đã được tạo")

    def setupTabs(self):
        """Thiết lập các tabs"""

        # Tab 1: Text to Video
        self.text_to_video_tab = self.create_text_to_video_tab()
        self.tabs.addTab(self.text_to_video_tab, f"{get_icon_text('video')} Text to Video")

        # Tab 2: Image to Video
        self.image_to_video_tab = self.create_image_to_video_tab()
        self.tabs.addTab(self.image_to_video_tab, f"{get_icon_text('image')} Image to Video")

        # Tab 3: Scene Manager
        self.scene_manager_tab = self.create_scene_manager_tab()
        self.tabs.addTab(self.scene_manager_tab, f"{get_icon_text('edit')} Scene Manager")

        # Tab 4: History & Library
        self.history_tab = self.create_history_tab()
        self.tabs.addTab(self.history_tab, f"{get_icon_text('database')} History & Library")

        logger.debug("Tabs đã được thiết lập")

    def create_text_to_video_tab(self) -> QWidget:
        """Tạo tab Text to Video"""
        from .tabs import TextToVideoTab

        tab = TextToVideoTab()

        # Connect signals
        tab.generate_requested.connect(self.on_generate_video_requested)
        tab.add_to_queue_requested.connect(self.on_add_to_queue_requested)
        tab.template_saved.connect(self.on_template_saved)

        return tab

    def create_image_to_video_tab(self) -> QWidget:
        """Tạo tab Image to Video"""
        from .tabs import ImageToVideoTab

        tab = ImageToVideoTab()

        # Connect signals
        tab.generate_requested.connect(self.on_image_to_video_requested)
        tab.add_to_queue_requested.connect(self.on_add_to_queue_requested)

        return tab

    def create_scene_manager_tab(self) -> QWidget:
        """Tạo tab Scene Manager"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        label = QLabel("Scene Manager Tab")
        label.setObjectName("titleLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Manage multi-scene video projects")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)
        layout.addWidget(subtitle)
        layout.addStretch()

        return tab

    def create_history_tab(self) -> QWidget:
        """Tạo tab History & Library"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        label = QLabel("History & Library Tab")
        label.setObjectName("titleLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Browse your video generation history and saved templates")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)
        layout.addWidget(subtitle)
        layout.addStretch()

        return tab

    # ===== SIDEBAR (DOCK WIDGET) =====

    def createSidebar(self):
        """Tạo sidebar với settings panel"""

        # Create dock widget
        self.sidebar_dock = QDockWidget("Settings Panel", self)
        self.sidebar_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea
        )

        # Sidebar content
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)

        # ===== MODEL SELECTION =====
        model_group = QGroupBox(f"{get_icon_text('api')} Model Selection")
        model_layout = QVBoxLayout(model_group)

        model_label = QLabel("Select Veo Model:")
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "Veo 2.0",
            "Veo 3.0",
            "Veo 3.1",
            "Veo 3.1-Fast"
        ])
        self.model_combo.setCurrentIndex(2)  # Default: Veo 3.1

        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)

        sidebar_layout.addWidget(model_group)

        # ===== VIDEO SETTINGS =====
        settings_group = QGroupBox(f"{get_icon_text('settings')} Video Settings")
        settings_layout = QVBoxLayout(settings_group)

        # Aspect Ratio
        aspect_label = QLabel("Aspect Ratio:")
        self.aspect_ratio_combo = QComboBox()
        self.aspect_ratio_combo.addItems(list(settings.ASPECT_RATIOS.keys()))
        self.aspect_ratio_combo.setCurrentText(settings.DEFAULT_ASPECT_RATIO)

        settings_layout.addWidget(aspect_label)
        settings_layout.addWidget(self.aspect_ratio_combo)

        # Resolution
        resolution_label = QLabel("Resolution:")
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(list(settings.RESOLUTIONS.keys()))
        self.resolution_combo.setCurrentText(settings.DEFAULT_RESOLUTION)

        settings_layout.addWidget(resolution_label)
        settings_layout.addWidget(self.resolution_combo)

        # Duration
        duration_label = QLabel("Duration (seconds):")
        self.duration_spin = QSpinBox()
        self.duration_spin.setMinimum(settings.VIDEO_DURATION_RANGE['min'])
        self.duration_spin.setMaximum(settings.VIDEO_DURATION_RANGE['max'])
        self.duration_spin.setValue(settings.VIDEO_DURATION_RANGE['default'])
        self.duration_spin.setSuffix(" sec")

        settings_layout.addWidget(duration_label)
        settings_layout.addWidget(self.duration_spin)

        # FPS
        fps_label = QLabel("Frame Rate (FPS):")
        self.fps_combo = QComboBox()
        self.fps_combo.addItems([str(fps) for fps in settings.FPS_OPTIONS])
        self.fps_combo.setCurrentText(str(settings.DEFAULT_FPS))

        settings_layout.addWidget(fps_label)
        settings_layout.addWidget(self.fps_combo)

        sidebar_layout.addWidget(settings_group)

        # ===== REFERENCE IMAGES =====
        reference_group = QGroupBox(f"{get_icon_text('image')} Reference Images")
        reference_layout = QVBoxLayout(reference_group)

        self.reference_list = QListWidget()
        self.reference_list.setMaximumHeight(200)

        add_reference_btn = QPushButton(f"{get_icon_text('add')} Add Image")
        add_reference_btn.setObjectName("secondaryButton")
        add_reference_btn.clicked.connect(self.on_add_reference_image)

        remove_reference_btn = QPushButton(f"{get_icon_text('remove')} Remove")
        remove_reference_btn.setObjectName("dangerButton")
        remove_reference_btn.clicked.connect(self.on_remove_reference_image)

        reference_layout.addWidget(self.reference_list)
        reference_layout.addWidget(add_reference_btn)
        reference_layout.addWidget(remove_reference_btn)

        sidebar_layout.addWidget(reference_group)

        # ===== QUICK ACTIONS =====
        actions_group = QGroupBox(f"{get_icon_text('play')} Quick Actions")
        actions_layout = QVBoxLayout(actions_group)

        generate_btn = QPushButton(f"{get_icon_text('video')} Generate Video")
        generate_btn.setObjectName("primaryButton")
        generate_btn.setMinimumHeight(40)
        generate_btn.clicked.connect(self.on_generate_video)

        reset_btn = QPushButton(f"{get_icon_text('refresh')} Reset Settings")
        reset_btn.setObjectName("secondaryButton")
        reset_btn.clicked.connect(self.on_reset_settings)

        actions_layout.addWidget(generate_btn)
        actions_layout.addWidget(reset_btn)

        sidebar_layout.addWidget(actions_group)

        # Spacer
        sidebar_layout.addStretch()

        # Set dock widget
        self.sidebar_dock.setWidget(sidebar_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.sidebar_dock)

        logger.debug("Sidebar đã được tạo")

    # ===== STATUS BAR =====

    def createStatusBar(self):
        """Tạo status bar"""

        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        # Status message
        self.status_label = QLabel("Ready")
        status_bar.addWidget(self.status_label)

        # API status
        self.api_status_label = QLabel(f"{get_icon_text('api')} API: Disconnected")
        self.api_status_label.setStyleSheet("color: #d32f2f;")
        status_bar.addPermanentWidget(self.api_status_label)

        # Progress indicator (hidden by default)
        self.status_progress_label = QLabel("")
        status_bar.addPermanentWidget(self.status_progress_label)

        logger.debug("Status bar đã được tạo")

    # ===== SIGNAL CONNECTIONS =====

    def connect_signals(self):
        """Kết nối signals và slots"""

        # API status changed
        self.api_status_changed.connect(self.update_api_status)

        # Project changed
        self.project_changed.connect(self.on_project_changed_internal)

        logger.debug("Signals đã được kết nối")

    # ===== SLOT HANDLERS =====

    def on_new_project(self):
        """Handler cho New Project action"""
        logger.info("New Project clicked")
        # TODO: Implement new project logic
        QMessageBox.information(self, "New Project", "Creating new project...")

    def on_open_project(self):
        """Handler cho Open Project action"""
        logger.info("Open Project clicked")
        # TODO: Implement open project logic
        QMessageBox.information(self, "Open Project", "Opening project...")

    def on_save_project(self):
        """Handler cho Save Project action"""
        logger.info("Save Project clicked")
        # TODO: Implement save logic
        self.status_label.setText("Project saved")

    def on_save_project_as(self):
        """Handler cho Save As action"""
        logger.info("Save As clicked")
        # TODO: Implement save as logic

    def on_export_video(self):
        """Handler cho Export Video action"""
        logger.info("Export Video clicked")
        # TODO: Implement export logic

    def on_open_settings(self):
        """Handler cho Settings action"""
        logger.info("Settings clicked")

        # Import here để tránh circular import
        from .settings_dialog import SettingsDialog

        # Tạo và hiển thị settings dialog
        dialog = SettingsDialog(self)
        dialog.settings_changed.connect(self.on_settings_changed)

        if dialog.exec():
            logger.info("Settings dialog accepted")
        else:
            logger.info("Settings dialog cancelled")

    def on_settings_changed(self):
        """Handler khi settings được thay đổi"""
        logger.info("Settings changed - reloading configuration")
        # TODO: Reload settings và update UI
        self.set_status_message("Settings updated")

    def on_refresh(self):
        """Handler cho Refresh action"""
        logger.info("Refresh clicked")
        self.status_label.setText("Refreshing...")
        # TODO: Implement refresh logic
        QTimer.singleShot(1000, lambda: self.status_label.setText("Ready"))

    def on_show_documentation(self):
        """Handler cho Documentation action"""
        logger.info("Documentation clicked")
        QMessageBox.information(
            self,
            "Documentation",
            "Documentation will be opened in your default browser.\n\n"
            "See README.md for more information."
        )

    def on_show_about(self):
        """Handler cho About action"""
        about_text = f"""
        <h2>{settings.APP_TITLE}</h2>
        <p><b>Version:</b> {settings.APP_VERSION}</p>
        <p>AI Video Generation using Google Veo API</p>
        <p><b>Features:</b></p>
        <ul>
            <li>Text to Video generation</li>
            <li>Image to Video animation</li>
            <li>Multi-scene project management</li>
            <li>Template library</li>
        </ul>
        <p>Made with ❤️ using Python and PyQt6</p>
        """
        QMessageBox.about(self, "About", about_text)

    def toggle_sidebar(self, checked: bool):
        """Toggle hiển thị sidebar"""
        self.sidebar_dock.setVisible(checked)
        logger.debug(f"Sidebar visibility: {checked}")

    def on_tab_changed(self, index: int):
        """Handler khi tab thay đổi"""
        tab_names = ["Text to Video", "Image to Video", "Scene Manager", "History & Library"]
        if 0 <= index < len(tab_names):
            logger.info(f"Switched to tab: {tab_names[index]}")
            # Check if status_label exists (it may not during initialization)
            if hasattr(self, 'status_label'):
                self.status_label.setText(f"Current tab: {tab_names[index]}")

    def on_add_reference_image(self):
        """Thêm reference image"""
        logger.info("Add reference image clicked")
        # TODO: Implement file picker
        self.reference_list.addItem("reference_image_1.jpg")

    def on_remove_reference_image(self):
        """Xóa reference image"""
        current_item = self.reference_list.currentItem()
        if current_item:
            self.reference_list.takeItem(self.reference_list.row(current_item))
            logger.info("Removed reference image")

    def on_generate_video(self):
        """Generate video với settings hiện tại"""
        logger.info("Generate video clicked")

        settings_summary = f"""
        Model: {self.model_combo.currentText()}
        Aspect Ratio: {self.aspect_ratio_combo.currentText()}
        Resolution: {self.resolution_combo.currentText()}
        Duration: {self.duration_spin.value()} seconds
        FPS: {self.fps_combo.currentText()}
        """

        QMessageBox.information(self, "Generate Video", f"Starting video generation...\n{settings_summary}")

    def on_reset_settings(self):
        """Reset settings về mặc định"""
        self.aspect_ratio_combo.setCurrentText(settings.DEFAULT_ASPECT_RATIO)
        self.resolution_combo.setCurrentText(settings.DEFAULT_RESOLUTION)
        self.duration_spin.setValue(settings.VIDEO_DURATION_RANGE['default'])
        self.fps_combo.setCurrentText(str(settings.DEFAULT_FPS))

        self.status_label.setText("Settings reset to default")
        logger.info("Settings reset to default")

    def update_api_status(self, connected: bool, message: str):
        """Cập nhật trạng thái API"""
        self.api_connected = connected

        if connected:
            status_text = f"{get_icon_text('success')} API: Connected"
            color = "#66bb6a"  # Green
        else:
            status_text = f"{get_icon_text('error')} API: {message}"
            color = "#d32f2f"  # Red

        self.api_status_label.setText(status_text)
        self.api_status_label.setStyleSheet(f"color: {color};")

        self.api_status_action.setText(status_text)

        logger.info(f"API Status updated: {status_text}")

    def on_project_changed_internal(self, project_id: int):
        """Internal handler khi project thay đổi"""
        self.current_project_id = project_id
        self.status_label.setText(f"Project ID: {project_id}")
        logger.info(f"Current project changed to: {project_id}")

    # ===== PUBLIC METHODS =====

    def set_api_status(self, connected: bool, message: str = ""):
        """
        Set trạng thái kết nối API

        Args:
            connected: True nếu connected
            message: Message mô tả
        """
        self.api_status_changed.emit(connected, message)

    def set_status_message(self, message: str):
        """
        Set message trong status bar

        Args:
            message: Status message
        """
        self.status_label.setText(message)

    def get_current_settings(self) -> dict:
        """
        Lấy settings hiện tại từ sidebar

        Returns:
            dict: Dictionary chứa settings
        """
        return {
            'model': self.model_combo.currentText(),
            'aspect_ratio': self.aspect_ratio_combo.currentText(),
            'resolution': self.resolution_combo.currentText(),
            'duration': self.duration_spin.value(),
            'fps': int(self.fps_combo.currentText())
        }

    # ===== TEXT TO VIDEO TAB SIGNAL HANDLERS =====

    def on_generate_video_requested(self, params: dict):
        """
        Handler khi user request generate video

        Args:
            params: Generation parameters
        """
        logger.info(f"Video generation requested: {params}")
        self.set_status_message(f"Generating video: {params['prompt'][:50]}...")

        # TODO: Implement actual video generation
        # For now, just log the params
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Generation Started",
            f"Video generation started!\n\nPrompt: {params['prompt'][:100]}..."
        )

    def on_add_to_queue_requested(self, params: dict):
        """Handler khi user add to queue"""
        logger.info(f"Added to queue: {params}")
        self.set_status_message("Added to generation queue")

    def on_template_saved(self, template: dict):
        """Handler khi template được save"""
        logger.info(f"Template saved: {template['name']}")
        self.set_status_message(f"Template '{template['name']}' saved")

    # ===== IMAGE TO VIDEO TAB SIGNAL HANDLERS =====

    def on_image_to_video_requested(self, params: dict):
        """
        Handler khi user request image to video generation

        Args:
            params: Generation parameters
        """
        logger.info(f"Image to video generation requested: {params}")
        self.set_status_message(f"Animating image: {Path(params['source_image']).name}")

        # TODO: Implement actual generation
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Generation Started",
            f"Image to video generation started!\n\n"
            f"Source: {Path(params['source_image']).name}\n"
            f"Animation: {params['animation_prompt'][:50]}..."
        )


# ===== EXPORT =====
__all__ = ['MainWindow']
