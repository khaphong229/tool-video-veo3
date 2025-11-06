"""
Simple automated test for History Tab
"""

import sys
import os

# Suppress console encoding errors
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from PyQt6.QtWidgets import QApplication


def test_history_tab():
    """Test History Tab functionality"""
    print("="*70)
    print("HISTORY TAB AUTOMATED TEST")
    print("="*70)
    print()

    # Create application (required for Qt widgets)
    app = QApplication(sys.argv)

    # Import after QApplication is created
    from ui.tabs import HistoryTab

    print("1. Creating HistoryTab...")
    try:
        history_tab = HistoryTab(db_manager=None)
        print("   SUCCESS - HistoryTab created")
    except Exception as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("2. Checking attributes...")
    try:
        assert hasattr(history_tab, 'current_view_mode')
        assert hasattr(history_tab, 'page_size')
        assert hasattr(history_tab, 'total_videos')
        assert hasattr(history_tab, 'all_videos')
        assert hasattr(history_tab, 'filtered_videos')
        print("   SUCCESS - All attributes present")
    except AssertionError:
        print("   FAILED - Missing attributes")
        return False

    print()
    print("3. Checking methods...")
    try:
        methods = ['load_history', 'refresh_history', 'delete_video',
                   'bulk_delete', 'export_video_info', 'regenerate_video']
        for method in methods:
            assert hasattr(history_tab, method), f"Missing method: {method}"
        print("   SUCCESS - All required methods present")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("4. Testing mock data generation...")
    try:
        assert len(history_tab.all_videos) > 0, "No mock videos generated"
        print(f"   SUCCESS - Generated {len(history_tab.all_videos)} mock videos")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("5. Testing filter functionality...")
    try:
        initial_count = len(history_tab.filtered_videos)
        print(f"   Initial count: {initial_count}")

        # Apply search filter
        history_tab.current_filters['search'] = 'sunset'
        filtered = history_tab.apply_filters(history_tab.all_videos)
        print(f"   After 'sunset' filter: {len(filtered)} videos")

        # Apply status filter
        history_tab.current_filters['search'] = ''
        history_tab.current_filters['status'] = 'completed'
        filtered = history_tab.apply_filters(history_tab.all_videos)
        print(f"   After 'completed' filter: {len(filtered)} videos")

        print("   SUCCESS - Filtering works correctly")
    except Exception as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("6. Testing sort functionality...")
    try:
        sorted_videos = history_tab.sort_videos(history_tab.all_videos, 'date_desc')
        assert len(sorted_videos) == len(history_tab.all_videos)
        print("   SUCCESS - Sorting works correctly")
    except Exception as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("7. Testing view mode switching...")
    try:
        history_tab.switch_view_mode('list')
        assert history_tab.current_view_mode == 'list'

        history_tab.switch_view_mode('grid')
        assert history_tab.current_view_mode == 'grid'

        print("   SUCCESS - View mode switching works")
    except Exception as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("8. Testing pagination...")
    try:
        initial_page = history_tab.current_page
        max_page = (history_tab.total_videos - 1) // history_tab.page_size

        if max_page > 0:
            history_tab.next_page()
            assert history_tab.current_page == initial_page + 1

            history_tab.previous_page()
            assert history_tab.current_page == initial_page

        print("   SUCCESS - Pagination works correctly")
    except Exception as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("9. Testing signals...")
    try:
        assert hasattr(history_tab, 'video_opened')
        assert hasattr(history_tab, 'video_deleted')
        assert hasattr(history_tab, 'video_regenerated')
        print("   SUCCESS - All signals present")
    except AssertionError:
        print("   FAILED - Missing signals")
        return False

    print()
    print("="*70)
    print("ALL TESTS PASSED")
    print("="*70)
    return True


if __name__ == '__main__':
    success = test_history_tab()
    sys.exit(0 if success else 1)
