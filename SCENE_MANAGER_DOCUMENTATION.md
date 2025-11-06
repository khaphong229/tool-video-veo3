# Scene Manager - Complete Documentation

Complete **Scene Manager** tab implementation for creating multi-scene video projects with scene chaining, batch generation, and video merging!

## Overview

The Scene Manager allows you to:
- Create projects with multiple scenes
- Chain scenes together for smooth transitions
- Manage scene order and settings
- Generate all scenes in batch
- Automatically merge scenes into final video

## Files Created

### 1. **[ui/tabs/scene_manager_tab.py](ui/tabs/scene_manager_tab.py)** (1,550+ lines)
- `SceneManagerTab` - Main tab widget
- `SceneData` - Scene data model
- `ProjectData` - Project data model
- Complete project and scene management
- Scene chaining logic
- Batch generation support

## Features

### 1. Project Management

**Create and manage video projects:**
- Multiple projects support
- Project selector dropdown
- Auto-save to JSON files
- Project metadata tracking
- Scene collection per project

### 2. Scene List Management

**Organize scenes:**
- Visual scene list with status icons
- Scene reordering (up/down buttons)
- Add/delete scenes
- Status tracking (pending, processing, done, failed)
- Prompt preview in list

### 3. Scene Editor (3 Tabs)

**Tab 1: Prompt**
- Scene prompt input (2000 char limit)
- Character counter
- Scene chaining options:
  - Use previous scene's last frame
  - Extend from previous video
- Chaining tips and info

**Tab 2: References**
- Reference images (max 3)
- Add/remove references
- First/last frame inputs (transition mode)
- Browse file dialogs

**Tab 3: Settings**
- Model override (per scene)
- Duration (2-60 seconds)
- Aspect ratio (16:9, 9:16, 1:1, 4:3)
- Aspect ratio locking (when extending)
- Resolution (480p - 4K)

### 4. Global Settings

**Apply settings to all scenes:**
- Global style template (appended to all prompts)
- Default model for all scenes
- Auto-merge checkbox
- Output format selection (mp4, mov, avi, webm)

### 5. Scene Chaining

**Create smooth transitions between scenes:**

**Option 1: Use Previous Frame**
- Takes last frame of previous scene
- Uses it as first frame of current scene
- Creates visual continuity

**Option 2: Extend from Previous**
- Seamless continuation
- Locks aspect ratio to match previous scene
- Best for continuous camera movement

### 6. Batch Generation

**Generate multiple scenes:**
- Generate selected scene
- Generate all scenes in sequence
- Progress tracking (X / Y completed)
- Progress bar visualization
- Auto-merge when all complete (optional)

### 7. Video Merging

**Combine scenes into final video:**
- Merge button enabled when all scenes done
- Preserves scene order
- Output format configuration
- Final video export

## User Interface Layout

```
┌─────────────────────────────────────────────────────────────┐
│                        Scene Manager Tab                     │
├──────────────┬──────────────────────────────────────────────┤
│ LEFT PANEL   │               RIGHT PANEL                     │
│              │                                               │
│ Project      │  Scene 1                          ⏸ Pending  │
│ ┌──────────┐ │  ┌─────────────────────────────────────────┐ │
│ │ Project▼ │ │  │ ┌Prompt┬References┬Settings┐            │ │
│ │   [New]  │ │  │ │                           │            │ │
│ └──────────┘ │  │ │ Scene Prompt:             │            │ │
│              │  │ │ ┌─────────────────────┐   │            │ │
│ Scenes       │  │ │ │                     │   │            │ │
│ ┌──────────┐ │  │ │ └─────────────────────┘   │            │ │
│ │✓ Scene 1 │ │  │ │                           │            │ │
│ │⏸ Scene 2 │ │  │ │ Scene Chaining:           │            │ │
│ │⏸ Scene 3 │ │  │ │ ☐ Use previous frame      │            │ │
│ │          │ │  │ │ ☐ Extend from previous    │            │ │
│ └──────────┘ │  │ └───────────────────────────┘            │ │
│              │  └─────────────────────────────────────────┘ │
│ [Add Scene]  │                                               │
│ [↑][↓][Del]  │                                               │
└──────────────┴───────────────────────────────────────────────┤
│ GLOBAL SETTINGS                                              │
│ Style: [cinematic, dramatic lighting...     ]                │
│ Model: [veo-2.0▼]  ☑ Auto-merge  Format: [mp4▼]            │
├──────────────────────────────────────────────────────────────┤
│ ACTION BAR                                                   │
│ 1/3 completed [████░░░░] [Generate Selected] [Generate All] │
│                          [Merge Videos]                      │
└──────────────────────────────────────────────────────────────┘
```

