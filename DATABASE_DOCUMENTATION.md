# Database Documentation - Veo Video Generator

## Tổng quan

DatabaseManager cung cấp một interface hoàn chỉnh để quản lý dữ liệu ứng dụng Veo Video Generator sử dụng SQLite.

## Database Schema

### 1. Bảng `schema_version`

Quản lý phiên bản schema cho migration.

| Column | Type | Description |
|--------|------|-------------|
| version | INTEGER | Phiên bản schema (PRIMARY KEY) |
| applied_at | TIMESTAMP | Thời gian áp dụng |
| description | TEXT | Mô tả migration |

### 2. Bảng `projects`

Lưu trữ thông tin các dự án video.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | ID tự động tăng (PRIMARY KEY) |
| name | TEXT | Tên project (UNIQUE) |
| description | TEXT | Mô tả project |
| style_template | TEXT | Template style sử dụng |
| settings | TEXT | JSON settings của project |
| created_at | TIMESTAMP | Thời gian tạo |
| updated_at | TIMESTAMP | Thời gian cập nhật |
| status | TEXT | Trạng thái (active/archived) |

**Constraints:**
- `UNIQUE(name)` - Tên project phải unique

### 3. Bảng `scenes`

Lưu trữ các scene trong project.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | ID tự động tăng (PRIMARY KEY) |
| project_id | INTEGER | ID của project (FOREIGN KEY) |
| scene_number | INTEGER | Số thứ tự scene |
| prompt | TEXT | Prompt mô tả scene |
| reference_images | TEXT | Đường dẫn ảnh tham khảo |
| duration | INTEGER | Độ dài scene (giây) |
| resolution | TEXT | Độ phân giải |
| aspect_ratio | TEXT | Tỷ lệ khung hình |
| model | TEXT | Model sử dụng |
| status | TEXT | Trạng thái scene |
| created_at | TIMESTAMP | Thời gian tạo |
| updated_at | TIMESTAMP | Thời gian cập nhật |

**Constraints:**
- `FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE`
- `UNIQUE(project_id, scene_number)` - Scene number phải unique trong project

**Indexes:**
- `idx_scenes_project` trên `(project_id, scene_number)`

### 4. Bảng `videos`

Lưu trữ lịch sử tạo video.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | ID tự động tăng (PRIMARY KEY) |
| project_id | INTEGER | ID của project (FOREIGN KEY, nullable) |
| scene_id | INTEGER | ID của scene (FOREIGN KEY, nullable) |
| prompt | TEXT | Prompt tạo video |
| model | TEXT | Model đã sử dụng |
| status | TEXT | Trạng thái (pending/processing/completed/failed) |
| video_path | TEXT | Đường dẫn file video |
| duration | INTEGER | Độ dài video (giây) |
| resolution | TEXT | Độ phân giải |
| aspect_ratio | TEXT | Tỷ lệ khung hình |
| file_size | INTEGER | Kích thước file (bytes) |
| error_message | TEXT | Thông báo lỗi (nếu có) |
| metadata | TEXT | JSON metadata bổ sung |
| created_at | TIMESTAMP | Thời gian bắt đầu |
| completed_at | TIMESTAMP | Thời gian hoàn thành |

**Constraints:**
- `FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL`
- `FOREIGN KEY (scene_id) REFERENCES scenes(id) ON DELETE SET NULL`

**Indexes:**
- `idx_videos_project` trên `project_id`
- `idx_videos_status` trên `status`
- `idx_videos_created` trên `created_at DESC`

### 5. Bảng `templates`

Lưu trữ các template style.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | ID tự động tăng (PRIMARY KEY) |
| name | TEXT | Tên template (UNIQUE) |
| base_style | TEXT | Style cơ bản |
| category | TEXT | Danh mục template |
| tags | TEXT | JSON array các tags |
| description | TEXT | Mô tả template |
| settings | TEXT | JSON settings |
| usage_count | INTEGER | Số lần sử dụng |
| created_at | TIMESTAMP | Thời gian tạo |
| updated_at | TIMESTAMP | Thời gian cập nhật |

