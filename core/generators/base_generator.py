"""
Base Generator Class
Shared functionality cho tất cả generators
"""

import asyncio
from typing import Callable, Optional, Dict, Any
from enum import Enum
from datetime import datetime

from utils import get_logger

logger = get_logger(__name__)


class GenerationStatus(Enum):
    """Trạng thái generation"""
    PENDING = "pending"
    PROCESSING = "processing"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GenerationError(Exception):
    """Base exception cho generation errors"""
    pass


class APIQuotaExceededError(GenerationError):
    """API quota exceeded"""
    pass


class GenerationTimeoutError(GenerationError):
    """Generation timeout"""
    pass


class GenerationFailedError(GenerationError):
    """Generation failed"""
    pass


class BaseGenerator:
    """
    Base class cho tất cả generators
    Cung cấp shared functionality: retry logic, progress tracking, error handling
    """

    def __init__(self, api_client, db_manager=None):
        """
        Khởi tạo Base Generator

        Args:
            api_client: VeoAPIClient instance
            db_manager: DatabaseManager instance (optional)
        """
        self.api_client = api_client
        self.db_manager = db_manager
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        self.timeout = 300  # 5 minutes

        logger.info(f"{self.__class__.__name__} initialized")

    async def emit_progress(
        self,
        progress: int,
        status: str,
        callback: Optional[Callable] = None
    ):
        """
        Emit progress update

        Args:
            progress: Progress percentage (0-100)
            status: Status message
            callback: Progress callback function
        """
        if callback:
            try:
                # If callback is async
                if asyncio.iscoroutinefunction(callback):
                    await callback(progress, status)
                else:
                    callback(progress, status)

                logger.debug(f"Progress: {progress}% - {status}")
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")

    async def retry_on_error(
        self,
        func: Callable,
        *args,
        max_retries: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        Retry function on error

        Args:
            func: Async function to retry
            *args: Function arguments
            max_retries: Max retry attempts (default: self.max_retries)
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Last exception if all retries fail
        """
        if max_retries is None:
            max_retries = self.max_retries

        last_exception = None

        for attempt in range(max_retries):
            try:
                logger.debug(f"Attempt {attempt + 1}/{max_retries}")
                result = await func(*args, **kwargs)
                return result

            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")

                if attempt < max_retries - 1:
                    delay = self.retry_delay * (attempt + 1)  # Exponential backoff
                    logger.info(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {max_retries} attempts failed")

        # All retries failed
        raise last_exception

    def validate_config(self, config: Dict[str, Any], required_keys: list) -> bool:
        """
        Validate configuration dictionary

        Args:
            config: Configuration dict
            required_keys: List of required keys

        Returns:
            bool: True if valid

        Raises:
            ValueError: If validation fails
        """
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required config key: {key}")

        return True

    def create_generation_record(
        self,
        prompt: str,
        model: str,
        config: Dict[str, Any]
    ) -> Optional[int]:
        """
        Create generation record in database

        Args:
            prompt: Generation prompt
            model: Model name
            config: Generation config

        Returns:
            int: Generation ID, or None if no database
        """
        if not self.db_manager:
            return None

        try:
            generation_id = self.db_manager.save_video_generation({
                'prompt': prompt,
                'model': model,
                'status': GenerationStatus.PENDING.value,
                'config': config,
                'created_at': datetime.now().isoformat()
            })

            logger.info(f"Created generation record: {generation_id}")
            return generation_id

        except Exception as e:
            logger.error(f"Error creating generation record: {e}")
            return None

    def update_generation_record(
        self,
        generation_id: int,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update generation record

        Args:
            generation_id: Generation ID
            updates: Updates dict

        Returns:
            bool: True if successful
        """
        if not self.db_manager or not generation_id:
            return False

        try:
            updates['updated_at'] = datetime.now().isoformat()
            # TODO: Implement update_video_generation in database
            logger.debug(f"Updated generation {generation_id}: {updates}")
            return True

        except Exception as e:
            logger.error(f"Error updating generation record: {e}")
            return False


# ===== EXPORT =====
__all__ = [
    'BaseGenerator',
    'GenerationStatus',
    'GenerationError',
    'APIQuotaExceededError',
    'GenerationTimeoutError',
    'GenerationFailedError'
]