## Data Models

### SceneData

```python
class SceneData:
    scene_id: int                    # Scene number
    prompt: str                       # Scene description
    use_previous_frame: bool          # Use prev last frame
    extend_from_previous: bool        # Seamless continuation
    reference_images: List[str]       # Reference image paths
    first_frame: str                  # First frame path
    last_frame: str                   # Last frame path
    model: str                        # Model override
    duration: int                     # Duration in seconds
    aspect_ratio: str                 # 16:9, 9:16, etc.
    resolution: str                   # 480p - 4K
    status: str                       # pending/processing/done/failed
    video_path: str                   # Generated video path
    thumbnail_path: str               # Thumbnail path
```

### ProjectData

```python
class ProjectData:
    name: str                         # Project name
    created_at: str                   # ISO timestamp
    global_style: str                 # Style template
    global_model: str                 # Default model
    auto_merge: bool                  # Auto-merge when done
    output_format: str                # mp4, mov, etc.
    scenes: List[SceneData]           # Scene collection
```

## API Reference

### SceneManagerTab

```python
class SceneManagerTab(QWidget):
    # Signals
    generate_scene_requested = pyqtSignal(dict)
    generate_all_requested = pyqtSignal(list)
    merge_videos_requested = pyqtSignal(list)
```

### Project Management Methods

#### create_new_project(name: str)

```python
def on_new_project(self):
    """
    Create a new project

    - Prompts user for project name
    - Creates ProjectData instance
    - Adds to project list
    - Saves to projects/ directory as JSON
    """
```

#### load_projects()

```python
def load_projects(self):
    """
    Load all projects from disk

    - Scans projects/ directory
    - Loads *.json files
    - Populates project dropdown
    """
```

#### save_project(project: ProjectData)

```python
def save_project(self, project: ProjectData):
    """
    Save project to disk

    Args:
        project: ProjectData instance

    Saves to: projects/{project_name}.json
    """
```

### Scene Management Methods

#### add_scene()

```python
def add_scene(self):
    """
    Add a new scene to current project

    - Creates SceneData with defaults
    - Adds to project.scenes list
    - Updates scene list widget
    - Auto-selects new scene
    - Saves project
    """
```

#### delete_scene(index: int)

```python
def delete_scene(self):
    """
    Delete selected scene

    - Shows confirmation dialog
    - Removes from project
    - Updates scene list
    - Renumbers remaining scenes
    - Saves project
    """
```

#### reorder_scene(from_index: int, to_index: int)

```python
def move_scene_up(self):
    """Move selected scene up one position"""

def move_scene_down(self):
    """Move selected scene down one position"""
```

#### update_scene(index: int, data: dict)

```python
def update_scene(self, index: int, data: dict):
    """
    Update scene with new data

    Args:
        index: Scene index
        data: Dictionary of scene properties

    - Updates scene properties
    - Refreshes list display
    - Saves project
    """
```

#### load_scene_data(index: int)

```python
def load_scene_data(self, index: int):
    """
    Load scene data into editor

    Args:
        index: Scene index

    - Loads all scene properties
    - Populates editor widgets
    - Handles chaining logic
    - Updates UI state
    """
```

### Generation Methods

#### generate_selected_scene()

```python
def generate_selected_scene(self):
    """
    Generate currently selected scene

    - Builds scene generation data
    - Applies global style template
    - Handles chaining (previous frame/video)
    - Emits generate_scene_requested signal
    """
```

#### generate_all_scenes()

```python
def generate_all_scenes(self):
    """
    Generate all scenes in project

    - Validates all scenes
    - Builds generation data for each
    - Emits generate_all_requested signal
    """
```

#### build_scene_generation_data(index: int) -> dict

