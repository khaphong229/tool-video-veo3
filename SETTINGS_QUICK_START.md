# Settings Dialog - Quick Start Guide

## Overview

Comprehensive Settings Dialog đã được tạo với đầy đủ tính năng quản lý cấu hình ứng dụng.

## 📁 Files Created

### 1. **ui/settings_dialog.py** (800 lines)
Complete Settings Dialog với 4 tabs:
- ✅ API Configuration
- ✅ Default Settings
- ✅ Templates Management
- ✅ Advanced Settings

### 2. **config/user_settings.py** (434 lines)
User Settings Manager với:
- ✅ JSON persistence
- ✅ Getter/Setter methods (dot notation support)
- ✅ Template management
- ✅ Recent projects tracking
- ✅ Export/Import functionality

### 3. **demo_settings.py**
Standalone demo để test Settings Dialog

### 4. **SETTINGS_DOCUMENTATION.md**
Complete documentation (400+ lines)

## 🚀 Quick Test

```bash
# Test Settings Dialog
python demo_settings.py
```

## 📋 Features Implemented

### Tab 1: API Configuration ✅

**Features:**
- 🔑 API Key input với show/hide toggle
- 🔌 Test Connection button (async, không block UI)
- ✅ Connection status indicator với color coding
- 📅 Last test timestamp
- 📊 Available models list
- 🔄 Refresh models button

**Key Methods:**
```python
test_api_connection()      # Async test trong thread
toggle_api_key_visibility() # Show/hide API key
load_available_models()    # Load models list
```

### Tab 2: Default Settings ✅

**Settings:**
- 🎬 Default Model (ComboBox)
- 📺 Default Resolution (480p/720p/1080p/4K)
- 📐 Default Aspect Ratio (16:9, 9:16, 1:1, 4:3, 21:9)
- ⏱️ Default Duration (2-60 sec với slider + live label)
- 🎞️ Default FPS (24/30/60)
- 📁 Output Directory (folder picker)
- 📂 Temp Directory (folder picker)

**Key Methods:**
```python
browse_output_directory()  # Folder picker cho output
browse_temp_directory()    # Folder picker cho temp
```

### Tab 3: Templates ✅

**Features:**
- 📋 Template list view
- ➕ Add template button
- ✏️ Edit template button
- 🗑️ Delete template button
- 👁️ Template preview panel
- 🔍 Selection change handler

**Template Structure:**
```json
{
    "name": "Template Name",
    "base_style": "style description",
    "category": "category",
    "tags": ["tag1", "tag2"]
}
```

**Key Methods:**
```python
load_templates()              # Load từ settings
add_template()                # Add new
edit_template()               # Edit selected
delete_template()             # Delete selected
on_template_selected()        # Show preview
```

### Tab 4: Advanced ✅

**Generation Settings:**
- ⚡ Max Concurrent Generations (1-10 spinbox)
- 🔄 Auto-retry failed (checkbox)
- 🔢 Retry Count (1-10 spinbox)

**Logging Settings:**
- 📝 Enable logging (checkbox)
- 📊 Log Level (DEBUG/INFO/WARNING/ERROR/CRITICAL)

**UI Preferences:**
- 🌙 Dark theme (checkbox)
- 💾 Auto-save projects (checkbox)
- ⏰ Auto-save interval (60-3600 sec spinbox)
- 🔔 Show notifications (checkbox)

**Maintenance:**
- 🗑️ Clear Cache button
- 📋 Clear Logs button

**Key Methods:**
```python
clear_cache()  # Clear temp files
clear_logs()   # Clear log files
```

## 🔧 Core Functionality

### Load/Save Settings ✅

```python
def load_settings()
    """Load ALL settings từ UserSettingsManager vào UI"""

def save_settings() -> bool
    """Save ALL settings từ UI vào UserSettingsManager + file"""

def validate_settings() -> bool
    """Validate trước khi save"""
```

### Validation ✅

**Validates:**
- ✅ API key length (min 20 chars if provided)
- ✅ Output directory not empty
- ✅ Path existence

**Error Handling:**
- Shows warning message boxes
- Switches to relevant tab
- Returns False to prevent save

### Dialog Buttons ✅

| Button | Action |
|--------|--------|
| **OK** | Save + Close dialog |
| **Cancel** | Close without saving |
| **Apply** | Save without closing |
| **Reset to Defaults** | Reset ALL settings (with confirmation) |

### Signals ✅

```python
settings_changed = pyqtSignal()  # Emitted khi settings saved
```

## 💾 User Settings Manager

### Singleton Access

```python
from config import get_user_settings

settings = get_user_settings()
```

### Key Features

**Dot Notation Support:**
```python
# Get nested values
api_key = settings.get('api.api_key')
model = settings.get('defaults.model')

# Set nested values
settings.set('api.api_key', 'new_key')
settings.set('advanced.log_level', 'DEBUG')
```

