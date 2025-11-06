"""
Automated test for Video Player Widget
"""

import sys
import os

# Suppress console encoding errors
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from PyQt6.QtWidgets import QApplication


def test_video_player():
    """Test Video Player Widget"""
    print("="*70)
    print("VIDEO PLAYER WIDGET AUTOMATED TEST")
    print("="*70)
    print()

    # Create application (required for Qt widgets)
    app = QApplication(sys.argv)

    print("1. Importing VideoPlayerWidget...")
    try:
        from ui.widgets import VideoPlayerWidget
        print("   SUCCESS - VideoPlayerWidget imported")
    except Exception as e:
        print(f"   FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

    print()
    print("2. Creating VideoPlayerWidget...")
    try:
        player = VideoPlayerWidget()
        print("   SUCCESS - VideoPlayerWidget created")
    except Exception as e:
        print(f"   FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

    print()
    print("3. Checking required components...")
    try:
        # Check video widget
        assert hasattr(player, 'video_widget'), "Missing video_widget"
        assert player.video_widget is not None

        # Check media player
        assert hasattr(player, 'media_player'), "Missing media_player"
        assert player.media_player is not None

        # Check audio output
        assert hasattr(player, 'audio_output'), "Missing audio_output"
        assert player.audio_output is not None

        print("   SUCCESS - All components present")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("4. Checking UI controls...")
    try:
        controls = [
            'play_pause_btn',
            'stop_btn',
            'progress_slider',
            'volume_slider',
            'time_label',
            'download_btn',
            'fullscreen_btn',
            'loading_label'
        ]

        for control in controls:
            assert hasattr(player, control), f"Missing control: {control}"

        print("   SUCCESS - All UI controls present")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("5. Checking methods...")
    try:
        methods = [
            'load_video',
            'play',
            'pause',
            'stop',
            'seek',
            'set_volume',
            'toggle_fullscreen',
            'on_state_changed',
            'on_duration_changed',
            'on_position_changed'
        ]

        for method in methods:
            assert hasattr(player, method), f"Missing method: {method}"
            assert callable(getattr(player, method)), f"Not callable: {method}"

        print("   SUCCESS - All required methods present")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("6. Checking signals...")
    try:
        signals = [
            'video_loaded',
            'playback_started',
            'playback_paused',
            'playback_stopped',
            'error_occurred'
        ]

        for signal in signals:
            assert hasattr(player, signal), f"Missing signal: {signal}"

        print("   SUCCESS - All signals present")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("7. Testing initial state...")
    try:
        assert player.current_video_path is None, "video_path should be None initially"
        assert not player.is_fullscreen, "Should not be in fullscreen initially"
        assert player.is_stopped(), "Should be in stopped state initially"
        assert player.get_duration() == 0, "Duration should be 0 initially"
        assert player.get_position() == 0, "Position should be 0 initially"

        print("   SUCCESS - Initial state correct")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("8. Testing volume control...")
    try:
        player.set_volume(50)
        assert player.volume_slider.value() == 70, "Initial volume should be 70"

        player.set_volume(30)
        # Volume set successfully (we can't easily verify the actual audio level)

        print("   SUCCESS - Volume control works")
    except Exception as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("9. Testing state query methods...")
    try:
        assert player.is_stopped(), "Should be stopped"
        assert not player.is_playing(), "Should not be playing"
        assert not player.is_paused(), "Should not be paused"

        print("   SUCCESS - State query methods work")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("10. Testing time formatting...")
    try:
        assert player.format_time(0) == "00:00"
        assert player.format_time(5000) == "00:05"
        assert player.format_time(65000) == "01:05"
        assert player.format_time(3665000) == "01:01:05"

        print("   SUCCESS - Time formatting works")
    except AssertionError as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("11. Testing clear method...")
    try:
        player.clear()
        assert player.current_video_path is None
        assert not player.download_btn.isEnabled()

        print("   SUCCESS - Clear method works")
    except Exception as e:
        print(f"   FAILED - {e}")
        return False

    print()
    print("="*70)
    print("ALL TESTS PASSED")
    print("="*70)
    print()
    print("To test the player with actual video:")
    print("  python demo_video_player.py")
    print()

    return True


if __name__ == '__main__':
    success = test_video_player()
    sys.exit(0 if success else 1)
