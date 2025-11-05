"""
Module quản lý cơ sở dữ liệu SQLite cho ứng dụng
Lưu trữ lịch sử video, projects, scenes, và templates
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from contextlib import contextmanager

from config import settings
from utils import get_logger

# Khởi tạo logger
logger = get_logger(__name__)

# Đường dẫn database
DB_PATH = settings.BASE_DIR / 'veo_database.db'

# Phiên bản schema hiện tại
CURRENT_SCHEMA_VERSION = 1


class DatabaseManager:
    """
    Class quản lý database SQLite cho ứng dụng Veo Video Generator

    Attributes:
        db_path (Path): Đường dẫn đến file database
        connection: Connection hiện tại (nếu có)
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Khởi tạo DatabaseManager

        Args:
            db_path (Path, optional): Đường dẫn custom cho database.
                                     Mặc định sử dụng DB_PATH
        """
        self.db_path = db_path or DB_PATH
        self.connection = None

        logger.info(f"Khởi tạo DatabaseManager với database: {self.db_path}")

        # Khởi tạo database nếu chưa tồn tại
        self.init_database()


    @contextmanager
    def get_connection(self):
        """
        Context manager để quản lý database connection
        Tự động commit và close connection

        Yields:
            sqlite3.Connection: Database connection

        Example:
            >>> db = DatabaseManager()
            >>> with db.get_connection() as conn:
            >>>     cursor = conn.cursor()
            >>>     cursor.execute("SELECT * FROM videos")
        """
        conn = sqlite3.connect(self.db_path)
        # Trả về rows dạng dict thay vì tuple
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Lỗi database transaction: {e}")
            raise
        finally:
            conn.close()


    def init_database(self):
        """
        Khởi tạo database và tạo tất cả các bảng cần thiết
        Chạy migrations nếu cần
        """
        logger.info("Đang khởi tạo database...")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # ===== BẢNG SCHEMA_VERSION =====
                # Lưu trữ phiên bản schema để quản lý migration
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS schema_version (
                        version INTEGER PRIMARY KEY,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        description TEXT
                    )
                """)

                # ===== BẢNG PROJECTS =====
                # Lưu trữ thông tin các dự án video
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        style_template TEXT,
                        settings TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'active',
                        UNIQUE(name)
                    )
                """)

                # ===== BẢNG SCENES =====
                # Lưu trữ các scene trong project
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS scenes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER NOT NULL,
                        scene_number INTEGER NOT NULL,
                        prompt TEXT NOT NULL,
                        reference_images TEXT,
                        duration INTEGER DEFAULT 5,
                        resolution TEXT DEFAULT '1080p',
                        aspect_ratio TEXT DEFAULT '16:9',
                        model TEXT DEFAULT 'veo-2.0',
                        status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                        UNIQUE(project_id, scene_number)
                    )
                """)

                # ===== BẢNG VIDEOS =====
                # Lưu trữ lịch sử tạo video
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS videos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER,
                        scene_id INTEGER,
                        prompt TEXT NOT NULL,
                        model TEXT NOT NULL,
                        status TEXT NOT NULL,
                        video_path TEXT,
                        duration INTEGER,
                        resolution TEXT,
                        aspect_ratio TEXT,
                        file_size INTEGER,
                        error_message TEXT,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL,
                        FOREIGN KEY (scene_id) REFERENCES scenes(id) ON DELETE SET NULL
                    )
                """)

                # ===== BẢNG TEMPLATES =====
                # Lưu trữ các template style
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        base_style TEXT NOT NULL,
                        category TEXT,
                        tags TEXT,
                        description TEXT,
                        settings TEXT,
                        usage_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # ===== TẠO INDEXES =====
                # Index cho tìm kiếm nhanh
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_videos_project
                    ON videos(project_id)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_videos_status
                    ON videos(status)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_videos_created
                    ON videos(created_at DESC)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_scenes_project
                    ON scenes(project_id, scene_number)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_templates_category
                    ON templates(category)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_projects_status
                    ON projects(status)
                """)

                # Kiểm tra và cập nhật schema version
                self._update_schema_version(cursor)

                logger.info("Database đã được khởi tạo thành công")

        except Exception as e:
            logger.error(f"Lỗi khi khởi tạo database: {e}")
            raise


    def _update_schema_version(self, cursor: sqlite3.Cursor):
        """
        Cập nhật phiên bản schema

        Args:
            cursor: Database cursor
        """
        cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
        result = cursor.fetchone()

        if result is None:
            # Lần đầu khởi tạo
            cursor.execute("""
                INSERT INTO schema_version (version, description)
                VALUES (?, ?)
            """, (CURRENT_SCHEMA_VERSION, "Initial schema"))
            logger.info(f"Đã tạo schema version {CURRENT_SCHEMA_VERSION}")
        elif result[0] < CURRENT_SCHEMA_VERSION:
            # Cần migration
            self._run_migrations(cursor, result[0], CURRENT_SCHEMA_VERSION)


    def _run_migrations(self, cursor: sqlite3.Cursor, from_version: int, to_version: int):
        """
        Chạy database migrations

        Args:
            cursor: Database cursor
            from_version: Version hiện tại
            to_version: Version đích
        """
        logger.info(f"Đang chạy migrations từ version {from_version} đến {to_version}")

        # Định nghĩa các migrations
        migrations = {
            # Ví dụ migration từ version 1 -> 2
            # 2: [
            #     "ALTER TABLE videos ADD COLUMN new_field TEXT",
            #     "CREATE INDEX idx_new_field ON videos(new_field)"
            # ]
        }

        for version in range(from_version + 1, to_version + 1):
            if version in migrations:
                logger.info(f"Áp dụng migration version {version}")
                for sql in migrations[version]:
                    cursor.execute(sql)

                cursor.execute("""
                    INSERT INTO schema_version (version, description)
                    VALUES (?, ?)
                """, (version, f"Migration to version {version}"))


    # ===== VIDEO MANAGEMENT =====

    def save_video_generation(self, data: Dict[str, Any]) -> int:
        """
        Lưu thông tin video generation vào database

        Args:
            data (dict): Thông tin video với các keys:
                - prompt (str, required)
                - model (str, required)
                - status (str, required)
                - project_id (int, optional)
                - scene_id (int, optional)
                - video_path (str, optional)
                - duration (int, optional)
                - resolution (str, optional)
                - aspect_ratio (str, optional)
                - file_size (int, optional)
                - error_message (str, optional)
                - metadata (dict, optional)

        Returns:
            int: ID của video record vừa tạo

        Example:
            >>> db = DatabaseManager()
            >>> video_id = db.save_video_generation({
            >>>     'prompt': 'A beautiful sunset',
            >>>     'model': 'veo-2.0',
            >>>     'status': 'completed',
            >>>     'video_path': '/path/to/video.mp4'
            >>> })
        """
        logger.info(f"Đang lưu video generation: {data.get('prompt', '')[:50]}...")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Chuẩn bị metadata
                metadata = data.get('metadata', {})
                if metadata:
                    metadata_json = json.dumps(metadata)
                else:
                    metadata_json = None

                # Insert video record
                cursor.execute("""
                    INSERT INTO videos (
                        project_id, scene_id, prompt, model, status,
                        video_path, duration, resolution, aspect_ratio,
                        file_size, error_message, metadata, completed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data.get('project_id'),
                    data.get('scene_id'),
                    data['prompt'],
                    data['model'],
                    data['status'],
                    data.get('video_path'),
                    data.get('duration'),
                    data.get('resolution'),
                    data.get('aspect_ratio'),
                    data.get('file_size'),
                    data.get('error_message'),
                    metadata_json,
                    datetime.now() if data['status'] == 'completed' else None
                ))

                video_id = cursor.lastrowid
                logger.info(f"Đã lưu video với ID: {video_id}")
                return video_id

        except Exception as e:
            logger.error(f"Lỗi khi lưu video generation: {e}")
            raise


    def get_video_history(
        self,
        project_id: Optional[int] = None,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lấy lịch sử các video đã tạo

        Args:
            project_id (int, optional): Lọc theo project ID
            limit (int): Số lượng records tối đa
            status (str, optional): Lọc theo status

        Returns:
            List[Dict]: Danh sách video records

        Example:
            >>> db = DatabaseManager()
            >>> videos = db.get_video_history(project_id=1, limit=10)
            >>> for video in videos:
            >>>     print(video['prompt'], video['status'])
        """
        logger.info(f"Đang lấy video history (project_id={project_id}, limit={limit})")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Build query động
                query = """
                    SELECT
                        v.id, v.project_id, v.scene_id, v.prompt, v.model,
                        v.status, v.video_path, v.duration, v.resolution,
                        v.aspect_ratio, v.file_size, v.error_message, v.metadata,
                        v.created_at, v.completed_at,
                        p.name as project_name,
                        s.scene_number
                    FROM videos v
                    LEFT JOIN projects p ON v.project_id = p.id
                    LEFT JOIN scenes s ON v.scene_id = s.id
                    WHERE 1=1
                """
                params = []

                if project_id is not None:
                    query += " AND v.project_id = ?"
                    params.append(project_id)

                if status is not None:
                    query += " AND v.status = ?"
                    params.append(status)

                query += " ORDER BY v.created_at DESC LIMIT ?"
                params.append(limit)

                cursor.execute(query, params)
                rows = cursor.fetchall()

                # Convert sang dict
                videos = []
                for row in rows:
                    video = dict(row)
                    # Parse metadata JSON
                    if video['metadata']:
                        video['metadata'] = json.loads(video['metadata'])
                    videos.append(video)

                logger.info(f"Đã lấy {len(videos)} video records")
                return videos

        except Exception as e:
            logger.error(f"Lỗi khi lấy video history: {e}")
            raise


    def update_video_status(
        self,
        video_id: int,
        status: str,
        video_path: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Cập nhật trạng thái của video

        Args:
            video_id (int): ID của video
            status (str): Status mới (pending, processing, completed, failed)
            video_path (str, optional): Đường dẫn video (khi completed)
            error_message (str, optional): Thông báo lỗi (khi failed)

        Returns:
            bool: True nếu cập nhật thành công
        """
        logger.info(f"Cập nhật video {video_id} sang status: {status}")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                completed_at = datetime.now() if status == 'completed' else None

                cursor.execute("""
                    UPDATE videos
                    SET status = ?,
                        video_path = COALESCE(?, video_path),
                        error_message = ?,
                        completed_at = COALESCE(?, completed_at)
                    WHERE id = ?
                """, (status, video_path, error_message, completed_at, video_id))

                logger.info(f"Đã cập nhật video {video_id}")
                return True

        except Exception as e:
            logger.error(f"Lỗi khi cập nhật video status: {e}")
            return False


    # ===== PROJECT MANAGEMENT =====

    def create_project(
        self,
        name: str,
        description: Optional[str] = None,
        style_template: Optional[str] = None,
        settings: Optional[Dict] = None
    ) -> int:
        """
        Tạo project mới

        Args:
            name (str): Tên project
            description (str, optional): Mô tả project
            style_template (str, optional): Template style
            settings (dict, optional): Cài đặt project

        Returns:
            int: ID của project vừa tạo

        Example:
            >>> db = DatabaseManager()
            >>> project_id = db.create_project(
            >>>     name="My Video Project",
            >>>     description="A series of promotional videos"
            >>> )
        """
        logger.info(f"Đang tạo project: {name}")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                settings_json = json.dumps(settings) if settings else None

                cursor.execute("""
                    INSERT INTO projects (name, description, style_template, settings)
                    VALUES (?, ?, ?, ?)
                """, (name, description, style_template, settings_json))

                project_id = cursor.lastrowid
                logger.info(f"Đã tạo project với ID: {project_id}")
                return project_id

        except sqlite3.IntegrityError:
            logger.error(f"Project với tên '{name}' đã tồn tại")
            raise ValueError(f"Project với tên '{name}' đã tồn tại")
        except Exception as e:
            logger.error(f"Lỗi khi tạo project: {e}")
            raise


    def get_projects(self, status: str = 'active') -> List[Dict[str, Any]]:
        """
        Lấy danh sách projects

        Args:
            status (str): Lọc theo status (active, archived, all)

        Returns:
            List[Dict]: Danh sách projects
        """
        logger.info(f"Đang lấy danh sách projects (status={status})")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                if status == 'all':
                    query = "SELECT * FROM projects ORDER BY created_at DESC"
                    cursor.execute(query)
                else:
                    query = "SELECT * FROM projects WHERE status = ? ORDER BY created_at DESC"
                    cursor.execute(query, (status,))

                rows = cursor.fetchall()

                projects = []
                for row in rows:
                    project = dict(row)
                    if project['settings']:
                        project['settings'] = json.loads(project['settings'])
                    projects.append(project)

                logger.info(f"Đã lấy {len(projects)} projects")
                return projects

        except Exception as e:
            logger.error(f"Lỗi khi lấy projects: {e}")
            raise


    def get_project_by_id(self, project_id: int) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin chi tiết một project

        Args:
            project_id (int): ID của project

        Returns:
            Dict hoặc None nếu không tìm thấy
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
                row = cursor.fetchone()

                if row:
                    project = dict(row)
                    if project['settings']:
                        project['settings'] = json.loads(project['settings'])
                    return project
                return None

        except Exception as e:
            logger.error(f"Lỗi khi lấy project {project_id}: {e}")
            raise


    def update_project(self, project_id: int, **kwargs) -> bool:
        """
        Cập nhật thông tin project

        Args:
            project_id (int): ID của project
            **kwargs: Các field cần cập nhật

        Returns:
            bool: True nếu thành công
        """
        logger.info(f"Đang cập nhật project {project_id}")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Build dynamic update query
                fields = []
                values = []

                for key, value in kwargs.items():
                    if key in ['name', 'description', 'style_template', 'status']:
                        fields.append(f"{key} = ?")
                        values.append(value)
                    elif key == 'settings' and isinstance(value, dict):
                        fields.append("settings = ?")
                        values.append(json.dumps(value))

                if not fields:
                    return False

                fields.append("updated_at = CURRENT_TIMESTAMP")
                values.append(project_id)

                query = f"UPDATE projects SET {', '.join(fields)} WHERE id = ?"
                cursor.execute(query, values)

                logger.info(f"Đã cập nhật project {project_id}")
                return True

        except Exception as e:
            logger.error(f"Lỗi khi cập nhật project: {e}")
            return False


    # ===== SCENE MANAGEMENT =====

    def save_scene(self, project_id: int, scene_data: Dict[str, Any]) -> int:
        """
        Lưu scene vào database

        Args:
            project_id (int): ID của project
            scene_data (dict): Thông tin scene với keys:
                - scene_number (int, required)
                - prompt (str, required)
                - reference_images (str, optional)
                - duration (int, optional)
                - resolution (str, optional)
                - aspect_ratio (str, optional)
                - model (str, optional)

        Returns:
            int: ID của scene vừa tạo

        Example:
            >>> db = DatabaseManager()
            >>> scene_id = db.save_scene(
            >>>     project_id=1,
            >>>     scene_data={
            >>>         'scene_number': 1,
            >>>         'prompt': 'Opening scene with sunset',
            >>>         'duration': 10
            >>>     }
            >>> )
        """
        logger.info(f"Đang lưu scene {scene_data.get('scene_number')} cho project {project_id}")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO scenes (
                        project_id, scene_number, prompt, reference_images,
                        duration, resolution, aspect_ratio, model
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    project_id,
                    scene_data['scene_number'],
                    scene_data['prompt'],
                    scene_data.get('reference_images'),
                    scene_data.get('duration', 5),
                    scene_data.get('resolution', settings.DEFAULT_RESOLUTION),
                    scene_data.get('aspect_ratio', settings.DEFAULT_ASPECT_RATIO),
                    scene_data.get('model', settings.DEFAULT_MODEL)
                ))

                scene_id = cursor.lastrowid
                logger.info(f"Đã lưu scene với ID: {scene_id}")
                return scene_id

        except sqlite3.IntegrityError:
            logger.error(f"Scene {scene_data['scene_number']} đã tồn tại trong project {project_id}")
            raise ValueError(f"Scene number {scene_data['scene_number']} đã tồn tại")
        except Exception as e:
            logger.error(f"Lỗi khi lưu scene: {e}")
            raise


    def get_scenes(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Lấy tất cả scenes của một project

        Args:
            project_id (int): ID của project

        Returns:
            List[Dict]: Danh sách scenes được sắp xếp theo scene_number
        """
        logger.info(f"Đang lấy scenes cho project {project_id}")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM scenes
                    WHERE project_id = ?
                    ORDER BY scene_number ASC
                """, (project_id,))

                rows = cursor.fetchall()
                scenes = [dict(row) for row in rows]

                logger.info(f"Đã lấy {len(scenes)} scenes")
                return scenes

        except Exception as e:
            logger.error(f"Lỗi khi lấy scenes: {e}")
            raise


    def update_scene_status(self, scene_id: int, status: str) -> bool:
        """
        Cập nhật trạng thái của scene

        Args:
            scene_id (int): ID của scene
            status (str): Status mới

        Returns:
            bool: True nếu thành công
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE scenes
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, scene_id))
                return True
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật scene status: {e}")
            return False


    # ===== TEMPLATE MANAGEMENT =====

    def save_template(
        self,
        name: str,
        base_style: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None,
        settings: Optional[Dict] = None
    ) -> int:
        """
        Lưu template style

        Args:
            name (str): Tên template
            base_style (str): Style cơ bản
            category (str, optional): Danh mục
            tags (List[str], optional): Các tags
            description (str, optional): Mô tả
            settings (dict, optional): Cài đặt bổ sung

        Returns:
            int: ID của template vừa tạo

        Example:
            >>> db = DatabaseManager()
            >>> template_id = db.save_template(
            >>>     name="Cinematic Sunset",
            >>>     base_style="cinematic, golden hour, dramatic lighting",
            >>>     category="cinematic",
            >>>     tags=["sunset", "dramatic", "golden"]
            >>> )
        """
        logger.info(f"Đang lưu template: {name}")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                tags_json = json.dumps(tags) if tags else None
                settings_json = json.dumps(settings) if settings else None

                cursor.execute("""
                    INSERT INTO templates (
                        name, base_style, category, tags, description, settings
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (name, base_style, category, tags_json, description, settings_json))

                template_id = cursor.lastrowid
                logger.info(f"Đã lưu template với ID: {template_id}")
                return template_id

        except sqlite3.IntegrityError:
            logger.error(f"Template với tên '{name}' đã tồn tại")
            raise ValueError(f"Template với tên '{name}' đã tồn tại")
        except Exception as e:
            logger.error(f"Lỗi khi lưu template: {e}")
            raise


    def get_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lấy danh sách templates

        Args:
            category (str, optional): Lọc theo category

        Returns:
            List[Dict]: Danh sách templates

        Example:
            >>> db = DatabaseManager()
            >>> templates = db.get_templates(category="cinematic")
            >>> for template in templates:
            >>>     print(template['name'], template['base_style'])
        """
        logger.info(f"Đang lấy templates (category={category})")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                if category is None:
                    cursor.execute("""
                        SELECT * FROM templates
                        ORDER BY usage_count DESC, name ASC
                    """)
                else:
                    cursor.execute("""
                        SELECT * FROM templates
                        WHERE category = ?
                        ORDER BY usage_count DESC, name ASC
                    """, (category,))

                rows = cursor.fetchall()

                templates = []
                for row in rows:
                    template = dict(row)
                    # Parse JSON fields
                    if template['tags']:
                        template['tags'] = json.loads(template['tags'])
                    if template['settings']:
                        template['settings'] = json.loads(template['settings'])
                    templates.append(template)

                logger.info(f"Đã lấy {len(templates)} templates")
                return templates

        except Exception as e:
            logger.error(f"Lỗi khi lấy templates: {e}")
            raise


    def increment_template_usage(self, template_id: int) -> bool:
        """
        Tăng counter sử dụng template

        Args:
            template_id (int): ID của template

        Returns:
            bool: True nếu thành công
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE templates
                    SET usage_count = usage_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (template_id,))
                return True
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật template usage: {e}")
            return False


    # ===== STATISTICS & UTILITIES =====

    def get_statistics(self) -> Dict[str, Any]:
        """
        Lấy thống kê tổng quan

        Returns:
            Dict chứa các thống kê
        """
        logger.info("Đang lấy thống kê database")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                stats = {}

                # Tổng số videos
                cursor.execute("SELECT COUNT(*) FROM videos")
                stats['total_videos'] = cursor.fetchone()[0]

                # Videos theo status
                cursor.execute("""
                    SELECT status, COUNT(*)
                    FROM videos
                    GROUP BY status
                """)
                stats['videos_by_status'] = dict(cursor.fetchall())

                # Tổng số projects
                cursor.execute("SELECT COUNT(*) FROM projects WHERE status = 'active'")
                stats['total_projects'] = cursor.fetchone()[0]

                # Tổng số scenes
                cursor.execute("SELECT COUNT(*) FROM scenes")
                stats['total_scenes'] = cursor.fetchone()[0]

                # Tổng số templates
                cursor.execute("SELECT COUNT(*) FROM templates")
                stats['total_templates'] = cursor.fetchone()[0]

                # Video được tạo gần nhất
                cursor.execute("""
                    SELECT created_at
                    FROM videos
                    ORDER BY created_at DESC
                    LIMIT 1
                """)
                result = cursor.fetchone()
                stats['last_video_created'] = result[0] if result else None

                logger.info(f"Thống kê: {stats}")
                return stats

        except Exception as e:
            logger.error(f"Lỗi khi lấy thống kê: {e}")
            raise


    def cleanup_old_records(self, days: int = 90) -> int:
        """
        Xóa các records cũ (failed videos)

        Args:
            days (int): Xóa records cũ hơn N ngày

        Returns:
            int: Số lượng records đã xóa
        """
        logger.info(f"Đang xóa records cũ hơn {days} ngày")

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    DELETE FROM videos
                    WHERE status = 'failed'
                    AND created_at < datetime('now', '-' || ? || ' days')
                """, (days,))

                deleted_count = cursor.rowcount
                logger.info(f"Đã xóa {deleted_count} records")
                return deleted_count

        except Exception as e:
            logger.error(f"Lỗi khi xóa records: {e}")
            raise


    def vacuum_database(self):
        """
        Tối ưu hóa database (VACUUM)
        Giảm kích thước file và cải thiện performance
        """
        logger.info("Đang chạy VACUUM database...")

        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("VACUUM")
            conn.close()
            logger.info("Đã VACUUM database thành công")
        except Exception as e:
            logger.error(f"Lỗi khi VACUUM database: {e}")


    def close(self):
        """Đóng connection nếu còn mở"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Đã đóng database connection")


# ===== HELPER FUNCTIONS =====

def get_database() -> DatabaseManager:
    """
    Helper function để lấy DatabaseManager instance

    Returns:
        DatabaseManager: Database manager instance

    Example:
        >>> db = get_database()
        >>> projects = db.get_projects()
    """
    return DatabaseManager()


# ===== EXPORT =====
__all__ = [
    'DatabaseManager',
    'get_database',
    'DB_PATH',
    'CURRENT_SCHEMA_VERSION'
]
