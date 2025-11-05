"""
Ví dụ sử dụng DatabaseManager
Hướng dẫn chi tiết cách làm việc với database
"""

import asyncio
from core.database import DatabaseManager, get_database

def example_1_basic_usage():
    """Ví dụ 1: Sử dụng cơ bản"""
    print("\n=== VÍ DỤ 1: SỬ DỤNG CƠ BẢN ===\n")

    # Khởi tạo database manager
    db = get_database()

    # Lấy thống kê
    stats = db.get_statistics()
    print(f"Thống kê database:")
    print(f"  - Tổng số videos: {stats['total_videos']}")
    print(f"  - Tổng số projects: {stats['total_projects']}")
    print(f"  - Tổng số templates: {stats['total_templates']}")


def example_2_create_project():
    """Ví dụ 2: Tạo project và scenes"""
    print("\n=== VÍ DỤ 2: TẠO PROJECT VÀ SCENES ===\n")

    db = get_database()

    # Tạo project mới
    try:
        project_id = db.create_project(
            name="Video Quảng Cáo Sản Phẩm",
            description="Series video quảng cáo cho sản phẩm mới",
            style_template="cinematic",
            settings={
                "resolution": "1080p",
                "aspect_ratio": "16:9",
                "model": "veo-2.0"
            }
        )
        print(f"✅ Đã tạo project với ID: {project_id}")

        # Thêm scenes vào project
        scene_1 = db.save_scene(
            project_id=project_id,
            scene_data={
                "scene_number": 1,
                "prompt": "Product showcase with dramatic lighting, slow rotation",
                "duration": 10,
                "resolution": "1080p"
            }
        )
        print(f"✅ Đã tạo scene 1 với ID: {scene_1}")

        scene_2 = db.save_scene(
            project_id=project_id,
            scene_data={
                "scene_number": 2,
                "prompt": "Close-up of product details, professional lighting",
                "duration": 8
            }
        )
        print(f"✅ Đã tạo scene 2 với ID: {scene_2}")

        # Lấy tất cả scenes của project
        scenes = db.get_scenes(project_id)
        print(f"\nProject có {len(scenes)} scenes:")
        for scene in scenes:
            print(f"  - Scene {scene['scene_number']}: {scene['prompt'][:50]}...")

    except ValueError as e:
        print(f"❌ Lỗi: {e}")


def example_3_video_generation():
    """Ví dụ 3: Lưu lịch sử tạo video"""
    print("\n=== VÍ DỤ 3: LƯU LỊCH SỬ VIDEO ===\n")

    db = get_database()

    # Lưu video generation
    video_id = db.save_video_generation({
        "prompt": "A beautiful sunset over the ocean with waves",
        "model": "veo-2.0",
        "status": "completed",
        "video_path": "outputs/video_20250105_120000.mp4",
        "duration": 10,
        "resolution": "1080p",
        "aspect_ratio": "16:9",
        "file_size": 15728640,  # 15 MB
        "metadata": {
            "fps": 30,
            "codec": "h264",
            "quality": "high"
        }
    })
    print(f"✅ Đã lưu video với ID: {video_id}")

    # Lưu video thất bại
    failed_video_id = db.save_video_generation({
        "prompt": "Test video generation",
        "model": "veo-2.0",
        "status": "failed",
        "error_message": "API timeout after 5 minutes"
    })
    print(f"✅ Đã lưu video thất bại với ID: {failed_video_id}")

    # Lấy lịch sử video
    print("\nLịch sử 5 videos gần nhất:")
    videos = db.get_video_history(limit=5)
    for video in videos:
        status_icon = "✅" if video['status'] == 'completed' else "❌"
        print(f"  {status_icon} [{video['created_at']}] {video['prompt'][:40]}... - {video['status']}")


def example_4_templates():
    """Ví dụ 4: Quản lý templates"""
    print("\n=== VÍ DỤ 4: QUẢN LÝ TEMPLATES ===\n")

    db = get_database()

    # Tạo templates
    templates_data = [
        {
            "name": "Cinematic Sunset",
            "base_style": "cinematic, golden hour, dramatic lighting, wide angle",
            "category": "cinematic",
            "tags": ["sunset", "dramatic", "golden", "wide"],
            "description": "Phong cách điện ảnh với ánh sáng hoàng hôn"
        },
        {
            "name": "Modern Tech",
            "base_style": "modern, tech, sleek, minimal, blue tones",
            "category": "technology",
            "tags": ["tech", "modern", "minimal", "blue"],
            "description": "Phong cách công nghệ hiện đại"
        },
        {
            "name": "Nature Documentary",
            "base_style": "nature, documentary, realistic, natural lighting",
            "category": "documentary",
            "tags": ["nature", "realistic", "natural"],
            "description": "Phong cách phim tài liệu thiên nhiên"
        }
    ]

    for template_data in templates_data:
        try:
            template_id = db.save_template(**template_data)
            print(f"✅ Đã tạo template '{template_data['name']}' với ID: {template_id}")
        except ValueError as e:
            print(f"⚠️  Template '{template_data['name']}' đã tồn tại")

    # Lấy templates theo category
    print("\nTemplates category 'cinematic':")
    cinematic_templates = db.get_templates(category="cinematic")
    for template in cinematic_templates:
        print(f"  - {template['name']}: {template['base_style']}")

    # Tăng usage count
    if cinematic_templates:
        db.increment_template_usage(cinematic_templates[0]['id'])
        print(f"\n✅ Đã tăng usage count cho template '{cinematic_templates[0]['name']}'")


