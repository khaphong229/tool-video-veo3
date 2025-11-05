# Settings System Documentation

## Overview

Hệ thống Settings cho Veo3 Video Generator bao gồm:
- **Settings Dialog** - UI để cấu hình
- **User Settings Manager** - Quản lý và persistence
- **Settings Persistence** - Lưu/load từ JSON file

## Architecture

```
Settings System
├── ui/settings_dialog.py
│   └── SettingsDialog (QDialog)
│       ├── API Configuration Tab
│       ├── Default Settings Tab
│       ├── Templates Tab
│       └── Advanced Tab
│
├── config/user_settings.py
│   └── UserSettingsManager
│       ├── Load/Save to JSON
│       ├── Getter/Setter methods
│       └── Template management
│
└── config/user_settings.json (auto-generated)
    └── Persisted settings data
```

## Settings Dialog

### Class: `SettingsDialog(QDialog)`

Dialog window với 4 tabs để cấu hình ứng dụng.

### Tabs

#### 1. API Configuration Tab

**Purpose:** Cấu hình Google AI API

**Features:**
- API Key input (password field với toggle visibility)
- Test Connection button (async testing)
- Connection status indicator
- Last test timestamp
- Available models list
- Refresh models button

**Methods:**
```python
def test_api_connection()
    """Test kết nối với API (async trong thread riêng)"""

def toggle_api_key_visibility()
    """Show/hide API key"""

def load_available_models()
    """Load danh sách models"""
```

#### 2. Default Settings Tab

**Purpose:** Cấu hình default values cho video generation

**Settings:**
- Default Model (ComboBox)
- Default Resolution (720p, 1080p, 4K)
- Default Aspect Ratio (16:9, 9:16, 1:1, 4:3, 21:9)
- Default Duration (2-60 seconds với slider)
- Default FPS (24, 30, 60)
- Output Directory (folder picker)
- Temp Directory (folder picker)

**Methods:**
```python
def browse_output_directory()
    """Chọn output folder"""

def browse_temp_directory()
    """Chọn temp folder"""
```

#### 3. Templates Tab

**Purpose:** Quản lý style templates

**Features:**
- Template list view
- Add/Edit/Delete buttons
- Template preview panel
- Template data: name, base_style, category, tags

**Methods:**
```python
def load_templates()
    """Load templates từ settings"""

def add_template()
    """Thêm template mới"""

def edit_template()
    """Edit template đã chọn"""

def delete_template()
    """Xóa template"""

def on_template_selected(current, previous)
    """Show preview khi template được chọn"""
```

#### 4. Advanced Tab

**Purpose:** Cấu hình nâng cao

**Settings:**

**Generation Settings:**
- Max Concurrent Generations (1-10)
- Auto-retry failed generations (CheckBox)
- Retry Count (1-10)

**Logging Settings:**
- Enable logging (CheckBox)
- Log Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

**UI Preferences:**
- Dark theme (CheckBox)
- Auto-save projects (CheckBox)
- Auto-save interval (60-3600 seconds)
- Show notifications (CheckBox)

**Maintenance:**
- Clear Cache button
- Clear Logs button

### Main Methods

```python
def load_settings()
    """Load tất cả settings từ UserSettingsManager vào UI"""

def save_settings() -> bool
    """Lưu settings từ UI vào UserSettingsManager

    Returns:
        bool: True nếu thành công
    """

def validate_settings() -> bool
    """Validate settings trước khi save

    Validates:
    - API key length (nếu có)
    - Output directory not empty

    Returns:
        bool: True nếu valid
    """
```

### Dialog Buttons

- **OK**: Save và đóng dialog
- **Cancel**: Đóng không save
- **Apply**: Save nhưng không đóng
- **Reset to Defaults**: Reset tất cả về mặc định

### Signals

```python
settings_changed = pyqtSignal()  # Phát khi settings được save
```

### Usage Example

```python
from ui import SettingsDialog

# Tạo dialog
dialog = SettingsDialog(parent_window)

# Connect signal
dialog.settings_changed.connect(on_settings_changed)

# Show dialog
if dialog.exec():
    print("Settings saved")
else:
    print("Cancelled")
```

## User Settings Manager

### Class: `UserSettingsManager`

Quản lý user settings với persistence vào JSON file.

