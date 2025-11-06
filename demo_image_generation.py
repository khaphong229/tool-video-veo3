"""
Demo for testing Image to Video generation system
Test ImageToVideoGenerator with mock API and real image processing
"""

import sys
import asyncio
from pathlib import Path

from core import (
    ImageToVideoGenerator,
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


async def test_single_image_generation():
    """Test single image to video generation"""

    print("="*70)
    print("SINGLE IMAGE TO VIDEO GENERATION TEST")
    print("="*70)
    print()

    # Initialize components
    print("📋 Initializing...")
    api_client = create_client(settings.GOOGLE_API_KEY or "test_key")
    db_manager = get_database()

    # Create generator
    generator = ImageToVideoGenerator(api_client, db_manager)

    print("✅ Generator initialized")
    print()

    # Create test image path (you'll need to provide a real image)
    test_image = Path("test_assets/sample_image.jpg")

    if not test_image.exists():
        print(f"⚠️  Test image not found: {test_image}")
        print("Please create test_assets/ folder and add sample_image.jpg")
        print()

        # Create a simple test image
        print("Creating a test image for demonstration...")
        test_image.parent.mkdir(exist_ok=True)

        from PIL import Image
        import random

        # Create a random gradient image
        img = Image.new('RGB', (1920, 1080))
        pixels = img.load()
        for x in range(img.width):
            for y in range(img.height):
                r = int((x / img.width) * 255)
                g = int((y / img.height) * 255)
                b = random.randint(100, 200)
                pixels[x, y] = (r, g, b)

        img.save(test_image)
        print(f"✅ Test image created: {test_image}")
        print()

    # Test parameters
    prompt = "Slow camera zoom in with cinematic lighting"
    model = "veo-2.0"
    config = {
        'aspect_ratio': '16:9',
        'duration': 5,
        'resolution': '1080p',
        'negative_prompt': 'blurry, shaky',
        'enable_audio': False
    }

    print("📝 Generation Parameters:")
    print(f"   Image: {test_image}")
    print(f"   Prompt: {prompt}")
    print(f"   Model: {model}")
    print(f"   Config: {config}")
    print()

    # Start generation
    print("🎬 Starting generation...")
    print()

    try:
        result = await generator.generate_from_image(
            image_path=str(test_image),
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


async def test_reference_images():
    """Test generation with reference images"""

    print("="*70)
    print("GENERATION WITH REFERENCE IMAGES TEST")
    print("="*70)
    print()

    api_client = create_client("test_key")
    db_manager = get_database()
    generator = ImageToVideoGenerator(api_client, db_manager)

    # Create test images
    test_image = Path("test_assets/sample_image.jpg")
    ref1 = Path("test_assets/ref1.jpg")
    ref2 = Path("test_assets/ref2.jpg")

    # Create test images if they don't exist
    from PIL import Image
    for img_path in [test_image, ref1, ref2]:
        if not img_path.exists():
            img_path.parent.mkdir(exist_ok=True)
            img = Image.new('RGB', (1920, 1080), color=(100, 150, 200))
            img.save(img_path)
            print(f"Created test image: {img_path}")

    print()
    print("📝 Generation Parameters:")
    print(f"   Source Image: {test_image}")
    print(f"   Reference Images: {ref1}, {ref2}")
    print(f"   Model: veo-3.1 (required for references)")
    print()

    # Generate
    print("🎬 Starting generation with references...")
    print()

    result = await generator.generate_from_image(
        image_path=str(test_image),
        prompt="Cinematic animation with dramatic style",
        model="veo-3.1",
        config={
            'aspect_ratio': '16:9',
            'duration': 8,
            'resolution': '1080p'
        },
        reference_images=[str(ref1), str(ref2)],
        progress_callback=progress_callback
    )

    print()
    print("="*70)
    print("RESULT")
    print("="*70)
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Video: {result['video_path']}")
    else:
        print(f"Error: {result.get('error')}")
    print("="*70)
    print()

    return result


async def test_transition_mode():
    """Test transition mode with first and last frames"""

    print("="*70)
    print("TRANSITION MODE TEST")
    print("="*70)
    print()

    api_client = create_client("test_key")
    db_manager = get_database()
    generator = ImageToVideoGenerator(api_client, db_manager)

    # Create test images
    first_frame = Path("test_assets/frame_first.jpg")
    last_frame = Path("test_assets/frame_last.jpg")

    # Create test images if they don't exist
    from PIL import Image, ImageDraw
    for img_path, color in [(first_frame, (255, 100, 100)), (last_frame, (100, 100, 255))]:
        if not img_path.exists():
            img_path.parent.mkdir(exist_ok=True)
            img = Image.new('RGB', (1920, 1080), color=color)

            # Add text
            draw = ImageDraw.Draw(img)
            text = "FIRST" if "first" in img_path.name else "LAST"
            draw.text((960, 540), text, fill=(255, 255, 255))

            img.save(img_path)
            print(f"Created test frame: {img_path}")

    print()
    print("📝 Transition Parameters:")
    print(f"   First Frame: {first_frame}")
    print(f"   Last Frame: {last_frame}")
    print(f"   Prompt: Smooth transition between states")
    print()

    # Generate
    print("🎬 Starting transition generation...")
    print()

    result = await generator.generate_with_frames(
        first_frame_path=str(first_frame),
        last_frame_path=str(last_frame),
        prompt="Smooth transition with gentle morph effect",
        model="veo-2.0",
        config={
            'aspect_ratio': '16:9',
            'duration': 5,
            'resolution': '1080p'
        },
        progress_callback=progress_callback
    )

    print()
    print("="*70)
    print("RESULT")
    print("="*70)
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Video: {result['video_path']}")
    else:
        print(f"Error: {result.get('error')}")
    print("="*70)
    print()

    return result


async def test_image_preprocessing():
    """Test image preprocessing capabilities"""

    print("="*70)
    print("IMAGE PREPROCESSING TEST")
    print("="*70)
    print()

    api_client = create_client("test_key")
    generator = ImageToVideoGenerator(api_client)

    # Create test images with various formats and sizes
    from PIL import Image
    test_assets = Path("test_assets")
    test_assets.mkdir(exist_ok=True)

    test_cases = [
        ("large_image.jpg", (3840, 2160), "JPEG"),  # 4K image
        ("portrait.png", (1080, 1920), "PNG"),      # Portrait
        ("square.webp", (1080, 1080), "WEBP"),      # Square
        ("wide.jpg", (2560, 1080), "JPEG"),         # Ultra-wide
    ]

    print("Creating test images...")
    for filename, size, format in test_cases:
        img_path = test_assets / filename
        if not img_path.exists():
            img = Image.new('RGB', size, color=(150, 150, 150))
            img.save(img_path, format=format)
            print(f"  ✅ {filename} ({size[0]}×{size[1]}, {format})")

    print()
    print("Testing image preparation...")
    print()

    for filename, original_size, format in test_cases:
        img_path = test_assets / filename

        print(f"📸 Processing: {filename}")
        print(f"   Original: {original_size[0]}×{original_size[1]} ({format})")

        try:
            # Test with different aspect ratios
            for aspect_ratio in ['16:9', '9:16', '1:1']:
                base64_data = generator.prepare_image(str(img_path), aspect_ratio)
                encoded_size = len(base64_data) / 1024  # KB

                print(f"   → {aspect_ratio}: {encoded_size:.1f}KB encoded")

            print(f"   ✅ Success")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        print()

    print("="*70)


async def test_validation():
    """Test input validation"""

    print("="*70)
    print("VALIDATION TEST")
    print("="*70)
    print()

    api_client = create_client("test_key")
    generator = ImageToVideoGenerator(api_client)

    # Test 1: Missing image
    print("🔬 Test 1: Non-existent image")
    try:
        result = await generator.generate_from_image(
            image_path="nonexistent.jpg",
            prompt="Test",
            model="veo-2.0",
            config={'aspect_ratio': '16:9', 'duration': 5, 'resolution': '1080p'}
        )
        print(f"   Result: {result['status']}")
    except Exception as e:
        print(f"   ✅ Caught error: {type(e).__name__}: {e}")

    print()

    # Test 2: Empty prompt
    print("🔬 Test 2: Empty prompt")

    # Create a test image
    test_image = Path("test_assets/sample_image.jpg")
    if not test_image.exists():
        test_image.parent.mkdir(exist_ok=True)
        from PIL import Image
        img = Image.new('RGB', (1920, 1080))
        img.save(test_image)

    try:
        result = await generator.generate_from_image(
            image_path=str(test_image),
            prompt="",
            model="veo-2.0",
            config={'aspect_ratio': '16:9', 'duration': 5, 'resolution': '1080p'}
        )
        print(f"   Result: {result['status']}")
    except Exception as e:
        print(f"   ✅ Caught error: {type(e).__name__}: {e}")

    print()

    # Test 3: Too many reference images
    print("🔬 Test 3: Too many reference images (>3)")
    try:
        result = await generator.generate_from_image(
            image_path=str(test_image),
            prompt="Test",
            model="veo-3.1",
            config={'aspect_ratio': '16:9', 'duration': 5, 'resolution': '1080p'},
            reference_images=["ref1.jpg", "ref2.jpg", "ref3.jpg", "ref4.jpg"]
        )
        print(f"   Result: {result['status']}")
    except Exception as e:
        print(f"   ✅ Caught error: {type(e).__name__}: {e}")

    print()
    print("="*70)


def main():
    """Main function"""

    print("\n" + "🎬" * 35)
    print("IMAGE TO VIDEO GENERATION SYSTEM DEMO")
    print("🎬" * 35 + "\n")

    # Menu
    print("Choose a test:")
    print("  1. Single image generation")
    print("  2. Generation with reference images")
    print("  3. Transition mode (first→last frame)")
    print("  4. Image preprocessing test")
    print("  5. Validation test")
    print("  6. All tests")
    print()

    choice = input("Enter choice (1-6) [1]: ").strip() or "1"

    print()

    if choice == "1":
        asyncio.run(test_single_image_generation())
    elif choice == "2":
        asyncio.run(test_reference_images())
    elif choice == "3":
        asyncio.run(test_transition_mode())
    elif choice == "4":
        asyncio.run(test_image_preprocessing())
    elif choice == "5":
        asyncio.run(test_validation())
    elif choice == "6":
        asyncio.run(test_single_image_generation())
        print("\n")
        asyncio.run(test_reference_images())
        print("\n")
        asyncio.run(test_transition_mode())
        print("\n")
        asyncio.run(test_image_preprocessing())
        print("\n")
        asyncio.run(test_validation())
    else:
        print("Invalid choice")
        return

    print("\n" + "✅" * 35)
    print("DEMO COMPLETE")
    print("✅" * 35 + "\n")


if __name__ == '__main__':
    main()
