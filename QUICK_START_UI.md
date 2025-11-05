# Quick Start - Veo3 UI

## Test giao diện mới

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Chạy UI Demo

```bash
python demo_ui.py
```

## Tính năng UI mới

### ✨ Main Window Features

- **Menu Bar**: File, Edit, View, Help với keyboard shortcuts
- **Tool Bar**: Quick actions (New, Open, Save, Settings, Refresh)
- **4 Tabs**:
  - 🎬 Text to Video
  - 🖼️ Image to Video
  - ✏️ Scene Manager
  - 🗄️ History & Library
- **Sidebar** (Right):
  - Model Selection (Veo 2.0, 3.0, 3.1, 3.1-Fast)
  - Video Settings (Aspect Ratio, Resolution, Duration, FPS)
  - Reference Images List
  - Quick Actions (Generate, Reset)
- **Status Bar**: Status message + API status indicator

### 🎨 Dark Theme

- Modern dark theme với accent color cyan (#14ffec)
- Smooth hover effects
- Custom button styles (Primary, Secondary, Danger)
- Responsive design

### 📁 Files Created

```
ui/
├── main_window.py    # Main window implementation (600+ lines)
├── styles.py         # Dark theme stylesheet
└── __init__.py       # Module exports

demo_ui.py            # UI demo launcher
UI_DOCUMENTATION.md   # Complete UI documentation
```

## Screenshots

### Main Window Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ File  Edit  View  Help                              [🔌 API]   │
├─────────────────────────────────────────────────────────────────┤
│ 📁 New  📂 Open  💾 Save  │  ⚙️ Settings  🔄 Refresh           │
├──────────────────────────────────┬──────────────────────────────┤
│                                  │  ┌─ Settings Panel ────────┐│
│  [🎬 Text to Video]              │  │ 🔌 Model Selection      ││
│   🖼️ Image to Video              │  │   [Veo 3.1 ▼]          ││
│   ✏️ Scene Manager                │  │                         ││
│   🗄️ History & Library            │  │ ⚙️ Video Settings      ││
│                                  │  │   Aspect Ratio: 16:9    ││
│                                  │  │   Resolution: 1080p     ││
│                                  │  │   Duration: 5 sec       ││
│  [Tab Content Area]              │  │   FPS: 30              ││
│                                  │  │                         ││
│                                  │  │ 🖼️ Reference Images     ││
│                                  │  │   [List...]            ││
│                                  │  │   [➕ Add]  [➖ Remove] ││
│                                  │  │                         ││
│                                  │  │ ▶️ Quick Actions        ││
│                                  │  │   [🎬 Generate Video]  ││
│                                  │  │   [🔄 Reset Settings]  ││
│                                  │  └─────────────────────────┘│
├──────────────────────────────────┴──────────────────────────────┤
│ Ready                                    🔴 API: Not configured │
└─────────────────────────────────────────────────────────────────┘
```

## Usage Examples

### Example 1: Set API Status

```python
from ui import MainWindow

window = MainWindow()
window.set_api_status(True, "Connected")  # Green indicator
window.show()
```

### Example 2: Get Current Settings

```python
settings = window.get_current_settings()
print(settings)
# {
#     'model': 'Veo 3.1',
#     'aspect_ratio': '16:9',
#     'resolution': '1080p',
#     'duration': 5,
#     'fps': 30
# }
```

### Example 3: Connect to Signals

```python
def on_api_changed(connected, message):
    print(f"API: {message}")

window.api_status_changed.connect(on_api_changed)
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New Project |
| `Ctrl+O` | Open Project |
| `Ctrl+S` | Save |
| `Ctrl+E` | Export Video |
| `Ctrl+B` | Toggle Sidebar |
| `F1` | Help |

## Customization

### Change Accent Color

```python
from ui import DARK_THEME

custom_theme = DARK_THEME.replace('#14ffec', '#ff6b6b')
window.setStyleSheet(custom_theme)
```

### Add Custom Tab

```python
from PyQt6.QtWidgets import QWidget

custom_tab = QWidget()
# ... setup custom tab ...
window.tabs.addTab(custom_tab, "Custom Tab")
```

## Next Steps

1. ✅ UI structure complete
2. 🔲 Implement tab content widgets
3. 🔲 Connect to API client
4. 🔲 Add video preview player
5. 🔲 Implement project management
6. 🔲 Add template library

## Documentation

- **Full UI Docs**: [UI_DOCUMENTATION.md](UI_DOCUMENTATION.md)
- **Database Docs**: [DATABASE_DOCUMENTATION.md](DATABASE_DOCUMENTATION.md)
- **Main README**: [README.md](README.md)

---

**🎉 UI is ready to use! Run `python demo_ui.py` to see it in action.**
