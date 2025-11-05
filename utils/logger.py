"""
Module quản lý logging cho toàn bộ ứng dụng
Cung cấp các hàm để ghi log với nhiều cấp độ khác nhau
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

from config import settings


# Dictionary lưu trữ các logger đã tạo để tránh tạo duplicate
_loggers = {}


def get_logger(name: str = __name__) -> logging.Logger:
    """
    Lấy hoặc tạo logger instance với tên được chỉ định

    Args:
        name (str): Tên của logger, thường là __name__ của module

    Returns:
        logging.Logger: Logger instance đã được cấu hình

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Thông báo thông tin")
        >>> logger.error("Thông báo lỗi")
    """
    # Kiểm tra xem logger đã tồn tại chưa
    if name in _loggers:
        return _loggers[name]

    # Tạo logger mới
    logger = logging.getLogger(name)

    # Chỉ cấu hình nếu logger chưa có handler
    if not logger.handlers:
        # Set log level từ settings
        log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(log_level)

        # Tạo formatter
        formatter = logging.Formatter(
            settings.LOG_FORMAT,
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # ===== Console Handler =====
        # Ghi log ra console (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # ===== File Handler =====
        # Ghi log ra file với rotation
        try:
            # Đảm bảo thư mục log tồn tại
            settings.LOG_DIR.mkdir(parents=True, exist_ok=True)

            # Tạo rotating file handler
            file_handler = RotatingFileHandler(
                filename=settings.LOG_FILE_PATH,
                maxBytes=settings.MAX_LOG_SIZE,
                backupCount=settings.LOG_BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        except Exception as e:
            # Nếu không thể tạo file handler, chỉ log ra console
            logger.warning(f"Không thể tạo file handler: {e}")

        # Ngăn log propagate lên parent logger
        logger.propagate = False

    # Lưu logger vào cache
    _loggers[name] = logger

    return logger


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None
) -> None:
    """
    Thiết lập cấu hình logging cho toàn bộ ứng dụng

    Args:
        log_level (str, optional): Cấp độ log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (Path, optional): Đường dẫn file log tùy chỉnh

    Example:
        >>> setup_logging(log_level='DEBUG', log_file=Path('custom.log'))
    """
    # Sử dụng giá trị mặc định nếu không được cung cấp
    if log_level is None:
        log_level = settings.LOG_LEVEL

    if log_file is None:
        log_file = settings.LOG_FILE_PATH

    # Chuyển đổi string log level thành constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Cấu hình root logger
    logging.basicConfig(
        level=numeric_level,
        format=settings.LOG_FORMAT,
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler với rotation
            RotatingFileHandler(
                filename=log_file,
                maxBytes=settings.MAX_LOG_SIZE,
                backupCount=settings.LOG_BACKUP_COUNT,
                encoding='utf-8'
            )
        ]
    )

    logger = get_logger(__name__)
    logger.info(f"Đã thiết lập logging với level: {log_level}")
    logger.info(f"Log file: {log_file}")


def log_exception(logger: logging.Logger, exception: Exception, message: str = None) -> None:
    """
    Log exception với đầy đủ stack trace

    Args:
        logger (logging.Logger): Logger instance
        exception (Exception): Exception cần log
        message (str, optional): Message bổ sung

    Example:
        >>> try:
        >>>     # some code
        >>>     pass
        >>> except Exception as e:
        >>>     log_exception(logger, e, "Lỗi khi xử lý dữ liệu")
    """
    if message:
        logger.error(f"{message}: {str(exception)}", exc_info=True)
    else:
        logger.error(f"Exception xảy ra: {str(exception)}", exc_info=True)


def clear_logs() -> bool:
    """
    Xóa tất cả các file log

    Returns:
        bool: True nếu xóa thành công, False nếu thất bại

    Example:
        >>> if clear_logs():
        >>>     print("Đã xóa logs")
    """
    try:
        logger = get_logger(__name__)
        logger.info("Đang xóa các file log...")

        # Xóa file log chính
        if settings.LOG_FILE_PATH.exists():
            settings.LOG_FILE_PATH.unlink()

        # Xóa các backup log files
        for i in range(1, settings.LOG_BACKUP_COUNT + 1):
            backup_file = settings.LOG_DIR / f"{settings.LOG_FILE}.{i}"
            if backup_file.exists():
                backup_file.unlink()

        logger.info("Đã xóa tất cả các file log")
        return True

    except Exception as e:
        logger.error(f"Lỗi khi xóa logs: {e}")
        return False


def get_log_size() -> int:
    """
    Lấy tổng kích thước của tất cả file log (bytes)

    Returns:
        int: Tổng kích thước tính bằng bytes

    Example:
        >>> size = get_log_size()
        >>> print(f"Log size: {size / 1024:.2f} KB")
    """
    total_size = 0

    try:
        # Kích thước file log chính
        if settings.LOG_FILE_PATH.exists():
            total_size += settings.LOG_FILE_PATH.stat().st_size

        # Kích thước các backup files
        for i in range(1, settings.LOG_BACKUP_COUNT + 1):
            backup_file = settings.LOG_DIR / f"{settings.LOG_FILE}.{i}"
            if backup_file.exists():
                total_size += backup_file.stat().st_size

    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Lỗi khi tính kích thước log: {e}")

    return total_size


def format_log_size(size_bytes: int) -> str:
    """
    Định dạng kích thước log thành string dễ đọc

    Args:
        size_bytes (int): Kích thước tính bằng bytes

    Returns:
        str: String đã được định dạng (ví dụ: "1.5 MB")

    Example:
        >>> size = get_log_size()
        >>> print(format_log_size(size))
        "2.3 MB"
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


class LoggerContext:
    """
    Context manager để log thời gian thực thi của một block code

    Example:
        >>> logger = get_logger(__name__)
        >>> with LoggerContext(logger, "Xử lý dữ liệu"):
        >>>     # Code xử lý
        >>>     pass
    """

    def __init__(self, logger: logging.Logger, operation: str):
        """
        Khởi tạo context

        Args:
            logger (logging.Logger): Logger instance
            operation (str): Tên operation đang thực hiện
        """
        self.logger = logger
        self.operation = operation
        self.start_time = None

    def __enter__(self):
        """Bắt đầu context"""
        import time
        self.start_time = time.time()
        self.logger.info(f"Bắt đầu: {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Kết thúc context"""
        import time
        elapsed = time.time() - self.start_time

        if exc_type is None:
            self.logger.info(f"Hoàn thành: {self.operation} (Thời gian: {elapsed:.2f}s)")
        else:
            self.logger.error(
                f"Lỗi trong: {self.operation} (Thời gian: {elapsed:.2f}s) - {exc_val}"
            )

        # Không suppress exception
        return False


# ===== EXPORT =====
__all__ = [
    'get_logger',
    'setup_logging',
    'log_exception',
    'clear_logs',
    'get_log_size',
    'format_log_size',
    'LoggerContext'
]
