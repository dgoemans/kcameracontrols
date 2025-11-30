#!/usr/bin/env python3
"""
Simple tests to verify KCamera Controls components.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from backend.camera import CameraBackend, CameraDevice
        print("  ✓ backend.camera")
    except ImportError as e:
        print(f"  ✗ backend.camera: {e}")
        return False
    
    try:
        from backend.effects import Effect, EffectType, EffectsPipeline
        print("  ✓ backend.effects")
    except ImportError as e:
        print(f"  ✗ backend.effects: {e}")
        return False
    
    try:
        from ui.system_tray import SystemTray
        print("  ✓ ui.system_tray")
    except ImportError as e:
        print(f"  ✗ ui.system_tray: {e}")
        return False
    
    try:
        from ui.effects_panel import EffectsPanel, EffectRow
        print("  ✓ ui.effects_panel")
    except ImportError as e:
        print(f"  ✗ ui.effects_panel: {e}")
        return False
    
    try:
        from ui.main_window import MainWindow
        print("  ✓ ui.main_window")
    except ImportError as e:
        print(f"  ✗ ui.main_window: {e}")
        return False
    
    return True


def test_camera_backend():
    """Test camera backend functionality."""
    print("\nTesting camera backend...")
    
    from backend.camera import CameraBackend, CameraDevice
    
    backend = CameraBackend()
    print("  ✓ CameraBackend instantiated")
    
    # Test camera detection (may not find cameras in test environment)
    cameras = backend.detect_cameras()
    print(f"  ✓ Camera detection ran (found {len(cameras)} cameras)")
    
    return True


def test_effects_pipeline():
    """Test effects pipeline functionality."""
    print("\nTesting effects pipeline...")
    
    from backend.effects import Effect, EffectType, EffectsPipeline
    
    pipeline = EffectsPipeline()
    print("  ✓ EffectsPipeline instantiated")
    
    # Add an effect
    effect = Effect(EffectType.BRIGHTNESS)
    pipeline.add_effect(effect)
    assert len(pipeline.get_all_effects()) == 1
    print("  ✓ Effect added to pipeline")
    
    # Remove the effect
    pipeline.remove_effect(0)
    assert len(pipeline.get_all_effects()) == 0
    print("  ✓ Effect removed from pipeline")
    
    return True


def main():
    """Run all tests."""
    print("=" * 50)
    print("KCamera Controls Component Tests")
    print("=" * 50)
    
    all_passed = True
    
    if not test_imports():
        all_passed = False
    
    if not test_camera_backend():
        all_passed = False
    
    if not test_effects_pipeline():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed! ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
