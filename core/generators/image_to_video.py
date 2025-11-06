"""
Image to Video Generator
Generates videos from static images using Google Veo API
"""

import asyncio
import base64
import io
import time
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable

from PIL import Image

from utils import get_logger
from .base_generator import (
    BaseGenerator,
    GenerationStatus,
    GenerationError,
    APIQuotaExceededError,
    GenerationTimeoutError,
    GenerationFailedError
)
from ..api_client import VeoAPIClient
from ..database import DatabaseManager
from config import settings

logger = get_logger(__name__)


class ImageToVideoGenerator(BaseGenerator):
    """
    Generator for creating videos from static images

    Features:
    - Single image animation
    - First/last frame transitions
    - Reference images support (Veo 3.1)
    - Image preprocessing (resize, compress, validate)
    - Progress tracking
    - Error handling with retry
    """

    # Image constraints
    SUPPORTED_FORMATS = ['jpg', 'jpeg', 'png', 'webp', 'bmp']
    MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50 MB
    MAX_COMPRESSED_SIZE = 5 * 1024 * 1024  # 5 MB (compress if larger)
    MAX_RESOLUTION = (1920, 1080)  # Max 1080p

    def __init__(
        self,
        api_client: VeoAPIClient,
        db_manager: Optional[DatabaseManager] = None
    ):
        """
        Initialize Image to Video generator

        Args:
            api_client: Veo API client instance
            db_manager: Optional database manager for tracking
        """
        super().__init__(api_client, db_manager)
        self.generation_type = 'image_to_video'

        logger.info("ImageToVideoGenerator initialized")

    async def generate_from_image(
        self,
        image_path: str,
        prompt: str,
        model: str,
        config: Dict[str, Any],
        reference_images: Optional[List[str]] = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Generate video from a single image

        Args:
            image_path: Path to source image
            prompt: Animation description
            model: Model name (veo-2.0, veo-3.1, etc.)
            config: Generation config (aspect_ratio, duration, resolution, etc.)
            reference_images: Optional list of reference image paths (max 3, Veo 3.1 only)
            progress_callback: Async callback for progress updates (progress, status)

        Returns:
            {
                'status': 'success' | 'error',
                'video_path': str,
                'operation_id': str,
                'duration': float,
                'generation_id': int,
                'error': str (if failed),
                'error_type': str (if failed)
            }
        """
        start_time = time.time()

        try:
            # Validate inputs
            self._validate_image_inputs(image_path, prompt, model, config, reference_images)

            # Create generation record
            generation_id = self.create_generation_record(
                generation_type='image_to_video',
                prompt=prompt,
                model=model,
                config={
                    **config,
                    'source_image': str(image_path),
                    'reference_images': reference_images or []
                }
            )

            await self.emit_progress(0, "Starting generation...", progress_callback)

            # Prepare source image
            logger.info(f"Preparing source image: {image_path}")
            source_image_data = self.prepare_image(image_path, config.get('aspect_ratio'))

            # Prepare reference images (if any)
            reference_data = []
            if reference_images and model in ['veo-3.1', 'veo-3.0']:
                logger.info(f"Preparing {len(reference_images)} reference images")
                for ref_path in reference_images[:3]:  # Max 3
                    ref_data = self.prepare_image(ref_path)
                    reference_data.append(ref_data)

            await self.emit_progress(10, "Sending request to API...", progress_callback)

            # Send generation request
            response = await self.retry_on_error(
                self._send_image_generation_request,
                image_data=source_image_data,
                prompt=prompt,
                model=model,
                config=config,
                reference_images=reference_data
            )

            operation_id = response.get('operation_id')
            if not operation_id:
                raise GenerationError("No operation ID returned from API")

            logger.info(f"Generation started with operation_id: {operation_id}")

            # Update generation record
            self.update_generation_record(
                generation_id,
                status='processing',
                operation_id=operation_id
            )

            # Poll for completion
            await self.emit_progress(20, "Processing image...", progress_callback)

            result = await self.check_operation_status(
                operation_id,
                progress_callback=progress_callback
            )

            if result['status'] != 'completed':
                raise GenerationFailedError(f"Generation failed: {result.get('error', 'Unknown error')}")

            # Download video
            await self.emit_progress(90, "Downloading video...", progress_callback)

            video_url = result.get('video_url')
            if not video_url:
                raise GenerationError("No video URL in response")

            # Generate filename from prompt and image
            image_name = Path(image_path).stem
            video_path = await self.download_video(
                video_url,
                prompt=f"{image_name}_{prompt}"
            )

            # Update generation record
            duration = time.time() - start_time
            self.update_generation_record(
                generation_id,
                status='completed',
                video_path=str(video_path),
                duration=duration
            )

            await self.emit_progress(100, "Complete!", progress_callback)

            logger.success(f"Image to video generation completed: {video_path}")

            return {
                'status': 'success',
                'video_path': str(video_path),
                'operation_id': operation_id,
                'duration': duration,
                'generation_id': generation_id
            }

        except (APIQuotaExceededError, GenerationTimeoutError, GenerationFailedError) as e:
            error_type = type(e).__name__
            logger.error(f"Generation failed: {error_type} - {e}")

            if generation_id:
                self.update_generation_record(
                    generation_id,
                    status='failed',
                    error=str(e)
                )

            return {
                'status': 'error',
                'error': str(e),
                'error_type': self._map_error_type(error_type)
            }

        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)

            if generation_id:
                self.update_generation_record(
                    generation_id,
                    status='failed',
                    error=str(e)
                )

            return {
                'status': 'error',
                'error': str(e),
                'error_type': 'unknown'
            }

    async def generate_with_frames(
        self,
        first_frame_path: str,
        last_frame_path: str,
        prompt: str,
        model: str,
        config: Dict[str, Any],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Generate video with first and last frame (transition mode)

        Args:
            first_frame_path: Path to first frame image
            last_frame_path: Path to last frame image
            prompt: Animation description
            model: Model name
            config: Generation config
            progress_callback: Async callback for progress updates

        Returns:
            Same format as generate_from_image()
        """
        start_time = time.time()

        try:
            # Validate inputs
            self._validate_transition_inputs(
                first_frame_path,
                last_frame_path,
                prompt,
                model,
                config
            )

            # Create generation record
            generation_id = self.create_generation_record(
                generation_type='image_to_video_transition',
                prompt=prompt,
                model=model,
                config={
                    **config,
                    'first_frame': str(first_frame_path),
                    'last_frame': str(last_frame_path),
                    'transition_mode': True
                }
            )

            await self.emit_progress(0, "Starting transition generation...", progress_callback)

            # Prepare frames
            logger.info(f"Preparing first frame: {first_frame_path}")
            first_frame_data = self.prepare_image(first_frame_path, config.get('aspect_ratio'))

            logger.info(f"Preparing last frame: {last_frame_path}")
            last_frame_data = self.prepare_image(last_frame_path, config.get('aspect_ratio'))

            # Validate frames have same dimensions
            self._validate_frame_consistency(first_frame_path, last_frame_path)

            await self.emit_progress(10, "Sending transition request...", progress_callback)

            # Send generation request
            response = await self.retry_on_error(
                self._send_transition_request,
                first_frame=first_frame_data,
                last_frame=last_frame_data,
                prompt=prompt,
                model=model,
                config=config
            )

            operation_id = response.get('operation_id')
            if not operation_id:
                raise GenerationError("No operation ID returned from API")

            logger.info(f"Transition generation started: {operation_id}")

            # Update generation record
            self.update_generation_record(
                generation_id,
                status='processing',
                operation_id=operation_id
            )

            # Poll for completion
            await self.emit_progress(20, "Generating transition...", progress_callback)

            result = await self.check_operation_status(
                operation_id,
                progress_callback=progress_callback
            )

            if result['status'] != 'completed':
                raise GenerationFailedError(f"Generation failed: {result.get('error', 'Unknown error')}")

            # Download video
            await self.emit_progress(90, "Downloading video...", progress_callback)

            video_url = result.get('video_url')
            if not video_url:
                raise GenerationError("No video URL in response")

            # Generate filename
            first_name = Path(first_frame_path).stem
            last_name = Path(last_frame_path).stem
            video_path = await self.download_video(
                video_url,
                prompt=f"{first_name}_to_{last_name}_{prompt}"
            )

            # Update generation record
            duration = time.time() - start_time
            self.update_generation_record(
                generation_id,
                status='completed',
                video_path=str(video_path),
                duration=duration
            )

            await self.emit_progress(100, "Complete!", progress_callback)

            logger.success(f"Transition video generated: {video_path}")

            return {
                'status': 'success',
                'video_path': str(video_path),
                'operation_id': operation_id,
                'duration': duration,
                'generation_id': generation_id
            }

        except (APIQuotaExceededError, GenerationTimeoutError, GenerationFailedError) as e:
            error_type = type(e).__name__
            logger.error(f"Transition generation failed: {error_type} - {e}")

            if generation_id:
                self.update_generation_record(
                    generation_id,
                    status='failed',
                    error=str(e)
                )

            return {
                'status': 'error',
                'error': str(e),
                'error_type': self._map_error_type(error_type)
            }

        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)

            if generation_id:
                self.update_generation_record(
                    generation_id,
                    status='failed',
                    error=str(e)
                )

            return {
                'status': 'error',
                'error': str(e),
                'error_type': 'unknown'
            }

    def prepare_image(
        self,
        image_path: str,
        target_aspect_ratio: Optional[str] = None
    ) -> str:
        """
        Prepare image for API submission

        Steps:
        1. Validate format and size
        2. Load image with PIL
        3. Convert to RGB if needed
        4. Resize if resolution > 1080p
        5. Validate/adjust aspect ratio
        6. Compress if size > 5MB
        7. Encode to base64

        Args:
            image_path: Path to image file
            target_aspect_ratio: Target aspect ratio (16:9, 9:16, 1:1, 4:3)

        Returns:
            Base64-encoded image string
        """
        try:
            image_path = Path(image_path)

            # Validate file exists
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")

            # Validate format
            ext = image_path.suffix.lower().lstrip('.')
            if ext not in self.SUPPORTED_FORMATS:
                raise ValueError(
                    f"Unsupported image format: {ext}. "
                    f"Supported: {', '.join(self.SUPPORTED_FORMATS)}"
                )

            # Validate file size
            file_size = image_path.stat().st_size
            if file_size > self.MAX_IMAGE_SIZE:
                size_mb = file_size / (1024 * 1024)
                raise ValueError(
                    f"Image file too large: {size_mb:.1f}MB. "
                    f"Max size: {self.MAX_IMAGE_SIZE / (1024 * 1024):.0f}MB"
                )

            # Load image
            logger.debug(f"Loading image: {image_path}")
            img = Image.open(image_path)

            # Convert to RGB if needed
            if img.mode not in ('RGB', 'L'):
                logger.debug(f"Converting image from {img.mode} to RGB")
                img = img.convert('RGB')
            elif img.mode == 'L':
                img = img.convert('RGB')

            original_size = img.size
            logger.debug(f"Original image size: {original_size}")

            # Resize if too large
            if img.width > self.MAX_RESOLUTION[0] or img.height > self.MAX_RESOLUTION[1]:
                logger.info(f"Resizing image from {img.size} to max {self.MAX_RESOLUTION}")
                img.thumbnail(self.MAX_RESOLUTION, Image.Resampling.LANCZOS)
                logger.debug(f"Resized to: {img.size}")

            # Validate/adjust aspect ratio if specified
            if target_aspect_ratio:
                img = self._adjust_aspect_ratio(img, target_aspect_ratio)

            # Compress to base64
            output = io.BytesIO()

            # Try to keep original format, fallback to JPEG
            save_format = 'JPEG' if ext in ['jpg', 'jpeg'] else 'PNG'

            # Initial save
            if save_format == 'JPEG':
                img.save(output, format=save_format, quality=95, optimize=True)
            else:
                img.save(output, format=save_format, optimize=True)

            # Check size and compress if needed
            output_size = output.tell()

            if output_size > self.MAX_COMPRESSED_SIZE:
                logger.info(f"Image too large ({output_size / (1024*1024):.1f}MB), compressing...")

                # Progressive quality reduction
                for quality in [85, 75, 65, 55]:
                    output = io.BytesIO()
                    img.save(output, format='JPEG', quality=quality, optimize=True)
                    output_size = output.tell()

                    if output_size <= self.MAX_COMPRESSED_SIZE:
                        logger.debug(f"Compressed to {output_size / (1024*1024):.1f}MB at quality {quality}")
                        break

                if output_size > self.MAX_COMPRESSED_SIZE:
                    logger.warning(
                        f"Could not compress below {self.MAX_COMPRESSED_SIZE / (1024*1024):.0f}MB. "
                        f"Final size: {output_size / (1024*1024):.1f}MB"
                    )

            # Encode to base64
            output.seek(0)
            image_bytes = output.read()
            base64_image = base64.b64encode(image_bytes).decode('utf-8')

            logger.success(
                f"Image prepared: {image_path.name} "
                f"({original_size} -> {img.size}, "
                f"{len(base64_image) / 1024:.1f}KB encoded)"
            )

            return base64_image

        except Exception as e:
            logger.error(f"Failed to prepare image {image_path}: {e}")
            raise

    def _adjust_aspect_ratio(
        self,
        img: Image.Image,
        target_aspect: str
    ) -> Image.Image:
        """
        Adjust image to target aspect ratio by center cropping

        Args:
            img: PIL Image
            target_aspect: Aspect ratio string (16:9, 9:16, 1:1, 4:3)

        Returns:
            Cropped PIL Image
        """
        # Parse aspect ratio
        aspect_ratios = {
            '16:9': 16/9,
            '9:16': 9/16,
            '1:1': 1.0,
            '4:3': 4/3
        }

        target_ratio = aspect_ratios.get(target_aspect)
        if not target_ratio:
            logger.warning(f"Unknown aspect ratio: {target_aspect}, skipping adjustment")
            return img

        # Calculate current ratio
        current_ratio = img.width / img.height

        # Check if already close enough (within 5%)
        if abs(current_ratio - target_ratio) / target_ratio < 0.05:
            logger.debug(f"Aspect ratio already close to {target_aspect}")
            return img

        # Calculate crop dimensions
        if current_ratio > target_ratio:
            # Image is too wide, crop width
            new_width = int(img.height * target_ratio)
            new_height = img.height
            left = (img.width - new_width) // 2
            top = 0
        else:
            # Image is too tall, crop height
            new_width = img.width
            new_height = int(img.width / target_ratio)
            left = 0
            top = (img.height - new_height) // 2

        # Crop
        cropped = img.crop((
            left,
            top,
            left + new_width,
            top + new_height
        ))

        logger.info(
            f"Adjusted aspect ratio from {img.size} to {cropped.size} "
            f"({current_ratio:.2f} -> {target_ratio:.2f})"
        )

        return cropped

    def _validate_image_inputs(
        self,
        image_path: str,
        prompt: str,
        model: str,
        config: Dict[str, Any],
        reference_images: Optional[List[str]]
    ):
        """Validate inputs for image to video generation"""
        # Validate image path
        if not image_path or not Path(image_path).exists():
            raise ValueError(f"Image file not found: {image_path}")

        # Validate prompt
        if not prompt or not prompt.strip():
            raise ValueError("Animation prompt cannot be empty")

        if len(prompt) > 2000:
            raise ValueError(f"Prompt too long ({len(prompt)} chars). Max 2000 characters")

        # Validate model
        if not model:
            raise ValueError("Model must be specified")

        # Validate config
        required_keys = ['aspect_ratio', 'duration', 'resolution']
        self.validate_config(config, required_keys)

        # Validate duration
        duration = config.get('duration', 0)
        if not (2 <= duration <= 60):
            raise ValueError(f"Duration must be between 2 and 60 seconds (got {duration})")

        # Validate reference images
        if reference_images:
            if len(reference_images) > 3:
                raise ValueError(f"Maximum 3 reference images allowed (got {len(reference_images)})")

            if model not in ['veo-3.1', 'veo-3.0']:
                logger.warning(
                    f"Reference images require Veo 3.0+ (using {model}). "
                    "Reference images will be ignored."
                )

            for ref_path in reference_images:
                if not Path(ref_path).exists():
                    raise ValueError(f"Reference image not found: {ref_path}")

    def _validate_transition_inputs(
        self,
        first_frame_path: str,
        last_frame_path: str,
        prompt: str,
        model: str,
        config: Dict[str, Any]
    ):
        """Validate inputs for transition mode"""
        # Validate frames
        if not first_frame_path or not Path(first_frame_path).exists():
            raise ValueError(f"First frame not found: {first_frame_path}")

        if not last_frame_path or not Path(last_frame_path).exists():
            raise ValueError(f"Last frame not found: {last_frame_path}")

        # Validate prompt
        if not prompt or not prompt.strip():
            raise ValueError("Animation prompt cannot be empty")

        if len(prompt) > 2000:
            raise ValueError(f"Prompt too long ({len(prompt)} chars). Max 2000 characters")

        # Validate model
        if not model:
            raise ValueError("Model must be specified")

        # Validate config
        required_keys = ['aspect_ratio', 'duration', 'resolution']
        self.validate_config(config, required_keys)

        duration = config.get('duration', 0)
        if not (2 <= duration <= 60):
            raise ValueError(f"Duration must be between 2 and 60 seconds (got {duration})")

    def _validate_frame_consistency(
        self,
        first_frame_path: str,
        last_frame_path: str
    ):
        """
        Validate that first and last frames have consistent dimensions

        Args:
            first_frame_path: Path to first frame
            last_frame_path: Path to last frame

        Raises:
            ValueError: If dimensions don't match
        """
        try:
            first_img = Image.open(first_frame_path)
            last_img = Image.open(last_frame_path)

            if first_img.size != last_img.size:
                logger.warning(
                    f"Frame size mismatch: first={first_img.size}, last={last_img.size}. "
                    "Images will be resized to match."
                )

            # Close images
            first_img.close()
            last_img.close()

        except Exception as e:
            raise ValueError(f"Failed to validate frame consistency: {e}")

    async def _send_image_generation_request(
        self,
        image_data: str,
        prompt: str,
        model: str,
        config: Dict[str, Any],
        reference_images: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send image to video generation request to API

        Args:
            image_data: Base64-encoded image
            prompt: Animation prompt
            model: Model name
            config: Generation config
            reference_images: List of base64-encoded reference images

        Returns:
            API response with operation_id
        """
        request_data = {
            'type': 'image_to_video',
            'image': image_data,
            'prompt': prompt,
            'model': model,
            'config': config
        }

        if reference_images:
            request_data['reference_images'] = reference_images

        # Mock API call (replace with actual API client call)
        logger.debug(f"Sending image generation request (model: {model})")

        # Simulate API call
        await asyncio.sleep(0.5)

        return {
            'operation_id': f"img_op_{int(time.time() * 1000)}",
            'status': 'processing'
        }

    async def _send_transition_request(
        self,
        first_frame: str,
        last_frame: str,
        prompt: str,
        model: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send transition generation request to API

        Args:
            first_frame: Base64-encoded first frame
            last_frame: Base64-encoded last frame
            prompt: Animation prompt
            model: Model name
            config: Generation config

        Returns:
            API response with operation_id
        """
        request_data = {
            'type': 'transition',
            'first_frame': first_frame,
            'last_frame': last_frame,
            'prompt': prompt,
            'model': model,
            'config': config
        }

        # Mock API call (replace with actual API client call)
        logger.debug(f"Sending transition request (model: {model})")

        # Simulate API call
        await asyncio.sleep(0.5)

        return {
            'operation_id': f"trans_op_{int(time.time() * 1000)}",
            'status': 'processing'
        }

    def _map_error_type(self, error_class_name: str) -> str:
        """Map exception class name to error type string"""
        error_map = {
            'APIQuotaExceededError': 'quota_exceeded',
            'GenerationTimeoutError': 'timeout',
            'GenerationFailedError': 'generation_failed'
        }
        return error_map.get(error_class_name, 'unknown')
