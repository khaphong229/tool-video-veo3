"""
Demo for testing Scene Manager
Test multi-scene generation and video merging
"""

import sys
import asyncio
from pathlib import Path

from core import SceneManager, create_client, get_database
from config import settings
from utils import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def progress_callback(scene_index, total_scenes, status, message):
    """
    Progress callback for scene sequence

    Args:
        scene_index: Current scene index (0-based)
        total_scenes: Total number of scenes
        status: Status string
        message: Progress message
    """
    # Create progress bar
    bar_length = 40
    progress = int((scene_index / total_scenes) * bar_length)
    bar = '█' * progress + '░' * (bar_length - progress)

    # Status icon
    status_icon = {
        'processing': '⏳',
        'completed': '✓',
        'failed': '✗',
        'error': '⚠',
        'done': '🎬'
    }.get(status, '•')

    print(f"\r[{bar}] {scene_index}/{total_scenes} {status_icon} {message}", end='', flush=True)

    if status == 'done':
        print()  # New line when complete


async def test_template_application():
    """Test global template application"""

    print("="*70)
    print("GLOBAL TEMPLATE APPLICATION TEST")
    print("="*70)
    print()

    api_client = create_client("test_key")
    manager = SceneManager(api_client)

    # Test cases
    test_cases = [
        {
            'prompt': "A person walks in the park",
            'template': "cinematic, dramatic lighting, film grain",
            'expected': "A person walks in the park. cinematic, dramatic lighting, film grain"
        },
        {
            'prompt': "Camera zooms in on character.",
            'template': "35mm film, natural colors",
            'expected': "Camera zooms in on character. 35mm film, natural colors"
        },
        {
            'prompt': "Sunset over mountains!",
            'template': "",
            'expected': "Sunset over mountains!"
        }
    ]

    for i, case in enumerate(test_cases, 1):
        result = manager.apply_global_template(case['prompt'], case['template'])
        success = result == case['expected']

        print(f"Test {i}: {'✓ PASS' if success else '✗ FAIL'}")
        print(f"  Prompt: '{case['prompt']}'")
        print(f"  Template: '{case['template']}'")
        print(f"  Expected: '{case['expected']}'")
        print(f"  Got: '{result}'")
        print()

    print("="*70)
    print()


async def test_scene_sequence():
    """Test scene sequence generation"""

    print("="*70)
    print("SCENE SEQUENCE GENERATION TEST")
    print("="*70)
    print()

    # Initialize
    print("📋 Initializing...")
    api_client = create_client("test_key")
    db_manager = get_database()
    manager = SceneManager(api_client, db_manager)

    print("✅ SceneManager initialized")
    print(f"   ffmpeg available: {manager.ffmpeg_available}")
    print()

    # Create test scenes
    scenes = [
        {
            'scene_id': 1,
            'scene_index': 0,
            'project_name': 'Test Project',
            'prompt': 'Opening shot: wide landscape view',
            'model': 'veo-2.0',
            'config': {
                'aspect_ratio': '16:9',
                'duration': 5,
                'resolution': '1080p'
            },
            'reference_images': [],
            'use_previous_frame': False,
            'extend_from_previous': False,
            'first_frame': None,
            'last_frame': None
        },
        {
            'scene_id': 2,
            'scene_index': 1,
            'project_name': 'Test Project',
            'prompt': 'Camera zooms in on character',
            'model': 'veo-2.0',
            'config': {
                'aspect_ratio': '16:9',
                'duration': 5,
                'resolution': '1080p'
            },
            'reference_images': [],
            'use_previous_frame': True,  # Chain from Scene 1
            'extend_from_previous': False,
            'first_frame': None,
            'last_frame': None
        },
        {
            'scene_id': 3,
            'scene_index': 2,
            'project_name': 'Test Project',
            'prompt': 'Close-up on character face',
            'model': 'veo-2.0',
            'config': {
                'aspect_ratio': '16:9',
                'duration': 5,
                'resolution': '1080p'
            },
            'reference_images': [],
            'use_previous_frame': False,
            'extend_from_previous': True,  # Extend from Scene 2
            'first_frame': None,
            'last_frame': None
        }
    ]

    global_template = "cinematic, dramatic lighting, film grain"

    print("📝 Test Configuration:")
    print(f"   Scenes: {len(scenes)}")
    print(f"   Global Template: '{global_template}'")
    print()

    # Generate sequence
    print("🎬 Starting scene sequence generation...")
    print()

    results = await manager.generate_scene_sequence(
        project_id=1,
        scenes=scenes,
        global_template=global_template,
        progress_callback=progress_callback
    )

    print()
    print("="*70)
    print("RESULTS")
    print("="*70)

    successful = 0
    failed = 0

    for i, result in enumerate(results, 1):
        status_icon = '✓' if result['status'] == 'success' else '✗'
        print(f"{status_icon} Scene {result.get('scene_id', i)}: {result['status']}")

        if result['status'] == 'success':
            print(f"   Video: {result.get('video_path', 'N/A')}")
            print(f"   Duration: {result.get('duration', 0):.2f}s")
            successful += 1
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
            failed += 1

        print()

    print("="*70)
    print(f"Summary: {successful} successful, {failed} failed")
    print("="*70)
    print()

    return results


