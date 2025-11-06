"""
Scene Manager
Manages multi-scene video generation and merging
"""

import asyncio
import subprocess
import shutil
import time
from pathlib import Path
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime
import json

from PIL import Image

from utils import get_logger
from core.api_client import VeoAPIClient
from core.database import DatabaseManager
from core.generators import TextToVideoGenerator, ImageToVideoGenerator
from config import settings

logger = get_logger(__name__)


class SceneGenerationError(Exception):
    """Error during scene generation"""
    pass


class VideoMergeError(Exception):
    """Error during video merging"""
    pass


class SceneManager:
    """
    Manages multi-scene video projects

    Features:
    - Sequential scene generation with chaining
    - Global template application
    - Progress tracking
    - Error recovery
    - Video merging with ffmpeg
    - Frame extraction
    """

    def __init__(
        self,
        api_client: VeoAPIClient,
        db_manager: Optional[DatabaseManager] = None
    ):
        """
        Initialize Scene Manager

        Args:
            api_client: Veo API client
            db_manager: Optional database manager
        """
        self.api_client = api_client
        self.db_manager = db_manager

        # Create generators
        self.text_generator = TextToVideoGenerator(api_client, db_manager)
        self.image_generator = ImageToVideoGenerator(api_client, db_manager)

        # Output directories
        self.scenes_dir = Path("outputs/scenes")
        self.merged_dir = Path("outputs/merged")
        self.frames_dir = Path("outputs/frames")

        # Create directories
        self.scenes_dir.mkdir(parents=True, exist_ok=True)
        self.merged_dir.mkdir(parents=True, exist_ok=True)
        self.frames_dir.mkdir(parents=True, exist_ok=True)

        # Check ffmpeg availability
        self.ffmpeg_available = self._check_ffmpeg()

        logger.info("SceneManager initialized")

    def _check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            available = result.returncode == 0
            if available:
                logger.info("ffmpeg is available")
            else:
                logger.warning("ffmpeg not found - video merging will be limited")
            return available
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.warning("ffmpeg not found - video merging will be limited")
            return False

    # ===== TEMPLATE APPLICATION =====

    def apply_global_template(
        self,
        scene_prompt: str,
        global_template: str
    ) -> str:
        """
        Apply global style template to scene prompt

        Args:
            scene_prompt: Scene-specific prompt
            global_template: Global style template

        Returns:
            Combined prompt

        Example:
            scene_prompt = "A person walks in the park"
            global_template = "cinematic, dramatic lighting"
            → "A person walks in the park. cinematic, dramatic lighting"
        """
        if not global_template or not global_template.strip():
            return scene_prompt

        # Clean up inputs
        scene_prompt = scene_prompt.strip()
        global_template = global_template.strip()

        # Combine with proper punctuation
        if scene_prompt and global_template:
            # Add period if scene_prompt doesn't end with punctuation
            if not scene_prompt[-1] in '.!?':
                scene_prompt += '.'

            combined = f"{scene_prompt} {global_template}"
            logger.debug(f"Applied template: '{scene_prompt}' + '{global_template}' → '{combined}'")
            return combined

        return scene_prompt

    # ===== SINGLE SCENE GENERATION =====

    async def generate_single_scene(
        self,
        scene_data: Dict[str, Any],
        previous_video_path: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Generate a single scene

        Args:
            scene_data: Scene configuration
                {
                    'scene_id': int,
                    'scene_index': int,
                    'project_name': str,
                    'prompt': str,
                    'model': str,
                    'config': dict,
                    'reference_images': List[str],
                    'use_previous_frame': bool,
                    'extend_from_previous': bool,
                    'first_frame': str,
                    'last_frame': str
                }
            previous_video_path: Path to previous scene's video (for chaining)
            progress_callback: Async progress callback

        Returns:
            {
                'status': 'success' | 'error',
                'scene_id': int,
                'video_path': str,
                'duration': float,
                'error': str (if failed)
            }
        """
        scene_id = scene_data.get('scene_id')
        scene_index = scene_data.get('scene_index', 0)
        project_name = scene_data.get('project_name', 'untitled')

        logger.info(f"Generating scene {scene_id} (index {scene_index})")

        try:
            # Determine generation type
            use_image = False
            source_image = None
            first_frame = scene_data.get('first_frame')
            last_frame = scene_data.get('last_frame')
            use_previous_frame = scene_data.get('use_previous_frame', False)
            extend_from_previous = scene_data.get('extend_from_previous', False)

            # Handle chaining from previous scene
            if scene_index > 0 and previous_video_path:
                if use_previous_frame:
                    # Extract last frame from previous video
                    logger.info(f"Extracting last frame from previous video: {previous_video_path}")
                    first_frame = await self.extract_last_frame(
                        previous_video_path,
                        scene_id=scene_id
                    )
                    use_image = True
                    source_image = first_frame

                elif extend_from_previous:
                    # Use previous video for extension
                    # Note: This would require API support for video-to-video
                    logger.info(f"Extending from previous video: {previous_video_path}")
                    # For now, extract last frame as fallback
                    first_frame = await self.extract_last_frame(
                        previous_video_path,
                        scene_id=scene_id
                    )
                    use_image = True
                    source_image = first_frame

            # Check if transition mode (first + last frame)
            elif first_frame and last_frame:
                use_image = True
                # Will use transition mode

            # Check if there's a source image
            elif first_frame:
                use_image = True
                source_image = first_frame

            # Generate scene
            if use_image:
                result = await self._generate_image_scene(
                    scene_data,
                    source_image=source_image or first_frame,
                    last_frame=last_frame,
                    progress_callback=progress_callback
                )
            else:
                result = await self._generate_text_scene(
                    scene_data,
                    progress_callback=progress_callback
                )

            if result['status'] == 'success':
                logger.success(f"Scene {scene_id} generated successfully: {result['video_path']}")
            else:
                logger.error(f"Scene {scene_id} generation failed: {result.get('error')}")

            # Add scene metadata
            result['scene_id'] = scene_id
            result['scene_index'] = scene_index

            return result

        except Exception as e:
            logger.error(f"Error generating scene {scene_id}: {e}", exc_info=True)
            return {
                'status': 'error',
                'scene_id': scene_id,
                'scene_index': scene_index,
                'error': str(e)
            }

    async def _generate_text_scene(
        self,
        scene_data: Dict[str, Any],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Generate scene from text prompt"""
        logger.info("Generating scene from text prompt")

        result = await self.text_generator.generate_video(
            prompt=scene_data['prompt'],
            model=scene_data['model'],
            config=scene_data['config'],
            progress_callback=progress_callback
        )

        return result

    async def _generate_image_scene(
        self,
        scene_data: Dict[str, Any],
        source_image: str,
        last_frame: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Generate scene from image(s)"""

        # Check if transition mode (first + last frame)
        if last_frame:
            logger.info("Generating scene with transition mode (first → last frame)")
            result = await self.image_generator.generate_with_frames(
                first_frame_path=source_image,
                last_frame_path=last_frame,
                prompt=scene_data['prompt'],
                model=scene_data['model'],
                config=scene_data['config'],
                progress_callback=progress_callback
            )
        else:
            logger.info("Generating scene from image")
            result = await self.image_generator.generate_from_image(
                image_path=source_image,
                prompt=scene_data['prompt'],
                model=scene_data['model'],
                config=scene_data['config'],
                reference_images=scene_data.get('reference_images'),
                progress_callback=progress_callback
            )

        return result

    # ===== SCENE SEQUENCE GENERATION =====

    async def generate_scene_sequence(
        self,
        project_id: int,
        scenes: List[Dict[str, Any]],
        global_template: str = "",
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate a sequence of scenes with chaining support

        Args:
            project_id: Project ID for tracking
            scenes: List of scene configurations
            global_template: Global style template to apply to all scenes
            progress_callback: Async callback(scene_index, total_scenes, status, message)

        Returns:
            List of generation results

        Process:
        1. Apply global template to each scene
        2. Generate scenes sequentially (required for chaining)
        3. Track progress
        4. Handle errors gracefully
        5. Return all results
        """
        logger.info(f"Starting scene sequence generation: {len(scenes)} scenes")

        results = []
        previous_video_path = None

        total_scenes = len(scenes)

        for i, scene_data in enumerate(scenes):
            scene_id = scene_data.get('scene_id', i + 1)

            # Emit progress
            if progress_callback:
                await progress_callback(
                    i,
                    total_scenes,
                    'processing',
                    f"Generating scene {scene_id}..."
                )

            try:
                # Apply global template to prompt
                if global_template:
                    original_prompt = scene_data['prompt']
                    scene_data['prompt'] = self.apply_global_template(
                        original_prompt,
                        global_template
                    )
                    logger.debug(f"Scene {scene_id} prompt with template: {scene_data['prompt']}")

                # Generate scene
                result = await self.generate_single_scene(
                    scene_data=scene_data,
                    previous_video_path=previous_video_path,
                    progress_callback=lambda p, s: self._scene_progress_wrapper(
                        progress_callback,
                        i,
                        total_scenes,
                        scene_id,
                        p,
                        s
                    ) if progress_callback else None
                )

                # Track result
                results.append(result)

                # Update previous video path for chaining
                if result['status'] == 'success':
                    previous_video_path = result.get('video_path')

                    # Emit completion
                    if progress_callback:
                        await progress_callback(
                            i + 1,
                            total_scenes,
                            'completed',
                            f"Scene {scene_id} completed"
                        )
                else:
                    # Scene failed
                    logger.error(f"Scene {scene_id} failed: {result.get('error')}")

                    # Emit failure
                    if progress_callback:
                        await progress_callback(
                            i + 1,
                            total_scenes,
                            'failed',
                            f"Scene {scene_id} failed: {result.get('error', 'Unknown error')}"
                        )

                    # Don't use failed scene for chaining
                    # Previous video path remains from last successful scene

            except Exception as e:
                logger.error(f"Error in scene sequence at scene {scene_id}: {e}", exc_info=True)

                # Record error
                results.append({
                    'status': 'error',
                    'scene_id': scene_id,
                    'scene_index': i,
                    'error': str(e)
                })

                # Emit error
                if progress_callback:
                    await progress_callback(
                        i + 1,
                        total_scenes,
                        'error',
                        f"Scene {scene_id} error: {str(e)}"
                    )

        # Final progress
        if progress_callback:
            successful = sum(1 for r in results if r['status'] == 'success')
            await progress_callback(
                total_scenes,
                total_scenes,
                'done',
                f"Sequence complete: {successful}/{total_scenes} scenes successful"
            )

        logger.info(
            f"Scene sequence generation complete: "
            f"{sum(1 for r in results if r['status'] == 'success')}/{total_scenes} successful"
        )

        return results

    async def _scene_progress_wrapper(
        self,
        progress_callback: Callable,
        scene_index: int,
        total_scenes: int,
        scene_id: int,
        progress: int,
        status: str
    ):
        """Wrap scene progress to include sequence context"""
        await progress_callback(
            scene_index,
            total_scenes,
            'processing',
            f"Scene {scene_id}: {progress}% - {status}"
        )

    # ===== FRAME EXTRACTION =====

    async def extract_last_frame(
        self,
        video_path: str,
        scene_id: Optional[int] = None,
        output_dir: Optional[Path] = None
    ) -> str:
        """
        Extract last frame from video

        Args:
            video_path: Path to video file
            scene_id: Scene ID for naming
            output_dir: Output directory (default: frames_dir)

        Returns:
            Path to extracted frame image

        Uses ffmpeg to extract the last frame
        """
        if not self.ffmpeg_available:
            raise VideoMergeError("ffmpeg not available for frame extraction")

        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        output_dir = output_dir or self.frames_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scene_prefix = f"scene{scene_id}_" if scene_id else ""
        output_path = output_dir / f"{scene_prefix}last_frame_{timestamp}.jpg"

        logger.info(f"Extracting last frame from {video_path.name}")

        try:
            # Use ffmpeg to extract last frame
            # Get video duration first
            duration_cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(video_path)
            ]

            duration_result = subprocess.run(
                duration_cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if duration_result.returncode != 0:
                raise VideoMergeError(f"Failed to get video duration: {duration_result.stderr}")

            duration = float(duration_result.stdout.strip())
            logger.debug(f"Video duration: {duration}s")

            # Extract frame from last second
            extract_cmd = [
                'ffmpeg',
                '-ss', str(max(0, duration - 0.1)),  # 0.1s before end
                '-i', str(video_path),
                '-vframes', '1',
                '-q:v', '2',  # High quality
                '-y',  # Overwrite
                str(output_path)
            ]

            extract_result = subprocess.run(
                extract_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if extract_result.returncode != 0:
                raise VideoMergeError(f"Failed to extract frame: {extract_result.stderr}")

            if not output_path.exists():
                raise VideoMergeError("Frame extraction failed - output file not created")

            logger.success(f"Last frame extracted: {output_path}")
            return str(output_path)

        except subprocess.TimeoutExpired:
            raise VideoMergeError("Frame extraction timed out")
        except Exception as e:
            logger.error(f"Error extracting frame: {e}")
            raise VideoMergeError(f"Frame extraction failed: {e}")

    async def extract_frame_at_time(
        self,
        video_path: str,
        time_seconds: float,
        output_path: Optional[str] = None
    ) -> str:
        """
        Extract frame at specific time

        Args:
            video_path: Path to video file
            time_seconds: Time in seconds
            output_path: Output path (auto-generated if not provided)

        Returns:
            Path to extracted frame
        """
        if not self.ffmpeg_available:
            raise VideoMergeError("ffmpeg not available for frame extraction")

        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        # Generate output path if not provided
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.frames_dir / f"frame_{time_seconds}s_{timestamp}.jpg"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Extracting frame at {time_seconds}s from {video_path.name}")

        try:
            cmd = [
                'ffmpeg',
                '-ss', str(time_seconds),
                '-i', str(video_path),
                '-vframes', '1',
                '-q:v', '2',
                '-y',
                str(output_path)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                raise VideoMergeError(f"Failed to extract frame: {result.stderr}")

            if not output_path.exists():
                raise VideoMergeError("Frame extraction failed")

            logger.success(f"Frame extracted: {output_path}")
            return str(output_path)

        except subprocess.TimeoutExpired:
            raise VideoMergeError("Frame extraction timed out")
        except Exception as e:
            logger.error(f"Error extracting frame: {e}")
            raise VideoMergeError(f"Frame extraction failed: {e}")

    # ===== VIDEO MERGING =====

    async def merge_videos(
        self,
        video_paths: List[str],
        output_path: Optional[str] = None,
        add_transitions: bool = False,
        transition_duration: float = 0.5
    ) -> str:
        """
        Merge multiple videos into one

        Args:
            video_paths: List of video file paths (in order)
            output_path: Output file path (auto-generated if not provided)
            add_transitions: Add crossfade transitions between scenes
            transition_duration: Transition duration in seconds

        Returns:
            Path to merged video

        Uses ffmpeg concat filter for simple concatenation
        or complex filter for transitions
        """
        if not self.ffmpeg_available:
            raise VideoMergeError("ffmpeg not available for video merging")

        if not video_paths:
            raise ValueError("No videos to merge")

        # Validate all videos exist
        for path in video_paths:
            if not Path(path).exists():
                raise FileNotFoundError(f"Video not found: {path}")

        # Generate output path if not provided
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.merged_dir / f"merged_{timestamp}.mp4"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Merging {len(video_paths)} videos")
        logger.debug(f"Videos: {[Path(p).name for p in video_paths]}")

        try:
            if add_transitions and len(video_paths) > 1:
                # Use complex filter for transitions
                result_path = await self._merge_with_transitions(
                    video_paths,
                    output_path,
                    transition_duration
                )
            else:
                # Simple concatenation
                result_path = await self._merge_simple(
                    video_paths,
                    output_path
                )

            logger.success(f"Videos merged successfully: {result_path}")
            return str(result_path)

        except Exception as e:
            logger.error(f"Error merging videos: {e}")
            raise VideoMergeError(f"Video merge failed: {e}")

    async def _merge_simple(
        self,
        video_paths: List[str],
        output_path: Path
    ) -> Path:
        """
        Simple video concatenation without transitions

        Creates a concat file and uses ffmpeg concat demuxer
        """
        # Create temporary concat file
        concat_file = self.merged_dir / "concat_list.txt"

        try:
            # Write concat file
            with open(concat_file, 'w', encoding='utf-8') as f:
                for video_path in video_paths:
                    # Use absolute paths
                    abs_path = Path(video_path).absolute()
                    # Escape single quotes in path
                    escaped_path = str(abs_path).replace("'", "'\\''")
                    f.write(f"file '{escaped_path}'\n")

            logger.debug(f"Concat file created: {concat_file}")

            # Run ffmpeg concat
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file),
                '-c', 'copy',  # Copy streams without re-encoding
                '-y',
                str(output_path)
            ]

            logger.debug(f"Running ffmpeg: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )

            if result.returncode != 0:
                logger.error(f"ffmpeg stderr: {result.stderr}")
                raise VideoMergeError(f"ffmpeg failed: {result.stderr}")

            if not output_path.exists():
                raise VideoMergeError("Merge failed - output file not created")

            return output_path

        finally:
            # Clean up concat file
            if concat_file.exists():
                concat_file.unlink()

    async def _merge_with_transitions(
        self,
        video_paths: List[str],
        output_path: Path,
        transition_duration: float
    ) -> Path:
        """
        Merge videos with crossfade transitions

        Uses ffmpeg complex filter with xfade
        """
        logger.info(f"Merging with {transition_duration}s transitions")

        # Build complex filter
        # This is complex - for now, fall back to simple merge
        # TODO: Implement proper xfade filter chain

        logger.warning("Transitions not yet implemented - using simple merge")
        return await self._merge_simple(video_paths, output_path)

    async def generate_thumbnail(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        time_seconds: float = 1.0
    ) -> str:
        """
        Generate thumbnail from video

        Args:
            video_path: Path to video
            output_path: Output path for thumbnail
            time_seconds: Time to capture thumbnail (default: 1.0s)

        Returns:
            Path to thumbnail image
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.frames_dir / f"thumb_{timestamp}.jpg"

        # Extract frame at specified time
        frame_path = await self.extract_frame_at_time(
            video_path,
            time_seconds,
            output_path
        )

        # Optionally resize to thumbnail size
        try:
            img = Image.open(frame_path)

            # Resize to max 320x180 (16:9)
            img.thumbnail((320, 180), Image.Resampling.LANCZOS)
            img.save(frame_path, quality=85, optimize=True)

            logger.info(f"Thumbnail generated: {frame_path}")

        except Exception as e:
            logger.warning(f"Could not resize thumbnail: {e}")

        return str(frame_path)

    # ===== UTILITY METHODS =====

    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Get video information using ffprobe

        Args:
            video_path: Path to video file

        Returns:
            {
                'duration': float,
                'width': int,
                'height': int,
                'fps': float,
                'codec': str
            }
        """
        if not self.ffmpeg_available:
            raise VideoMergeError("ffmpeg/ffprobe not available")

        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height,r_frame_rate,codec_name:format=duration',
                '-of', 'json',
                str(video_path)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                raise VideoMergeError(f"ffprobe failed: {result.stderr}")

            data = json.loads(result.stdout)

            # Parse frame rate (e.g., "30/1" → 30.0)
            fps_str = data['streams'][0].get('r_frame_rate', '30/1')
            if '/' in fps_str:
                num, den = fps_str.split('/')
                fps = float(num) / float(den)
            else:
                fps = float(fps_str)

            return {
                'duration': float(data['format']['duration']),
                'width': int(data['streams'][0]['width']),
                'height': int(data['streams'][0]['height']),
                'fps': fps,
                'codec': data['streams'][0].get('codec_name', 'unknown')
            }

        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            raise VideoMergeError(f"Failed to get video info: {e}")

    def validate_videos_compatible(self, video_paths: List[str]) -> bool:
        """
        Check if videos are compatible for merging

        Args:
            video_paths: List of video paths

        Returns:
            True if compatible, False otherwise

        Checks:
        - Same resolution
        - Same frame rate
        - Same codec (preferred but not required)
        """
        if len(video_paths) < 2:
            return True

        try:
            infos = [self.get_video_info(path) for path in video_paths]

            # Check resolution
            first_res = (infos[0]['width'], infos[0]['height'])
            if not all((info['width'], info['height']) == first_res for info in infos):
                logger.warning("Videos have different resolutions - merge may fail")
                return False

            # Check frame rate
            first_fps = infos[0]['fps']
            if not all(abs(info['fps'] - first_fps) < 0.1 for info in infos):
                logger.warning("Videos have different frame rates - merge may have issues")
                return False

            logger.info("Videos are compatible for merging")
            return True

        except Exception as e:
            logger.error(f"Error validating videos: {e}")
            return False