**Constraints:**
- `UNIQUE(name)` - Tên template phải unique

**Indexes:**
- `idx_templates_category` trên `category`

## API Reference

### Class: DatabaseManager

#### Constructor

```python
DatabaseManager(db_path: Optional[Path] = None)
```

**Args:**
- `db_path`: Đường dẫn custom cho database. Mặc định: `veo_database.db`

**Example:**
```python
from core import DatabaseManager

# Sử dụng đường dẫn mặc định
db = DatabaseManager()

# Hoặc chỉ định đường dẫn
db = DatabaseManager(Path("custom_db.db"))
```

---

### Video Management Methods

#### `save_video_generation(data: Dict[str, Any]) -> int`

Lưu thông tin video generation.

**Args:**
- `data` (dict): Thông tin video
  - `prompt` (str, **required**): Prompt tạo video
  - `model` (str, **required**): Model sử dụng
  - `status` (str, **required**): Trạng thái
  - `project_id` (int, optional): ID project
  - `scene_id` (int, optional): ID scene
  - `video_path` (str, optional): Đường dẫn video
  - `duration` (int, optional): Độ dài video
  - `resolution` (str, optional): Độ phân giải
  - `aspect_ratio` (str, optional): Tỷ lệ khung hình
  - `file_size` (int, optional): Kích thước file
  - `error_message` (str, optional): Thông báo lỗi
  - `metadata` (dict, optional): Metadata bổ sung

**Returns:** ID của video record

**Example:**
```python
video_id = db.save_video_generation({
    'prompt': 'A beautiful sunset over the ocean',
    'model': 'veo-2.0',
    'status': 'completed',
    'video_path': 'outputs/video.mp4',
    'duration': 10,
    'resolution': '1080p',
    'aspect_ratio': '16:9',
    'file_size': 15728640,
    'metadata': {'fps': 30, 'codec': 'h264'}
})
```

#### `get_video_history(project_id: Optional[int] = None, limit: int = 100, status: Optional[str] = None) -> List[Dict]`

Lấy lịch sử videos.

**Args:**
- `project_id` (int, optional): Lọc theo project
- `limit` (int): Số lượng tối đa (mặc định: 100)
- `status` (str, optional): Lọc theo status

**Returns:** List các video records

**Example:**
```python
# Lấy tất cả videos
all_videos = db.get_video_history()

# Lấy videos của project
project_videos = db.get_video_history(project_id=1)

# Lấy videos đã hoàn thành
completed = db.get_video_history(status='completed', limit=50)
```

#### `update_video_status(video_id: int, status: str, video_path: Optional[str] = None, error_message: Optional[str] = None) -> bool`

Cập nhật trạng thái video.

**Args:**
- `video_id` (int): ID của video
- `status` (str): Status mới
- `video_path` (str, optional): Đường dẫn video
- `error_message` (str, optional): Thông báo lỗi

**Returns:** True nếu thành công

**Example:**
```python
# Cập nhật sang processing
db.update_video_status(video_id=1, status='processing')

# Cập nhật sang completed với path
db.update_video_status(
    video_id=1,
    status='completed',
    video_path='outputs/video.mp4'
)

# Cập nhật sang failed với error
db.update_video_status(
    video_id=1,
    status='failed',
    error_message='API timeout'
)
```

---

### Project Management Methods

#### `create_project(name: str, description: Optional[str] = None, style_template: Optional[str] = None, settings: Optional[Dict] = None) -> int`

Tạo project mới.

**Args:**
- `name` (str): Tên project (unique)
- `description` (str, optional): Mô tả
- `style_template` (str, optional): Template style
- `settings` (dict, optional): Settings

**Returns:** ID của project

**Raises:** `ValueError` nếu tên đã tồn tại

