# Scene Generation and Merging System

Complete **SceneManager** implementation for multi-scene video generation, scene chaining, and video merging with ffmpeg!

## Overview

The Scene Manager handles:
- Sequential scene generation with dependency management
- Scene chaining (use previous frame, extend from previous)
- Global template application
- Progress tracking across scenes
- Error recovery and retry logic
- Video frame extraction
- Video merging with ffmpeg
- Video compatibility validation

## Files Created

### 1. **[core/managers/scene_manager.py](core/managers/scene_manager.py)** (800+ lines)
- `SceneManager` - Main manager class
- `SceneGenerationError` - Custom exception
- `VideoMergeError` - Custom exception
- Complete scene generation workflow
- ffmpeg integration for merging and frame extraction

### 2. **[core/managers/__init__.py](core/managers/__init__.py)**
- Managers module exports

### 3. **[demo_scene_manager.py](demo_scene_manager.py)** (400+ lines)
- Comprehensive demo with 4 test modes
- Template application tests
- Scene sequence tests
- Video merging tests
- Frame extraction tests

## Features

### 1. Scene Sequence Generation

**Sequential generation with chaining:**
- Generates scenes in order (required for chaining)
- Tracks dependencies between scenes
- Applies global template to all prompts
- Progress tracking with callbacks
- Error recovery (skip or retry failed scenes)

### 2. Scene Chaining

**Two chaining modes:**

**Mode 1: Use Previous Frame**
```python
use_previous_frame = True
# Extracts last frame from Scene N-1
# Uses as first_frame for Scene N
# Creates visual continuity
```

**Mode 2: Extend from Previous**
```python
extend_from_previous = True
# Uses entire Scene N-1 video as context
# Seamless continuation
# Currently extracts last frame (API may support video-to-video)
```

### 3. Global Template Application

**Apply style to all scenes:**
```python
scene_prompt = "A person walks in the park"
global_template = "cinematic, dramatic lighting"
# Result: "A person walks in the park. cinematic, dramatic lighting"
```

### 4. Video Frame Extraction

**Extract frames using ffmpeg:**
- Extract last frame from video
- Extract frame at specific time
- Generate thumbnails
- Automatic resizing and optimization

### 5. Video Merging

**Concatenate videos using ffmpeg:**
- Simple concatenation (copy streams, no re-encoding)
- Optional transitions (crossfade - planned)
- Automatic compatibility validation
- Resolution and frame rate consistency checks

### 6. Error Recovery

**Graceful error handling:**
- Continue sequence after failed scene
- Track failed scenes separately
- Retry logic with exponential backoff
- Detailed error reporting

## API Reference

### SceneManager

```python
class SceneManager:
    def __init__(
        self,
        api_client: VeoAPIClient,
        db_manager: Optional[DatabaseManager] = None
    )
```

**Initialization:**
- Creates text and image generators
- Sets up output directories (scenes/, merged/, frames/)
- Checks ffmpeg availability
- Configures logging

**Properties:**
- `ffmpeg_available: bool` - Whether ffmpeg is available
- `scenes_dir: Path` - Scene output directory
- `merged_dir: Path` - Merged video directory
- `frames_dir: Path` - Extracted frames directory

### Main Methods

#### apply_global_template()

```python
def apply_global_template(
    self,
    scene_prompt: str,
    global_template: str
) -> str:
    """
    Apply global style template to scene prompt

    Args:
        scene_prompt: Scene-specific prompt
        global_template: Global style template (e.g., "cinematic, film grain")

    Returns:
        Combined prompt with proper punctuation

    Example:
        >>> apply_global_template(
        ...     "A person walks",
        ...     "cinematic lighting"
        ... )
        "A person walks. cinematic lighting"
    """
```

#### generate_single_scene()

