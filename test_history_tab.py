"""
Quick test for History Tab functionality
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.tabs import HistoryTab
from utils import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


def test_history_tab_ui():
    """Test History Tab UI creation"""
    print("=" * 70)
    print("HISTORY TAB UI TEST")
    print("=" * 70)
    print()

    # Create application
    app = QApplication(sys.argv)

    # Create HistoryTab (with mock data)
    print("Creating HistoryTab...")
    history_tab = HistoryTab(db_manager=None)
    print("✓ HistoryTab created successfully")
    print()

    # Test attributes
    print("Checking HistoryTab attributes:")
    print(f"  - Current view mode: {history_tab.current_view_mode}")
    print(f"  - Page size: {history_tab.page_size}")
    print(f"  - Total videos: {history_tab.total_videos}")
    print(f"  - Filtered videos: {len(history_tab.filtered_videos)}")
    print(f"  - Current page: {history_tab.current_page}")
    print()

    # Test methods exist
    print("Checking HistoryTab methods:")
    methods = [
        'load_history',
        'refresh_history',
        'delete_video',
        'bulk_delete',
        'export_video_info',
        'regenerate_video',
        'switch_view_mode',
        'apply_filters',
        'display_current_page'
    ]

    for method in methods:
        if hasattr(history_tab, method):
            print(f"  ✓ {method}")
        else:
            print(f"  ✗ {method} - MISSING")
    print()

    # Test filter functionality
    print("Testing filter functionality:")
    initial_count = len(history_tab.filtered_videos)
    print(f"  Initial video count: {initial_count}")

    # Apply search filter
    history_tab.current_filters['search'] = 'sunset'
    history_tab.filtered_videos = history_tab.apply_filters(history_tab.all_videos)
    filtered_count = len(history_tab.filtered_videos)
    print(f"  After search filter 'sunset': {filtered_count}")

    # Clear filter
    history_tab.current_filters['search'] = ''
    history_tab.filtered_videos = history_tab.apply_filters(history_tab.all_videos)
    cleared_count = len(history_tab.filtered_videos)
    print(f"  After clearing filter: {cleared_count}")
    print()

    # Test view modes
    print("Testing view modes:")
    print(f"  Current mode: {history_tab.current_view_mode}")

    history_tab.switch_view_mode('list')
    print(f"  Switched to: {history_tab.current_view_mode}")

    history_tab.switch_view_mode('grid')
    print(f"  Switched to: {history_tab.current_view_mode}")
    print()

    # Test pagination
    print("Testing pagination:")
    max_page = max(0, (history_tab.total_videos - 1) // history_tab.page_size)
    print(f"  Total pages: {max_page + 1}")
    print(f"  Current page: {history_tab.current_page + 1}")

    if max_page > 0:
        history_tab.next_page()
        print(f"  After next_page(): Page {history_tab.current_page + 1}")

        history_tab.previous_page()
        print(f"  After previous_page(): Page {history_tab.current_page + 1}")
    print()

    # Test signals
    print("Testing signals:")
    signals = ['video_opened', 'video_deleted', 'video_regenerated']
    for signal in signals:
        if hasattr(history_tab, signal):
            print(f"  ✓ {signal}")
        else:
            print(f"  ✗ {signal} - MISSING")
    print()

    # Show window
    print("=" * 70)
    print("Opening HistoryTab window...")
    print("Close the window to complete the test")
    print("=" * 70)
    print()

    history_tab.setWindowTitle("History Tab Test")
    history_tab.resize(1200, 800)
    history_tab.show()

    sys.exit(app.exec())


def test_history_tab_filters():
    """Test filter and sort functionality"""
    print("=" * 70)
    print("FILTER AND SORT TEST")
    print("=" * 70)
    print()

    app = QApplication(sys.argv)
    history_tab = HistoryTab(db_manager=None)

    # Test different filters
    test_cases = [
        {'search': 'sunset', 'model': 'All', 'status': 'All'},
        {'search': '', 'model': 'veo-2.0', 'status': 'All'},
        {'search': '', 'model': 'All', 'status': 'completed'},
        {'search': '', 'model': 'veo-1.0', 'status': 'failed'}
    ]

    print(f"Total videos: {len(history_tab.all_videos)}\n")

    for i, filters in enumerate(test_cases, 1):
        history_tab.current_filters.update(filters)
        filtered = history_tab.apply_filters(history_tab.all_videos)

        print(f"Test {i}:")
        print(f"  Filters: {filters}")
        print(f"  Results: {len(filtered)} videos")
        print()

    # Test sorting
    print("Testing sort options:")
    sort_options = [
        ('date_desc', 'Date (Newest First)'),
        ('date_asc', 'Date (Oldest First)'),
        ('duration_desc', 'Duration (Longest)'),
        ('duration_asc', 'Duration (Shortest)'),
        ('name_asc', 'Name (A-Z)'),
        ('name_desc', 'Name (Z-A)')
    ]

    for sort_key, sort_name in sort_options:
        sorted_videos = history_tab.sort_videos(history_tab.all_videos, sort_key)
        print(f"  {sort_name}: First video - {sorted_videos[0].get('prompt', 'N/A')[:40]}...")

    print()
    print("=" * 70)
    print("Filter test complete")
    print("=" * 70)


def main():
    """Main test function"""
    print("\n" + "=" * 70)
    print("HISTORY TAB TEST SUITE")
    print("=" * 70 + "\n")

    # Menu
    print("Choose a test:")
    print("  1. UI Test (opens window)")
    print("  2. Filter and Sort Test")
    print("  3. Both")
    print()

    choice = input("Enter choice (1-3) [1]: ").strip() or "1"
    print()

    if choice == "1":
        test_history_tab_ui()
    elif choice == "2":
        test_history_tab_filters()
    elif choice == "3":
        test_history_tab_filters()
        test_history_tab_ui()
    else:
        print("Invalid choice")


if __name__ == '__main__':
    main()