**Example:**
```python
project_id = db.create_project(
    name="Marketing Videos 2025",
    description="Promotional video series",
    style_template="cinematic",
    settings={
        "resolution": "4K",
        "aspect_ratio": "16:9"
    }
)
```

#### `get_projects(status: str = 'active') -> List[Dict]`

Lấy danh sách projects.

**Args:**
- `status` (str): Lọc theo status (active/archived/all)

**Returns:** List projects

**Example:**
```python
# Lấy active projects
active_projects = db.get_projects()

# Lấy tất cả
all_projects = db.get_projects(status='all')
```

#### `get_project_by_id(project_id: int) -> Optional[Dict]`

Lấy chi tiết một project.

**Args:**
- `project_id` (int): ID của project

**Returns:** Dict hoặc None

**Example:**
```python
project = db.get_project_by_id(1)
if project:
    print(project['name'], project['description'])
```

#### `update_project(project_id: int, **kwargs) -> bool`

Cập nhật project.

**Args:**
- `project_id` (int): ID của project
- `**kwargs`: Các field cần update (name, description, style_template, status, settings)

**Returns:** True nếu thành công

**Example:**
```python
db.update_project(
    project_id=1,
    description="Updated description",
    status="archived"
)
```

---

### Scene Management Methods

#### `save_scene(project_id: int, scene_data: Dict[str, Any]) -> int`

Lưu scene vào database.

**Args:**
- `project_id` (int): ID của project
- `scene_data` (dict): Thông tin scene
  - `scene_number` (int, **required**): Số thứ tự
  - `prompt` (str, **required**): Prompt
  - `reference_images` (str, optional): Ảnh tham khảo
  - `duration` (int, optional): Độ dài
  - `resolution` (str, optional): Độ phân giải
  - `aspect_ratio` (str, optional): Tỷ lệ
  - `model` (str, optional): Model

**Returns:** ID của scene

**Raises:** `ValueError` nếu scene_number đã tồn tại

**Example:**
```python
scene_id = db.save_scene(
    project_id=1,
    scene_data={
        'scene_number': 1,
        'prompt': 'Opening scene with sunset',
        'duration': 10,
        'resolution': '4K'
    }
)
```

#### `get_scenes(project_id: int) -> List[Dict]`

Lấy tất cả scenes của project.

**Args:**
- `project_id` (int): ID của project

**Returns:** List scenes (sorted by scene_number)

**Example:**
```python
scenes = db.get_scenes(project_id=1)
for scene in scenes:
    print(f"Scene {scene['scene_number']}: {scene['prompt']}")
```

#### `update_scene_status(scene_id: int, status: str) -> bool`

Cập nhật trạng thái scene.

**Args:**
- `scene_id` (int): ID của scene
- `status` (str): Status mới

**Returns:** True nếu thành công

---

### Template Management Methods

#### `save_template(name: str, base_style: str, category: Optional[str] = None, tags: Optional[List[str]] = None, description: Optional[str] = None, settings: Optional[Dict] = None) -> int`

Lưu template style.

**Args:**
- `name` (str): Tên template (unique)
- `base_style` (str): Style cơ bản
- `category` (str, optional): Danh mục
- `tags` (List[str], optional): Tags
- `description` (str, optional): Mô tả
- `settings` (dict, optional): Settings

**Returns:** ID của template

**Raises:** `ValueError` nếu tên đã tồn tại

**Example:**
```python
template_id = db.save_template(
    name="Cinematic Sunset",
    base_style="cinematic, golden hour, dramatic lighting",
    category="cinematic",
    tags=["sunset", "dramatic", "golden"],
    description="Cinematic style with sunset lighting"
)
```

#### `get_templates(category: Optional[str] = None) -> List[Dict]`

Lấy danh sách templates.

**Args:**
- `category` (str, optional): Lọc theo category

**Returns:** List templates (sorted by usage_count DESC)

**Example:**
```python
# Lấy tất cả
all_templates = db.get_templates()

# Lọc theo category
cinematic = db.get_templates(category="cinematic")
```

