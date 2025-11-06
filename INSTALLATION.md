# Installation Guide - Veo3 Video Generator

Complete installation guide for the Veo3 Video Generator application.

## System Requirements

- **Python**: 3.8 or higher (tested on Python 3.13)
- **Operating System**: Windows, macOS, or Linux
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: 500MB for dependencies + storage for generated videos

## Quick Installation

### 1. Clone or Download Repository

```bash
cd E:\Workspace\Tool\Veo3
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages:
- PyQt6 (GUI framework)
- google-genai (Google AI SDK - optional)
- python-dotenv (environment variables)
- aiohttp (async HTTP client)
- Pillow (image processing)
- requests (HTTP library)

### 3. Verify Installation

```bash
python -c "from core import ImageToVideoGenerator, TextToVideoGenerator; print('Installation successful!')"
```

## Dependencies Overview

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| PyQt6 | >=6.7.0 | GUI framework for desktop interface |
| Pillow | >=10.3.0 | Image processing (resize, crop, compress) |
| aiohttp | >=3.9.5 | Async HTTP client for API calls |
| python-dotenv | >=1.0.1 | Environment variable management |
| requests | >=2.31.0 | HTTP requests library |

### Optional Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| google-genai | >=1.48.0 | Google Generative AI SDK (app works without it in mock mode) |

### Development Tools (Not Required)

| Package | Version | Notes |
|---------|---------|-------|
| PyQt6-tools | 6.4.2.3.3 | Qt Designer, etc. (has version conflicts with PyQt6 6.7+, commented out) |

## Common Installation Issues

### Issue 1: PIL Package Not Found

**Error:**
```
ERROR: Could not find a version that satisfies the requirement PIL
```

**Solution:**
The package name is `Pillow`, not `PIL`:
```bash
pip install Pillow
```

Import in code uses `PIL`:
```python
from PIL import Image  # Correct
```

### Issue 2: PyQt6-tools Version Conflict

**Error:**
```
ERROR: Cannot install PyQt6>=6.7.0 and PyQt6-tools==6.4.2.3.3
```

**Solution:**
PyQt6-tools is not required to run the application. It's commented out in requirements.txt. The app works perfectly without it.

If you need Qt Designer, install it separately:
```bash
pip install PyQt6-tools==6.4.2.3.3
```

This will downgrade PyQt6 to 6.4.2, which is still compatible with the app.

### Issue 3: google-genai Not Found

**Error:**
```
ERROR: No matching distribution found for google-genai
```

**Solution:**
The app works in **mock mode** without google-genai. Just skip it:
```bash
# Install without google-genai
pip install PyQt6 Pillow aiohttp python-dotenv requests
```

The app will automatically detect and use mock mode for testing.

### Issue 4: Dependency Conflicts with pyppeteer

**Warning:**
```
pyppeteer 2.0.0 requires websockets<11.0, but you have websockets 15.0.1
```

**Solution:**
This warning is safe to ignore. pyppeteer is not used by Veo3. If it causes issues, you can uninstall it:
```bash
pip uninstall pyppeteer
```

## Environment Configuration

### 1. Create .env File

```bash
cp .env.example .env
```

### 2. Edit .env

```env
# Google Veo API Configuration
GOOGLE_API_KEY=your_api_key_here

# Optional: Output directory
OUTPUT_DIR=outputs

# Optional: Database path
DATABASE_PATH=veo_generator.db
```

### 3. Get API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and paste into `.env` file

**Note:** The app works in mock mode without a valid API key for testing purposes.

## Verify Installation

### Quick Test

```bash
python -c "from core import ImageToVideoGenerator, TextToVideoGenerator; print('OK')"
```

### Detailed Test

```python
# test_installation.py
import sys

print("Testing Veo3 Video Generator installation...")
print(f"Python version: {sys.version}")
print()

# Test imports
try:
    from core import ImageToVideoGenerator, TextToVideoGenerator
    print("✅ Core generators: OK")
except ImportError as e:
    print(f"❌ Core generators: FAILED - {e}")

try:
    from PyQt6.QtWidgets import QApplication
    print("✅ PyQt6: OK")
except ImportError as e:
    print(f"❌ PyQt6: FAILED - {e}")

try:
    from PIL import Image
    print("✅ Pillow (PIL): OK")
except ImportError as e:
    print(f"❌ Pillow: FAILED - {e}")

try:
    import aiohttp
    print("✅ aiohttp: OK")
except ImportError as e:
    print(f"❌ aiohttp: FAILED - {e}")

