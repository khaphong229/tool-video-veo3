"""
Test main application with History tab integrated
"""

import sys
import os

# Suppress console encoding errors
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from PyQt6.QtWidgets import QApplication


def test_main_window():
    """Test MainWindow with History tab"""
    print("="*70)
    print("MAIN WINDOW WITH HISTORY TAB TEST")
    print("="*70)
    print()

    # Create application
    app = QApplication(sys.argv)

    print("1. Importing MainWindow...")
    try:
        from ui import MainWindow
        print("   SUCCESS - MainWindow imported")
    except Exception as e:
        print(f"   FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

    print()
    print("2. Creating MainWindow...")
    try:
        window = MainWindow()
        print("   SUCCESS - MainWindow created")
    except Exception as e:
        print(f"   FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

    print()
    print("3. Checking tab count...")
    try:
        tab_count = window.tabs.count()
        assert tab_count == 4, f"Expected 4 tabs, got {tab_count}"
        print(f"   SUCCESS - Found {tab_count} tabs")
    except Exception as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("4. Checking tab names...")
    try:
        expected_tabs = [
            "Text to Video",
            "Image to Video",
            "Scene Manager",
            "History & Library"
        ]

        for i, expected_name in enumerate(expected_tabs):
            actual_name = window.tabs.tabText(i)
            assert actual_name == expected_name, f"Tab {i}: expected '{expected_name}', got '{actual_name}'"
            print(f"   Tab {i}: {actual_name}")

        print("   SUCCESS - All tab names correct")
    except Exception as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("5. Checking History tab widget...")
    try:
        history_tab = window.tabs.widget(3)  # 4th tab (index 3)
        from ui.tabs import HistoryTab
        assert isinstance(history_tab, HistoryTab), f"Expected HistoryTab, got {type(history_tab)}"
        print("   SUCCESS - History tab is correct type")
    except Exception as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("6. Checking History tab functionality...")
    try:
        assert hasattr(history_tab, 'load_history')
        assert hasattr(history_tab, 'refresh_history')
        assert hasattr(history_tab, 'delete_video')
        assert len(history_tab.all_videos) > 0
        print(f"   SUCCESS - History tab has {len(history_tab.all_videos)} mock videos")
    except Exception as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("7. Checking signal connections...")
    try:
        # Check that MainWindow has the signal handlers
        assert hasattr(window, 'on_video_opened')
        assert hasattr(window, 'on_video_deleted')
        assert hasattr(window, 'on_video_regenerated')
        print("   SUCCESS - All signal handlers present")
    except Exception as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("8. Switching to History tab...")
    try:
        window.tabs.setCurrentIndex(3)
        current_index = window.tabs.currentIndex()
        assert current_index == 3
        print("   SUCCESS - Switched to History tab")
    except Exception as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("="*70)
    print("ALL TESTS PASSED - Application is ready!")
    print("="*70)
    print()
    print("You can now run 'python main.py' to start the application")
    print("and navigate to the History & Library tab.")
    print()

    return True


if __name__ == '__main__':
    success = test_main_window()
    sys.exit(0 if success else 1)