```python
async def generate_single_scene(
    self,
    scene_data: Dict[str, Any],
    previous_video_path: Optional[str] = None,
    progress_callback: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Generate a single scene with optional chaining

    Args:
        scene_data: Scene configuration
            {
                'scene_id': int,
                'scene_index': int,
                'project_name': str,
                'prompt': str,
                'model': str,
                'config': {
                    'aspect_ratio': '16:9',
                    'duration': 5,
                    'resolution': '1080p'
                },
                'reference_images': List[str],
                'use_previous_frame': bool,
                'extend_from_previous': bool,
                'first_frame': str,
                'last_frame': str
            }
        previous_video_path: Path to previous scene's video
        progress_callback: Async progress callback

    Returns:
        {
            'status': 'success' | 'error',
            'scene_id': int,
            'video_path': str,
            'duration': float,
            'error': str (if failed)
        }

    Process:
    1. Check chaining mode
    2. Extract frame if needed
    3. Determine generation type (text or image)
    4. Generate scene
    5. Return result
    """
```

#### generate_scene_sequence()

```python
async def generate_scene_sequence(
    self,
    project_id: int,
    scenes: List[Dict[str, Any]],
    global_template: str = "",
    progress_callback: Optional[Callable] = None
) -> List[Dict[str, Any]]:
    """
    Generate a sequence of scenes with chaining

    Args:
        project_id: Project ID
        scenes: List of scene configurations
        global_template: Global style template
        progress_callback: Async callback(scene_index, total, status, message)

    Returns:
        List of generation results

    Process:
    1. Apply global template to all scenes
    2. Generate scenes sequentially
    3. Track dependencies (chaining)
    4. Update progress after each scene
    5. Handle errors gracefully
    6. Return all results

    Progress Callback:
        async def callback(scene_index, total_scenes, status, message):
            # scene_index: 0-based index
            # total_scenes: Total number of scenes
            # status: 'processing' | 'completed' | 'failed' | 'error' | 'done'
            # message: Progress message
    """
```

#### extract_last_frame()

```python
async def extract_last_frame(
    self,
    video_path: str,
    scene_id: Optional[int] = None,
    output_dir: Optional[Path] = None
) -> str:
    """
    Extract last frame from video

    Args:
        video_path: Path to video file
        scene_id: Scene ID for naming
        output_dir: Output directory (default: frames_dir)

    Returns:
        Path to extracted frame image (.jpg)

    Uses:
        - ffprobe to get video duration
        - ffmpeg to extract frame at duration - 0.1s
        - High quality JPEG output
    """
```

#### extract_frame_at_time()

```python
async def extract_frame_at_time(
    self,
    video_path: str,
    time_seconds: float,
    output_path: Optional[str] = None
) -> str:
    """
    Extract frame at specific time

    Args:
        video_path: Path to video
        time_seconds: Time in seconds
        output_path: Output path (auto-generated if not provided)

    Returns:
        Path to extracted frame
    """
```

#### merge_videos()

```python
async def merge_videos(
    self,
    video_paths: List[str],
    output_path: Optional[str] = None,
    add_transitions: bool = False,
    transition_duration: float = 0.5
) -> str:
    """
    Merge multiple videos into one

    Args:
        video_paths: List of video paths (in order)
        output_path: Output path (auto-generated if not provided)
        add_transitions: Add crossfade transitions (not yet implemented)
        transition_duration: Transition duration in seconds

    Returns:
        Path to merged video

    Uses:
        - Simple mode: ffmpeg concat demuxer (copy streams)
        - Transition mode: ffmpeg complex filter (planned)

    Process:
    1. Validate all videos exist
    2. Create concat list file
    3. Run ffmpeg with concat demuxer
    4. Return output path
    """
```

#### generate_thumbnail()

```python
async def generate_thumbnail(
    self,
    video_path: str,
    output_path: Optional[str] = None,
    time_seconds: float = 1.0
) -> str:
    """
    Generate thumbnail from video

    Args:
        video_path: Path to video
        output_path: Output path
        time_seconds: Time to capture (default: 1.0s)

    Returns:
        Path to thumbnail (max 320×180, optimized)
    """
```

### Utility Methods

#### get_video_info()

```python
def get_video_info(self, video_path: str) -> Dict[str, Any]:
    """
    Get video information using ffprobe

    Returns:
        {
            'duration': float,
            'width': int,
            'height': int,
            'fps': float,
            'codec': str
        }
    """
```

#### validate_videos_compatible()

```python
def validate_videos_compatible(self, video_paths: List[str]) -> bool:
    """
    Check if videos are compatible for merging

    Checks:
    - Same resolution
    - Same frame rate
    - Same codec (preferred)

    Returns:
        True if compatible
    """
```