async def test_video_merging():
    """Test video merging"""

    print("="*70)
    print("VIDEO MERGING TEST")
    print("="*70)
    print()

    api_client = create_client("test_key")
    manager = SceneManager(api_client)

    if not manager.ffmpeg_available:
        print("⚠️  ffmpeg not available - skipping merge test")
        print()
        return

    # Create test video paths (you'll need actual videos for this)
    test_videos = [
        "outputs/test_video_1.mp4",
        "outputs/test_video_2.mp4",
        "outputs/test_video_3.mp4"
    ]

    # Check if test videos exist
    existing_videos = [v for v in test_videos if Path(v).exists()]

    if not existing_videos:
        print("⚠️  No test videos found - skipping merge test")
        print("   Create test videos at:")
        for v in test_videos:
            print(f"   - {v}")
        print()
        return

    print(f"📹 Found {len(existing_videos)} test videos:")
    for v in existing_videos:
        print(f"   - {Path(v).name}")
    print()

    # Validate compatibility
    print("🔍 Validating video compatibility...")
    compatible = manager.validate_videos_compatible(existing_videos)
    print(f"   Compatible: {compatible}")
    print()

    if not compatible:
        print("⚠️  Videos not compatible - merge may have issues")
        print()

    # Merge videos
    print("🎬 Merging videos...")

    try:
        output_path = await manager.merge_videos(
            video_paths=existing_videos,
            output_path="outputs/merged/test_merge.mp4",
            add_transitions=False
        )

        print(f"✅ Videos merged successfully!")
        print(f"   Output: {output_path}")

        # Get video info
        info = manager.get_video_info(output_path)
        print(f"   Duration: {info['duration']:.2f}s")
        print(f"   Resolution: {info['width']}×{info['height']}")
        print(f"   FPS: {info['fps']:.2f}")
        print(f"   Codec: {info['codec']}")

    except Exception as e:
        print(f"❌ Merge failed: {e}")

    print()
    print("="*70)
    print()


async def test_frame_extraction():
    """Test frame extraction"""

    print("="*70)
    print("FRAME EXTRACTION TEST")
    print("="*70)
    print()

    api_client = create_client("test_key")
    manager = SceneManager(api_client)

    if not manager.ffmpeg_available:
        print("⚠️  ffmpeg not available - skipping extraction test")
        print()
        return

    # Find a test video
    test_video = None
    for video_file in Path("outputs").rglob("*.mp4"):
        test_video = str(video_file)
        break

    if not test_video:
        print("⚠️  No test video found - skipping extraction test")
        print()
        return

    print(f"📹 Test video: {Path(test_video).name}")
    print()

    try:
        # Extract last frame
        print("🖼️  Extracting last frame...")
        last_frame = await manager.extract_last_frame(test_video, scene_id=1)
        print(f"✅ Last frame extracted: {Path(last_frame).name}")
        print()

        # Extract frame at time
        print("🖼️  Extracting frame at 2.0s...")
        frame_at_2s = await manager.extract_frame_at_time(test_video, 2.0)
        print(f"✅ Frame extracted: {Path(frame_at_2s).name}")
        print()

        # Generate thumbnail
        print("🖼️  Generating thumbnail...")
        thumbnail = await manager.generate_thumbnail(test_video)
        print(f"✅ Thumbnail generated: {Path(thumbnail).name}")
        print()

    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        print()

    print("="*70)
    print()


def main():
    """Main function"""

    print("\n" + "🎬" * 35)
    print("SCENE MANAGER SYSTEM DEMO")
    print("🎬" * 35 + "\n")

    # Menu
    print("Choose a test:")
    print("  1. Template application")
    print("  2. Scene sequence generation")
    print("  3. Video merging (requires ffmpeg + test videos)")
    print("  4. Frame extraction (requires ffmpeg + test videos)")
    print("  5. All tests")
    print()

    choice = input("Enter choice (1-5) [1]: ").strip() or "1"

    print()

    if choice == "1":
        asyncio.run(test_template_application())
    elif choice == "2":
        asyncio.run(test_scene_sequence())
    elif choice == "3":
        asyncio.run(test_video_merging())
    elif choice == "4":
        asyncio.run(test_frame_extraction())
    elif choice == "5":
        asyncio.run(test_template_application())
        print("\n")
        asyncio.run(test_scene_sequence())
        print("\n")
        asyncio.run(test_video_merging())
        print("\n")
        asyncio.run(test_frame_extraction())
    else:
        print("Invalid choice")
        return

    print("\n" + "✅" * 35)
    print("DEMO COMPLETE")
    print("✅" * 35 + "\n")


if __name__ == '__main__':
    main()