### Initialization

```python
from config import get_user_settings

# Get singleton instance
settings = get_user_settings()

# Or create custom instance
from config import UserSettingsManager
from pathlib import Path

settings = UserSettingsManager(Path("custom_settings.json"))
```

### Settings Structure

```json
{
    "api": {
        "api_key": "",
        "last_test_date": null,
        "connection_status": "not_tested"
    },
    "defaults": {
        "model": "veo-2.0",
        "resolution": "1080p",
        "aspect_ratio": "16:9",
        "duration": 5,
        "fps": 30,
        "output_directory": "outputs",
        "temp_directory": "temp"
    },
    "templates": [],
    "advanced": {
        "max_concurrent_generations": 3,
        "auto_retry_failed": true,
        "retry_count": 3,
        "enable_logging": true,
        "log_level": "INFO",
        "auto_save_project": true,
        "auto_save_interval": 300,
        "show_notifications": true,
        "dark_theme": true
    },
    "ui": {
        "sidebar_visible": true,
        "last_tab_index": 0,
        "window_geometry": null,
        "recent_projects": []
    },
    "metadata": {
        "version": "1.0.0",
        "created_date": "2025-01-05T10:00:00",
        "last_modified": "2025-01-05T10:00:00"
    }
}
```

### Core Methods

#### Load/Save

```python
def load_settings() -> Dict[str, Any]
    """Load settings từ file"""

def save_settings() -> bool
    """Save settings vào file"""
```

#### Getters (Dot Notation Support)

```python
# Generic getter
settings.get('api.api_key')  # Returns API key
settings.get('defaults.model')  # Returns default model

# Specific getters
settings.get_api_key() -> str
settings.get_default_model() -> str
settings.get_default_resolution() -> str
settings.get_default_aspect_ratio() -> str
settings.get_default_duration() -> int
settings.get_output_directory() -> str
settings.get_templates() -> list
settings.get_max_concurrent() -> int
settings.get_auto_retry() -> bool
```

#### Setters

```python
# Generic setter
settings.set('api.api_key', 'new_key')
settings.set('defaults.duration', 10)

# Specific setters
settings.set_api_key(api_key: str)
settings.set_default_model(model: str)
settings.set_default_resolution(resolution: str)
settings.set_default_aspect_ratio(aspect_ratio: str)
settings.set_default_duration(duration: int)
settings.set_output_directory(directory: str)
settings.set_connection_status(status: str, test_date: str = None)
```

#### Template Management

```python
def add_template(template: Dict[str, Any])
    """Thêm template mới"""

def update_template(index: int, template: Dict[str, Any])
    """Update template tại index"""

def delete_template(index: int)
    """Xóa template"""
```

Example:
```python
# Add template
template = {
    'name': 'Cinematic Sunset',
    'base_style': 'cinematic, golden hour, dramatic lighting',
    'category': 'cinematic',
    'tags': ['sunset', 'dramatic', 'nature']
}
settings.add_template(template)
settings.save_settings()

# Get templates
templates = settings.get_templates()
for template in templates:
    print(template['name'])
```

#### Recent Projects

```python
def add_recent_project(project_path: str)
    """Thêm project vào recent list (max 10)"""

def get_recent_projects() -> list
    """Lấy danh sách recent projects"""
```

Example:
```python
settings.add_recent_project('/path/to/project')
recent = settings.get_recent_projects()
```

#### Utility Methods

```python
def reset_to_defaults()
    """Reset tất cả settings về mặc định"""

def export_settings(export_path: Path) -> bool
    """Export settings ra file"""

def import_settings(import_path: Path) -> bool
    """Import settings từ file"""
```

### Advanced Usage

#### Custom Settings Path

```python
from config import UserSettingsManager
from pathlib import Path

# Custom settings file
settings = UserSettingsManager(
    settings_file=Path("my_custom_settings.json")
)
```

#### Export/Import Settings

```python
# Export
settings.export_settings(Path("backup_settings.json"))

# Import
settings.import_settings(Path("backup_settings.json"))
```

#### Nested Settings Access

```python
# Get nested value với default
value = settings.get('advanced.max_concurrent_generations', 3)

# Set nested value
settings.set('advanced.log_level', 'DEBUG')
```

## Integration with Main Window