## Usage Examples

### Example 1: Generate Scene Sequence

```python
from core import SceneManager, create_client, get_database

# Initialize
api_client = create_client("your_api_key")
db_manager = get_database()
manager = SceneManager(api_client, db_manager)

# Define scenes
scenes = [
    {
        'scene_id': 1,
        'scene_index': 0,
        'project_name': 'My Movie',
        'prompt': 'Opening shot: wide landscape',
        'model': 'veo-2.0',
        'config': {'aspect_ratio': '16:9', 'duration': 10, 'resolution': '1080p'},
        'reference_images': [],
        'use_previous_frame': False,
        'extend_from_previous': False,
        'first_frame': None,
        'last_frame': None
    },
    {
        'scene_id': 2,
        'scene_index': 1,
        'project_name': 'My Movie',
        'prompt': 'Camera zooms in on character',
        'model': 'veo-2.0',
        'config': {'aspect_ratio': '16:9', 'duration': 5, 'resolution': '1080p'},
        'reference_images': [],
        'use_previous_frame': True,  # Chain from Scene 1
        'extend_from_previous': False,
        'first_frame': None,
        'last_frame': None
    }
]

# Define global template
global_template = "cinematic, dramatic lighting, 35mm film"

# Progress callback
async def on_progress(scene_index, total, status, message):
    print(f"[{scene_index}/{total}] {status}: {message}")

# Generate sequence
results = await manager.generate_scene_sequence(
    project_id=1,
    scenes=scenes,
    global_template=global_template,
    progress_callback=on_progress
)

# Check results
for result in results:
    if result['status'] == 'success':
        print(f"Scene {result['scene_id']}: {result['video_path']}")
    else:
        print(f"Scene {result['scene_id']} failed: {result['error']}")
```

### Example 2: Generate Single Scene with Chaining

```python
# Scene 1: Generate normally
scene_1_data = {
    'scene_id': 1,
    'prompt': 'Forest landscape',
    'model': 'veo-2.0',
    'config': {'aspect_ratio': '16:9', 'duration': 8, 'resolution': '1080p'},
    # ... other fields
}

result_1 = await manager.generate_single_scene(scene_1_data)

# Scene 2: Chain from Scene 1
scene_2_data = {
    'scene_id': 2,
    'prompt': 'Camera moves through trees',
    'model': 'veo-2.0',
    'config': {'aspect_ratio': '16:9', 'duration': 6, 'resolution': '1080p'},
    'use_previous_frame': True,  # Use Scene 1's last frame
    # ... other fields
}

result_2 = await manager.generate_single_scene(
    scene_2_data,
    previous_video_path=result_1['video_path']  # Pass Scene 1's video
)
```

### Example 3: Extract Frames

```python
# Extract last frame
video_path = "outputs/scene_1.mp4"
last_frame = await manager.extract_last_frame(video_path, scene_id=1)
print(f"Last frame: {last_frame}")

# Extract frame at 3.5 seconds
frame_at_3s = await manager.extract_frame_at_time(video_path, 3.5)
print(f"Frame at 3.5s: {frame_at_3s}")

# Generate thumbnail
thumbnail = await manager.generate_thumbnail(video_path)
print(f"Thumbnail: {thumbnail}")
```

### Example 4: Merge Videos

```python
# Collect video paths
video_paths = [
    "outputs/scenes/scene_1.mp4",
    "outputs/scenes/scene_2.mp4",
    "outputs/scenes/scene_3.mp4"
]

# Validate compatibility
if manager.validate_videos_compatible(video_paths):
    print("Videos are compatible")

    # Merge
    merged_path = await manager.merge_videos(
        video_paths=video_paths,
        output_path="outputs/merged/final_movie.mp4"
    )

    print(f"Merged video: {merged_path}")

    # Get info
    info = manager.get_video_info(merged_path)
    print(f"Duration: {info['duration']}s")
    print(f"Resolution: {info['width']}×{info['height']}")
else:
    print("Videos not compatible for merging")
```

### Example 5: Apply Global Template