def example_5_update_operations():
    """Ví dụ 5: Cập nhật dữ liệu"""
    print("\n=== VÍ DỤ 5: CẬP NHẬT DỮ LIỆU ===\n")

    db = get_database()

    # Tạo project để test update
    project_id = db.create_project(
        name="Test Update Project",
        description="Project for testing updates"
    )
    print(f"✅ Đã tạo project test với ID: {project_id}")

    # Cập nhật project
    success = db.update_project(
        project_id,
        description="Updated description",
        status="active"
    )
    if success:
        print(f"✅ Đã cập nhật project {project_id}")

    # Xem project sau khi update
    project = db.get_project_by_id(project_id)
    print(f"\nThông tin project sau update:")
    print(f"  - Name: {project['name']}")
    print(f"  - Description: {project['description']}")
    print(f"  - Status: {project['status']}")

    # Tạo video để test update status
    video_id = db.save_video_generation({
        "prompt": "Test video for status update",
        "model": "veo-2.0",
        "status": "pending"
    })
    print(f"\n✅ Đã tạo video với status 'pending': {video_id}")

    # Update video status
    db.update_video_status(
        video_id,
        status="processing"
    )
    print(f"✅ Đã cập nhật video {video_id} sang 'processing'")

    db.update_video_status(
        video_id,
        status="completed",
        video_path="outputs/test_video.mp4"
    )
    print(f"✅ Đã cập nhật video {video_id} sang 'completed'")


def example_6_complex_query():
    """Ví dụ 6: Truy vấn phức tạp"""
    print("\n=== VÍ DỤ 6: TRUY VẤN PHỨC TẠP ===\n")

    db = get_database()

    # Tạo project với nhiều scenes và videos
    project_id = db.create_project(
        name="Complete Video Series",
        description="Project với nhiều scenes"
    )

    # Tạo 3 scenes
    for i in range(1, 4):
        scene_id = db.save_scene(
            project_id=project_id,
            scene_data={
                "scene_number": i,
                "prompt": f"Scene {i} content description",
                "duration": 5 + i
            }
        )

        # Tạo video cho mỗi scene
        db.save_video_generation({
            "project_id": project_id,
            "scene_id": scene_id,
            "prompt": f"Scene {i} content description",
            "model": "veo-2.0",
            "status": "completed" if i % 2 == 0 else "processing",
            "video_path": f"outputs/scene_{i}.mp4" if i % 2 == 0 else None,
            "duration": 5 + i
        })

    print(f"✅ Đã tạo project với 3 scenes và videos")

    # Lấy tất cả videos của project
    print(f"\nVideos của project {project_id}:")
    project_videos = db.get_video_history(project_id=project_id)
    for video in project_videos:
        print(f"  - Scene {video['scene_number']}: {video['status']}")

    # Lấy tất cả scenes
    scenes = db.get_scenes(project_id)
    print(f"\nScenes của project (sorted):")
    for scene in scenes:
        print(f"  - Scene {scene['scene_number']}: {scene['prompt']}")


def example_7_statistics_and_cleanup():
    """Ví dụ 7: Thống kê và dọn dẹp"""
    print("\n=== VÍ DỤ 7: THỐNG KÊ VÀ DỌN DẸP ===\n")

    db = get_database()

    # Lấy thống kê chi tiết
    stats = db.get_statistics()
    print("Thống kê tổng quan:")
    print(f"  - Tổng số videos: {stats['total_videos']}")
    print(f"  - Videos by status: {stats['videos_by_status']}")
    print(f"  - Tổng số projects: {stats['total_projects']}")
    print(f"  - Tổng số scenes: {stats['total_scenes']}")
    print(f"  - Tổng số templates: {stats['total_templates']}")
    print(f"  - Video gần nhất: {stats['last_video_created']}")

    # Cleanup old failed records (90 days)
    # deleted = db.cleanup_old_records(days=90)
    # print(f"\n✅ Đã xóa {deleted} records cũ")

    # Optimize database
    # db.vacuum_database()
    # print("✅ Đã optimize database")


def example_8_error_handling():
    """Ví dụ 8: Xử lý lỗi"""
    print("\n=== VÍ DỤ 8: XỬ LÝ LỖI ===\n")

    db = get_database()

    # Thử tạo project với tên trùng
    try:
        db.create_project(name="Duplicate Test Project")
        print("✅ Đã tạo project lần 1")

        db.create_project(name="Duplicate Test Project")
        print("✅ Đã tạo project lần 2")
    except ValueError as e:
        print(f"❌ Lỗi như mong đợi: {e}")

    # Thử tạo scene với scene_number trùng
    try:
        project_id = db.create_project(name="Scene Test Project")

        db.save_scene(project_id, {
            "scene_number": 1,
            "prompt": "First scene"
        })
        print("✅ Đã tạo scene 1")

        db.save_scene(project_id, {
            "scene_number": 1,
            "prompt": "Duplicate scene"
        })
        print("✅ Đã tạo scene 1 lần 2")
    except ValueError as e:
        print(f"❌ Lỗi như mong đợi: {e}")

    # Lấy project không tồn tại
    project = db.get_project_by_id(99999)
    if project is None:
        print("✅ Project không tồn tại trả về None như mong đợi")


def main():
    """Chạy tất cả examples"""
    print("=" * 60)
    print("EXAMPLES DATABASE MANAGER - VEO VIDEO GENERATOR")
    print("=" * 60)

    try:
        example_1_basic_usage()
        example_2_create_project()
        example_3_video_generation()
        example_4_templates()
        example_5_update_operations()
        example_6_complex_query()
        example_7_statistics_and_cleanup()
        example_8_error_handling()

        print("\n" + "=" * 60)
        print("✅ HOÀN THÀNH TẤT CẢ EXAMPLES")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
