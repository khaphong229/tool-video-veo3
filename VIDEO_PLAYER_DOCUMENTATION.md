# Video Player Widget Documentation

## Overview

The `VideoPlayerWidget` is a custom video player component built with PyQt6 multimedia framework. It provides a complete video playback experience with intuitive controls and keyboard shortcuts.

## Features

### Core Playback
- ✅ Play, Pause, Stop controls
- ✅ Seek through video using progress slider
- ✅ Display current time and total duration
- ✅ Auto-play when video loads
- ✅ Loading indicator during buffering

### Controls
- ✅ Play/Pause button with state indication
- ✅ Stop button to reset playback
- ✅ Progress slider for seeking
- ✅ Volume slider (0-100%)
- ✅ Time display (MM:SS or HH:MM:SS format)
- ✅ Download button to save video
- ✅ Fullscreen toggle button

### Keyboard Shortcuts
- **Space**: Play/Pause toggle
- **F**: Toggle fullscreen mode
- **Escape**: Exit fullscreen
- **Left Arrow**: Seek backward 5 seconds
- **Right Arrow**: Seek forward 5 seconds

### Advanced Features
- ✅ Fullscreen mode support
- ✅ Error handling with user notifications
- ✅ Signal-based event system
- ✅ State management (playing, paused, stopped)
- ✅ Video format support (MP4, AVI, MOV, MKV, WEBM, FLV)

## File Structure

```
ui/widgets/
├── __init__.py           # Exports VideoPlayerWidget
└── video_player.py       # Main implementation (600+ lines)

demo_video_player.py      # Interactive demo with playlist
test_video_player.py      # Automated test suite
```

## Usage

### Basic Usage

```python
from PyQt6.QtWidgets import QApplication
from ui.widgets import VideoPlayerWidget

app = QApplication([])

# Create player
player = VideoPlayerWidget()

# Load and play video
player.load_video("path/to/video.mp4")

# Controls
player.play()
player.pause()
player.stop()
player.seek(5000)  # Seek to 5 seconds
player.set_volume(70)  # Set volume to 70%

player.show()
app.exec()
```

### With Signal Connections

```python
from ui.widgets import VideoPlayerWidget

player = VideoPlayerWidget()

# Connect signals
player.video_loaded.connect(lambda path: print(f"Loaded: {path}"))
player.playback_started.connect(lambda: print("Playing"))
player.playback_paused.connect(lambda: print("Paused"))
player.playback_stopped.connect(lambda: print("Stopped"))
player.error_occurred.connect(lambda msg: print(f"Error: {msg}"))

player.load_video("video.mp4")
```

### In a Custom Application

```python
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from ui.widgets import VideoPlayerWidget

class VideoApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Add video player
        self.player = VideoPlayerWidget()
        layout.addWidget(self.player)

        # Connect signals
        self.player.video_loaded.connect(self.on_video_loaded)

    def on_video_loaded(self, path):
        self.setWindowTitle(f"Playing: {path}")
```

## API Reference

### Methods

#### Video Control

```python
load_video(video_path: str)
```
Load a video file. Validates file existence and displays errors if file not found.
- **Parameters**: `video_path` - Absolute or relative path to video file
- **Emits**: `video_loaded` signal
- **Auto-plays**: Video starts playing automatically after loading

```python
play()
```
Start or resume playback.
- **Emits**: `playback_started` signal

```python
pause()
```
Pause playback at current position.
- **Emits**: `playback_paused` signal

```python
stop()
```
Stop playback and reset position to beginning.
- **Emits**: `playback_stopped` signal

```python
toggle_play_pause()
```
Toggle between play and pause states.

#### Seeking

```python
seek(position: int)
```
Seek to specific position.
- **Parameters**: `position` - Position in milliseconds

```python
seek_relative(offset: int)
```
Seek relative to current position.
- **Parameters**: `offset` - Offset in milliseconds (negative for backward)

#### Volume

```python
set_volume(volume: int)
```
Set volume level.
- **Parameters**: `volume` - Volume level (0-100)

#### Fullscreen

```python
toggle_fullscreen()
```
Toggle fullscreen mode.

```python
enter_fullscreen()
```
Enter fullscreen mode.

```python
exit_fullscreen()
```
Exit fullscreen mode.

#### Utility

```python
clear()
```
Clear the player and reset all state.

```python
download_video()
```
Open save dialog to download/copy current video.

#### State Query

```python
is_playing() -> bool
```
Check if video is currently playing.

```python
is_paused() -> bool
```
Check if video is paused.

```python
is_stopped() -> bool
```
Check if video is stopped.

```python
get_duration() -> int
```
Get video duration in milliseconds.

```python
get_position() -> int
```
Get current playback position in milliseconds.

```python
get_current_video_path() -> Optional[str]
```
Get path of currently loaded video.

#### Static Methods

```python
@staticmethod
format_time(milliseconds: int) -> str
```
Format time to MM:SS or HH:MM:SS string.
- **Parameters**: `milliseconds` - Time in milliseconds
- **Returns**: Formatted time string

### Signals

```python
video_loaded = pyqtSignal(str)
```
Emitted when video is successfully loaded.
- **Parameter**: Video file path

```python
playback_started = pyqtSignal()
```
Emitted when playback starts.

```python
playback_paused = pyqtSignal()
```
Emitted when playback pauses.

```python
playback_stopped = pyqtSignal()
```
Emitted when playback stops.

```python
error_occurred = pyqtSignal(str)
```
Emitted when an error occurs.
- **Parameter**: Error message

### Event Handlers

These methods are called automatically by the media player. You typically don't call them directly, but you can override them in subclasses.

```python
on_state_changed(state: QMediaPlayer.PlaybackState)
```
Handle playback state changes.

