"""
Scene Manager Tab
Allows creating multiple scenes and chaining them together into complete videos
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QListWidget, QListWidgetItem, QTextEdit,
    QCheckBox, QSpinBox, QSplitter, QTabWidget, QLineEdit,
    QGroupBox, QProgressBar, QMessageBox, QInputDialog,
    QFileDialog, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap

from utils import get_logger
from ui.styles import get_icon_text
from ui.widgets import CollapsibleSection
from config import settings

logger = get_logger(__name__)


class SceneData:
    """Data model for a single scene"""

    def __init__(
        self,
        scene_id: int,
        prompt: str = "",
        use_previous_frame: bool = False,
        extend_from_previous: bool = False,
        reference_images: Optional[List[str]] = None,
        first_frame: Optional[str] = None,
        last_frame: Optional[str] = None,
        model: Optional[str] = None,
        duration: int = 5,
        aspect_ratio: str = "16:9",
        resolution: str = "1080p",
        status: str = "pending",
        video_path: Optional[str] = None,
        thumbnail_path: Optional[str] = None
    ):
        self.scene_id = scene_id
        self.prompt = prompt
        self.use_previous_frame = use_previous_frame
        self.extend_from_previous = extend_from_previous
        self.reference_images = reference_images or []
        self.first_frame = first_frame
        self.last_frame = last_frame
        self.model = model
        self.duration = duration
        self.aspect_ratio = aspect_ratio
        self.resolution = resolution
        self.status = status  # pending, processing, done, failed
        self.video_path = video_path
        self.thumbnail_path = thumbnail_path

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'scene_id': self.scene_id,
            'prompt': self.prompt,
            'use_previous_frame': self.use_previous_frame,
            'extend_from_previous': self.extend_from_previous,
            'reference_images': self.reference_images,
            'first_frame': self.first_frame,
            'last_frame': self.last_frame,
            'model': self.model,
            'duration': self.duration,
            'aspect_ratio': self.aspect_ratio,
            'resolution': self.resolution,
            'status': self.status,
            'video_path': self.video_path,
            'thumbnail_path': self.thumbnail_path
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SceneData':
        """Create from dictionary"""
        return SceneData(**data)

    def get_display_text(self) -> str:
        """Get display text for list widget"""
        prompt_preview = self.prompt[:50] + "..." if len(self.prompt) > 50 else self.prompt
        status_icon = {
            'pending': '⏸',
            'processing': '⏳',
            'done': '✓',
            'failed': '✗'
        }.get(self.status, '?')

        return f"{status_icon} Scene {self.scene_id} | {self.duration}s | {prompt_preview}"


class ProjectData:
    """Data model for a project (collection of scenes)"""

    def __init__(
        self,
        name: str,
        created_at: Optional[str] = None,
        global_style: str = "",
        global_model: str = "veo-2.0",
        auto_merge: bool = True,
        output_format: str = "mp4",
        scenes: Optional[List[SceneData]] = None
    ):
        self.name = name
        self.created_at = created_at or datetime.now().isoformat()
        self.global_style = global_style
        self.global_model = global_model
        self.auto_merge = auto_merge
        self.output_format = output_format
        self.scenes = scenes or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'created_at': self.created_at,
            'global_style': self.global_style,
            'global_model': self.global_model,
            'auto_merge': self.auto_merge,
            'output_format': self.output_format,
            'scenes': [scene.to_dict() for scene in self.scenes]
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ProjectData':
        """Create from dictionary"""
        scenes = [SceneData.from_dict(s) for s in data.get('scenes', [])]
        return ProjectData(
            name=data['name'],
            created_at=data.get('created_at'),
            global_style=data.get('global_style', ''),
            global_model=data.get('global_model', 'veo-2.0'),
            auto_merge=data.get('auto_merge', True),
            output_format=data.get('output_format', 'mp4'),
            scenes=scenes
        )

    def add_scene(self, scene: SceneData):
        """Add a scene to the project"""
        self.scenes.append(scene)

    def remove_scene(self, index: int):
        """Remove scene at index"""
        if 0 <= index < len(self.scenes):
            self.scenes.pop(index)

    def reorder_scene(self, from_index: int, to_index: int):
        """Reorder scenes"""
        if 0 <= from_index < len(self.scenes) and 0 <= to_index < len(self.scenes):
            scene = self.scenes.pop(from_index)
            self.scenes.insert(to_index, scene)
            # Update scene IDs
            for i, s in enumerate(self.scenes):
                s.scene_id = i + 1

    def get_completed_count(self) -> int:
        """Get number of completed scenes"""
        return sum(1 for scene in self.scenes if scene.status == 'done')

    def is_all_completed(self) -> bool:
        """Check if all scenes are completed"""
        return len(self.scenes) > 0 and all(s.status == 'done' for s in self.scenes)


class SceneManagerTab(QWidget):
    """
    Scene Manager Tab - Create and manage multiple scenes

    Features:
    - Project management
    - Scene list with status
    - Scene editor (prompt, references, settings)
    - Global settings
    - Scene chaining (use previous frame, extend)
    - Batch generation
    - Video merging
    """

    # Signals
    generate_scene_requested = pyqtSignal(dict)  # scene_data
    generate_all_requested = pyqtSignal(list)  # list of scene_data
    merge_videos_requested = pyqtSignal(list)  # list of video paths

    def __init__(self):
        super().__init__()

        # Data
        self.projects: Dict[str, ProjectData] = {}
        self.current_project: Optional[ProjectData] = None
        self.current_scene_index: int = -1
        self.projects_dir = Path("projects")
        self.projects_dir.mkdir(exist_ok=True)

        # UI
        self.setup_ui()
        self.load_projects()

        logger.info("SceneManagerTab initialized")

    def setup_ui(self):
        """Setup the user interface"""

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create main splitter (horizontal)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions (30% - 70%)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 7)

        main_layout.addWidget(splitter, stretch=8)

        # Bottom panel (global settings)
        bottom_panel = self.create_bottom_panel()
        main_layout.addWidget(bottom_panel, stretch=2)

        # Action bar
        action_bar = self.create_action_bar()
        main_layout.addWidget(action_bar)

    def create_left_panel(self) -> QWidget:
        """Create left panel with project selector and scene list"""

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)

        # === Project Selector ===
        project_group = QGroupBox("Project")
        project_layout = QVBoxLayout(project_group)

        # Project combo + New button
        project_row = QHBoxLayout()

        self.project_combo = QComboBox()
        self.project_combo.setPlaceholderText("Select or create project...")
        self.project_combo.currentIndexChanged.connect(self.on_project_changed)
        project_row.addWidget(self.project_combo, stretch=7)

        new_project_btn = QPushButton(f"{get_icon_text('add')} New")
        new_project_btn.clicked.connect(self.on_new_project)
        new_project_btn.setObjectName("secondaryButton")
        project_row.addWidget(new_project_btn, stretch=3)

        project_layout.addLayout(project_row)

        # Project info
        self.project_info_label = QLabel("No project selected")
        self.project_info_label.setWordWrap(True)
        self.project_info_label.setStyleSheet("color: #888; font-size: 11px; padding: 5px;")
        project_layout.addWidget(self.project_info_label)

        layout.addWidget(project_group)

        # === Scene List ===
        scene_group = QGroupBox("Scenes")
        scene_layout = QVBoxLayout(scene_group)

        self.scene_list = QListWidget()
        self.scene_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.scene_list.currentRowChanged.connect(self.on_scene_selected)
        scene_layout.addWidget(self.scene_list)

        # Scene control buttons
        scene_btn_row = QHBoxLayout()

        self.add_scene_btn = QPushButton(f"{get_icon_text('add')} Add Scene")
        self.add_scene_btn.clicked.connect(self.add_scene)
        self.add_scene_btn.setObjectName("primaryButton")
        self.add_scene_btn.setEnabled(False)
        scene_btn_row.addWidget(self.add_scene_btn)

        scene_layout.addLayout(scene_btn_row)

        # Reorder buttons
        reorder_row = QHBoxLayout()

        self.move_up_btn = QPushButton(f"{get_icon_text('arrow_up')} Up")
        self.move_up_btn.clicked.connect(self.move_scene_up)
        self.move_up_btn.setEnabled(False)
        reorder_row.addWidget(self.move_up_btn)

        self.move_down_btn = QPushButton(f"{get_icon_text('arrow_down')} Down")
        self.move_down_btn.clicked.connect(self.move_scene_down)
        self.move_down_btn.setEnabled(False)
        reorder_row.addWidget(self.move_down_btn)

        self.delete_scene_btn = QPushButton(f"{get_icon_text('delete')} Delete")
        self.delete_scene_btn.clicked.connect(self.delete_scene)
        self.delete_scene_btn.setEnabled(False)
        self.delete_scene_btn.setObjectName("dangerButton")
        reorder_row.addWidget(self.delete_scene_btn)

        scene_layout.addLayout(reorder_row)

        layout.addWidget(scene_group)

        return panel

    def create_right_panel(self) -> QWidget:
        """Create right panel with scene editor"""

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)

        # Scene header
        header = QHBoxLayout()

        self.scene_number_label = QLabel("No scene selected")
        self.scene_number_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header.addWidget(self.scene_number_label)

        header.addStretch()

        self.scene_status_label = QLabel("")
        header.addWidget(self.scene_status_label)

        layout.addLayout(header)

        # Tab widget for scene editor
        self.scene_tabs = QTabWidget()

        # Tab 1: Prompt
        prompt_tab = self.create_prompt_tab()
        self.scene_tabs.addTab(prompt_tab, f"{get_icon_text('edit')} Prompt")

        # Tab 2: References
        references_tab = self.create_references_tab()
        self.scene_tabs.addTab(references_tab, f"{get_icon_text('image')} References")

        # Tab 3: Settings
        settings_tab = self.create_settings_tab()
        self.scene_tabs.addTab(settings_tab, f"{get_icon_text('settings')} Settings")

        self.scene_tabs.setEnabled(False)

        layout.addWidget(self.scene_tabs)

        return panel

    def create_prompt_tab(self) -> QWidget:
        """Create prompt tab"""

        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Prompt input
        prompt_label = QLabel("Scene Prompt:")
        layout.addWidget(prompt_label)

        self.scene_prompt_input = QTextEdit()
        self.scene_prompt_input.setPlaceholderText("Describe what happens in this scene...")
        self.scene_prompt_input.setMaximumHeight(150)
        self.scene_prompt_input.textChanged.connect(self.on_scene_data_changed)
        layout.addWidget(self.scene_prompt_input)

        # Character counter
        self.scene_prompt_counter = QLabel("0 / 2000 characters")
        self.scene_prompt_counter.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(self.scene_prompt_counter)

        # Chaining options
        chain_group = QGroupBox("Scene Chaining")
        chain_layout = QVBoxLayout(chain_group)

        self.use_previous_frame_check = QCheckBox("Use previous scene's last frame as first frame")
        self.use_previous_frame_check.setToolTip(
            "Use the last frame of the previous scene as the starting point for this scene"
        )
        self.use_previous_frame_check.stateChanged.connect(self.on_scene_data_changed)
        chain_layout.addWidget(self.use_previous_frame_check)

        self.extend_from_previous_check = QCheckBox("Extend from previous video (seamless continuation)")
        self.extend_from_previous_check.setToolTip(
            "Create a seamless continuation from the previous scene (locks aspect ratio)"
        )
        self.extend_from_previous_check.stateChanged.connect(self.on_scene_data_changed)
        chain_layout.addWidget(self.extend_from_previous_check)

        info_label = QLabel(
            "💡 Tip: Enable chaining options to create smooth transitions between scenes"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #14ffec; font-size: 11px; padding: 5px; background: rgba(20, 255, 236, 0.1); border-radius: 3px;")
        chain_layout.addWidget(info_label)

        layout.addWidget(chain_group)

        layout.addStretch()

        return tab

    def create_references_tab(self) -> QWidget:
        """Create references tab"""

        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Reference images
        ref_group = QGroupBox("Reference Images (Max 3)")
        ref_layout = QVBoxLayout(ref_group)

        self.reference_list = QListWidget()
        self.reference_list.setMaximumHeight(100)
        ref_layout.addWidget(self.reference_list)

        ref_btn_row = QHBoxLayout()

        add_ref_btn = QPushButton(f"{get_icon_text('add')} Add Reference")
        add_ref_btn.clicked.connect(self.add_reference_image)
        ref_btn_row.addWidget(add_ref_btn)

        remove_ref_btn = QPushButton(f"{get_icon_text('delete')} Remove")
        remove_ref_btn.clicked.connect(self.remove_reference_image)
        ref_btn_row.addWidget(remove_ref_btn)

        ref_layout.addLayout(ref_btn_row)

        layout.addWidget(ref_group)

        # First / Last frame
        frames_group = QGroupBox("First / Last Frame (Transition Mode)")
        frames_layout = QVBoxLayout(frames_group)

        # First frame
        first_frame_row = QHBoxLayout()
        first_frame_row.addWidget(QLabel("First Frame:"))

        self.first_frame_path = QLineEdit()
        self.first_frame_path.setPlaceholderText("No first frame selected")
        self.first_frame_path.setReadOnly(True)
        first_frame_row.addWidget(self.first_frame_path, stretch=7)

        browse_first_btn = QPushButton("Browse...")
        browse_first_btn.clicked.connect(self.browse_first_frame)
        first_frame_row.addWidget(browse_first_btn, stretch=3)

        frames_layout.addLayout(first_frame_row)

        # Last frame
        last_frame_row = QHBoxLayout()
        last_frame_row.addWidget(QLabel("Last Frame:"))

        self.last_frame_path = QLineEdit()
        self.last_frame_path.setPlaceholderText("No last frame selected")
        self.last_frame_path.setReadOnly(True)
        last_frame_row.addWidget(self.last_frame_path, stretch=7)

        browse_last_btn = QPushButton("Browse...")
        browse_last_btn.clicked.connect(self.browse_last_frame)
        last_frame_row.addWidget(browse_last_btn, stretch=3)

        frames_layout.addLayout(last_frame_row)

        layout.addWidget(frames_group)

        layout.addStretch()

        return tab

    def create_settings_tab(self) -> QWidget:
        """Create settings tab"""

        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Model override
        model_group = QGroupBox("Model (Override)")
        model_layout = QVBoxLayout(model_group)

        model_row = QHBoxLayout()

        self.override_model_check = QCheckBox("Override global model for this scene")
        self.override_model_check.stateChanged.connect(self.on_model_override_changed)
        model_row.addWidget(self.override_model_check)

        model_layout.addLayout(model_row)

        self.scene_model_combo = QComboBox()
        self.scene_model_combo.addItems(settings.AVAILABLE_MODELS)
        self.scene_model_combo.setEnabled(False)
        self.scene_model_combo.currentTextChanged.connect(self.on_scene_data_changed)
        model_layout.addWidget(self.scene_model_combo)

        layout.addWidget(model_group)

        # Duration
        duration_group = QGroupBox("Duration")
        duration_layout = QHBoxLayout(duration_group)

        duration_layout.addWidget(QLabel("Duration:"))

        self.scene_duration_spin = QSpinBox()
        self.scene_duration_spin.setRange(2, 60)
        self.scene_duration_spin.setValue(5)
        self.scene_duration_spin.setSuffix(" seconds")
        self.scene_duration_spin.valueChanged.connect(self.on_scene_data_changed)
        duration_layout.addWidget(self.scene_duration_spin)

        duration_layout.addStretch()

        layout.addWidget(duration_group)

        # Aspect ratio
        aspect_group = QGroupBox("Aspect Ratio")
        aspect_layout = QHBoxLayout(aspect_group)

        aspect_layout.addWidget(QLabel("Aspect Ratio:"))

        self.scene_aspect_combo = QComboBox()
        self.scene_aspect_combo.addItems(["16:9", "9:16", "1:1", "4:3"])
        self.scene_aspect_combo.currentTextChanged.connect(self.on_scene_data_changed)
        aspect_layout.addWidget(self.scene_aspect_combo)

        self.aspect_locked_label = QLabel("")
        aspect_layout.addWidget(self.aspect_locked_label)

        aspect_layout.addStretch()

        layout.addWidget(aspect_group)

        # Resolution
        resolution_group = QGroupBox("Resolution")
        resolution_layout = QHBoxLayout(resolution_group)

        resolution_layout.addWidget(QLabel("Resolution:"))

        self.scene_resolution_combo = QComboBox()
        self.scene_resolution_combo.addItems(["480p", "720p", "1080p", "4K"])
        self.scene_resolution_combo.setCurrentText("1080p")
        self.scene_resolution_combo.currentTextChanged.connect(self.on_scene_data_changed)
        resolution_layout.addWidget(self.scene_resolution_combo)

        resolution_layout.addStretch()

        layout.addWidget(resolution_group)

        layout.addStretch()

        return tab

    def create_bottom_panel(self) -> QWidget:
        """Create bottom panel with global settings"""

        panel = QGroupBox("Global Settings (Apply to All Scenes)")
        layout = QVBoxLayout(panel)

        # Global style template
        style_row = QHBoxLayout()
        style_row.addWidget(QLabel("Global Style Template:"))

        self.global_style_input = QLineEdit()
        self.global_style_input.setPlaceholderText("e.g., cinematic, dramatic lighting, film grain (appended to all prompts)")
        self.global_style_input.textChanged.connect(self.on_global_settings_changed)
        style_row.addWidget(self.global_style_input, stretch=8)

        layout.addLayout(style_row)

        # Settings row
        settings_row = QHBoxLayout()

        # Global model
        settings_row.addWidget(QLabel("Model:"))
        self.global_model_combo = QComboBox()
        self.global_model_combo.addItems(settings.AVAILABLE_MODELS)
        self.global_model_combo.currentTextChanged.connect(self.on_global_settings_changed)
        settings_row.addWidget(self.global_model_combo, stretch=2)

        settings_row.addSpacing(20)

        # Auto-merge
        self.auto_merge_check = QCheckBox("Auto-merge scenes when all completed")
        self.auto_merge_check.setChecked(True)
        self.auto_merge_check.stateChanged.connect(self.on_global_settings_changed)
        settings_row.addWidget(self.auto_merge_check, stretch=3)

        settings_row.addSpacing(20)

        # Output format
        settings_row.addWidget(QLabel("Output Format:"))
        self.output_format_combo = QComboBox()
        self.output_format_combo.addItems(["mp4", "mov", "avi", "webm"])
        self.output_format_combo.currentTextChanged.connect(self.on_global_settings_changed)
        settings_row.addWidget(self.output_format_combo, stretch=1)

        settings_row.addStretch()

        layout.addLayout(settings_row)

        return panel

    def create_action_bar(self) -> QWidget:
        """Create action bar with generation controls"""

        bar = QWidget()
        bar.setObjectName("actionBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(10, 10, 10, 10)

        # Progress info
        self.progress_label = QLabel("No scenes")
        self.progress_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        layout.addStretch()

        # Action buttons
        self.generate_selected_btn = QPushButton(f"{get_icon_text('play')} Generate Selected")
        self.generate_selected_btn.clicked.connect(self.generate_selected_scene)
        self.generate_selected_btn.setEnabled(False)
        layout.addWidget(self.generate_selected_btn)

        self.generate_all_btn = QPushButton(f"{get_icon_text('play')} Generate All Scenes")
        self.generate_all_btn.clicked.connect(self.generate_all_scenes)
        self.generate_all_btn.setObjectName("primaryButton")
        self.generate_all_btn.setEnabled(False)
        layout.addWidget(self.generate_all_btn)

        self.merge_videos_btn = QPushButton(f"{get_icon_text('save')} Merge Videos")
        self.merge_videos_btn.clicked.connect(self.merge_all_videos)
        self.merge_videos_btn.setEnabled(False)
        layout.addWidget(self.merge_videos_btn)

        return bar

    # ===== PROJECT MANAGEMENT =====

    def load_projects(self):
        """Load all projects from disk"""
        try:
            for project_file in self.projects_dir.glob("*.json"):
                with open(project_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    project = ProjectData.from_dict(data)
                    self.projects[project.name] = project
                    self.project_combo.addItem(project.name)

            logger.info(f"Loaded {len(self.projects)} projects")

        except Exception as e:
            logger.error(f"Failed to load projects: {e}")

    def save_project(self, project: ProjectData):
        """Save project to disk"""
        try:
            project_file = self.projects_dir / f"{project.name}.json"
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project.to_dict(), f, indent=2)

            logger.info(f"Project saved: {project.name}")

        except Exception as e:
            logger.error(f"Failed to save project: {e}")
            QMessageBox.warning(self, "Save Error", f"Failed to save project: {e}")

    def on_new_project(self):
        """Create a new project"""
        name, ok = QInputDialog.getText(
            self,
            "New Project",
            "Project name:",
            QLineEdit.EchoMode.Normal,
            f"Project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        if ok and name:
            if name in self.projects:
                QMessageBox.warning(self, "Project Exists", f"Project '{name}' already exists")
                return

            # Create new project
            project = ProjectData(name=name)
            self.projects[name] = project

            # Add to combo
            self.project_combo.addItem(name)
            self.project_combo.setCurrentText(name)

            # Save
            self.save_project(project)

            logger.info(f"Created new project: {name}")

    def on_project_changed(self, index: int):
        """Handle project selection change"""
        if index < 0:
            self.current_project = None
            self.add_scene_btn.setEnabled(False)
            self.update_project_info()
            return

        project_name = self.project_combo.currentText()
        self.current_project = self.projects.get(project_name)

        if self.current_project:
            self.add_scene_btn.setEnabled(True)
            self.load_project_data()
            logger.info(f"Switched to project: {project_name}")

    def update_project_info(self):
        """Update project info label"""
        if not self.current_project:
            self.project_info_label.setText("No project selected")
            return

        info = (
            f"Scenes: {len(self.current_project.scenes)} | "
            f"Completed: {self.current_project.get_completed_count()} | "
            f"Created: {self.current_project.created_at[:10]}"
        )
        self.project_info_label.setText(info)

    def load_project_data(self):
        """Load project data into UI"""
        if not self.current_project:
            return

        # Load scenes into list
        self.scene_list.clear()
        for scene in self.current_project.scenes:
            item = QListWidgetItem(scene.get_display_text())
            item.setData(Qt.ItemDataRole.UserRole, scene.scene_id)
            self.scene_list.addItem(item)

        # Load global settings
        self.global_style_input.setText(self.current_project.global_style)
        self.global_model_combo.setCurrentText(self.current_project.global_model)
        self.auto_merge_check.setChecked(self.current_project.auto_merge)
        self.output_format_combo.setCurrentText(self.current_project.output_format)

        # Update UI state
        self.update_project_info()
        self.update_progress()
        self.update_action_buttons()

        # Select first scene if available
        if len(self.current_project.scenes) > 0:
            self.scene_list.setCurrentRow(0)

    # ===== SCENE MANAGEMENT =====

    def add_scene(self):
        """Add a new scene to current project"""
        if not self.current_project:
            return

        # Create new scene
        scene_id = len(self.current_project.scenes) + 1
        scene = SceneData(
            scene_id=scene_id,
            model=self.current_project.global_model,
            aspect_ratio="16:9",
            duration=5
        )

        # Add to project
        self.current_project.add_scene(scene)

        # Add to list
        item = QListWidgetItem(scene.get_display_text())
        item.setData(Qt.ItemDataRole.UserRole, scene.scene_id)
        self.scene_list.addItem(item)

        # Select new scene
        self.scene_list.setCurrentRow(len(self.current_project.scenes) - 1)

        # Save
        self.save_project(self.current_project)

        # Update UI
        self.update_project_info()
        self.update_progress()
        self.update_action_buttons()

        logger.info(f"Added scene {scene_id} to project {self.current_project.name}")

    def delete_scene(self):
        """Delete selected scene"""
        if not self.current_project or self.current_scene_index < 0:
            return

        # Confirm
        reply = QMessageBox.question(
            self,
            "Delete Scene",
            f"Delete Scene {self.current_scene_index + 1}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Remove from project
        self.current_project.remove_scene(self.current_scene_index)

        # Remove from list
        self.scene_list.takeItem(self.current_scene_index)

        # Update scene numbers in list
        for i in range(self.scene_list.count()):
            item = self.scene_list.item(i)
            scene = self.current_project.scenes[i]
            item.setText(scene.get_display_text())
            item.setData(Qt.ItemDataRole.UserRole, scene.scene_id)

        # Save
        self.save_project(self.current_project)

        # Update UI
        self.update_project_info()
        self.update_progress()
        self.update_action_buttons()

        logger.info(f"Deleted scene from project {self.current_project.name}")

    def move_scene_up(self):
        """Move selected scene up"""
        if not self.current_project or self.current_scene_index <= 0:
            return

        # Reorder in project
        self.current_project.reorder_scene(self.current_scene_index, self.current_scene_index - 1)

        # Reload list
        current_id = self.current_project.scenes[self.current_scene_index - 1].scene_id
        self.load_project_data()

        # Restore selection
        for i in range(self.scene_list.count()):
            if self.scene_list.item(i).data(Qt.ItemDataRole.UserRole) == current_id:
                self.scene_list.setCurrentRow(i)
                break

        # Save
        self.save_project(self.current_project)

        logger.info(f"Moved scene up in project {self.current_project.name}")

    def move_scene_down(self):
        """Move selected scene down"""
        if not self.current_project or self.current_scene_index < 0:
            return

        if self.current_scene_index >= len(self.current_project.scenes) - 1:
            return

        # Reorder in project
        self.current_project.reorder_scene(self.current_scene_index, self.current_scene_index + 1)

        # Reload list
        current_id = self.current_project.scenes[self.current_scene_index + 1].scene_id
        self.load_project_data()

        # Restore selection
        for i in range(self.scene_list.count()):
            if self.scene_list.item(i).data(Qt.ItemDataRole.UserRole) == current_id:
                self.scene_list.setCurrentRow(i)
                break

        # Save
        self.save_project(self.current_project)

        logger.info(f"Moved scene down in project {self.current_project.name}")

    def on_scene_selected(self, index: int):
        """Handle scene selection"""
        self.current_scene_index = index

        if index < 0 or not self.current_project:
            self.scene_tabs.setEnabled(False)
            self.scene_number_label.setText("No scene selected")
            self.delete_scene_btn.setEnabled(False)
            self.move_up_btn.setEnabled(False)
            self.move_down_btn.setEnabled(False)
            self.generate_selected_btn.setEnabled(False)
            return

        # Enable scene editor
        self.scene_tabs.setEnabled(True)
        self.delete_scene_btn.setEnabled(True)
        self.generate_selected_btn.setEnabled(True)

        # Update move buttons
        self.move_up_btn.setEnabled(index > 0)
        self.move_down_btn.setEnabled(index < len(self.current_project.scenes) - 1)

        # Load scene data
        self.load_scene_data(index)

        logger.debug(f"Selected scene {index + 1}")

    def load_scene_data(self, index: int):
        """Load scene data into editor"""
        if not self.current_project or index < 0 or index >= len(self.current_project.scenes):
            return

        scene = self.current_project.scenes[index]

        # Update header
        self.scene_number_label.setText(f"Scene {scene.scene_id}")

        status_text = {
            'pending': '⏸ Pending',
            'processing': '⏳ Processing',
            'done': '✓ Completed',
            'failed': '✗ Failed'
        }.get(scene.status, '?')
        self.scene_status_label.setText(status_text)

        # Load prompt tab
        self.scene_prompt_input.blockSignals(True)
        self.scene_prompt_input.setPlainText(scene.prompt)
        self.scene_prompt_input.blockSignals(False)
        self.update_prompt_counter()

        self.use_previous_frame_check.blockSignals(True)
        self.use_previous_frame_check.setChecked(scene.use_previous_frame)
        self.use_previous_frame_check.blockSignals(False)

        self.extend_from_previous_check.blockSignals(True)
        self.extend_from_previous_check.setChecked(scene.extend_from_previous)
        self.extend_from_previous_check.blockSignals(False)

        # Disable chaining for first scene
        is_first_scene = index == 0
        self.use_previous_frame_check.setEnabled(not is_first_scene)
        self.extend_from_previous_check.setEnabled(not is_first_scene)

        # Load references tab
        self.reference_list.clear()
        for ref in scene.reference_images:
            self.reference_list.addItem(Path(ref).name)

        self.first_frame_path.setText(scene.first_frame or "")
        self.last_frame_path.setText(scene.last_frame or "")

        # Load settings tab
        has_model_override = scene.model is not None
        self.override_model_check.blockSignals(True)
        self.override_model_check.setChecked(has_model_override)
        self.override_model_check.blockSignals(False)

        self.scene_model_combo.setEnabled(has_model_override)
        if has_model_override:
            self.scene_model_combo.setCurrentText(scene.model)

        self.scene_duration_spin.blockSignals(True)
        self.scene_duration_spin.setValue(scene.duration)
        self.scene_duration_spin.blockSignals(False)

        self.scene_aspect_combo.blockSignals(True)
        self.scene_aspect_combo.setCurrentText(scene.aspect_ratio)
        self.scene_aspect_combo.blockSignals(False)

        # Lock aspect ratio if extending
        if scene.extend_from_previous and index > 0:
            prev_scene = self.current_project.scenes[index - 1]
            self.scene_aspect_combo.setEnabled(False)
            self.aspect_locked_label.setText(f"🔒 Locked to {prev_scene.aspect_ratio}")
        else:
            self.scene_aspect_combo.setEnabled(True)
            self.aspect_locked_label.setText("")

        self.scene_resolution_combo.blockSignals(True)
        self.scene_resolution_combo.setCurrentText(scene.resolution)
        self.scene_resolution_combo.blockSignals(False)

    def update_scene(self, index: int, data: dict):
        """Update scene with new data"""
        if not self.current_project or index < 0 or index >= len(self.current_project.scenes):
            return

        scene = self.current_project.scenes[index]

        # Update scene data
        for key, value in data.items():
            if hasattr(scene, key):
                setattr(scene, key, value)

        # Update list item
        item = self.scene_list.item(index)
        if item:
            item.setText(scene.get_display_text())

        # Save
        self.save_project(self.current_project)

    def on_scene_data_changed(self):
        """Handle scene data change"""
        if self.current_scene_index < 0 or not self.current_project:
            return

        scene = self.current_project.scenes[self.current_scene_index]

        # Collect updated data
        data = {
            'prompt': self.scene_prompt_input.toPlainText(),
            'use_previous_frame': self.use_previous_frame_check.isChecked(),
            'extend_from_previous': self.extend_from_previous_check.isChecked(),
            'model': self.scene_model_combo.currentText() if self.override_model_check.isChecked() else None,
            'duration': self.scene_duration_spin.value(),
            'aspect_ratio': self.scene_aspect_combo.currentText(),
            'resolution': self.scene_resolution_combo.currentText()
        }

        # Update scene
        self.update_scene(self.current_scene_index, data)

        # Update prompt counter
        self.update_prompt_counter()

        # If extending, lock aspect ratio to previous scene
        if data['extend_from_previous'] and self.current_scene_index > 0:
            prev_scene = self.current_project.scenes[self.current_scene_index - 1]
            self.scene_aspect_combo.setEnabled(False)
            self.aspect_locked_label.setText(f"🔒 Locked to {prev_scene.aspect_ratio}")
            data['aspect_ratio'] = prev_scene.aspect_ratio
            self.scene_aspect_combo.blockSignals(True)
            self.scene_aspect_combo.setCurrentText(prev_scene.aspect_ratio)
            self.scene_aspect_combo.blockSignals(False)
        else:
            self.scene_aspect_combo.setEnabled(True)
            self.aspect_locked_label.setText("")

    def on_model_override_changed(self, state: int):
        """Handle model override checkbox"""
        enabled = state == Qt.CheckState.Checked.value
        self.scene_model_combo.setEnabled(enabled)
        self.on_scene_data_changed()

    def update_prompt_counter(self):
        """Update prompt character counter"""
        text = self.scene_prompt_input.toPlainText()
        count = len(text)
        self.scene_prompt_counter.setText(f"{count} / 2000 characters")

        if count > 2000:
            self.scene_prompt_counter.setStyleSheet("color: #d32f2f; font-size: 11px;")
        else:
            self.scene_prompt_counter.setStyleSheet("color: #888; font-size: 11px;")

    # ===== REFERENCES =====

    def add_reference_image(self):
        """Add reference image"""
        if self.current_scene_index < 0:
            return

        scene = self.current_project.scenes[self.current_scene_index]

        if len(scene.reference_images) >= 3:
            QMessageBox.warning(self, "Limit Reached", "Maximum 3 reference images allowed")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Reference Image",
            "",
            "Images (*.jpg *.jpeg *.png *.webp *.bmp)"
        )

        if file_path:
            scene.reference_images.append(file_path)
            self.reference_list.addItem(Path(file_path).name)
            self.save_project(self.current_project)

    def remove_reference_image(self):
        """Remove selected reference image"""
        if self.current_scene_index < 0:
            return

        current_item = self.reference_list.currentItem()
        if not current_item:
            return

        row = self.reference_list.row(current_item)
        scene = self.current_project.scenes[self.current_scene_index]

        scene.reference_images.pop(row)
        self.reference_list.takeItem(row)
        self.save_project(self.current_project)

    def browse_first_frame(self):
        """Browse for first frame"""
        if self.current_scene_index < 0:
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select First Frame",
            "",
            "Images (*.jpg *.jpeg *.png *.webp *.bmp)"
        )

        if file_path:
            self.first_frame_path.setText(file_path)
            self.update_scene(self.current_scene_index, {'first_frame': file_path})

    def browse_last_frame(self):
        """Browse for last frame"""
        if self.current_scene_index < 0:
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Last Frame",
            "",
            "Images (*.jpg *.jpeg *.png *.webp *.bmp)"
        )

        if file_path:
            self.last_frame_path.setText(file_path)
            self.update_scene(self.current_scene_index, {'last_frame': file_path})

    # ===== GLOBAL SETTINGS =====

    def on_global_settings_changed(self):
        """Handle global settings change"""
        if not self.current_project:
            return

        self.current_project.global_style = self.global_style_input.text()
        self.current_project.global_model = self.global_model_combo.currentText()
        self.current_project.auto_merge = self.auto_merge_check.isChecked()
        self.current_project.output_format = self.output_format_combo.currentText()

        self.save_project(self.current_project)

    # ===== GENERATION =====

    def generate_selected_scene(self):
        """Generate selected scene"""
        if self.current_scene_index < 0 or not self.current_project:
            return

        scene = self.current_project.scenes[self.current_scene_index]

        # Build scene data for generation
        scene_data = self.build_scene_generation_data(self.current_scene_index)

        if not scene_data:
            return

        # Emit signal
        self.generate_scene_requested.emit(scene_data)

        logger.info(f"Generate scene {scene.scene_id} requested")

    def generate_all_scenes(self):
        """Generate all scenes in project"""
        if not self.current_project or len(self.current_project.scenes) == 0:
            return

        # Build all scene data
        all_scenes = []
        for i in range(len(self.current_project.scenes)):
            scene_data = self.build_scene_generation_data(i)
            if scene_data:
                all_scenes.append(scene_data)

        if not all_scenes:
            QMessageBox.warning(self, "No Scenes", "No valid scenes to generate")
            return

        # Emit signal
        self.generate_all_requested.emit(all_scenes)

        logger.info(f"Generate all scenes requested ({len(all_scenes)} scenes)")

    def build_scene_generation_data(self, index: int) -> Optional[Dict[str, Any]]:
        """Build scene data for generation"""
        if not self.current_project or index < 0 or index >= len(self.current_project.scenes):
            return None

        scene = self.current_project.scenes[index]

        # Build full prompt (scene + global style)
        full_prompt = scene.prompt
        if self.current_project.global_style:
            full_prompt = f"{full_prompt}. {self.current_project.global_style}"

        # Determine model
        model = scene.model or self.current_project.global_model

        # Build config
        config = {
            'aspect_ratio': scene.aspect_ratio,
            'duration': scene.duration,
            'resolution': scene.resolution
        }

        # Get previous scene data if chaining
        previous_scene_data = None
        if index > 0:
            previous_scene_data = self.current_project.scenes[index - 1]

        # Build generation data
        data = {
            'scene_id': scene.scene_id,
            'scene_index': index,
            'project_name': self.current_project.name,
            'prompt': full_prompt,
            'model': model,
            'config': config,
            'reference_images': scene.reference_images,
            'use_previous_frame': scene.use_previous_frame,
            'extend_from_previous': scene.extend_from_previous,
            'previous_video_path': previous_scene_data.video_path if previous_scene_data else None,
            'first_frame': scene.first_frame,
            'last_frame': scene.last_frame
        }

        return data

    def merge_all_videos(self):
        """Merge all completed scene videos"""
        if not self.current_project or not self.current_project.is_all_completed():
            QMessageBox.warning(
                self,
                "Cannot Merge",
                "All scenes must be completed before merging"
            )
            return

        # Collect video paths
        video_paths = [scene.video_path for scene in self.current_project.scenes if scene.video_path]

        if len(video_paths) != len(self.current_project.scenes):
            QMessageBox.warning(
                self,
                "Missing Videos",
                "Some scenes don't have video files"
            )
            return

        # Emit signal
        self.merge_videos_requested.emit(video_paths)

        logger.info(f"Merge videos requested ({len(video_paths)} videos)")

    # ===== UI UPDATES =====

    def update_progress(self):
        """Update progress bar and label"""
        if not self.current_project:
            self.progress_label.setText("No scenes")
            self.progress_bar.setValue(0)
            return

        total = len(self.current_project.scenes)
        completed = self.current_project.get_completed_count()

        self.progress_label.setText(f"{completed} / {total} scenes completed")

        if total > 0:
            progress = int((completed / total) * 100)
            self.progress_bar.setValue(progress)
        else:
            self.progress_bar.setValue(0)

    def update_action_buttons(self):
        """Update action button states"""
        if not self.current_project:
            self.generate_all_btn.setEnabled(False)
            self.merge_videos_btn.setEnabled(False)
            return

        has_scenes = len(self.current_project.scenes) > 0
        all_completed = self.current_project.is_all_completed()

        self.generate_all_btn.setEnabled(has_scenes)
        self.merge_videos_btn.setEnabled(all_completed)

    def update_scene_status(self, scene_index: int, status: str, video_path: Optional[str] = None):
        """Update scene status after generation"""
        if not self.current_project or scene_index < 0 or scene_index >= len(self.current_project.scenes):
            return

        scene = self.current_project.scenes[scene_index]
        scene.status = status

        if video_path:
            scene.video_path = video_path

        # Update list item
        item = self.scene_list.item(scene_index)
        if item:
            item.setText(scene.get_display_text())

        # Update status label if this scene is selected
        if scene_index == self.current_scene_index:
            status_text = {
                'pending': '⏸ Pending',
                'processing': '⏳ Processing',
                'done': '✓ Completed',
                'failed': '✗ Failed'
            }.get(status, '?')
            self.scene_status_label.setText(status_text)

        # Save
        self.save_project(self.current_project)

        # Update progress
        self.update_progress()
        self.update_action_buttons()

        logger.info(f"Scene {scene.scene_id} status updated: {status}")