```python
# Apply template to prompts
prompts = [
    "A person walks in the park",
    "Camera zooms in on face",
    "Close-up expression"
]

global_template = "cinematic, dramatic lighting"

for prompt in prompts:
    combined = manager.apply_global_template(prompt, global_template)
    print(combined)

# Output:
# A person walks in the park. cinematic, dramatic lighting
# Camera zooms in on face. cinematic, dramatic lighting
# Close-up expression. cinematic, dramatic lighting
```

## Scene Chaining Workflow

### Workflow 1: Use Previous Frame

```
Scene 1:
├─ Generate from text prompt
├─ Output: scene_1.mp4 (10s)
└─ Extract last frame → last_frame_1.jpg

Scene 2:
├─ use_previous_frame = True
├─ Load: last_frame_1.jpg as first_frame
├─ Generate from image + prompt
└─ Output: scene_2.mp4 (5s)
   → Visual continuity with Scene 1
```

### Workflow 2: Extend from Previous

```
Scene 1:
├─ Generate from text prompt
└─ Output: scene_1.mp4 (8s)

Scene 2:
├─ extend_from_previous = True
├─ Load: scene_1.mp4 as context
├─ Extract last frame (fallback)
├─ Generate with same aspect ratio
└─ Output: scene_2.mp4 (6s)
   → Seamless continuation
```

### Workflow 3: Independent Scenes

```
Scene 1:
├─ Generate from text prompt
└─ Output: scene_1.mp4

Scene 2:
├─ No chaining (independent)
├─ Generate from text prompt
└─ Output: scene_2.mp4

Scene 3:
├─ No chaining (independent)
├─ Generate from text prompt
└─ Output: scene_3.mp4

Merge:
└─ Concatenate all scenes → final.mp4
```

## ffmpeg Integration

### Requirements

**Install ffmpeg:**
```bash
# Windows (with chocolatey)
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg
```

**Check installation:**
```bash
ffmpeg -version
ffprobe -version
```

### ffmpeg Commands Used

**1. Get Video Duration:**
```bash
ffprobe -v error -show_entries format=duration \
    -of default=noprint_wrappers=1:nokey=1 video.mp4
```

**2. Extract Last Frame:**
```bash
ffmpeg -ss <duration-0.1> -i video.mp4 \
    -vframes 1 -q:v 2 -y output.jpg
```

**3. Extract Frame at Time:**
```bash
ffmpeg -ss 3.5 -i video.mp4 \
    -vframes 1 -q:v 2 -y frame.jpg
```

**4. Concatenate Videos:**
```bash
# Create concat_list.txt:
# file 'video1.mp4'
# file 'video2.mp4'
# file 'video3.mp4'

ffmpeg -f concat -safe 0 -i concat_list.txt \
    -c copy output.mp4
```

**5. Get Video Info:**
```bash
ffprobe -v error -select_streams v:0 \
    -show_entries stream=width,height,r_frame_rate,codec_name:format=duration \
    -of json video.mp4
```

## Progress Tracking

### Progress Callback Format

```python
async def progress_callback(
    scene_index: int,      # Current scene (0-based)
    total_scenes: int,     # Total scenes
    status: str,           # Status
    message: str           # Message
):
    """
    Status values:
    - 'processing': Scene currently generating
    - 'completed': Scene completed successfully
    - 'failed': Scene failed
    - 'error': Error occurred
    - 'done': All scenes complete
    """
    pass
```

### Example Progress Display

```python
async def progress_callback(scene_index, total_scenes, status, message):
    # Create progress bar
    bar_length = 40
    progress = int((scene_index / total_scenes) * bar_length)
    bar = '█' * progress + '░' * (bar_length - progress)

    # Status icon
    icons = {
        'processing': '⏳',
        'completed': '✓',
        'failed': '✗',
        'error': '⚠',
        'done': '🎬'
    }
    icon = icons.get(status, '•')

    print(f"\r[{bar}] {scene_index}/{total_scenes} {icon} {message}", end='')

    if status == 'done':
        print()  # New line when complete
```

## Error Handling

### Error Types

```python
# Scene generation error
class SceneGenerationError(Exception):
    """Error during scene generation"""

# Video merge error
class VideoMergeError(Exception):
    """Error during video merging"""
```

