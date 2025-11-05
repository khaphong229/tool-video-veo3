"""
Text to Video Generator
Generates videos from text prompts using Google Veo API
"""

import asyncio
import aiohttp
from typing import Callable, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import time

from config import settings
from utils import get_logger
from .base_generator import (
    BaseGenerator,
    GenerationStatus,
    GenerationError,
    APIQuotaExceededError,
    GenerationTimeoutError,
    GenerationFailedError
)

logger = get_logger(__name__)


class TextToVideoGenerator(BaseGenerator):
    """
    Text to Video Generator

    Tạo video từ text prompts sử dụng Google Veo API
    với progress tracking, error handling, và database integration
    """

    def __init__(self, api_client, db_manager=None):
        """
        Khởi tạo Text to Video Generator

        Args:
            api_client: VeoAPIClient instance
            db_manager: DatabaseManager instance (optional)
        """
        super().__init__(api_client, db_manager)

        # Configuration
        self.poll_interval = 2  # seconds
        self.max_poll_attempts = 150  # 5 minutes / 2 seconds
        self.download_timeout = 60  # seconds

        logger.info("TextToVideoGenerator initialized")

    async def generate_video(
        self,
        prompt: str,
        model: str,
        config: Dict[str, Any],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Generate video from text prompt

        Args:
            prompt: Text prompt describing the video
            model: Model name to use
            config: Generation configuration
                {
                    'aspect_ratio': str,
                    'duration': int,
                    'resolution': str,
                    'negative_prompt': str (optional),
                    'seed': int (optional),
                    'enable_audio': bool (optional)
                }
            progress_callback: Progress callback function(progress: int, status: str)

        Returns:
            dict: Generation result
            {
                'status': str,
                'video_path': str,
                'operation_id': str,
                'duration': float,
                'error': str (if failed)
            }

        Raises:
            GenerationError: If generation fails
        """
        start_time = time.time()

        try:
            # Validate inputs
            self._validate_inputs(prompt, model, config)

            # Create database record
            generation_id = self.create_generation_record(prompt, model, config)

            # Stage 1: Starting generation (0%)
            await self.emit_progress(0, "Starting generation...", progress_callback)

            # Stage 2: Send request (10%)
            await self.emit_progress(10, "Sending request to API...", progress_callback)

            operation_id = await self._send_generation_request(
                prompt,
                model,
                config
            )

            logger.info(f"Generation started. Operation ID: {operation_id}")

            # Update database
            self.update_generation_record(generation_id, {
                'operation_id': operation_id,
                'status': GenerationStatus.PROCESSING.value
            })

            # Stage 3: Processing (20-80%)
            await self.emit_progress(20, "Processing video generation...", progress_callback)

            result = await self.check_operation_status(
                operation_id,
                progress_callback
            )

            # Stage 4: Downloading (90%)
            await self.emit_progress(90, "Downloading video...", progress_callback)

            video_path = await self._download_video(
                result['video_url'],
                prompt,
                config
            )

            # Stage 5: Complete (100%)
            await self.emit_progress(100, "Complete!", progress_callback)

            elapsed_time = time.time() - start_time

            # Update database
            self.update_generation_record(generation_id, {
                'status': GenerationStatus.COMPLETED.value,
                'video_path': str(video_path),
                'duration': elapsed_time
            })

            logger.info(f"Video generation completed in {elapsed_time:.2f}s")

            return {
                'status': 'success',
                'video_path': str(video_path),
                'operation_id': operation_id,
                'duration': elapsed_time,
                'generation_id': generation_id
            }

        except APIQuotaExceededError as e:
            logger.error(f"API quota exceeded: {e}")
            await self.emit_progress(0, f"Error: API quota exceeded", progress_callback)

            self.update_generation_record(generation_id, {
                'status': GenerationStatus.FAILED.value,
                'error': str(e)
            })

            return {
                'status': 'error',
                'error': 'API quota exceeded. Please check your quota and try again later.',
                'error_type': 'quota_exceeded'
            }

        except GenerationTimeoutError as e:
            logger.error(f"Generation timeout: {e}")
            await self.emit_progress(0, f"Error: Timeout", progress_callback)

            self.update_generation_record(generation_id, {
                'status': GenerationStatus.FAILED.value,
                'error': str(e)
            })

            return {
                'status': 'error',
                'error': 'Generation timed out. Please try again.',
                'error_type': 'timeout'
            }

        except GenerationFailedError as e:
            logger.error(f"Generation failed: {e}")
            await self.emit_progress(0, f"Error: Generation failed", progress_callback)

            self.update_generation_record(generation_id, {
                'status': GenerationStatus.FAILED.value,
                'error': str(e)
            })

            return {
                'status': 'error',
                'error': str(e),
                'error_type': 'generation_failed'
            }

        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            await self.emit_progress(0, f"Error: {str(e)}", progress_callback)

            self.update_generation_record(generation_id, {
                'status': GenerationStatus.FAILED.value,
                'error': str(e)
            })

            return {
                'status': 'error',
                'error': f'Unexpected error: {str(e)}',
                'error_type': 'unknown'
            }

    async def check_operation_status(
        self,
        operation_id: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Check operation status với polling

        Args:
            operation_id: Operation ID
            progress_callback: Progress callback

        Returns:
            dict: Operation result
            {
                'status': str,
                'video_url': str,
                'metadata': dict
            }

        Raises:
            GenerationTimeoutError: If timeout
            GenerationFailedError: If generation failed
        """
        logger.info(f"Checking status for operation: {operation_id}")

        start_time = time.time()
        attempt = 0

        while attempt < self.max_poll_attempts:
            try:
                # Check elapsed time
                elapsed = time.time() - start_time
                if elapsed > self.timeout:
                    raise GenerationTimeoutError(
                        f"Operation timed out after {self.timeout}s"
                    )

                # Poll status
                status_response = await self._poll_operation_status(operation_id)

                # Calculate progress (20-80%)
                progress = 20 + int((attempt / self.max_poll_attempts) * 60)
                progress = min(progress, 80)

                # Check status
                if status_response['status'] == 'completed':
                    logger.info(f"Operation completed: {operation_id}")

                    await self.emit_progress(
                        80,
                        "Video generation complete!",
                        progress_callback
                    )

                    return status_response

                elif status_response['status'] == 'failed':
                    error_msg = status_response.get('error', 'Unknown error')
                    raise GenerationFailedError(f"Generation failed: {error_msg}")

                elif status_response['status'] == 'processing':
                    stage = status_response.get('stage', 'Processing')
                    await self.emit_progress(
                        progress,
                        f"{stage}...",
                        progress_callback
                    )

                else:
                    # Unknown status
                    logger.warning(f"Unknown status: {status_response['status']}")

                # Wait before next poll
                await asyncio.sleep(self.poll_interval)
                attempt += 1

            except (GenerationTimeoutError, GenerationFailedError):
                raise

            except Exception as e:
                logger.error(f"Error polling status: {e}")
                attempt += 1
                await asyncio.sleep(self.poll_interval)

        # Max attempts reached
        raise GenerationTimeoutError(
            f"Operation timed out after {self.max_poll_attempts} attempts"
        )

    def parse_result(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse API response

        Args:
            response: Raw API response

        Returns:
            dict: Parsed result
        """
        try:
            return {
                'status': response.get('status', 'unknown'),
                'video_url': response.get('video_url'),
                'operation_id': response.get('operation_id'),
                'metadata': response.get('metadata', {}),
                'error': response.get('error')
            }

        except Exception as e:
            logger.error(f"Error parsing result: {e}")
            return {
                'status': 'error',
                'error': f'Failed to parse response: {str(e)}'
            }

    # ===== PRIVATE METHODS =====

    def _validate_inputs(
        self,
        prompt: str,
        model: str,
        config: Dict[str, Any]
    ):
        """
        Validate generation inputs

        Raises:
            ValueError: If validation fails
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        if len(prompt) > 2000:
            raise ValueError("Prompt too long (max 2000 characters)")

        if not model:
            raise ValueError("Model cannot be empty")

        # Validate required config keys
        required_keys = ['aspect_ratio', 'duration', 'resolution']
        self.validate_config(config, required_keys)

        # Validate duration
        duration = config['duration']
        if not (settings.VIDEO_DURATION_RANGE['min'] <= duration <= settings.VIDEO_DURATION_RANGE['max']):
            raise ValueError(
                f"Duration must be between {settings.VIDEO_DURATION_RANGE['min']} "
                f"and {settings.VIDEO_DURATION_RANGE['max']} seconds"
            )

        logger.debug("Input validation passed")

    async def _send_generation_request(
        self,
        prompt: str,
        model: str,
        config: Dict[str, Any]
    ) -> str:
        """
        Send generation request to API

        Returns:
            str: Operation ID

        Raises:
            APIQuotaExceededError: If quota exceeded
            GenerationError: If request fails
        """
        try:
            # Use retry logic
            result = await self.retry_on_error(
                self._make_api_request,
                prompt,
                model,
                config
            )

            operation_id = result.get('operation_id')

            if not operation_id:
                raise GenerationError("No operation_id in response")

            return operation_id

        except Exception as e:
            # Check for quota error
            if 'quota' in str(e).lower() or 'limit' in str(e).lower():
                raise APIQuotaExceededError(str(e))

            raise GenerationError(f"Failed to send request: {str(e)}")

    async def _make_api_request(
        self,
        prompt: str,
        model: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Make actual API request

        This is a placeholder implementation.
        TODO: Implement actual Veo API call when API is available

        Returns:
            dict: API response with operation_id
        """
        logger.info(f"Making API request for model: {model}")

        # TODO: Replace with actual API call
        # For now, simulate API response

        # Simulate API delay
        await asyncio.sleep(0.5)

        # Mock operation ID
        operation_id = f"op_{int(time.time() * 1000)}"

        logger.info(f"API request successful. Operation ID: {operation_id}")

        return {
            'operation_id': operation_id,
            'status': 'processing'
        }

    async def _poll_operation_status(self, operation_id: str) -> Dict[str, Any]:
        """
        Poll operation status

        TODO: Implement actual API polling when available

        Returns:
            dict: Status response
        """
        logger.debug(f"Polling status for: {operation_id}")

        # TODO: Replace with actual API call
        # For now, simulate status check

        await asyncio.sleep(0.1)

        # Simulate progress
        # Extract timestamp from operation_id
        try:
            timestamp = int(operation_id.split('_')[1])
            elapsed = int(time.time() * 1000) - timestamp

            # Simulate completion after 5 seconds
            if elapsed > 5000:
                return {
                    'status': 'completed',
                    'video_url': f'https://example.com/videos/{operation_id}.mp4',
                    'stage': 'Complete',
                    'metadata': {
                        'duration': 5,
                        'resolution': '1080p'
                    }
                }
            else:
                # Calculate stage
                progress = elapsed / 5000
                if progress < 0.3:
                    stage = "Initializing"
                elif progress < 0.6:
                    stage = "Generating frames"
                elif progress < 0.9:
                    stage = "Rendering video"
                else:
                    stage = "Finalizing"

                return {
                    'status': 'processing',
                    'stage': stage
                }

        except:
            return {
                'status': 'processing',
                'stage': 'Processing'
            }

    async def _download_video(
        self,
        video_url: str,
        prompt: str,
        config: Dict[str, Any]
    ) -> Path:
        """
        Download video from URL

        Args:
            video_url: Video URL
            prompt: Original prompt (for filename)
            config: Generation config

        Returns:
            Path: Downloaded video path

        Raises:
            GenerationError: If download fails
        """
        try:
            logger.info(f"Downloading video from: {video_url}")

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Sanitize prompt for filename
            safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_'))
            safe_prompt = safe_prompt.replace(' ', '_')

            filename = f"{timestamp}_{safe_prompt}.mp4"
            output_path = settings.OUTPUT_DIR / filename

            # Ensure output directory exists
            settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

            # Download with timeout
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    video_url,
                    timeout=aiohttp.ClientTimeout(total=self.download_timeout)
                ) as response:

                    if response.status != 200:
                        raise GenerationError(
                            f"Download failed with status {response.status}"
                        )

                    # Download in chunks
                    with open(output_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(settings.DOWNLOAD_BUFFER_SIZE):
                            f.write(chunk)

            logger.info(f"Video downloaded successfully: {output_path}")

            return output_path

        except asyncio.TimeoutError:
            raise GenerationError("Download timeout")

        except Exception as e:
            raise GenerationError(f"Download failed: {str(e)}")

    async def cancel_generation(self, operation_id: str) -> bool:
        """
        Cancel ongoing generation

        Args:
            operation_id: Operation ID to cancel

        Returns:
            bool: True if cancelled successfully
        """
        try:
            logger.info(f"Cancelling operation: {operation_id}")

            # TODO: Implement API cancellation call

            return True

        except Exception as e:
            logger.error(f"Error cancelling generation: {e}")
            return False


# ===== EXPORT =====
__all__ = ['TextToVideoGenerator']
