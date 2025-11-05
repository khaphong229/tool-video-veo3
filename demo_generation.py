"""
Demo để test video generation system
Test TextToVideoGenerator với mock API
"""

import sys
import asyncio
from pathlib import Path

from core import (
    TextToVideoGenerator,
    create_client,
    get_database,
    GenerationStatus
)
from config import settings
from utils import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def progress_callback(progress: int, status: str):
    """
    Progress callback function

    Args:
        progress: Progress percentage (0-100)
        status: Status message
    """
    # Create progress bar
    bar_length = 40
    filled = int(bar_length * progress / 100)
    bar = '█' * filled + '░' * (bar_length - filled)

    # Print progress
    print(f"\r[{bar}] {progress:3d}% - {status}", end='', flush=True)

    if progress == 100:
        print()  # New line when complete


async def test_generation():
    """Test video generation"""

    print("="*70)
    print("TEXT TO VIDEO GENERATION TEST")
    print("="*70)
    print()

    # Initialize components
    print("📋 Initializing...")
    api_client = create_client(settings.GOOGLE_API_KEY or "test_key")
    db_manager = get_database()

    # Create generator
    generator = TextToVideoGenerator(api_client, db_manager)

    print("✅ Generator initialized")
    print()

    # Test parameters
    prompt = "A serene mountain landscape at sunset, with golden light reflecting off a calm lake"
    model = "veo-2.0"
    config = {
        'aspect_ratio': '16:9',
        'duration': 5,
        'resolution': '1080p',
        'negative_prompt': 'blurry, low quality',
        'seed': 42,
        'enable_audio': False
    }

    print("📝 Generation Parameters:")
    print(f"   Prompt: {prompt}")
    print(f"   Model: {model}")
    print(f"   Config: {config}")
    print()

    # Start generation
    print("🎬 Starting generation...")
    print()

    try:
        result = await generator.generate_video(
            prompt=prompt,
            model=model,
            config=config,
            progress_callback=progress_callback
        )

        print()
        print("="*70)
        print("GENERATION RESULT")
        print("="*70)

        if result['status'] == 'success':
            print(f"✅ Status: {result['status']}")
            print(f"📁 Video Path: {result['video_path']}")
            print(f"🆔 Operation ID: {result['operation_id']}")
            print(f"⏱️  Duration: {result['duration']:.2f}s")
            print(f"🗄️  Generation ID: {result.get('generation_id', 'N/A')}")
        else:
            print(f"❌ Status: {result['status']}")
            print(f"⚠️  Error: {result.get('error', 'Unknown error')}")
            print(f"🏷️  Error Type: {result.get('error_type', 'unknown')}")

        print("="*70)
        print()

        return result

    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        logger.error(f"Generation failed: {e}", exc_info=True)
        return None


async def test_multiple_generations():
    """Test multiple generations"""

    print("="*70)
    print("MULTIPLE GENERATIONS TEST")
    print("="*70)
    print()

    api_client = create_client("test_key")
    db_manager = get_database()
    generator = TextToVideoGenerator(api_client, db_manager)

    # Test prompts
    prompts = [
        "A cat playing with a red ball in a sunny garden",
        "Ocean waves crashing on a rocky beach at dawn",
        "City street at night with neon lights reflecting on wet pavement"
    ]

    config = {
        'aspect_ratio': '16:9',
        'duration': 5,
        'resolution': '720p',
        'enable_audio': False
    }

    results = []

    for i, prompt in enumerate(prompts, 1):
        print(f"\n📹 Generation {i}/{len(prompts)}")
        print(f"   Prompt: {prompt[:50]}...")
        print()

        async def numbered_progress(progress, status):
            await progress_callback(progress, f"[{i}] {status}")

        result = await generator.generate_video(
            prompt=prompt,
            model="veo-2.0",
            config=config,
            progress_callback=numbered_progress
        )

        results.append(result)

        # Small delay between generations
        await asyncio.sleep(1)

    # Summary
    print()
    print("="*70)
    print("SUMMARY")
    print("="*70)

    successful = sum(1 for r in results if r['status'] == 'success')
    failed = len(results) - successful

    print(f"Total: {len(results)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print()

    return results


async def test_error_handling():
    """Test error handling"""

    print("="*70)
    print("ERROR HANDLING TEST")
    print("="*70)
    print()

    api_client = create_client("test_key")
    generator = TextToVideoGenerator(api_client)

    # Test 1: Empty prompt
    print("🔬 Test 1: Empty prompt")
    try:
        result = await generator.generate_video(
            prompt="",
            model="veo-2.0",
            config={'aspect_ratio': '16:9', 'duration': 5, 'resolution': '1080p'},
            progress_callback=progress_callback
        )
        print(f"   Result: {result['status']}")
    except Exception as e:
        print(f"   ✅ Caught error: {type(e).__name__}: {e}")

    print()

    # Test 2: Invalid duration
    print("🔬 Test 2: Invalid duration")
    try:
        result = await generator.generate_video(
            prompt="Test",
            model="veo-2.0",
            config={'aspect_ratio': '16:9', 'duration': 999, 'resolution': '1080p'},
            progress_callback=progress_callback
        )
        print(f"   Result: {result['status']}")
    except Exception as e:
        print(f"   ✅ Caught error: {type(e).__name__}: {e}")

    print()

    # Test 3: Too long prompt
    print("🔬 Test 3: Too long prompt (>2000 chars)")
    try:
        long_prompt = "A" * 2001
        result = await generator.generate_video(
            prompt=long_prompt,
            model="veo-2.0",
            config={'aspect_ratio': '16:9', 'duration': 5, 'resolution': '1080p'},
            progress_callback=progress_callback
        )
        print(f"   Result: {result['status']}")
    except Exception as e:
        print(f"   ✅ Caught error: {type(e).__name__}: {e}")

    print()
    print("="*70)


def main():
    """Main function"""

    print("\n" + "🎬" * 35)
    print("VIDEO GENERATION SYSTEM DEMO")
    print("🎬" * 35 + "\n")

    # Menu
    print("Choose a test:")
    print("  1. Single generation test")
    print("  2. Multiple generations test")
    print("  3. Error handling test")
    print("  4. All tests")
    print()

    choice = input("Enter choice (1-4) [1]: ").strip() or "1"

    print()

    if choice == "1":
        asyncio.run(test_generation())
    elif choice == "2":
        asyncio.run(test_multiple_generations())
    elif choice == "3":
        asyncio.run(test_error_handling())
    elif choice == "4":
        asyncio.run(test_generation())
        print("\n")
        asyncio.run(test_multiple_generations())
        print("\n")
        asyncio.run(test_error_handling())
    else:
        print("Invalid choice")
        return

    print("\n" + "✅" * 35)
    print("DEMO COMPLETE")
    print("✅" * 35 + "\n")


if __name__ == '__main__':
    main()