```python
on_duration_changed(duration: int)
```
Handle duration changes when video loads.

```python
on_position_changed(position: int)
```
Handle position updates during playback.

```python
on_error_occurred(error: QMediaPlayer.Error, error_string: str)
```
Handle media player errors.

### UI Components

```python
video_widget: QVideoWidget
```
The video display area.

```python
media_player: QMediaPlayer
```
The underlying media player backend.

```python
audio_output: QAudioOutput
```
Audio output device.

```python
play_pause_btn: QPushButton
```
Play/Pause button.

```python
stop_btn: QPushButton
```
Stop button.

```python
progress_slider: QSlider
```
Progress/seek slider.

```python
volume_slider: QSlider
```
Volume control slider.

```python
time_label: QLabel
```
Time display (current / total).

```python
download_btn: QPushButton
```
Download video button.

```python
fullscreen_btn: QPushButton
```
Fullscreen toggle button.

```python
loading_label: QLabel
```
Loading indicator overlay.

## Supported Video Formats

The player supports all formats that PyQt6's multimedia framework can handle:

- **MP4** (H.264/H.265)
- **AVI**
- **MOV** (QuickTime)
- **MKV** (Matroska)
- **WEBM**
- **FLV** (Flash Video)

Format support may vary depending on system codecs.

## Testing

### Run Automated Tests

```bash
python test_video_player.py
```

Tests include:
- Component initialization
- UI control presence
- Method availability
- Signal definitions
- Initial state validation
- Volume control
- State query methods
- Time formatting
- Clear functionality

### Run Interactive Demo

```bash
python demo_video_player.py
```

Demo features:
- Load video files via dialog
- Scan outputs/ folder for videos
- Playlist management
- Full player controls testing
- Keyboard shortcuts demonstration

## Integration Examples

### In History Tab

Add video preview to History tab:

```python
from ui.widgets import VideoPlayerWidget

class HistoryTab(QWidget):
    def __init__(self):
        super().__init__()

        # Add player to tab
        self.video_player = VideoPlayerWidget()
        layout.addWidget(self.video_player)

    def on_video_clicked(self, video_id):
        video_data = self.get_video_by_id(video_id)
        video_path = video_data.get('video_path')
        if video_path:
            self.video_player.load_video(video_path)
```

### In Preview Dialog

Create a video preview dialog:

```python
from PyQt6.QtWidgets import QDialog, QVBoxLayout
from ui.widgets import VideoPlayerWidget

class VideoPreviewDialog(QDialog):
    def __init__(self, video_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Video Preview")
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        self.player = VideoPlayerWidget()
        layout.addWidget(self.player)

        self.player.load_video(video_path)

    def closeEvent(self, event):
        self.player.stop()
        super().closeEvent(event)
```

### As Standalone Player

```python
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from ui.widgets import VideoPlayerWidget

class SimplePlayer(QMainWindow):
    def __init__(self, video_path=None):
        super().__init__()
        self.setWindowTitle("Simple Video Player")

        self.player = VideoPlayerWidget()
        self.setCentralWidget(self.player)

        if video_path:
            self.player.load_video(video_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Play video from command line
    video_path = sys.argv[1] if len(sys.argv) > 1 else None
    player = SimplePlayer(video_path)
    player.show()

    sys.exit(app.exec())
```

## Error Handling

The player provides comprehensive error handling:

1. **File Not Found**: Shows error dialog if video file doesn't exist
2. **Codec Errors**: Displays codec/format errors from media player
3. **Playback Errors**: Handles and displays playback failures
4. **Invalid Operations**: Gracefully handles invalid state transitions

All errors emit the `error_occurred` signal and display user-friendly dialogs.

## Performance Notes

- **Hardware Acceleration**: Uses system hardware acceleration when available
- **Memory Efficient**: Streams video from disk, doesn't load entire file
- **Responsive UI**: Progress updates use signals to avoid blocking
- **Seeking**: Fast seeking without re-buffering entire video

## Limitations

1. **Codec Support**: Depends on system-installed codecs
2. **DRM Content**: Cannot play DRM-protected videos
3. **Streaming**: Designed for local files, not optimized for streaming URLs
4. **Thumbnails**: Seeking preview thumbnails not implemented (future feature)

## Future Enhancements

Potential improvements for future versions:

- [ ] Seek preview thumbnails
- [ ] Playback speed control (0.5x, 1x, 1.5x, 2x)
- [ ] Audio track selection
- [ ] Subtitle support
- [ ] Playlist auto-advance
- [ ] Video filters/effects
- [ ] Screenshot capture
- [ ] Loop mode
- [ ] A-B repeat section
- [ ] Picture-in-picture mode

## Troubleshooting

### Video doesn't play

**Check:**
1. File format is supported
2. File exists and is readable
3. Required codecs are installed
4. File isn't corrupted

**Solution:**
```python
# Test with a known-good video file
player.load_video("path/to/sample.mp4")
```

### No audio

**Check:**
1. Volume slider is not at 0
2. System audio is not muted
3. Audio codec is supported

**Solution:**
```python
player.set_volume(70)  # Set volume to 70%
```

### Fullscreen doesn't work

**Issue**: Fullscreen mode only affects video widget, not entire window.

**Workaround**: Use parent window's fullscreen:
```python
self.window().showFullScreen()
```

### Progress slider jumps

**Cause**: Network delay or codec issues.

**Solution**: Use local files or higher quality codecs.

## License

Part of Veo3 Video Generator application.

## Support

For issues or questions:
1. Check this documentation
2. Run test suite: `python test_video_player.py`
3. Try demo: `python demo_video_player.py`
4. Review source code: `ui/widgets/video_player.py`