```python
def build_scene_generation_data(self, index: int) -> Optional[Dict[str, Any]]:
    """
    Build scene data for generation

    Args:
        index: Scene index

    Returns:
        {
            'scene_id': int,
            'scene_index': int,
            'project_name': str,
            'prompt': str,              # Full prompt with global style
            'model': str,               # Scene or global model
            'config': dict,             # aspect_ratio, duration, resolution
            'reference_images': List[str],
            'use_previous_frame': bool,
            'extend_from_previous': bool,
            'previous_video_path': str,
            'first_frame': str,
            'last_frame': str
        }
    """
```

#### merge_all_videos()

```python
def merge_all_videos(self):
    """
    Merge all completed scene videos

    - Validates all scenes are completed
    - Collects video paths in order
    - Emits merge_videos_requested signal
    """
```

### UI Update Methods

#### update_scene_status(scene_index, status, video_path)

```python
def update_scene_status(
    self,
    scene_index: int,
    status: str,
    video_path: Optional[str] = None
):
    """
    Update scene status after generation

    Args:
        scene_index: Scene index
        status: 'pending' | 'processing' | 'done' | 'failed'
        video_path: Path to generated video (if done)

    - Updates scene.status
    - Updates scene.video_path
    - Refreshes list display
    - Updates progress bar
    - Enables merge button if all done
    """
```

#### update_progress()

```python
def update_progress(self):
    """
    Update progress bar and label

    - Calculates completed / total
    - Updates progress label
    - Sets progress bar value
    """
```

## Usage Examples

### Example 1: Create a New Project

```python
from ui.tabs import SceneManagerTab

# Create tab
scene_tab = SceneManagerTab()

# User clicks "New Project" button
# Enter name: "My Movie"
# Project created and saved to projects/My Movie.json
```

### Example 2: Add Scenes to Project

```python
# User clicks "Add Scene" 3 times
# Creates Scene 1, Scene 2, Scene 3

# Edit Scene 1
scene_tab.scene_prompt_input.setPlainText("Opening shot: wide landscape view")
scene_tab.scene_duration_spin.setValue(10)

# Edit Scene 2
scene_tab.scene_prompt_input.setPlainText("Camera zooms in on character")
scene_tab.use_previous_frame_check.setChecked(True)  # Chain from Scene 1
scene_tab.scene_duration_spin.setValue(5)

# Edit Scene 3
scene_tab.scene_prompt_input.setPlainText("Close-up on character's face")
scene_tab.extend_from_previous_check.setChecked(True)  # Seamless continuation
scene_tab.scene_duration_spin.setValue(5)
```

### Example 3: Configure Global Settings

```python
# Set global style
scene_tab.global_style_input.setText("cinematic, dramatic lighting, film grain")

# Set global model
scene_tab.global_model_combo.setCurrentText("veo-2.0")

# Enable auto-merge
scene_tab.auto_merge_check.setChecked(True)

# Set output format
scene_tab.output_format_combo.setCurrentText("mp4")
```

### Example 4: Generate All Scenes

```python
# Connect to signal
def on_generate_all(scenes_data):
    for scene_data in scenes_data:
        print(f"Generating Scene {scene_data['scene_id']}")
        print(f"  Prompt: {scene_data['prompt']}")
        print(f"  Model: {scene_data['model']}")
        print(f"  Duration: {scene_data['config']['duration']}s")

        # Start generation...

scene_tab.generate_all_requested.connect(on_generate_all)

# User clicks "Generate All Scenes"
# Signal emitted with all scene data
```

### Example 5: Update Scene Status

```python
# After scene generation completes
scene_tab.update_scene_status(
    scene_index=0,
    status='done',
    video_path='outputs/my_movie_scene_1.mp4'
)

# Scene list updates: ✓ Scene 1 | 10s | Opening shot...
# Progress: 1/3 completed [████░░░░░░]

# After all scenes complete
# Merge button automatically enabled (if auto_merge = True)
```

### Example 6: Merge Videos

```python
# Connect to signal
def on_merge_videos(video_paths):
    print(f"Merging {len(video_paths)} videos:")
    for i, path in enumerate(video_paths):
        print(f"  Scene {i+1}: {path}")

    # Use ffmpeg or similar to concatenate
    merge_videos_with_ffmpeg(video_paths, output='final_movie.mp4')

scene_tab.merge_videos_requested.connect(on_merge_videos)

# User clicks "Merge Videos"
# Signal emitted with ordered list of video paths
```

