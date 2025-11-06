"""
Template Manager - Manage and apply prompt templates
"""

import sqlite3
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from pathlib import Path

from utils import get_logger

logger = get_logger(__name__)


@dataclass
class PromptTemplate:
    """
    Data class for prompt template

    Attributes:
        id: Unique template ID
        name: Template name
        category: Template category (e.g., "Cinematic", "Anime")
        base_style: Base style description
        camera_movement: Camera movement description
        lighting: Lighting description
        color_palette: Color palette description
        audio_description: Audio/music description
        tags: List of searchable tags
        is_favorite: Whether template is marked as favorite
        usage_count: Number of times template has been used
    """
    id: int
    name: str
    category: str
    base_style: str
    camera_movement: str
    lighting: str
    color_palette: str
    audio_description: str
    tags: List[str]
    is_favorite: bool = False
    usage_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert list to comma-separated string for storage
        data['tags'] = ','.join(self.tags) if self.tags else ''
        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PromptTemplate':
        """Create from dictionary"""
        # Convert comma-separated string to list
        if isinstance(data.get('tags'), str):
            data['tags'] = [t.strip() for t in data['tags'].split(',') if t.strip()]
        return PromptTemplate(**data)


class TemplateManager:
    """
    Manages prompt templates for video generation

    Features:
    - Create, read, update, delete templates
    - Search and filter templates
    - Apply templates to custom prompts
    - Track usage statistics
    - Pre-defined template library
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize Template Manager

        Args:
            db_path: Path to database file (default: veo_database.db)
        """
        if db_path is None:
            db_path = "veo_database.db"

        self.db_path = Path(db_path)
        self.init_database()

        logger.info(f"TemplateManager initialized with database: {self.db_path}")

    def init_database(self):
        """Initialize database schema for templates"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create templates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    base_style TEXT NOT NULL,
                    camera_movement TEXT NOT NULL,
                    lighting TEXT NOT NULL,
                    color_palette TEXT NOT NULL,
                    audio_description TEXT NOT NULL,
                    tags TEXT,
                    is_favorite INTEGER DEFAULT 0,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            conn.close()

            logger.info("Template database schema initialized")

            # Create pre-defined templates if table is empty
            self.create_predefined_templates()

        except Exception as e:
            logger.error(f"Failed to initialize template database: {e}")
            raise

    def create_predefined_templates(self):
        """Create pre-defined template library"""
        # Check if templates already exist
        if len(self.get_all_templates()) > 0:
            logger.debug("Pre-defined templates already exist")
            return

        logger.info("Creating pre-defined templates...")

        predefined = [
            {
                'name': 'Cinematic Epic',
                'category': 'Cinematic',
                'base_style': 'epic cinematic film style, Hollywood blockbuster aesthetic, dramatic and powerful',
                'camera_movement': 'sweeping camera movements, dynamic crane shots, smooth tracking',
                'lighting': 'dramatic lighting with strong contrast, golden hour tones, volumetric fog',
                'color_palette': 'rich saturated colors, deep shadows, warm highlights',
                'audio_description': 'orchestral epic soundtrack, deep bass, rising crescendo',
                'tags': ['cinematic', 'epic', 'dramatic', 'hollywood', 'blockbuster']
            },
            {
                'name': 'Anime Style',
                'category': 'Anime',
                'base_style': 'Japanese anime art style, vibrant and expressive, hand-drawn aesthetic',
                'camera_movement': 'dynamic anime camera angles, speed lines, dramatic zooms',
                'lighting': 'bright cel-shaded lighting, high contrast shadows, vibrant highlights',
                'color_palette': 'vibrant saturated colors, bold outlines, anime color grading',
                'audio_description': 'J-pop inspired music, energetic soundtrack',
                'tags': ['anime', 'japanese', 'vibrant', 'cartoon', 'manga']
            },
            {
                'name': 'Cyberpunk Game',
                'category': 'Game',
                'base_style': 'cyberpunk video game aesthetic, futuristic dystopian, neon-soaked streets',
                'camera_movement': 'first-person perspective, smooth gimbal movements, urban exploration',
                'lighting': 'neon lighting, volumetric fog, holographic displays, rain-soaked reflections',
                'color_palette': 'neon pink and cyan, deep purples, high contrast blacks',
                'audio_description': 'synthwave electronic music, cyberpunk ambience, dystopian sounds',
                'tags': ['cyberpunk', 'futuristic', 'neon', 'dystopian', 'scifi', 'game']
            },
            {
                'name': 'Nature Documentary',
                'category': 'Documentary',
                'base_style': 'BBC nature documentary style, ultra-realistic, educational, awe-inspiring',
                'camera_movement': 'slow panning shots, stable macro photography, aerial drone footage',
                'lighting': 'natural sunlight, soft diffused lighting, golden hour warmth',
                'color_palette': 'natural earth tones, vibrant wildlife colors, realistic rendering',
                'audio_description': 'ambient nature sounds, gentle orchestral score, narrator-friendly',
                'tags': ['nature', 'documentary', 'realistic', 'wildlife', 'natural']
            },
            {
                'name': 'Abstract Art',
                'category': 'Art',
                'base_style': 'abstract expressionist art style, non-representational, experimental',
                'camera_movement': 'fluid morphing movements, kaleidoscopic rotations, abstract transitions',
                'lighting': 'artistic lighting, bold shadows, experimental color casts',
                'color_palette': 'bold primary colors, high saturation, artistic color theory',
                'audio_description': 'ambient experimental music, abstract soundscape',
                'tags': ['abstract', 'art', 'experimental', 'artistic', 'creative']
            },
            {
                'name': 'Studio Ghibli Style',
                'category': 'Anime',
                'base_style': 'Studio Ghibli aesthetic, whimsical hand-drawn animation, peaceful and dreamlike',
                'camera_movement': 'gentle flowing camera, peaceful panning, magical transitions',
                'lighting': 'soft diffused lighting, warm natural glow, magical sparkles',
                'color_palette': 'pastel watercolor palette, soft greens and blues, warm earth tones',
                'audio_description': 'gentle piano melody, whimsical orchestration, peaceful ambience',
                'tags': ['ghibli', 'anime', 'whimsical', 'peaceful', 'dreamy', 'magical']
            },
            {
                'name': 'Pixel Art',
                'category': 'Game',
                'base_style': '8-bit pixel art style, retro video game aesthetic, nostalgic gaming',
                'camera_movement': 'fixed camera angles, 2D side-scrolling movement, retro transitions',
                'lighting': 'flat pixel lighting, bold shadows, retro color banding',
                'color_palette': 'limited 8-bit color palette, vibrant retro colors, pixel-perfect',
                'audio_description': 'chiptune music, 8-bit sound effects, retro gaming audio',
                'tags': ['pixel', 'retro', '8bit', 'game', 'nostalgic', 'gaming']
            },
            {
                'name': 'Realistic Photography',
                'category': 'Photography',
                'base_style': 'ultra-realistic photographic style, professional DSLR quality, cinematic realism',
                'camera_movement': 'smooth stabilized camera, professional gimbal work, documentary style',
                'lighting': 'natural realistic lighting, professional three-point setup, soft key light',
                'color_palette': 'natural realistic colors, proper white balance, film-like color grading',
                'audio_description': 'ambient environmental sounds, natural acoustics',
                'tags': ['realistic', 'photography', 'professional', 'dslr', 'cinematic']
            }
        ]

        for template_data in predefined:
            try:
                self.create_template(template_data)
                logger.debug(f"Created template: {template_data['name']}")
            except Exception as e:
                logger.error(f"Failed to create template {template_data['name']}: {e}")

        logger.info(f"Created {len(predefined)} pre-defined templates")

    def create_template(self, template_data: Dict[str, Any]) -> int:
        """
        Create a new template

        Args:
            template_data: Template data dictionary

        Returns:
            Template ID

        Raises:
            ValueError: If required fields are missing
        """
        required_fields = [
            'name', 'category', 'base_style', 'camera_movement',
            'lighting', 'color_palette', 'audio_description'
        ]

        for field in required_fields:
            if field not in template_data:
                raise ValueError(f"Missing required field: {field}")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Convert tags list to comma-separated string
            tags_str = ','.join(template_data.get('tags', []))

            cursor.execute("""
                INSERT INTO templates (
                    name, category, base_style, camera_movement,
                    lighting, color_palette, audio_description,
                    tags, is_favorite, usage_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                template_data['name'],
                template_data['category'],
                template_data['base_style'],
                template_data['camera_movement'],
                template_data['lighting'],
                template_data['color_palette'],
                template_data['audio_description'],
                tags_str,
                template_data.get('is_favorite', False),
                template_data.get('usage_count', 0)
            ))

            template_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.info(f"Created template: {template_data['name']} (ID: {template_id})")
            return template_id

        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            raise

    def _row_to_template(self, row: sqlite3.Row) -> PromptTemplate:
        """
        Convert database row to PromptTemplate object

        Args:
            row: Database row

        Returns:
            PromptTemplate object
        """
        data = dict(row)

        # Convert tags string to list
        if data.get('tags'):
            data['tags'] = [t.strip() for t in data['tags'].split(',') if t.strip()]
        else:
            data['tags'] = []

        # Convert SQLite integers to booleans
        data['is_favorite'] = bool(data.get('is_favorite', False))

        # Remove database-only fields
        data.pop('created_at', None)
        data.pop('updated_at', None)

        return PromptTemplate(**data)

    def get_template(self, template_id: int) -> Optional[PromptTemplate]:
        """
        Get template by ID

        Args:
            template_id: Template ID

        Returns:
            PromptTemplate object or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM templates WHERE id = ?
            """, (template_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return self._row_to_template(row)

            return None

        except Exception as e:
            logger.error(f"Failed to get template {template_id}: {e}")
            return None

    def get_all_templates(self, category: Optional[str] = None) -> List[PromptTemplate]:
        """
        Get all templates, optionally filtered by category

        Args:
            category: Filter by category (optional)

        Returns:
            List of PromptTemplate objects
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if category:
                cursor.execute("""
                    SELECT * FROM templates
                    WHERE category = ?
                    ORDER BY usage_count DESC, name ASC
                """, (category,))
            else:
                cursor.execute("""
                    SELECT * FROM templates
                    ORDER BY usage_count DESC, name ASC
                """)

            rows = cursor.fetchall()
            conn.close()

            templates = [self._row_to_template(row) for row in rows]

            logger.debug(f"Retrieved {len(templates)} templates" +
                        (f" in category '{category}'" if category else ""))
            return templates

        except Exception as e:
            logger.error(f"Failed to get templates: {e}")
            return []

    def get_favorite_templates(self) -> List[PromptTemplate]:
        """
        Get all favorite templates

        Returns:
            List of favorite PromptTemplate objects
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM templates
                WHERE is_favorite = 1
                ORDER BY usage_count DESC, name ASC
            """)

            rows = cursor.fetchall()
            conn.close()

            templates = [self._row_to_template(row) for row in rows]

            logger.debug(f"Retrieved {len(templates)} favorite templates")
            return templates

        except Exception as e:
            logger.error(f"Failed to get favorite templates: {e}")
            return []

    def get_categories(self) -> List[str]:
        """
        Get all unique categories

        Returns:
            List of category names
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT category FROM templates
                ORDER BY category ASC
            """)

            rows = cursor.fetchall()
            conn.close()

            categories = [row[0] for row in rows]
            return categories

        except Exception as e:
            logger.error(f"Failed to get categories: {e}")
            return []

    def update_template(self, template_id: int, data: Dict[str, Any]):
        """
        Update template

        Args:
            template_id: Template ID
            data: Dictionary with fields to update

        Raises:
            ValueError: If template not found
        """
        try:
            # Check if template exists
            if not self.get_template(template_id):
                raise ValueError(f"Template not found: {template_id}")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Build UPDATE query dynamically
            update_fields = []
            values = []

            allowed_fields = [
                'name', 'category', 'base_style', 'camera_movement',
                'lighting', 'color_palette', 'audio_description',
                'tags', 'is_favorite'
            ]

            for field in allowed_fields:
                if field in data:
                    if field == 'tags':
                        # Convert list to comma-separated string
                        values.append(','.join(data[field]) if isinstance(data[field], list) else data[field])
                    else:
                        values.append(data[field])
                    update_fields.append(f"{field} = ?")

            if not update_fields:
                logger.warning(f"No valid fields to update for template {template_id}")
                return

            # Add updated_at timestamp
            update_fields.append("updated_at = CURRENT_TIMESTAMP")

            query = f"UPDATE templates SET {', '.join(update_fields)} WHERE id = ?"
            values.append(template_id)

            cursor.execute(query, values)
            conn.commit()
            conn.close()

            logger.info(f"Updated template {template_id}")

        except Exception as e:
            logger.error(f"Failed to update template {template_id}: {e}")
            raise

    def delete_template(self, template_id: int):
        """
        Delete template

        Args:
            template_id: Template ID

        Raises:
            ValueError: If template not found
        """
        try:
            # Check if template exists
            template = self.get_template(template_id)
            if not template:
                raise ValueError(f"Template not found: {template_id}")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM templates WHERE id = ?", (template_id,))

            conn.commit()
            conn.close()

            logger.info(f"Deleted template: {template.name} (ID: {template_id})")

        except Exception as e:
            logger.error(f"Failed to delete template {template_id}: {e}")
            raise

    def search_templates(self, query: str) -> List[PromptTemplate]:
        """
        Search templates by name, category, or tags

        Args:
            query: Search query

        Returns:
            List of matching PromptTemplate objects
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            search_pattern = f"%{query}%"

            cursor.execute("""
                SELECT * FROM templates
                WHERE name LIKE ?
                   OR category LIKE ?
                   OR tags LIKE ?
                   OR base_style LIKE ?
                ORDER BY usage_count DESC, name ASC
            """, (search_pattern, search_pattern, search_pattern, search_pattern))

            rows = cursor.fetchall()
            conn.close()

            templates = [self._row_to_template(row) for row in rows]

            logger.debug(f"Found {len(templates)} templates matching '{query}'")
            return templates

        except Exception as e:
            logger.error(f"Failed to search templates: {e}")
            return []

    def apply_template(
        self,
        template: PromptTemplate,
        custom_prompt: str
    ) -> str:
        """
        Apply template to custom prompt

        Formula: [Custom Prompt] + [Base Style] + [Camera] + [Lighting] + [Color] + [Audio]

        Args:
            template: PromptTemplate object
            custom_prompt: User's custom prompt text

        Returns:
            Final combined prompt string
        """
        components = [
            custom_prompt.strip(),
            template.base_style.strip(),
            template.camera_movement.strip(),
            template.lighting.strip(),
            template.color_palette.strip(),
            template.audio_description.strip()
        ]

        # Filter out empty components
        components = [c for c in components if c]

        # Join with proper punctuation
        final_prompt = self._join_prompt_components(components)

        logger.info(f"Applied template '{template.name}' to custom prompt")
        logger.debug(f"Final prompt length: {len(final_prompt)} characters")

        return final_prompt

    def _join_prompt_components(self, components: List[str]) -> str:
        """
        Join prompt components with proper punctuation

        Args:
            components: List of prompt components

        Returns:
            Joined prompt string
        """
        if not components:
            return ""

        result = []

        for component in components:
            # Ensure component ends with proper punctuation
            if not component[-1] in '.!?,;:':
                component += '.'

            result.append(component)

        # Join with spaces
        return ' '.join(result)

    def increment_usage(self, template_id: int):
        """
        Increment template usage count

        Args:
            template_id: Template ID
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE templates
                SET usage_count = usage_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (template_id,))

            conn.commit()
            conn.close()

            logger.debug(f"Incremented usage count for template {template_id}")

        except Exception as e:
            logger.error(f"Failed to increment usage for template {template_id}: {e}")

    def toggle_favorite(self, template_id: int) -> bool:
        """
        Toggle favorite status of template

        Args:
            template_id: Template ID

        Returns:
            New favorite status (True/False)

        Raises:
            ValueError: If template not found
        """
        try:
            template = self.get_template(template_id)
            if not template:
                raise ValueError(f"Template not found: {template_id}")

            new_status = not template.is_favorite

            self.update_template(template_id, {'is_favorite': new_status})

            logger.info(f"Template {template_id} favorite status: {new_status}")
            return new_status

        except Exception as e:
            logger.error(f"Failed to toggle favorite for template {template_id}: {e}")
            raise

    def get_most_used_templates(self, limit: int = 10) -> List[PromptTemplate]:
        """
        Get most frequently used templates

        Args:
            limit: Maximum number of templates to return

        Returns:
            List of most used PromptTemplate objects
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM templates
                WHERE usage_count > 0
                ORDER BY usage_count DESC, name ASC
                LIMIT ?
            """, (limit,))

            rows = cursor.fetchall()
            conn.close()

            templates = [self._row_to_template(row) for row in rows]

            logger.debug(f"Retrieved {len(templates)} most used templates")
            return templates

        except Exception as e:
            logger.error(f"Failed to get most used templates: {e}")
            return []

    def export_template(self, template_id: int) -> Dict[str, Any]:
        """
        Export template as dictionary for sharing

        Args:
            template_id: Template ID

        Returns:
            Template data dictionary

        Raises:
            ValueError: If template not found
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        return template.to_dict()

    def import_template(self, template_data: Dict[str, Any]) -> int:
        """
        Import template from dictionary

        Args:
            template_data: Template data dictionary

        Returns:
            New template ID
        """
        # Remove id if present (will be auto-generated)
        if 'id' in template_data:
            del template_data['id']

        # Reset usage count and favorite for imported templates
        template_data['usage_count'] = 0
        template_data['is_favorite'] = False

        return self.create_template(template_data)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get template usage statistics

        Returns:
            Dictionary with statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            stats = {}

            # Total templates
            cursor.execute("SELECT COUNT(*) FROM templates")
            stats['total_templates'] = cursor.fetchone()[0]

            # Total usage
            cursor.execute("SELECT SUM(usage_count) FROM templates")
            stats['total_usage'] = cursor.fetchone()[0] or 0

            # Favorite count
            cursor.execute("SELECT COUNT(*) FROM templates WHERE is_favorite = 1")
            stats['favorite_count'] = cursor.fetchone()[0]

            # Categories
            cursor.execute("SELECT COUNT(DISTINCT category) FROM templates")
            stats['category_count'] = cursor.fetchone()[0]

            # Most used template
            cursor.execute("""
                SELECT name, usage_count FROM templates
                ORDER BY usage_count DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                stats['most_used_template'] = {'name': row[0], 'usage_count': row[1]}
            else:
                stats['most_used_template'] = None

            conn.close()

            logger.debug(f"Retrieved template statistics: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}


# Singleton instance
_template_manager: Optional[TemplateManager] = None


def get_template_manager(db_path: Optional[str] = None) -> TemplateManager:
    """
    Get singleton TemplateManager instance

    Args:
        db_path: Database path (optional)

    Returns:
        TemplateManager instance
    """
    global _template_manager

    if _template_manager is None:
        _template_manager = TemplateManager(db_path)

    return _template_manager


# Export
__all__ = ['PromptTemplate', 'TemplateManager', 'get_template_manager']
