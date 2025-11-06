"""
Video Merger Utility
Merge multiple video clips using FFmpeg with optional transitions
"""

import asyncio
import subprocess
import shutil
import json
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any
import tempfile
import time

from .logger import get_logger

logger = get_logger(__name__)


class VideoMergeError(Exception):
    """Error during video merging"""
    pass


class FFmpegNotFoundError(Exception):
    """FFmpeg not found in system"""
    pass


class VideoMerger:
    """
    Video merging utility using FFmpeg

    Features:
    - Merge multiple videos
    - Add crossfade transitions
    - Extract frames
    - Get video metadata
    - Progress tracking
    - Error handling
    """

    # Supported video formats
    SUPPORTED_FORMATS = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv']

    @staticmethod
    def check_ffmpeg_installed() -> bool:
        """
        Check if FFmpeg is installed and available

        Returns:
            True if FFmpeg is available, False otherwise
        """
        try:
            # Check ffmpeg
            result_ffmpeg = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Check ffprobe
            result_ffprobe = subprocess.run(
                ['ffprobe', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )

            ffmpeg_ok = result_ffmpeg.returncode == 0
            ffprobe_ok = result_ffprobe.returncode == 0

            if ffmpeg_ok and ffprobe_ok:
                logger.info("FFmpeg and FFprobe are installed and available")
                return True
            else:
                if not ffmpeg_ok:
                    logger.warning("ffmpeg not available")
                if not ffprobe_ok:
                    logger.warning("ffprobe not available")
                return False

        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.warning(f"FFmpeg check failed: {e}")
            return False

    @staticmethod
    def _validate_inputs(video_paths: List[str], output_path: str):
        """
        Validate input videos and output path

        Args:
            video_paths: List of video file paths
            output_path: Output file path

        Raises:
            ValueError: If validation fails
        """
        if not video_paths:
            raise ValueError("No video paths provided")

        if len(video_paths) < 1:
            raise ValueError("At least one video is required")

        # Check all videos exist
        for path in video_paths:
            path_obj = Path(path)
            if not path_obj.exists():
                raise FileNotFoundError(f"Video file not found: {path}")

            # Check format
            if path_obj.suffix.lower() not in VideoMerger.SUPPORTED_FORMATS:
                logger.warning(
                    f"Video format {path_obj.suffix} may not be supported. "
                    f"Supported formats: {', '.join(VideoMerger.SUPPORTED_FORMATS)}"
                )

        # Check output path
        output_path_obj = Path(output_path)
        if output_path_obj.suffix.lower() not in VideoMerger.SUPPORTED_FORMATS:
            logger.warning(
                f"Output format {output_path_obj.suffix} may not be supported"
            )

        # Create output directory if needed
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Validated {len(video_paths)} input videos")

    @staticmethod
    async def merge_videos(
        video_paths: List[str],
        output_path: str,
        add_transitions: bool = False,
        transition_duration: float = 0.5,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> str:
        """
        Merge multiple videos into one

        Args:
            video_paths: List of video file paths (in order)
            output_path: Output file path
            add_transitions: Add crossfade transitions between clips
            transition_duration: Transition duration in seconds (default: 0.5)
            progress_callback: Optional callback for progress updates (0-100)

        Returns:
            Path to merged video

        Raises:
            FFmpegNotFoundError: If FFmpeg is not installed
            VideoMergeError: If merge fails
            ValueError: If inputs are invalid
        """
        # Check FFmpeg
        if not VideoMerger.check_ffmpeg_installed():
            raise FFmpegNotFoundError(
                "FFmpeg is not installed. Please install FFmpeg to merge videos.\n"
                "Windows: choco install ffmpeg\n"
                "macOS: brew install ffmpeg\n"
                "Linux: sudo apt-get install ffmpeg"
            )

        # Validate inputs
        VideoMerger._validate_inputs(video_paths, output_path)

        logger.info(f"Merging {len(video_paths)} videos into {output_path}")
        logger.info(f"Transitions: {add_transitions}")

        try:
            # Emit initial progress
            if progress_callback:
                progress_callback(0)

            # Choose merge method
            if add_transitions and len(video_paths) > 1:
                # Use complex filter for transitions
                result_path = await VideoMerger._merge_with_transitions(
                    video_paths,
                    output_path,
                    transition_duration,
                    progress_callback
                )
            else:
                # Simple concatenation
                result_path = await VideoMerger._merge_simple(
                    video_paths,
                    output_path,
                    progress_callback
                )

            # Emit completion
            if progress_callback:
                progress_callback(100)

            logger.success(f"Videos merged successfully: {result_path}")
            return result_path

        except Exception as e:
            logger.error(f"Video merge failed: {e}")
            raise VideoMergeError(f"Failed to merge videos: {e}")

    @staticmethod
    async def _merge_simple(
        video_paths: List[str],
        output_path: str,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> str:
        """
        Simple video concatenation without re-encoding

        Uses FFmpeg concat demuxer for fast merging
        """
        logger.info("Using simple concatenation (no transitions)")

        # Create temporary concat file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.txt',
            delete=False,
            encoding='utf-8'
        ) as concat_file:
            concat_file_path = concat_file.name

            # Write video list
            for video_path in video_paths:
                # Use absolute paths
                abs_path = Path(video_path).absolute()
                # Escape single quotes in path
                escaped_path = str(abs_path).replace("'", "'\\''")
                concat_file.write(f"file '{escaped_path}'\n")

        logger.debug(f"Concat file created: {concat_file_path}")

        try:
            # Build FFmpeg command
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file_path,
                '-c', 'copy',  # Copy streams without re-encoding (fast)
                '-y',  # Overwrite output file
                str(output_path)
            ]

            logger.debug(f"Running: {' '.join(cmd)}")

            # Emit progress
            if progress_callback:
                progress_callback(20)

            # Run FFmpeg
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Track progress
            if progress_callback:
                # Simple progress simulation (since concat is fast)
                progress_callback(40)
                await asyncio.sleep(0.5)
                progress_callback(60)
                await asyncio.sleep(0.5)
                progress_callback(80)

            # Wait for completion
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='ignore')
                logger.error(f"FFmpeg error: {error_msg}")
                raise VideoMergeError(f"FFmpeg failed: {error_msg}")

            # Verify output
            if not Path(output_path).exists():
                raise VideoMergeError("Output file was not created")

            logger.info("Simple merge completed successfully")
            return str(output_path)

        finally:
            # Clean up concat file
            try:
                Path(concat_file_path).unlink()
            except Exception as e:
                logger.warning(f"Failed to delete concat file: {e}")

    @staticmethod
    async def _merge_with_transitions(
        video_paths: List[str],
        output_path: str,
        transition_duration: float,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> str:
        """
        Merge videos with crossfade transitions

        Uses FFmpeg complex filter with xfade
        """
        logger.info(f"Merging with {transition_duration}s crossfade transitions")

        # Emit progress
        if progress_callback:
            progress_callback(10)

        try:
            # Get video info for all clips
            video_infos = []
            for path in video_paths:
                info = VideoMerger.get_video_info(path)
                video_infos.append(info)

            # Build complex filter for xfade
            filter_complex = VideoMerger._build_xfade_filter(
                video_infos,
                transition_duration
            )

            # Build FFmpeg command
            cmd = ['ffmpeg']

            # Add input files
            for path in video_paths:
                cmd.extend(['-i', str(path)])

            # Add filter complex
            cmd.extend([
                '-filter_complex', filter_complex,
                '-y',  # Overwrite
                str(output_path)
            ])

            logger.debug(f"Running: {' '.join(cmd[:20])}...")  # Log first part only

            # Emit progress
            if progress_callback:
                progress_callback(30)

            # Run FFmpeg
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Parse progress from stderr
            async def track_progress():
                if not progress_callback:
                    return

                # Total duration
                total_duration = sum(info['duration'] for info in video_infos)

                while True:
                    line = await process.stderr.readline()
                    if not line:
                        break

                    line = line.decode('utf-8', errors='ignore')

                    # Look for time progress
                    if 'time=' in line:
                        try:
                            # Extract time (format: HH:MM:SS.MS)
                            time_str = line.split('time=')[1].split()[0]
                            h, m, s = time_str.split(':')
                            current_time = float(h) * 3600 + float(m) * 60 + float(s)

                            # Calculate progress
                            progress = int((current_time / total_duration) * 60) + 30
                            progress = min(progress, 90)

                            progress_callback(progress)

                        except Exception:
                            pass

            # Track progress in background
            if progress_callback:
                progress_task = asyncio.create_task(track_progress())

            # Wait for completion
            stdout, stderr = await process.communicate()

            if progress_callback:
                try:
                    await progress_task
                except Exception:
                    pass

            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='ignore')
                logger.error(f"FFmpeg error: {error_msg}")
                raise VideoMergeError(f"FFmpeg failed: {error_msg}")

            # Verify output
            if not Path(output_path).exists():
                raise VideoMergeError("Output file was not created")

            logger.info("Merge with transitions completed successfully")
            return str(output_path)

        except Exception as e:
            logger.error(f"Transition merge failed: {e}")
            raise

    @staticmethod
    def _build_xfade_filter(
        video_infos: List[Dict[str, Any]],
        transition_duration: float
    ) -> str:
        """
        Build FFmpeg xfade filter complex string

        Args:
            video_infos: List of video info dicts
            transition_duration: Transition duration in seconds

        Returns:
            Filter complex string
        """
        if len(video_infos) == 1:
            return "[0:v]copy[v]"

        # Build filter
        filter_parts = []
        current_offset = 0

        for i in range(len(video_infos) - 1):
            current_duration = video_infos[i]['duration']
            next_offset = current_offset + current_duration - transition_duration

            if i == 0:
                # First transition
                filter_parts.append(
                    f"[0:v][1:v]xfade=transition=fade:duration={transition_duration}:"
                    f"offset={next_offset}[v{i}]"
                )
            else:
                # Subsequent transitions
                filter_parts.append(
                    f"[v{i-1}][{i+1}:v]xfade=transition=fade:duration={transition_duration}:"
                    f"offset={next_offset}[v{i}]"
                )

            current_offset = next_offset

        # Final output
        last_index = len(video_infos) - 2
        filter_complex = ';'.join(filter_parts)
        filter_complex += f";[v{last_index}]copy[v]"

        return filter_complex

    @staticmethod
    def extract_last_frame(
        video_path: str,
        output_image_path: str
    ) -> str:
        """
        Extract the last frame from a video

        Args:
            video_path: Path to video file
            output_image_path: Path for output image

        Returns:
            Path to extracted frame

        Raises:
            FFmpegNotFoundError: If FFmpeg is not installed
            VideoMergeError: If extraction fails
        """
        # Check FFmpeg
        if not VideoMerger.check_ffmpeg_installed():
            raise FFmpegNotFoundError("FFmpeg is not installed")

        # Validate input
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        # Create output directory
        Path(output_image_path).parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Extracting last frame from {Path(video_path).name}")

        try:
            # Get video duration
            info = VideoMerger.get_video_info(video_path)
            duration = info['duration']

            logger.debug(f"Video duration: {duration}s")

            # Extract frame from last 0.1 seconds
            timestamp = max(0, duration - 0.1)

            cmd = [
                'ffmpeg',
                '-ss', str(timestamp),
                '-i', str(video_path),
                '-vframes', '1',
                '-q:v', '2',  # High quality
                '-y',
                str(output_image_path)
            ]

            logger.debug(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                raise VideoMergeError(f"FFmpeg failed: {result.stderr}")

            if not Path(output_image_path).exists():
                raise VideoMergeError("Frame extraction failed - output not created")

            logger.success(f"Last frame extracted: {output_image_path}")
            return str(output_image_path)

        except subprocess.TimeoutExpired:
            raise VideoMergeError("Frame extraction timed out")
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}")
            raise VideoMergeError(f"Failed to extract frame: {e}")

    @staticmethod
    def extract_frame_at_time(
        video_path: str,
        timestamp: float,
        output_image_path: str
    ) -> str:
        """
        Extract a frame at specific timestamp

        Args:
            video_path: Path to video file
            timestamp: Time in seconds
            output_image_path: Path for output image

        Returns:
            Path to extracted frame
        """
        # Check FFmpeg
        if not VideoMerger.check_ffmpeg_installed():
            raise FFmpegNotFoundError("FFmpeg is not installed")

        # Validate input
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        # Create output directory
        Path(output_image_path).parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Extracting frame at {timestamp}s from {Path(video_path).name}")

        try:
            cmd = [
                'ffmpeg',
                '-ss', str(timestamp),
                '-i', str(video_path),
                '-vframes', '1',
                '-q:v', '2',
                '-y',
                str(output_image_path)
            ]

            logger.debug(f"Running: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                raise VideoMergeError(f"FFmpeg failed: {result.stderr}")

            if not Path(output_image_path).exists():
                raise VideoMergeError("Frame extraction failed")

            logger.success(f"Frame extracted: {output_image_path}")
            return str(output_image_path)

        except subprocess.TimeoutExpired:
            raise VideoMergeError("Frame extraction timed out")
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}")
            raise VideoMergeError(f"Failed to extract frame: {e}")

    @staticmethod
    def get_video_info(video_path: str) -> Dict[str, Any]:
        """
        Get video metadata using ffprobe

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video information:
            {
                'duration': float,      # Duration in seconds
                'width': int,           # Video width
                'height': int,          # Video height
                'fps': float,           # Frames per second
                'codec': str,           # Video codec
                'bitrate': int,         # Bitrate in bits/s
                'format': str           # Container format
            }

        Raises:
            FFmpegNotFoundError: If FFmpeg is not installed
            VideoMergeError: If probe fails
        """
        # Check FFmpeg
        if not VideoMerger.check_ffmpeg_installed():
            raise FFmpegNotFoundError("FFmpeg is not installed")

        # Validate input
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        logger.debug(f"Getting video info for {Path(video_path).name}")

        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries',
                'stream=width,height,r_frame_rate,codec_name,bit_rate:format=duration,format_name',
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

            # Parse video stream
            stream = data['streams'][0]
            format_info = data['format']

            # Parse frame rate
            fps_str = stream.get('r_frame_rate', '30/1')
            if '/' in fps_str:
                num, den = fps_str.split('/')
                fps = float(num) / float(den) if float(den) != 0 else 30.0
            else:
                fps = float(fps_str)

            # Parse bitrate
            bitrate = stream.get('bit_rate')
            if bitrate is None:
                bitrate = format_info.get('bit_rate', 0)
            bitrate = int(bitrate) if bitrate else 0

            info = {
                'duration': float(format_info['duration']),
                'width': int(stream['width']),
                'height': int(stream['height']),
                'fps': fps,
                'codec': stream.get('codec_name', 'unknown'),
                'bitrate': bitrate,
                'format': format_info.get('format_name', 'unknown')
            }

            logger.debug(f"Video info: {info}")
            return info

        except subprocess.TimeoutExpired:
            raise VideoMergeError("ffprobe timed out")
        except json.JSONDecodeError as e:
            raise VideoMergeError(f"Failed to parse ffprobe output: {e}")
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            raise VideoMergeError(f"Failed to get video info: {e}")

    @staticmethod
    def validate_videos_compatible(video_paths: List[str]) -> bool:
        """
        Check if videos are compatible for merging

        Args:
            video_paths: List of video paths

        Returns:
            True if videos are compatible, False otherwise

        Checks:
        - Same resolution
        - Same frame rate
        - Same codec (preferred but not required)
        """
        if len(video_paths) < 2:
            return True

        try:
            # Get info for all videos
            infos = [VideoMerger.get_video_info(path) for path in video_paths]

            # Check resolution
            first_res = (infos[0]['width'], infos[0]['height'])
            if not all((info['width'], info['height']) == first_res for info in infos):
                logger.warning(
                    f"Videos have different resolutions. "
                    f"First: {first_res}, "
                    f"Others: {[(i['width'], i['height']) for i in infos[1:]]}"
                )
                return False

            # Check frame rate
            first_fps = infos[0]['fps']
            if not all(abs(info['fps'] - first_fps) < 0.1 for info in infos):
                logger.warning(
                    f"Videos have different frame rates. "
                    f"First: {first_fps}, "
                    f"Others: {[i['fps'] for i in infos[1:]]}"
                )
                return False

            # Check codec (warning only)
            first_codec = infos[0]['codec']
            if not all(info['codec'] == first_codec for info in infos):
                logger.info(
                    f"Videos have different codecs. "
                    f"This is okay but may require re-encoding."
                )

            logger.info("Videos are compatible for merging")
            return True

        except Exception as e:
            logger.error(f"Failed to validate videos: {e}")
            return False