#### `increment_template_usage(template_id: int) -> bool`

Tăng counter sử dụng template.

**Args:**
- `template_id` (int): ID của template

**Returns:** True nếu thành công

---

### Statistics & Utilities

#### `get_statistics() -> Dict[str, Any]`

Lấy thống kê tổng quan.

**Returns:** Dict chứa thống kê

**Example:**
```python
stats = db.get_statistics()
print(f"Total videos: {stats['total_videos']}")
print(f"Videos by status: {stats['videos_by_status']}")
```

#### `cleanup_old_records(days: int = 90) -> int`

Xóa các records cũ (failed videos).

**Args:**
- `days` (int): Xóa records cũ hơn N ngày

**Returns:** Số lượng records đã xóa

**Example:**
```python
deleted = db.cleanup_old_records(days=90)
print(f"Deleted {deleted} old records")
```

#### `vacuum_database()`

Tối ưu hóa database (VACUUM).

**Example:**
```python
db.vacuum_database()
```

---

## Migration System

Database tự động quản lý schema version và chạy migrations khi cần.

### Thêm Migration Mới

Trong file `core/database.py`, thêm migration vào dict `migrations` trong method `_run_migrations()`:

```python
migrations = {
    2: [
        "ALTER TABLE videos ADD COLUMN new_field TEXT",
        "CREATE INDEX idx_new_field ON videos(new_field)"
    ],
    3: [
        "ALTER TABLE projects ADD COLUMN priority INTEGER DEFAULT 0"
    ]
}
```

Cập nhật `CURRENT_SCHEMA_VERSION`:

```python
CURRENT_SCHEMA_VERSION = 3
```

Migrations sẽ tự động chạy khi khởi tạo database.

---

## Best Practices

### 1. Sử dụng Context Manager

```python
with db.get_connection() as conn:
    cursor = conn.cursor()
    # Your queries here
    # Auto commit/rollback
```

### 2. Error Handling

```python
try:
    project_id = db.create_project(name="Test Project")
except ValueError as e:
    print(f"Project already exists: {e}")
except Exception as e:
    print(f"Database error: {e}")
```

### 3. JSON Fields

Database tự động serialize/deserialize JSON:

```python
# Lưu
db.save_video_generation({
    'metadata': {'fps': 30, 'codec': 'h264'}  # Dict
})

# Lấy
videos = db.get_video_history()
print(videos[0]['metadata'])  # Đã parse thành dict
```

### 4. Transactions

Tất cả operations sử dụng transactions tự động:
- Thành công → commit
- Lỗi → rollback

---

## Examples

Xem file `examples_database_usage.py` để có ví dụ đầy đủ về:
- Tạo projects và scenes
- Lưu video history
- Quản lý templates
- Update operations
- Complex queries
- Error handling

**Chạy examples:**
```bash
python examples_database_usage.py
```

---

## Database File Location

Mặc định: `veo_database.db` trong thư mục gốc project.

Có thể thay đổi trong `config/settings.py` hoặc truyền vào constructor.

---

## Performance Tips

1. **Indexes**: Đã có indexes tối ưu cho các queries thường dùng
2. **VACUUM**: Chạy định kỳ để tối ưu database
3. **Cleanup**: Xóa old records để giảm kích thước
4. **Connection pooling**: Sử dụng context manager

---

## Troubleshooting

### Database locked

```python
# Đảm bảo đóng connections
db.close()
```

### Migration failed

```python
# Xem logs để biết migration nào thất bại
# Có thể cần restore từ backup
```

### Corrupt database

```python
# Chạy integrity check
conn = sqlite3.connect('veo_database.db')
cursor = conn.cursor()
cursor.execute("PRAGMA integrity_check")
print(cursor.fetchall())
```

---

## Support

Mọi thắc mắc về database, vui lòng tạo issue trên GitHub hoặc liên hệ qua email.
