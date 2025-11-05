# Google Veo Video Generator

Ứng dụng desktop Python sử dụng PyQt6 để tạo video AI thông qua Google Veo API.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## Tính năng

- ✨ Giao diện đồ họa thân thiện với PyQt6
- 🎬 Tạo video AI từ text prompt
- 🔧 Tùy chỉnh độ phân giải, tỷ lệ khung hình, độ dài video
- 📝 Logging chi tiết
- ⚡ Xử lý bất đồng bộ không chặn UI
- 🔐 Quản lý API key an toàn
- 📊 Hỗ trợ nhiều model Veo
- 💾 **SQLite database** để lưu trữ projects, scenes, video history, và templates
- 🗂️ Quản lý projects với nhiều scenes
- 📋 Template system cho style presets

## Cấu trúc dự án

```
Veo3/
├── config/                 # Cấu hình ứng dụng
│   ├── __init__.py
│   └── settings.py        # Settings và constants
├── core/                  # Logic nghiệp vụ chính
│   ├── __init__.py
│   ├── api_client.py     # Client kết nối Veo API
│   └── database.py       # SQLite database manager
├── ui/                    # Components giao diện (tùy chỉnh)
├── utils/                 # Tiện ích
│   ├── __init__.py
│   └── logger.py         # Hệ thống logging
├── assets/                # Tài nguyên (icons, images)
├── outputs/               # Thư mục lưu video (tự động tạo)
├── logs/                  # Log files (tự động tạo)
├── main.py               # File chạy chính
├── requirements.txt      # Dependencies
├── .env.example         # Template file .env
├── veo_database.db       # SQLite database (tự động tạo)
├── examples_database_usage.py  # Examples sử dụng database
├── test_database.py      # Tests cho database
├── DATABASE_DOCUMENTATION.md   # Tài liệu database chi tiết
└── README.md            # Tài liệu này
```

## Yêu cầu hệ thống

