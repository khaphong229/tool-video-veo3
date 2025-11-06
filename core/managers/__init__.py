"""
Managers module
High-level managers for complex operations
"""

from .scene_manager import SceneManager
from .template_manager import TemplateManager, PromptTemplate, get_template_manager

__all__ = ['SceneManager', 'TemplateManager', 'PromptTemplate', 'get_template_manager']
