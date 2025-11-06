"""
Tệp cấu hình chính cho ứng dụng Google Veo Video Generator
Chứa các hằng số, đường dẫn và cài đặt API
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

# ===== CẤU HÌNH API =====

# API Key từ biến môi trường
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')

# URL endpoint API (nếu cần)
API_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta'

# Timeout cho các request (giây)
REQUEST_TIMEOUT = int(os.getenv('DEFAULT_TIMEOUT', '300'))

# Số lượng request đồng thời tối đa
MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', '3'))


# ===== CẤU HÌNH MÔ HÌNH VEO =====

# Danh sách các model Veo có sẵn
AVAILABLE_MODELS = [
    'veo-2.0',
    'veo-1.0',
    'veo-lite'
]

# Model mặc định
DEFAULT_MODEL = 'veo-2.0'


# ===== CẤU HÌNH VIDEO =====

# Các độ phân giải hỗ trợ (width x height)
RESOLUTIONS = {
    '720p': (1280, 720),
    '1080p': (1920, 1080),
    '4K': (3840, 2160),
    '480p': (854, 480),
}

# Độ phân giải mặc định
DEFAULT_RESOLUTION = '1080p'

# Các tỷ lệ khung hình hỗ trợ
ASPECT_RATIOS = {
    '16:9': (16, 9),
    '9:16': (9, 16),     # Vertical (cho điện thoại)
    '1:1': (1, 1),       # Vuông (cho social media)
    '4:3': (4, 3),       # Truyền thống
    '21:9': (21, 9),     # Ultrawide
}

# Tỷ lệ khung hình mặc định
DEFAULT_ASPECT_RATIO = '16:9'

# Độ dài video (giây)
VIDEO_DURATION_RANGE = {
    'min': 2,
    'max': 60,
    'default': 5
}

# Số frame mỗi giây
FPS_OPTIONS = [24, 30, 60]
DEFAULT_FPS = 30


# ===== CẤU HÌNH ĐƯỜNG DẪN =====

# Thư mục gốc của dự án
BASE_DIR = Path(__file__).parent.parent

# Thư mục lưu video đầu ra
OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'outputs')
OUTPUT_DIR = BASE_DIR / OUTPUT_FOLDER

# Thư mục tạm để xử lý
TEMP_FOLDER = os.getenv('TEMP_FOLDER', 'temp')
TEMP_DIR = BASE_DIR / TEMP_FOLDER

# Thư mục assets (icon, hình ảnh UI)
ASSETS_DIR = BASE_DIR / 'assets'

# Thư mục log
LOG_DIR = BASE_DIR / 'logs'

# Tạo các thư mục nếu chưa tồn tại
def ensure_directories():
    """Đảm bảo tất cả các thư mục cần thiết đều tồn tại"""
    for directory in [OUTPUT_DIR, TEMP_DIR, ASSETS_DIR, LOG_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


# ===== CẤU HÌNH LOGGING =====

# Cấp độ log
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Định dạng log
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Tên file log
LOG_FILE = 'veo_app.log'

# Đường dẫn file log đầy đủ
LOG_FILE_PATH = LOG_DIR / LOG_FILE

# Kích thước tối đa của file log (bytes) - 10MB
MAX_LOG_SIZE = 10 * 1024 * 1024

# Số lượng file log backup
LOG_BACKUP_COUNT = 5


# ===== CẤU HÌNH UI =====

# Kích thước cửa sổ mặc định
WINDOW_SIZE = {
    'width': 1200,
    'height': 800,
    'min_width': 800,
    'min_height': 600
}

# Tiêu đề ứng dụng
APP_TITLE = 'Google Veo Video Generator'

# Phiên bản ứng dụng
APP_VERSION = '1.0.0'


# ===== CẤU HÌNH NÂNG CAO =====

# Số lần thử lại khi request thất bại
MAX_RETRIES = 3

# Thời gian chờ giữa các lần thử lại (giây)
RETRY_DELAY = 2

# Kích thước buffer tải xuống (bytes)
DOWNLOAD_BUFFER_SIZE = 8192

# Kiểm tra API key
def validate_api_key():
    """Kiểm tra xem API key đã được cấu hình chưa"""
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == 'your_api_key_here':
        return False
    return True


# Khởi tạo các thư mục khi import module
ensure_directories()


# ===== EXPORT =====
__all__ = [
    'GOOGLE_API_KEY',
    'API_BASE_URL',
    'REQUEST_TIMEOUT',
    'MAX_CONCURRENT_REQUESTS',
    'AVAILABLE_MODELS',
    'DEFAULT_MODEL',
    'RESOLUTIONS',
    'DEFAULT_RESOLUTION',
    'ASPECT_RATIOS',
    'DEFAULT_ASPECT_RATIO',
    'VIDEO_DURATION_RANGE',
    'FPS_OPTIONS',
    'DEFAULT_FPS',
    'OUTPUT_DIR',
    'TEMP_DIR',
    'ASSETS_DIR',
    'LOG_DIR',
    'LOG_LEVEL',
    'LOG_FORMAT',
    'LOG_FILE_PATH',
    'MAX_LOG_SIZE',
    'LOG_BACKUP_COUNT',
    'WINDOW_SIZE',
    'APP_TITLE',
    'APP_VERSION',
    'MAX_RETRIES',
    'RETRY_DELAY',
    'DOWNLOAD_BUFFER_SIZE',
    'validate_api_key',
    'ensure_directories'
]