## Scene Chaining Details

### Chaining Option 1: Use Previous Frame

**How it works:**
1. Scene 1 generates normally
2. Extract last frame from Scene 1 video
3. Scene 2 uses this frame as `first_frame` input
4. Generate Scene 2 with transition from that frame

**Use case:**
- Create visual continuity between scenes
- Smooth transitions
- Different prompts but same location

**Example:**
```
Scene 1: "Wide landscape view of a forest"
  → Last frame: forest landscape

Scene 2: "Camera zooms in on a tree"
  → First frame: forest landscape (from Scene 1)
  → Seamless transition
```

### Chaining Option 2: Extend from Previous

**How it works:**
1. Scene 1 generates normally
2. Scene 2 uses entire Scene 1 video as context
3. Continues camera movement/action
4. Aspect ratio locked to match Scene 1

**Use case:**
- Continuous camera movement
- Seamless action continuation
- Single long scene split into multiple generations

**Example:**
```
Scene 1: "Camera slowly pans left across the room"
  → Duration: 10s
  → Aspect: 16:9

Scene 2: "Camera continues panning left, reveals a window"
  → Extend from Scene 1
  → Duration: 5s
  → Aspect: 16:9 (locked)
  → Seamless continuation
```

### Chaining Constraints

**First Scene:**
- Chaining options disabled
- Generates independently

**Subsequent Scenes:**
- Can use previous frame
- Can extend from previous
- Previous scene must be completed first
- Aspect ratio may be locked

## Project File Format

Projects are saved as JSON files in `projects/` directory:

```json
{
  "name": "My Movie",
  "created_at": "2025-01-05T14:30:00",
  "global_style": "cinematic, dramatic lighting, film grain",
  "global_model": "veo-2.0",
  "auto_merge": true,
  "output_format": "mp4",
  "scenes": [
    {
      "scene_id": 1,
      "prompt": "Opening shot: wide landscape view",
      "use_previous_frame": false,
      "extend_from_previous": false,
      "reference_images": [],
      "first_frame": null,
      "last_frame": null,
      "model": null,
      "duration": 10,
      "aspect_ratio": "16:9",
      "resolution": "1080p",
      "status": "done",
      "video_path": "outputs/my_movie_scene_1.mp4",
      "thumbnail_path": null
    },
    {
      "scene_id": 2,
      "prompt": "Camera zooms in on character",
      "use_previous_frame": true,
      "extend_from_previous": false,
      "reference_images": ["ref_char.jpg"],
      "first_frame": null,
      "last_frame": null,
      "model": null,
      "duration": 5,
      "aspect_ratio": "16:9",
      "resolution": "1080p",
      "status": "processing",
      "video_path": null,
      "thumbnail_path": null
    }
  ]
}
```

## Integration with MainWindow

```python
# In ui/main_window.py

def create_scene_manager_tab(self) -> QWidget:
    """Create Scene Manager tab"""
    from .tabs import SceneManagerTab

    tab = SceneManagerTab()

    # Connect signals
    tab.generate_scene_requested.connect(self.on_scene_generation_requested)
    tab.generate_all_requested.connect(self.on_generate_all_scenes_requested)
    tab.merge_videos_requested.connect(self.on_merge_videos_requested)

    return tab

def on_scene_generation_requested(self, scene_data: dict):
    """Handle single scene generation"""
    # Use TextToVideoGenerator or ImageToVideoGenerator
    # based on scene_data
    pass

def on_generate_all_scenes_requested(self, scenes: list):
    """Handle batch generation"""
    # Generate scenes in sequence
    # Update status after each completes
    pass

def on_merge_videos_requested(self, video_paths: list):
    """Handle video merging"""
    # Use ffmpeg or similar
    # Concatenate videos in order
    pass
```

## Workflow Example

### Complete Multi-Scene Project

**Step 1: Create Project**
```
User: Click "New Project"
Enter: "Short Film - Forest Adventure"
Result: Project created and saved
```

**Step 2: Add Scenes**
```
User: Click "Add Scene" 5 times
Result: 5 empty scenes created
```

