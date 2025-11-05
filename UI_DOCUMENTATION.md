# UI Documentation - Veo3 Video Generator

## Overview

Giao diện người dùng cho Veo3 Video Generator được xây dựng với PyQt6, sử dụng dark theme hiện đại và layout responsive.

## Architecture

### Main Components

```
MainWindow (QMainWindow)
├── Menu Bar
│   ├── File Menu
│   ├── Edit Menu
│   ├── View Menu
│   └── Help Menu
├── Tool Bar
│   └── Quick Actions
├── Central Widget
│   └── Tab Widget
│       ├── Text to Video Tab
│       ├── Image to Video Tab
│       ├── Scene Manager Tab
│       └── History & Library Tab
├── Sidebar (QDockWidget)
│   ├── Model Selection
│   ├── Video Settings
│   ├── Reference Images
│   └── Quick Actions
└── Status Bar
    ├── Status Message
    ├── API Status
    └── Progress Indicator
```

## File Structure

```
ui/
├── __init__.py           # Module exports
├── main_window.py        # Main window implementation
├── styles.py             # Dark theme & styling
├── text_to_video_tab.py  # Text to Video tab (TODO)
├── image_to_video_tab.py # Image to Video tab (TODO)
├── scene_manager_tab.py  # Scene Manager tab (TODO)
└── history_tab.py        # History & Library tab (TODO)
```

## Main Window (main_window.py)

### Class: `MainWindow(QMainWindow)`

Main window của ứng dụng với đầy đủ features.

#### Properties

- `current_project_id: Optional[int]` - ID của project hiện tại
- `api_connected: bool` - Trạng thái kết nối API
- `tabs: QTabWidget` - Tab widget chính
- `sidebar_dock: QDockWidget` - Sidebar dock

#### Signals

```python
api_status_changed = pyqtSignal(bool, str)  # (connected, message)
project_changed = pyqtSignal(int)           # project_id
```

#### Methods

**Setup Methods:**
- `setupUi()` - Thiết lập giao diện
- `createMenuBar()` - Tạo menu bar
- `createToolBar()` - Tạo toolbar
- `createCentralWidget()` - Tạo central widget
- `createSidebar()` - Tạo sidebar
- `createStatusBar()` - Tạo status bar
- `setupTabs()` - Thiết lập tabs

**Public Methods:**
```python
def set_api_status(connected: bool, message: str = "")
    """Set trạng thái kết nối API"""

def set_status_message(message: str)
    """Set message trong status bar"""

def get_current_settings() -> dict
    """Lấy settings hiện tại từ sidebar"""
```

#### Usage Example

```python
from ui import MainWindow
from PyQt6.QtWidgets import QApplication

app = QApplication([])
window = MainWindow()

# Set API status
window.set_api_status(True, "Connected")

# Set status message
window.set_status_message("Generating video...")

# Get current settings
settings = window.get_current_settings()
print(settings)
# Output: {
#     'model': 'Veo 3.1',
#     'aspect_ratio': '16:9',
#     'resolution': '1080p',
#     'duration': 5,
#     'fps': 30
# }

window.show()
app.exec()
```

## Styling (styles.py)

### Dark Theme

Dark theme được định nghĩa trong `DARK_THEME` stylesheet.

**Color Palette:**
- Background: `#1e1e1e`
- Secondary Background: `#252525`
- Borders: `#3c3c3c`
- Text: `#e0e0e0`
- Primary Accent: `#14ffec` (Cyan)
- Secondary Accent: `#0d7377` (Dark Cyan)

### Accent Colors

```python
from ui import get_accent_color

primary = get_accent_color('primary')    # '#14ffec'
danger = get_accent_color('danger')      # '#d32f2f'
success = get_accent_color('success')    # '#66bb6a'
```

### Icons

Unicode emoji icons được sử dụng làm placeholders:

```python
from ui import get_icon_text, ICONS

# Get icon
video_icon = get_icon_text('video')  # '🎬'
save_icon = get_icon_text('save')    # '💾'

# Use in button
button.setText(f"{get_icon_text('play')} Generate")
```

**Available Icons:**
- `new_project`, `open_project`, `save`, `save_as`
- `export`, `import`, `settings`, `refresh`
- `play`, `pause`, `stop`, `video`, `image`
- `delete`, `edit`, `add`, `remove`
- `success`, `error`, `warning`, `info`
- và nhiều hơn... (xem `styles.py` để biết full list)

### Custom Button Styles

Sử dụng `objectName` để apply custom styles:

```python
# Primary button (cyan background)
button = QPushButton("Generate")
button.setObjectName("primaryButton")

# Secondary button (gray background)
button = QPushButton("Cancel")
button.setObjectName("secondaryButton")

# Danger button (red background)
button = QPushButton("Delete")
button.setObjectName("dangerButton")
```

## Menu Bar

### File Menu
- **New Project** (Ctrl+N) - Tạo project mới
- **Open Project** (Ctrl+O) - Mở project
- **Save** (Ctrl+S) - Lưu project
- **Save As** (Ctrl+Shift+S) - Lưu với tên mới
- **Export Video** (Ctrl+E) - Export video
- **Exit** (Ctrl+Q) - Thoát ứng dụng

### Edit Menu
- **Undo** (Ctrl+Z)
- **Redo** (Ctrl+Y)
- **Copy** (Ctrl+C)
- **Paste** (Ctrl+V)

### View Menu
- **Toggle Sidebar** (Ctrl+B) - Ẩn/hiện sidebar
- **Zoom In** (Ctrl++)
- **Zoom Out** (Ctrl+-)

