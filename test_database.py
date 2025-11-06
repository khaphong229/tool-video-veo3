"""
Script test đơn giản để kiểm tra DatabaseManager
"""

from core.database import DatabaseManager
from pathlib import Path
import sys

def test_database():
    """Test basic database operations"""
    print("=" * 60)
    print("TESTING DATABASE MANAGER")
    print("=" * 60)

    # Sử dụng database test
    test_db_path = Path("test_veo_database.db")

    # Xóa database cũ nếu tồn tại
    if test_db_path.exists():
        test_db_path.unlink()
        print("✅ Đã xóa database test cũ")

    try:
        # 1. Khởi tạo database
        print("\n1. Khởi tạo database...")
        db = DatabaseManager(test_db_path)
        print("✅ Database đã được khởi tạo")

        # 2. Kiểm tra thống kê ban đầu
        print("\n2. Kiểm tra thống kê ban đầu...")
        stats = db.get_statistics()
        assert stats['total_videos'] == 0, "Should have 0 videos"
        assert stats['total_projects'] == 0, "Should have 0 projects"
        print("✅ Thống kê ban đầu đúng")

        # 3. Tạo project
        print("\n3. Tạo project test...")
        project_id = db.create_project(
            name="Test Project",
            description="This is a test project"
        )
        assert project_id > 0, "Project ID should be positive"
        print(f"✅ Đã tạo project với ID: {project_id}")

        # 4. Tạo scenes
        print("\n4. Tạo scenes...")
        scene_1 = db.save_scene(project_id, {
            'scene_number': 1,
            'prompt': 'Test scene 1'
        })
        scene_2 = db.save_scene(project_id, {
            'scene_number': 2,
            'prompt': 'Test scene 2'
        })
        assert scene_1 > 0 and scene_2 > 0, "Scene IDs should be positive"
        print(f"✅ Đã tạo 2 scenes: {scene_1}, {scene_2}")

        # 5. Lấy scenes
        print("\n5. Lấy danh sách scenes...")
        scenes = db.get_scenes(project_id)
        assert len(scenes) == 2, "Should have 2 scenes"
        assert scenes[0]['scene_number'] == 1, "First scene should be scene 1"
        print("✅ Lấy scenes thành công")

        # 6. Tạo video
        print("\n6. Tạo video generation record...")
        video_id = db.save_video_generation({
            'prompt': 'Test video',
            'model': 'veo-2.0',
            'status': 'completed',
            'project_id': project_id,
            'scene_id': scene_1,
            'video_path': 'test/video.mp4',
            'metadata': {'test': True}
        })
        assert video_id > 0, "Video ID should be positive"
        print(f"✅ Đã tạo video với ID: {video_id}")

        # 7. Lấy video history
        print("\n7. Lấy video history...")
        videos = db.get_video_history(project_id=project_id)
        assert len(videos) == 1, "Should have 1 video"
        assert videos[0]['metadata']['test'] == True, "Metadata should be parsed"
        print("✅ Lấy video history thành công")

        # 8. Update video status
        print("\n8. Update video status...")
        success = db.update_video_status(video_id, 'processing')
        assert success, "Update should succeed"
        updated_videos = db.get_video_history()
        assert updated_videos[0]['status'] == 'processing', "Status should be updated"
        print("✅ Update status thành công")

        # 9. Tạo template
        print("\n9. Tạo template...")
        template_id = db.save_template(
            name="Test Template",
            base_style="test style",
            category="test",
            tags=["test", "demo"]
        )
        assert template_id > 0, "Template ID should be positive"
        print(f"✅ Đã tạo template với ID: {template_id}")

        # 10. Lấy templates
        print("\n10. Lấy templates...")
        templates = db.get_templates()
        assert len(templates) == 1, "Should have 1 template"
        assert templates[0]['tags'] == ["test", "demo"], "Tags should be parsed"
        print("✅ Lấy templates thành công")

        # 11. Test duplicate project name
        print("\n11. Test duplicate project name...")
        try:
            db.create_project(name="Test Project")
            print("❌ Should raise ValueError for duplicate name")
            sys.exit(1)
        except ValueError:
            print("✅ ValueError raised như mong đợi")

        # 12. Test duplicate scene number
        print("\n12. Test duplicate scene number...")
        try:
            db.save_scene(project_id, {
                'scene_number': 1,
                'prompt': 'Duplicate scene'
            })
            print("❌ Should raise ValueError for duplicate scene number")
            sys.exit(1)
        except ValueError:
            print("✅ ValueError raised như mong đợi")

        # 13. Final statistics
        print("\n13. Thống kê cuối cùng...")
        final_stats = db.get_statistics()
        print(f"   - Total videos: {final_stats['total_videos']}")
        print(f"   - Total projects: {final_stats['total_projects']}")
        print(f"   - Total scenes: {final_stats['total_scenes']}")
        print(f"   - Total templates: {final_stats['total_templates']}")
        assert final_stats['total_videos'] == 1
        assert final_stats['total_projects'] == 1
        assert final_stats['total_scenes'] == 2
        assert final_stats['total_templates'] == 1
        print("✅ Thống kê đúng")

        # Cleanup
        print("\n14. Cleanup...")
        db.close()
        test_db_path.unlink()
        print("✅ Đã xóa test database")

        print("\n" + "=" * 60)
        print("✅ TẤT CẢ TESTS PASSED!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

        # Cleanup on error
        if test_db_path.exists():
            test_db_path.unlink()

        return False


if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1)