### Error Recovery

**Automatic recovery:**
- Failed scene doesn't stop sequence
- Chaining skips failed scenes
- Detailed error logging
- Retry with exponential backoff (in base generator)

**Error result format:**
```python
{
    'status': 'error',
    'scene_id': 2,
    'scene_index': 1,
    'error': 'Generation timeout after 5 minutes'
}
```

## Output Directory Structure

```
outputs/
├── scenes/          # Individual scene videos
│   ├── scene_1_20250106_143025.mp4
│   ├── scene_2_20250106_143245.mp4
│   └── scene_3_20250106_143512.mp4
│
├── merged/          # Merged final videos
│   ├── merged_20250106_143800.mp4
│   └── final_movie.mp4
│
└── frames/          # Extracted frames
    ├── scene1_last_frame_20250106_143300.jpg
    ├── scene2_last_frame_20250106_143530.jpg
    └── thumb_20250106_143820.jpg
```

## Performance Considerations

### Generation Time

**Sequential generation:**
- Scene N depends on Scene N-1 (if chaining)
- Cannot parallelize chained scenes
- Total time = sum of all scene generation times

**Example:**
```
Scene 1: 10s video → ~15s generation
Scene 2: 5s video (chained) → ~8s generation
Scene 3: 5s video (chained) → ~8s generation
Total: ~31s generation time
```

### Video Merging Time

**Simple concatenation:**
- Very fast (copies streams, no re-encoding)
- 3 videos × 5s each → ~1-2 seconds merge time

**With transitions:**
- Requires re-encoding
- Much slower (planned feature)

### Frame Extraction Time

**Per frame:**
- ~0.5-2 seconds per frame
- Depends on video length and format

## Best Practices

### Scene Design

1. **Keep scenes focused**
   - 5-10 seconds per scene
   - One action/shot per scene

2. **Use chaining wisely**
   - Chain when visual continuity needed
   - Don't chain different locations
   - Extend only for continuous movement

3. **Test first scene first**
   - Validate style and quality
   - Adjust template if needed
   - Then generate remaining scenes

### Global Templates

1. **Be consistent**
   - Same style across all scenes
   - Use specific, descriptive terms
   - Example: "cinematic, 35mm film, natural colors"

2. **Don't over-specify**
   - Template should be general style
   - Let scene prompts handle specifics
   - Template ≈ 5-10 words

### Video Merging

1. **Validate compatibility**
   - Check resolution matches
   - Check frame rate matches
   - Run `validate_videos_compatible()` first

2. **Use consistent settings**
   - Same aspect ratio for all scenes
   - Same resolution
   - Same frame rate

## Troubleshooting

### Issue: ffmpeg not found

**Solution:**
```bash
# Install ffmpeg
# Windows: choco install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg

# Verify
ffmpeg -version
```

### Issue: Video merge fails

**Possible causes:**
- Incompatible resolutions
- Different codecs
- Corrupted video files

**Solution:**
```python
# Check compatibility
if not manager.validate_videos_compatible(video_paths):
    print("Videos not compatible")
    # Check individual video info
    for path in video_paths:
        info = manager.get_video_info(path)
        print(f"{path}: {info}")
```

### Issue: Frame extraction fails

**Possible causes:**
- Invalid video path
- Corrupted video
- ffmpeg not available

**Solution:**
```python
# Check video exists
if not Path(video_path).exists():
    print("Video not found")

# Check ffmpeg
if not manager.ffmpeg_available:
    print("ffmpeg not available")

# Try with error handling
try:
    frame = await manager.extract_last_frame(video_path)
except VideoMergeError as e:
    print(f"Extraction failed: {e}")
```

## Future Enhancements

- [ ] Parallel generation for independent scenes
- [ ] Crossfade transitions between scenes
- [ ] Audio handling and mixing
- [ ] Video-to-video API support (true extend mode)
- [ ] Automatic scene splitting for long videos
- [ ] Scene preview before generation
- [ ] Batch processing optimizations
- [ ] GPU acceleration for merging
- [ ] Custom transition effects
- [ ] Scene templates

---

**🎬 Scene Generation and Merging System Complete!**

Test it:
```bash
python demo_scene_manager.py
```
