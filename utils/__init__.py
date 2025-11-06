"""
Module utils chứa các tiện ích và helper functions
"""

from .logger import (
    get_logger,
    setup_logging,
    log_exception,
    clear_logs,
    get_log_size,
    format_log_size,
    LoggerContext
)

# Lazy import to avoid circular dependency
def __getattr__(name):
    if name == 'VideoMerger':
        from .video_merger import VideoMerger
        return VideoMerger
    elif name == 'VideoMergeError':
        from .video_merger import VideoMergeError
        return VideoMergeError
    elif name == 'FFmpegNotFoundError':
        from .video_merger import FFmpegNotFoundError
        return FFmpegNotFoundError
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    'get_logger',
    'setup_logging',
    'log_exception',
    'clear_logs',
    'get_log_size',
    'format_log_size',
    'LoggerContext',
    'VideoMerger',
    'VideoMergeError',
    'FFmpegNotFoundError'
]