### Opening Settings Dialog

```python
# In MainWindow
def on_open_settings(self):
    from .settings_dialog import SettingsDialog

    dialog = SettingsDialog(self)
    dialog.settings_changed.connect(self.on_settings_changed)

    if dialog.exec():
        logger.info("Settings saved")

def on_settings_changed(self):
    """Reload settings và update UI"""
    # Reload configuration
    # Update UI components
```

### Loading User Settings on Startup

```python
# In MainWindow.__init__()
from config import get_user_settings

self.user_settings = get_user_settings()

# Apply settings to UI
self.model_combo.setCurrentText(
    self.user_settings.get_default_model()
)
```

## Validation

### API Key Validation

```python
def validate_api_key(api_key: str) -> bool:
    """Validate API key format"""
    if not api_key:
        return False
    if len(api_key) < 20:  # Too short
        return False
    return True
```

### Directory Validation

```python
def validate_directory(directory: str) -> bool:
    """Validate directory path"""
    if not directory:
        return False

    path = Path(directory)
    if not path.exists():
        # Try to create
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except:
            return False

    return True
```

## Error Handling

### Load Settings Failure

```python
try:
    settings = get_user_settings()
except Exception as e:
    logger.error(f"Could not load settings: {e}")
    # Use defaults
    settings = UserSettingsManager()
    settings.settings = settings.get_default_settings()
```

### Save Settings Failure

```python
if not settings.save_settings():
    QMessageBox.critical(
        self,
        "Error",
        "Could not save settings to file"
    )
```

## Best Practices

### 1. Always Validate Before Save

```python
if dialog.validate_settings():
    dialog.save_settings()
```

### 2. Use Signals for Changes

```python
dialog.settings_changed.connect(reload_ui)
```

### 3. Handle Defaults Gracefully

```python
# Always provide defaults
value = settings.get('key', default_value)
```

### 4. Save After Important Changes

```python
settings.set_api_key(new_key)
settings.save_settings()  # Persist immediately
```

### 5. Log Settings Changes

```python
logger.info(f"Setting changed: {key} = {value}")
```

## Testing

### Test Settings Dialog

```bash
python demo_settings.py
```

### Manual Testing Checklist

- [ ] API key input (show/hide)
- [ ] Test connection button
- [ ] Model list loads
- [ ] All default settings load correctly
- [ ] Directory pickers work
- [ ] Duration slider updates label
- [ ] Templates load/add/delete
- [ ] Template preview shows
- [ ] All checkboxes toggle
- [ ] Spinbox values validate
- [ ] OK saves and closes
- [ ] Cancel closes without saving
- [ ] Apply saves without closing
- [ ] Reset to defaults works
- [ ] Validation prevents invalid input
- [ ] Settings persist after restart

### Unit Testing Example

```python
def test_user_settings():
    from config import UserSettingsManager
    from pathlib import Path
    import tempfile

    # Create temp settings file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
        settings_file = Path(f.name)

    # Test
    settings = UserSettingsManager(settings_file)

    # Set value
    settings.set_api_key('test_key_123')
    settings.save_settings()

    # Load again
    settings2 = UserSettingsManager(settings_file)
    assert settings2.get_api_key() == 'test_key_123'

    # Cleanup
    settings_file.unlink()
```

## Troubleshooting

### Settings Not Persisting

**Problem:** Settings không được lưu sau khi đóng app

**Solutions:**
1. Check file permissions cho `config/user_settings.json`
2. Verify `save_settings()` được gọi
3. Check logs cho errors

### Invalid JSON Error

**Problem:** Lỗi khi load settings

**Solution:**
1. Delete `config/user_settings.json`
2. Restart app (sẽ tạo file mới với defaults)

### Missing Settings Keys

**Problem:** Một số settings không load

**Solution:**
- Settings sẽ tự động merge với defaults
- Nếu vẫn thiếu, reset to defaults

## Future Enhancements

- [ ] Settings profiles (multiple configs)
- [ ] Cloud sync
- [ ] Settings import/export UI
- [ ] Settings search
- [ ] Advanced template editor dialog
- [ ] Settings history/undo
- [ ] Keyboard shortcut editor
- [ ] Theme customization UI

---

**Version:** 1.0.0
**Last Updated:** 2025-01-05
