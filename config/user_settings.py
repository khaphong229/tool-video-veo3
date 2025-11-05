"""
Module quản lý user settings và persistence
Lưu và load cài đặt người dùng từ JSON file
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

from .settings import BASE_DIR, OUTPUT_DIR, TEMP_DIR, DEFAULT_MODEL, DEFAULT_RESOLUTION, DEFAULT_ASPECT_RATIO, VIDEO_DURATION_RANGE, DEFAULT_FPS
from utils import get_logger

logger = get_logger(__name__)


class UserSettingsManager:
    """
    Quản lý settings của người dùng
    Lưu trữ và load từ JSON file
    """

    def __init__(self, settings_file: Optional[Path] = None):
        """
        Khởi tạo Settings Manager

        Args:
            settings_file: Đường dẫn file settings. Mặc định: config/user_settings.json
        """
        if settings_file is None:
            settings_file = BASE_DIR / 'config' / 'user_settings.json'

        self.settings_file = settings_file
        self.settings: Dict[str, Any] = {}
        self.load_settings()

    def get_default_settings(self) -> Dict[str, Any]:
        """
        Trả về settings mặc định

        Returns:
            dict: Default settings
        """
        return {
            # API Configuration
            'api': {
                'api_key': '',
                'last_test_date': None,
                'connection_status': 'not_tested'
            },

            # Default Video Settings
            'defaults': {
                'model': DEFAULT_MODEL,
                'resolution': DEFAULT_RESOLUTION,
                'aspect_ratio': DEFAULT_ASPECT_RATIO,
                'duration': VIDEO_DURATION_RANGE['default'],
                'fps': DEFAULT_FPS,
                'output_directory': str(OUTPUT_DIR),
                'temp_directory': str(TEMP_DIR)
            },

            # Templates
            'templates': [],

            # Advanced Settings
            'advanced': {
                'max_concurrent_generations': 3,
                'auto_retry_failed': True,
                'retry_count': 3,
                'enable_logging': True,
                'log_level': 'INFO',
                'auto_save_project': True,
                'auto_save_interval': 300,  # seconds
                'show_notifications': True,
                'dark_theme': True
            },

            # UI Preferences
            'ui': {
                'sidebar_visible': True,
                'last_tab_index': 0,
                'window_geometry': None,
                'recent_projects': []
            },

            # Metadata
            'metadata': {
                'version': '1.0.0',
                'created_date': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat()
            }
        }

    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings từ file

        Returns:
            dict: Loaded settings
        """
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)

                # Merge với default settings để đảm bảo có đầy đủ keys
                self.settings = self._merge_settings(
                    self.get_default_settings(),
                    loaded_settings
                )

                logger.info(f"Đã load settings từ {self.settings_file}")
            else:
                logger.info("Không tìm thấy settings file, sử dụng default")
                self.settings = self.get_default_settings()

        except Exception as e:
            logger.error(f"Lỗi khi load settings: {e}")
            self.settings = self.get_default_settings()

        return self.settings

    def save_settings(self) -> bool:
        """
        Lưu settings vào file

        Returns:
            bool: True nếu thành công
        """
        try:
            # Update last modified
            self.settings['metadata']['last_modified'] = datetime.now().isoformat()

            # Tạo thư mục nếu chưa tồn tại
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)

            # Ghi file
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)

            logger.info(f"Đã lưu settings vào {self.settings_file}")
            return True

        except Exception as e:
            logger.error(f"Lỗi khi lưu settings: {e}")
            return False

    def _merge_settings(self, default: dict, loaded: dict) -> dict:
        """
        Merge loaded settings với default settings
        Đảm bảo có đầy đủ keys

        Args:
            default: Default settings
            loaded: Loaded settings

        Returns:
            dict: Merged settings
        """
        merged = default.copy()

        for key, value in loaded.items():
            if key in merged:
                if isinstance(value, dict) and isinstance(merged[key], dict):
                    # Recursive merge cho nested dicts
                    merged[key] = self._merge_settings(merged[key], value)
                else:
                    merged[key] = value
            else:
                merged[key] = value

        return merged

    # ===== GETTER METHODS =====

    def get(self, key: str, default: Any = None) -> Any:
        """
        Lấy giá trị setting theo key (hỗ trợ nested keys với dot notation)

        Args:
            key: Setting key (e.g., 'api.api_key', 'defaults.model')
            default: Default value nếu không tìm thấy

        Returns:
            Giá trị setting

        Example:
            >>> manager.get('api.api_key')
            'your_api_key'
        """
        keys = key.split('.')
        value = self.settings

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_api_key(self) -> str:
        """Lấy API key"""
        return self.get('api.api_key', '')

    def get_default_model(self) -> str:
        """Lấy default model"""
        return self.get('defaults.model', DEFAULT_MODEL)

    def get_default_resolution(self) -> str:
        """Lấy default resolution"""
        return self.get('defaults.resolution', DEFAULT_RESOLUTION)

    def get_default_aspect_ratio(self) -> str:
        """Lấy default aspect ratio"""
        return self.get('defaults.aspect_ratio', DEFAULT_ASPECT_RATIO)

    def get_default_duration(self) -> int:
        """Lấy default duration"""
        return self.get('defaults.duration', VIDEO_DURATION_RANGE['default'])

    def get_output_directory(self) -> str:
        """Lấy output directory"""
        return self.get('defaults.output_directory', str(OUTPUT_DIR))

    def get_templates(self) -> list:
        """Lấy danh sách templates"""
        return self.get('templates', [])

    def get_max_concurrent(self) -> int:
        """Lấy max concurrent generations"""
        return self.get('advanced.max_concurrent_generations', 3)

    def get_auto_retry(self) -> bool:
        """Lấy auto retry setting"""
        return self.get('advanced.auto_retry_failed', True)

    # ===== SETTER METHODS =====

    def set(self, key: str, value: Any) -> None:
        """
        Set giá trị setting (hỗ trợ nested keys với dot notation)

        Args:
            key: Setting key
            value: Giá trị mới

        Example:
            >>> manager.set('api.api_key', 'new_key')
        """
        keys = key.split('.')
        current = self.settings

        # Navigate to the nested dict
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]

        # Set value
        current[keys[-1]] = value

    def set_api_key(self, api_key: str) -> None:
        """Set API key"""
        self.set('api.api_key', api_key)

    def set_default_model(self, model: str) -> None:
        """Set default model"""
        self.set('defaults.model', model)

    def set_default_resolution(self, resolution: str) -> None:
        """Set default resolution"""
        self.set('defaults.resolution', resolution)

    def set_default_aspect_ratio(self, aspect_ratio: str) -> None:
        """Set default aspect ratio"""
        self.set('defaults.aspect_ratio', aspect_ratio)

    def set_default_duration(self, duration: int) -> None:
        """Set default duration"""
        self.set('defaults.duration', duration)

    def set_output_directory(self, directory: str) -> None:
        """Set output directory"""
        self.set('defaults.output_directory', directory)

    def set_connection_status(self, status: str, test_date: str = None) -> None:
        """Set API connection status"""
        self.set('api.connection_status', status)
        if test_date:
            self.set('api.last_test_date', test_date)

    # ===== TEMPLATE METHODS =====

    def add_template(self, template: Dict[str, Any]) -> None:
        """
        Thêm template mới

        Args:
            template: Template data
        """
        templates = self.get_templates()
        templates.append(template)
        self.set('templates', templates)

    def update_template(self, index: int, template: Dict[str, Any]) -> None:
        """
        Update template

        Args:
            index: Index của template
            template: Template data mới
        """
        templates = self.get_templates()
        if 0 <= index < len(templates):
            templates[index] = template
            self.set('templates', templates)

    def delete_template(self, index: int) -> None:
        """
        Xóa template

        Args:
            index: Index của template
        """
        templates = self.get_templates()
        if 0 <= index < len(templates):
            templates.pop(index)
            self.set('templates', templates)

    # ===== RECENT PROJECTS =====

    def add_recent_project(self, project_path: str) -> None:
        """
        Thêm project vào recent list

        Args:
            project_path: Đường dẫn project
        """
        recent = self.get('ui.recent_projects', [])

        # Remove nếu đã tồn tại
        if project_path in recent:
            recent.remove(project_path)

        # Add to front
        recent.insert(0, project_path)

        # Keep only 10 recent
        recent = recent[:10]

        self.set('ui.recent_projects', recent)

    def get_recent_projects(self) -> list:
        """Lấy danh sách recent projects"""
        return self.get('ui.recent_projects', [])

    # ===== UTILITY METHODS =====

    def reset_to_defaults(self) -> None:
        """Reset tất cả settings về mặc định"""
        self.settings = self.get_default_settings()
        logger.info("Đã reset settings về mặc định")

    def export_settings(self, export_path: Path) -> bool:
        """
        Export settings ra file

        Args:
            export_path: Đường dẫn export

        Returns:
            bool: True nếu thành công
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            logger.info(f"Đã export settings ra {export_path}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi export settings: {e}")
            return False

    def import_settings(self, import_path: Path) -> bool:
        """
        Import settings từ file

        Args:
            import_path: Đường dẫn file

        Returns:
            bool: True nếu thành công
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported = json.load(f)

            self.settings = self._merge_settings(
                self.get_default_settings(),
                imported
            )

            logger.info(f"Đã import settings từ {import_path}")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi import settings: {e}")
            return False


# ===== SINGLETON INSTANCE =====
_settings_manager: Optional[UserSettingsManager] = None


def get_user_settings() -> UserSettingsManager:
    """
    Lấy singleton instance của UserSettingsManager

    Returns:
        UserSettingsManager instance
    """
    global _settings_manager

    if _settings_manager is None:
        _settings_manager = UserSettingsManager()

    return _settings_manager


# ===== EXPORT =====
__all__ = [
    'UserSettingsManager',
    'get_user_settings'
]