### Help Menu
- **Documentation** (F1) - Mở documentation
- **About** - Thông tin về app

## Tool Bar

Quick actions toolbar với các nút:
- 📁 New - Tạo project mới
- 📂 Open - Mở project
- 💾 Save - Lưu project
- ⚙️ Settings - Mở settings
- 🔄 Refresh - Làm mới dữ liệu
- 🔌 API Status - Hiển thị trạng thái API

## Tabs

### Tab 1: Text to Video
Convert text prompts thành AI-generated videos.

**Features (planned):**
- Text prompt input
- Style settings
- Generation controls
- Preview area

### Tab 2: Image to Video
Animate images với AI.

**Features (planned):**
- Image upload
- Animation settings
- Motion controls
- Preview

### Tab 3: Scene Manager
Quản lý multi-scene projects.

**Features (planned):**
- Scene list
- Timeline view
- Scene editor
- Transitions

### Tab 4: History & Library
Browse video history và templates.

**Features (planned):**
- Generation history
- Template library
- Search & filter
- Export/import

## Sidebar

### Model Selection
ComboBox để chọn Veo model:
- Veo 2.0
- Veo 3.0
- Veo 3.1
- Veo 3.1-Fast

### Video Settings
- **Aspect Ratio**: 16:9, 9:16, 1:1, 4:3, 21:9
- **Resolution**: 480p, 720p, 1080p, 4K
- **Duration**: 2-60 seconds
- **FPS**: 24, 30, 60

### Reference Images
List widget để quản lý reference images:
- Add Image button
- Remove button
- List hiển thị

### Quick Actions
- **Generate Video** - Primary action button
- **Reset Settings** - Reset về default

## Status Bar

Hiển thị 3 phần:
1. **Status Message** (left) - Messages và thông báo
2. **API Status** (right) - Trạng thái kết nối API
3. **Progress** (right) - Progress indicator

### API Status Colors
- 🟢 Green (`#66bb6a`) - Connected
- 🔴 Red (`#d32f2f`) - Disconnected/Error

## Signals & Slots

### Custom Signals

```python
# API status changed
window.api_status_changed.connect(handler)
# Signature: (connected: bool, message: str)

# Project changed
window.project_changed.connect(handler)
# Signature: (project_id: int)
```

### Example

```python
def on_api_status_changed(connected, message):
    if connected:
        print(f"API Connected: {message}")
    else:
        print(f"API Disconnected: {message}")

window.api_status_changed.connect(on_api_status_changed)
window.set_api_status(True, "Ready")
```

## Customization

### Thay đổi Theme

```python
from ui import DARK_THEME

# Modify theme
custom_theme = DARK_THEME.replace('#14ffec', '#ff00ff')  # Change accent color

window.setStyleSheet(custom_theme)
```

### Thêm Custom Widgets

```python
# Tạo custom widget
class CustomWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Setup UI
        pass

# Thêm vào tab
window.tabs.addTab(CustomWidget(), "Custom Tab")
```

## Running the UI

### Method 1: Demo Mode

```bash
python demo_ui.py
```

### Method 2: Full App

```bash
python main.py
```

### Method 3: Standalone

```python
import sys
from PyQt6.QtWidgets import QApplication
from ui import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Project |
| Ctrl+O | Open Project |
| Ctrl+S | Save Project |
| Ctrl+Shift+S | Save As |
| Ctrl+E | Export Video |
| Ctrl+Q | Exit |
| Ctrl+Z | Undo |
| Ctrl+Y | Redo |
| Ctrl+C | Copy |
| Ctrl+V | Paste |
| Ctrl+B | Toggle Sidebar |
| Ctrl++ | Zoom In |
| Ctrl+- | Zoom Out |
| F1 | Documentation |

## Future Enhancements

### Planned Features
- [ ] Implement detailed tab widgets
- [ ] Add drag-and-drop support
- [ ] Implement preview player
- [ ] Add timeline view
- [ ] Implement undo/redo system
- [ ] Add custom keyboard shortcuts editor
- [ ] Implement theme switcher (Light/Dark)
- [ ] Add multi-language support

### Advanced Features
- [ ] Real-time collaboration
- [ ] Cloud sync
- [ ] Plugin system
- [ ] Custom widget library
- [ ] Advanced animation editor

## Troubleshooting

### UI không hiển thị đúng
**Solution:** Đảm bảo PyQt6 đã được cài đặt:
```bash
pip install PyQt6
```

### Theme không apply
**Solution:** Gọi `apply_theme()` sau khi tạo window:
```python
window = MainWindow()
window.apply_theme()
```

### Icons không hiển thị
**Solution:** Icons hiện đang sử dụng Unicode emojis. Nếu muốn dùng icon files thực:
1. Tạo thư mục `assets/icons/`
2. Thêm icon files (.png, .svg)
3. Cập nhật code để load icons:
```python
QIcon('assets/icons/save.png')
```

## Best Practices

1. **Sử dụng Signals & Slots** thay vì direct function calls
2. **Keep UI code separate** từ business logic
3. **Use meaningful object names** cho custom styling
4. **Handle errors gracefully** với try-except và user feedback
5. **Log all important actions** để debugging
6. **Test UI responsiveness** ở nhiều kích thước màn hình
7. **Use layouts** thay vì fixed positioning

## Contributing

Khi thêm UI components mới:
1. Tạo file riêng trong `ui/` folder
2. Export từ `ui/__init__.py`
3. Follow existing naming conventions
4. Add docstrings (Vietnamese)
5. Update documentation
6. Test trên nhiều platforms

---

**Version:** 1.0.0
**Last Updated:** 2025-01-05
**Author:** Veo3 Development Team
