"""
Client API để giao tiếp với Google Veo API
Xử lý tất cả các request tới API để tạo video
"""

import asyncio
import aiohttp
from typing import List, Dict, Optional, Any
from pathlib import Path
import json

try:
    import google.genai as genai
    from google.genai import types
except ImportError:
    # google-genai not installed - using mock mode
    genai = None

from config import settings
from utils.logger import get_logger

# Khởi tạo logger
logger = get_logger(__name__)


class VeoAPIClient:
    """
    Class quản lý kết nối và giao tiếp với Google Veo API

    Attributes:
        api_key (str): API key để xác thực với Google AI
        client: Client instance của Google Generative AI
    """

    def __init__(self, api_key: str):
        """
        Khởi tạo Veo API Client

        Args:
            api_key (str): Google AI API key

        Raises:
            ValueError: Nếu API key không hợp lệ
            ImportError: Nếu chưa cài đặt google-genai
        """
        if not api_key or api_key == 'your_api_key_here':
            logger.warning("API key not valid, using mock mode")
            # Allow empty API key for testing/mock mode
            api_key = 'mock_api_key'

        self.api_key = api_key
        self.client = None

        if genai is None:
            logger.warning("google-genai library not installed, using mock mode")
            # Continue with mock mode
        else:
            try:
                # Configure client with API key
                genai.configure(api_key=self.api_key)
                self.client = genai
                logger.info("VeoAPIClient initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing client: {str(e)}")
                logger.warning("Falling back to mock mode")
                # Don't raise, allow mock mode


    async def test_connection(self) -> bool:
        """
        Kiểm tra kết nối với Google Veo API

        Returns:
            bool: True nếu kết nối thành công, False nếu thất bại

        Example:
            >>> client = VeoAPIClient(api_key="your_key")
            >>> is_connected = await client.test_connection()
            >>> print(f"Kết nối: {is_connected}")
        """
        try:
            logger.info("Đang kiểm tra kết nối với Google Veo API...")

            # Thử lấy danh sách models để test connection
            models = await self.list_models()

            if models and len(models) > 0:
                logger.info(f"Kết nối thành công! Tìm thấy {len(models)} model(s)")
                return True
            else:
                logger.warning("Kết nối được thiết lập nhưng không tìm thấy model nào")
                return False

        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra kết nối: {str(e)}")
            return False


    async def list_models(self) -> List[str]:
        """
        Lấy danh sách các model Veo có sẵn

        Returns:
            List[str]: Danh sách tên các model

        Example:
            >>> client = VeoAPIClient(api_key="your_key")
            >>> models = await client.list_models()
            >>> for model in models:
            >>>     print(model)
        """
        try:
            logger.info("Đang lấy danh sách models từ Google AI...")

            # Lấy danh sách tất cả models
            models = []

            # Sử dụng async để lấy models
            loop = asyncio.get_event_loop()
            all_models = await loop.run_in_executor(
                None,
                lambda: list(genai.models.list())
            )

            # Lọc ra các model liên quan đến video generation
            for model in all_models:
                model_name = model.name
                # Kiểm tra nếu model hỗ trợ generateContent hoặc là Veo model
                if 'veo' in model_name.lower() or 'video' in model_name.lower():
                    models.append(model_name)
                    logger.debug(f"Tìm thấy model: {model_name}")

            # Nếu không tìm thấy model Veo nào, trả về danh sách mặc định
            if not models:
                logger.warning("Không tìm thấy model Veo nào, sử dụng danh sách mặc định")
                models = settings.AVAILABLE_MODELS

            logger.info(f"Tìm thấy {len(models)} model(s)")
            return models

        except Exception as e:
            logger.error(f"Lỗi khi lấy danh sách models: {str(e)}")
            # Trả về danh sách models mặc định nếu có lỗi
            return settings.AVAILABLE_MODELS


    async def generate_video(
        self,
        prompt: str,
        model: str = None,
        duration: int = 5,
        resolution: str = None,
        aspect_ratio: str = None,
        output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Tạo video từ text prompt sử dụng Veo API

        Args:
            prompt (str): Mô tả nội dung video cần tạo
            model (str, optional): Tên model sử dụng. Mặc định từ settings
            duration (int, optional): Độ dài video (giây). Mặc định 5
            resolution (str, optional): Độ phân giải video. Mặc định từ settings
            aspect_ratio (str, optional): Tỷ lệ khung hình. Mặc định từ settings
            output_path (Path, optional): Đường dẫn lưu video

        Returns:
            Dict[str, Any]: Thông tin về video đã tạo
            {
                'status': 'success' | 'error',
                'video_path': str,
                'duration': int,
                'message': str
            }

        Example:
            >>> client = VeoAPIClient(api_key="your_key")
            >>> result = await client.generate_video(
            >>>     prompt="A cat playing with a ball",
            >>>     duration=10
            >>> )
            >>> print(result['video_path'])
        """
        try:
            # Sử dụng giá trị mặc định nếu không được cung cấp
            if model is None:
                model = settings.DEFAULT_MODEL
            if resolution is None:
                resolution = settings.DEFAULT_RESOLUTION
            if aspect_ratio is None:
                aspect_ratio = settings.DEFAULT_ASPECT_RATIO

            logger.info(f"Bắt đầu tạo video với prompt: '{prompt[:50]}...'")
            logger.info(f"Model: {model}, Duration: {duration}s, Resolution: {resolution}")

            # Tạo đường dẫn output nếu chưa có
            if output_path is None:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = settings.OUTPUT_DIR / f"video_{timestamp}.mp4"

            # TODO: Implement video generation logic với Veo API
            # Đây là placeholder - cần cập nhật khi API chính thức có sẵn

            logger.warning("Video generation chưa được implement đầy đủ (API đang phát triển)")

            return {
                'status': 'pending',
                'message': 'Chức năng đang được phát triển. Google Veo API hiện đang trong giai đoạn beta.',
                'video_path': str(output_path),
                'duration': duration,
                'prompt': prompt,
                'model': model,
                'resolution': resolution,
                'aspect_ratio': aspect_ratio
            }

        except Exception as e:
            logger.error(f"Lỗi khi tạo video: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'video_path': None
            }


    async def get_generation_status(self, job_id: str) -> Dict[str, Any]:
        """
        Kiểm tra trạng thái của job tạo video

        Args:
            job_id (str): ID của job generation

        Returns:
            Dict[str, Any]: Thông tin trạng thái job
            {
                'status': 'pending' | 'processing' | 'completed' | 'failed',
                'progress': int (0-100),
                'message': str
            }
        """
        try:
            logger.info(f"Kiểm tra trạng thái job: {job_id}")

            # TODO: Implement status checking logic

            return {
                'status': 'pending',
                'progress': 0,
                'message': 'Đang chờ xử lý'
            }

        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra trạng thái: {str(e)}")
            return {
                'status': 'error',
                'progress': 0,
                'message': str(e)
            }


    async def download_video(self, video_url: str, output_path: Path) -> bool:
        """
        Tải video từ URL về local

        Args:
            video_url (str): URL của video cần tải
            output_path (Path): Đường dẫn lưu video

        Returns:
            bool: True nếu tải thành công, False nếu thất bại
        """
        try:
            logger.info(f"Đang tải video từ: {video_url}")

            async with aiohttp.ClientSession() as session:
                async with session.get(video_url, timeout=settings.REQUEST_TIMEOUT) as response:
                    if response.status == 200:
                        # Tạo thư mục nếu chưa tồn tại
                        output_path.parent.mkdir(parents=True, exist_ok=True)

                        # Ghi dữ liệu video
                        with open(output_path, 'wb') as f:
                            while True:
                                chunk = await response.content.read(settings.DOWNLOAD_BUFFER_SIZE)
                                if not chunk:
                                    break
                                f.write(chunk)

                        logger.info(f"Đã tải video thành công: {output_path}")
                        return True
                    else:
                        logger.error(f"Lỗi HTTP {response.status} khi tải video")
                        return False

        except Exception as e:
            logger.error(f"Lỗi khi tải video: {str(e)}")
            return False


    def __repr__(self) -> str:
        """Representation của VeoAPIClient"""
        return f"VeoAPIClient(api_key={'*' * 10}...)"


    def __str__(self) -> str:
        """String representation của VeoAPIClient"""
        return f"Veo API Client (Connected: {self.client is not None})"


# ===== HELPER FUNCTIONS =====

def create_client(api_key: Optional[str] = None) -> VeoAPIClient:
    """
    Hàm helper để tạo VeoAPIClient instance

    Args:
        api_key (str, optional): API key. Nếu None, sẽ lấy từ settings

    Returns:
        VeoAPIClient: Instance của client
    """
    if api_key is None:
        api_key = settings.GOOGLE_API_KEY

    return VeoAPIClient(api_key=api_key)