try:
    import google.genai
    print("✅ google-genai: OK")
except ImportError:
    print("⚠️  google-genai: Not installed (app will use mock mode)")

print()
print("Installation verification complete!")
```

Run with:
```bash
python test_installation.py
```

## Running the Application

### 1. Text to Video Demo

```bash
python demo_generation.py
```

Choose from:
1. Single generation test
2. Multiple generations test
3. Error handling test
4. All tests

### 2. Image to Video Demo

```bash
python demo_image_generation.py
```

Choose from:
1. Single image generation
2. Generation with reference images
3. Transition mode (first→last frame)
4. Image preprocessing test
5. Validation test
6. All tests

### 3. Full UI Application

```bash
python demo_ui.py
```

This launches the complete GUI with:
- Text to Video tab
- Image to Video tab
- Scene Manager tab (placeholder)
- History & Library tab (placeholder)

## Updating Dependencies

### Update All Packages

```bash
pip install --upgrade -r requirements.txt
```

### Update Specific Package

```bash
pip install --upgrade PyQt6
pip install --upgrade Pillow
```

### Check Outdated Packages

```bash
pip list --outdated
```

## Uninstallation

### Remove All Dependencies

```bash
pip uninstall -r requirements.txt -y
```

### Remove Application Files

```bash
# Windows
rmdir /s /q E:\Workspace\Tool\Veo3

# Linux/macOS
rm -rf /path/to/Veo3
```

## Virtual Environment (Recommended)

### Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

### Install in Virtual Environment

```bash
(venv) pip install -r requirements.txt
```

### Deactivate

```bash
deactivate
```

## Troubleshooting

### Import Errors

If you see import errors:

1. **Check Python version**:
   ```bash
   python --version
   # Should be 3.8 or higher
   ```

2. **Verify pip installation**:
   ```bash
   pip --version
   ```

3. **Reinstall dependencies**:
   ```bash
   pip install --force-reinstall -r requirements.txt
   ```

### Path Issues

If modules are not found:

1. **Check PYTHONPATH**:
   ```bash
   echo %PYTHONPATH%  # Windows
   echo $PYTHONPATH   # Linux/macOS
   ```

2. **Run from project root**:
   ```bash
   cd E:\Workspace\Tool\Veo3
   python demo_ui.py
   ```

### Permission Issues

If you get permission errors:

1. **Use --user flag**:
   ```bash
   pip install --user -r requirements.txt
   ```

2. **Or use virtual environment** (recommended)

### Module Not Found

If a specific module is not found:

1. **Check if installed**:
   ```bash
   pip show PyQt6
   pip show Pillow
   ```

2. **Reinstall specific package**:
   ```bash
   pip install --force-reinstall PyQt6
   ```

## Platform-Specific Notes

### Windows

- Use `python` command (not `python3`)
- Paths use backslashes: `E:\Workspace\Tool\Veo3`
- PowerShell may require execution policy change for venv

### macOS

- May need to install system dependencies:
  ```bash
  brew install python-tk
  ```

### Linux

- Install system packages:
  ```bash
  sudo apt-get install python3-pyqt6 python3-pil
  ```

## Performance Optimization

### GPU Acceleration

Currently not utilized, but future versions may support:
- CUDA for NVIDIA GPUs
- Metal for Apple Silicon
- DirectML for Windows

### Memory Management

- Close other applications during video generation
- Monitor memory usage with Task Manager/Activity Monitor
- Increase virtual memory if needed

## Next Steps

After installation:

1. **Read Documentation**:
   - [README.md](README.md) - Project overview
   - [TEXT_TO_VIDEO_QUICK_START.md](TEXT_TO_VIDEO_QUICK_START.md) - Text to Video guide
   - [IMAGE_TO_VIDEO_QUICK_START.md](IMAGE_TO_VIDEO_QUICK_START.md) - Image to Video guide
   - [GENERATION_DOCUMENTATION.md](GENERATION_DOCUMENTATION.md) - Generation system details

2. **Run Demos**:
   ```bash
   python demo_generation.py      # Text to Video
   python demo_image_generation.py # Image to Video
   python demo_ui.py               # Full UI
   ```

3. **Configure API Key** (optional):
   - Edit `.env` file
   - Add Google AI API key
   - Test connection in Settings dialog

4. **Start Creating Videos**!

## Support

For issues or questions:

1. Check documentation in `*.md` files
2. Review code comments in source files
3. Check error logs in `logs/` directory
4. Open an issue on GitHub (if applicable)

---

**Installation complete! You're ready to start generating videos with Veo3.** 🎉