**Convenience Methods:**
```python
# Getters
settings.get_api_key()
settings.get_default_model()
settings.get_default_resolution()
settings.get_templates()
settings.get_max_concurrent()

# Setters
settings.set_api_key('key')
settings.set_default_model('veo-3.1')
settings.set_output_directory('/path')
```

**Template Management:**
```python
template = {
    'name': 'Cinematic',
    'base_style': 'cinematic, dramatic',
    'category': 'cinematic',
    'tags': ['dramatic', 'moody']
}

settings.add_template(template)
settings.update_template(0, template)
settings.delete_template(0)
```

**Recent Projects:**
```python
settings.add_recent_project('/path/to/project')
recent = settings.get_recent_projects()  # Max 10
```

**Utility:**
```python
settings.reset_to_defaults()
settings.export_settings(Path('backup.json'))
settings.import_settings(Path('backup.json'))
```

## 🔗 Integration with Main Window

### Opening Settings Dialog

Settings button trong toolbar và menu đã được kết nối:

```python
# In MainWindow.on_open_settings()
dialog = SettingsDialog(self)
dialog.settings_changed.connect(self.on_settings_changed)

if dialog.exec():
    # Settings saved
    pass
```

### Reloading After Changes

```python
def on_settings_changed(self):
    """Called when settings changed"""
    # Reload và update UI
    self.set_status_message("Settings updated")
```

## 📂 Settings File Location

```
config/user_settings.json
```

**Auto-created** khi app chạy lần đầu với default values.

### Settings File Structure

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

## 🎨 UI/UX Features

### Visual Design ✅
- Modern dark theme
- Color-coded status (Green = success, Red = error)
- Icon placeholders (Unicode emojis)
- Grouped settings với QGroupBox
- Form layouts cho clean alignment

### User Experience ✅
- Live duration slider label update
- Async API testing (không block UI)
- Confirmation dialogs cho destructive actions
- Auto-scroll to validation errors
- Tab switching cho error fields

### Keyboard Shortcuts
- Enter = OK (trong fields)
- Esc = Cancel
- Tab navigation works

## 📊 Code Statistics

| File | Lines | Description |
|------|-------|-------------|
| ui/settings_dialog.py | 800 | Complete dialog implementation |
| config/user_settings.py | 434 | Settings manager + persistence |
| **Total** | **1,234** | **Production-ready code** |

## ✅ Testing Checklist

### Basic Functionality
- [x] Dialog opens
- [x] All tabs render
- [x] Load settings on open
- [x] Save settings on OK
- [x] Cancel closes without saving
- [x] Apply saves without closing

### API Tab
- [x] API key input works
- [x] Show/hide toggle works
- [x] Test connection button (async)
- [x] Status indicator updates
- [x] Models list loads

### Defaults Tab
- [x] All combos populate
- [x] Slider updates label
- [x] Folder pickers open
- [x] Values save correctly

### Templates Tab
- [x] Template list loads
- [x] Add button works
- [x] Delete with confirmation
- [x] Preview shows on select

### Advanced Tab
- [x] All checkboxes toggle
- [x] Spinboxes validate
- [x] Clear cache works
- [x] Clear logs works

### Validation
- [x] API key validation
- [x] Directory validation
- [x] Error messages show
- [x] Tab switches to error

### Persistence
- [x] Settings save to JSON
- [x] Settings load from JSON
- [x] Defaults merge correctly
- [x] Export/import works

## 🚀 Usage Examples

### Example 1: Open from Main Window

```python
# In main window
settings_btn.clicked.connect(self.on_open_settings)

def on_open_settings(self):
    from ui import SettingsDialog
    dialog = SettingsDialog(self)
    dialog.exec()
```

### Example 2: Get User Settings

```python
from config import get_user_settings

settings = get_user_settings()

# Use in your code
output_dir = settings.get_output_directory()
model = settings.get_default_model()
```

### Example 3: Listen to Changes

```python
dialog = SettingsDialog()

def reload_config():
    print("Settings changed!")
    # Reload your config

dialog.settings_changed.connect(reload_config)
dialog.exec()
```

### Example 4: Validate API Key

```python
settings = get_user_settings()
api_key = settings.get_api_key()

if not api_key:
    # Show settings dialog
    dialog = SettingsDialog()
    dialog.tabs.setCurrentIndex(0)  # API tab
    dialog.exec()
```

## 📚 Documentation

- **Full Documentation**: [SETTINGS_DOCUMENTATION.md](SETTINGS_DOCUMENTATION.md)
- **UI Documentation**: [UI_DOCUMENTATION.md](UI_DOCUMENTATION.md)
- **Main README**: [README.md](README.md)

## 🎯 Next Steps

The Settings Dialog is **production-ready**! Optional enhancements:

1. **Template Editor Dialog** - Rich editor cho templates
2. **Keyboard Shortcuts Editor** - Custom shortcuts
3. **Theme Customization** - Color picker cho themes
4. **Settings Profiles** - Multiple saved configs
5. **Cloud Sync** - Sync settings across devices

---

**🎉 Settings System Complete!**

Run `python demo_settings.py` to see it in action!