- Python 3.8 trở lên
- Windows / macOS / Linux
- Google AI API Key (đăng ký tại [Google AI Studio](https://makersuite.google.com/app/apikey))

## Cài đặt

### 1. Clone hoặc tải dự án

```bash
git clone <repository-url>
cd Veo3
```

### 2. Tạo môi trường ảo (khuyến nghị)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình API Key

Sao chép file `.env.example` thành `.env`:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Mở file `.env` và điền API key của bạn:

```env
GOOGLE_API_KEY=your_actual_api_key_here
```

## Sử dụng

### Khởi động ứng dụng

```bash
python main.py
```

### Sử dụng giao diện

#### Tab "Tạo Video"

1. **Nhập mô tả video**: Nhập prompt chi tiết mô tả video bạn muốn tạo

   Ví dụ:
   ```
   A serene mountain landscape at sunset, with golden light
   reflecting off a calm lake, surrounded by pine trees
   ```

2. **Chọn cài đặt**:
   - **Model**: Chọn model Veo (veo-2.0, veo-1.0, veo-lite)
   - **Độ phân giải**: 480p, 720p, 1080p, 4K
   - **Tỷ lệ khung hình**: 16:9, 9:16, 1:1, 4:3, 21:9
   - **Độ dài**: 2-60 giây

3. **Tạo video**: Nhấn nút "Tạo Video"

4. **Theo dõi tiến độ**: Xem thanh tiến trình và log output

#### Tab "Cài đặt"

- **API Key**: Nhập và lưu Google AI API Key
- **Test Kết nối**: Kiểm tra kết nối với API
- **Đường dẫn**: Cấu hình thư mục lưu video

#### Tab "Logs"

- Xem logs chi tiết của ứng dụng
- Làm mới hoặc xóa logs

## Cấu hình nâng cao

### File `config/settings.py`

Bạn có thể tùy chỉnh các cài đặt trong file này:

```python
# Timeout cho requests (giây)
REQUEST_TIMEOUT = 300

# Số lượng request đồng thời
MAX_CONCURRENT_REQUESTS = 3

# Kích thước cửa sổ
WINDOW_SIZE = {
    'width': 1200,
    'height': 800,
}

# Cấp độ log
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## API Reference

### VeoAPIClient

Client chính để giao tiếp với Google Veo API.

#### Khởi tạo

```python
from core import VeoAPIClient

client = VeoAPIClient(api_key="your_api_key")
```

#### Phương thức

##### `async test_connection() -> bool`

Kiểm tra kết nối với API.

```python
is_connected = await client.test_connection()
```

##### `async list_models() -> List[str]`

Lấy danh sách các model có sẵn.

```python
models = await client.list_models()
for model in models:
    print(model)
```

##### `async generate_video(...) -> Dict[str, Any]`

Tạo video từ text prompt.

```python
result = await client.generate_video(
    prompt="A beautiful sunset",
    model="veo-2.0",
    duration=10,
    resolution="1080p",
    aspect_ratio="16:9"
)
```

### DatabaseManager

Database manager để lưu trữ projects, scenes, video history, và templates.

#### Khởi tạo

```python
from core import DatabaseManager, get_database

# Sử dụng đường dẫn mặc định
db = get_database()

# Hoặc custom path
db = DatabaseManager(Path("custom.db"))
```

#### Các phương thức chính

**Project Management:**
```python
# Tạo project
project_id = db.create_project(
    name="My Video Project",
    description="Project description"
)

# Lấy danh sách projects
projects = db.get_projects()

# Lấy chi tiết project
project = db.get_project_by_id(project_id)
```

**Scene Management:**
```python
# Lưu scene
scene_id = db.save_scene(project_id, {
    'scene_number': 1,
    'prompt': 'Opening scene',
    'duration': 10
})

# Lấy scenes của project
scenes = db.get_scenes(project_id)
```

**Video History:**
```python
# Lưu video generation
video_id = db.save_video_generation({
    'prompt': 'A beautiful sunset',
    'model': 'veo-2.0',
    'status': 'completed',
    'video_path': 'outputs/video.mp4'
})

# Lấy lịch sử
videos = db.get_video_history(limit=10)
```

**Templates:**
```python
# Lưu template
template_id = db.save_template(
    name="Cinematic Sunset",
    base_style="cinematic, golden hour",
    category="cinematic",
    tags=["sunset", "dramatic"]
)

# Lấy templates
templates = db.get_templates(category="cinematic")
```

**Xem chi tiết:** [DATABASE_DOCUMENTATION.md](DATABASE_DOCUMENTATION.md)

## Logging

Logs được lưu tại `logs/veo_app.log` với rotation tự động:

- Kích thước tối đa: 10 MB
- Số file backup: 5
- Format: `timestamp - module - level - message`

### Sử dụng logger trong code

```python
from utils import get_logger

logger = get_logger(__name__)

logger.info("Thông tin")
logger.warning("Cảnh báo")
logger.error("Lỗi")
logger.debug("Debug info")
```

## Xử lý lỗi

### API Key không hợp lệ

```
Lỗi: API key không được để trống hoặc sử dụng giá trị mặc định
```

**Giải pháp**: Kiểm tra và cập nhật API key trong tab "Cài đặt" hoặc file `.env`

### Không thể kết nối API

```
Lỗi: Không thể kết nối đến API
```

**Giải pháp**:
- Kiểm tra kết nối internet
- Xác nhận API key còn hiệu lực
- Thử lại sau vài phút

### Import Error

```
ImportError: No module named 'PyQt6'
```

**Giải pháp**:
```bash
pip install -r requirements.txt
```

## Phát triển

### Thêm tính năng mới

1. **Tạo module mới** trong `core/` hoặc `utils/`
2. **Import vào `__init__.py`** của package
3. **Sử dụng logger** để tracking
4. **Cập nhật README** nếu cần

### Style Guide

- Sử dụng docstrings cho tất cả functions/classes
- Comments bằng tiếng Việt
- Follow PEP 8
- Type hints khi có thể

## Roadmap

- [ ] Hỗ trợ batch generation (tạo nhiều video cùng lúc)
- [ ] Preview video trực tiếp trong app
- [ ] Export settings thành preset
- [ ] Dark mode
- [ ] Multi-language support
- [ ] Video editing features (trim, merge)
- [ ] Cloud storage integration

## Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng:

1. Fork dự án
2. Tạo branch cho feature (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## Giấy phép

Dự án này được phân phối dưới giấy phép MIT. Xem file `LICENSE` để biết thêm chi tiết.

## Liên hệ

- Báo lỗi: [GitHub Issues](https://github.com/your-repo/issues)
- Email: your-email@example.com

## Ghi nhận

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI Framework
- [Google Generative AI](https://ai.google.dev/) - AI API
- [Python](https://www.python.org/) - Programming Language

---

**Lưu ý**: Google Veo API hiện đang trong giai đoạn beta. Một số tính năng có thể chưa hoạt động đầy đủ hoặc thay đổi trong tương lai.

Made with ❤️ using Python and PyQt6