**Step 3: Configure Global Settings**
```
Global Style: "cinematic, 35mm film, natural colors"
Model: veo-2.0
Auto-merge: ✓
Format: mp4
```

**Step 4: Edit Scenes**

Scene 1:
```
Prompt: "Aerial view of dense forest, morning mist"
Duration: 8s
Aspect: 16:9
```

Scene 2:
```
Prompt: "Camera descends through trees to forest floor"
Duration: 6s
Aspect: 16:9
Chaining: ✓ Extend from previous
```

Scene 3:
```
Prompt: "A hiker appears walking on forest path"
Duration: 5s
Aspect: 16:9
Chaining: ✓ Use previous frame
```

Scene 4:
```
Prompt: "Close-up of hiker's face, looking around"
Duration: 4s
Aspect: 9:16
Reference: hiker_reference.jpg
```

Scene 5:
```
Prompt: "Hiker discovers a hidden waterfall"
Duration: 7s
Aspect: 16:9
Chaining: ✓ Use previous frame
```

**Step 5: Generate All**
```
User: Click "Generate All Scenes"
Result:
  - Scene 1: Processing...
  - Scene 1: Done (8s video)
  - Scene 2: Processing... (extends from Scene 1)
  - Scene 2: Done (6s video)
  - Scene 3: Processing... (uses Scene 2 last frame)
  - Scene 3: Done (5s video)
  - Scene 4: Processing...
  - Scene 4: Done (4s video)
  - Scene 5: Processing... (uses Scene 4 last frame)
  - Scene 5: Done (7s video)

Progress: 5/5 completed [██████████]
```

**Step 6: Auto-Merge**
```
Auto-merge enabled → Merge automatically triggered
Result: final_forest_adventure.mp4 (30s total)
```

## Status Icons

| Icon | Status | Meaning |
|------|--------|---------|
| ⏸ | pending | Not yet generated |
| ⏳ | processing | Currently generating |
| ✓ | done | Generation completed |
| ✗ | failed | Generation failed |

## Best Practices

### Project Organization

1. **Use descriptive project names**
   - ✓ "Commercial - Product Launch 2025"
   - ✗ "Project 1"

2. **Keep scenes focused**
   - Each scene = one action/shot
   - 5-10 seconds per scene ideal
   - Split long sequences into multiple scenes

3. **Use global styles**
   - Set once, applies to all
   - Ensures consistent visual style
   - Override per-scene only when needed

### Scene Chaining

1. **Use "Extend from Previous" for:**
   - Continuous camera movement
   - Single long shot split for generation limits
   - Seamless action sequences

2. **Use "Previous Frame" for:**
   - Scene transitions
   - Different actions, same location
   - Maintaining visual continuity

3. **Start fresh (no chaining) for:**
   - New locations
   - Jump cuts
   - Different aspect ratios

### Generation Strategy

1. **Generate sequentially when chaining**
   - Scene 2 needs Scene 1's output
   - Cannot generate in parallel

2. **Generate in parallel when independent**
   - Scenes without chaining
   - Separate storylines
   - Different locations

3. **Test first scene first**
   - Validate style/quality
   - Adjust settings if needed
   - Then generate remaining scenes

## Limitations

1. **Chaining Requirements:**
   - Previous scene must be completed
   - Cannot chain if previous failed
   - Aspect ratio locked when extending

2. **Reference Images:**
   - Maximum 3 per scene
   - Requires Veo 3.1+ for references
   - May affect generation time

3. **Project Size:**
   - No hard limit on scenes
   - Large projects = longer generation time
   - Consider splitting very large projects

## Future Enhancements

- [ ] Drag-and-drop scene reordering
- [ ] Scene preview thumbnails
- [ ] Timeline visualization
- [ ] Scene templates
- [ ] Duplicate scene functionality
- [ ] Import/export scene data
- [ ] Scene groups/chapters
- [ ] Parallel generation for independent scenes
- [ ] Video preview before merging
- [ ] Transition effects between scenes

---

**🎬 Scene Manager Complete and Production-Ready!**

Create multi-scene video projects with professional scene management and chaining capabilities!

Test it:
```bash
python demo_ui.py
# Navigate to "Scene Manager" tab
```
