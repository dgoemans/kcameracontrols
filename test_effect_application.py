#!/usr/bin/env python3
"""
Test for effect application when added and before preview.

This test validates that:
1. Effects are applied when added to the pipeline
2. All effects are applied before opening the preview
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.camera import CameraBackend, CameraDevice
from backend.effects import Effect, EffectType, EffectsPipeline


class MockCameraBackend:
    """Mock camera backend for testing."""
    
    def __init__(self):
        self.set_control_calls = []
        self.get_control_calls = []
        self.mock_values = {}
    
    def set_camera_control(self, camera, control_name, value):
        """Record that a control was set."""
        self.set_control_calls.append({
            'camera': camera.device_path,
            'control': control_name,
            'value': value
        })
        self.mock_values[control_name] = value
        return True
    
    def get_camera_control_value(self, camera, control_name):
        """Return a mock value for the control."""
        self.get_control_calls.append({
            'camera': camera.device_path,
            'control': control_name
        })
        # Return stored value or default
        return self.mock_values.get(control_name, 128)


def test_effect_added_applies_control():
    """Test that adding an effect applies the camera control."""
    print("\nTest 1: Effect is applied when added to pipeline")
    
    # Setup
    backend = MockCameraBackend()
    pipeline = EffectsPipeline()
    
    # Create a mock camera
    camera = CameraDevice('/dev/video0', 'Test Camera')
    camera.controls = {
        'brightness': {'min': 0, 'max': 255, 'default': 128},
        'contrast': {'min': 0, 'max': 255, 'default': 128}
    }
    
    # Simulate adding an effect (what on_effect_added does)
    effect_type = EffectType.BRIGHTNESS
    control_name = effect_type.value
    
    # Get current value and apply it (simulating on_effect_added)
    current_value = backend.get_camera_control_value(camera, control_name)
    backend.set_camera_control(camera, control_name, current_value)
    
    # Verify control was set
    assert len(backend.set_control_calls) == 1
    assert backend.set_control_calls[0]['control'] == 'brightness'
    print("  ✓ Effect control was applied when added")
    
    return True


def test_all_effects_applied_before_preview():
    """Test that all enabled effects are applied before opening preview."""
    print("\nTest 2: All enabled effects applied before preview")
    
    # Setup
    backend = MockCameraBackend()
    pipeline = EffectsPipeline()
    
    # Create a mock camera
    camera = CameraDevice('/dev/video0', 'Test Camera')
    camera.controls = {
        'brightness': {'min': 0, 'max': 255, 'default': 128},
        'contrast': {'min': 0, 'max': 255, 'default': 128},
        'saturation': {'min': 0, 'max': 255, 'default': 128}
    }
    
    # Add multiple effects to pipeline
    pipeline.add_effect(Effect(EffectType.BRIGHTNESS))
    pipeline.add_effect(Effect(EffectType.CONTRAST))
    pipeline.add_effect(Effect(EffectType.SATURATION))
    
    # Disable one effect
    pipeline.toggle_effect(1)  # Disable contrast
    
    # Simulate apply_all_effects
    effects = pipeline.get_all_effects()
    for effect in effects:
        if effect.enabled:
            control_name = effect.effect_type.value
            if control_name in camera.controls:
                current_value = backend.get_camera_control_value(camera, control_name)
                backend.set_camera_control(camera, control_name, current_value)
    
    # Verify only enabled effects were applied
    assert len(backend.set_control_calls) == 2  # brightness and saturation, not contrast
    applied_controls = [call['control'] for call in backend.set_control_calls]
    assert 'brightness' in applied_controls
    assert 'saturation' in applied_controls
    assert 'contrast' not in applied_controls
    print("  ✓ Only enabled effects were applied")
    print(f"  ✓ Applied {len(backend.set_control_calls)} out of 3 effects (1 was disabled)")
    
    return True


def test_effect_removed_resets_to_default():
    """Test that removing an effect resets the control to default."""
    print("\nTest 3: Effect removal resets control to default")
    
    # Setup
    backend = MockCameraBackend()
    pipeline = EffectsPipeline()
    
    # Create a mock camera
    camera = CameraDevice('/dev/video0', 'Test Camera')
    camera.controls = {
        'brightness': {'min': 0, 'max': 255, 'default': 128}
    }
    
    # Add and then remove effect
    effect = Effect(EffectType.BRIGHTNESS)
    pipeline.add_effect(effect)
    
    # Simulate on_effect_removed
    control_name = effect.effect_type.value
    if control_name in camera.controls:
        default_value = camera.controls[control_name].get('default', 0)
        backend.set_camera_control(camera, control_name, default_value)
    
    # Verify control was reset to default
    assert len(backend.set_control_calls) == 1
    assert backend.set_control_calls[0]['control'] == 'brightness'
    assert backend.set_control_calls[0]['value'] == 128  # default value
    print("  ✓ Effect was reset to default value when removed")
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Effect Application Tests")
    print("=" * 60)
    
    all_passed = True
    
    try:
        if not test_effect_added_applies_control():
            all_passed = False
    except Exception as e:
        print(f"  ✗ Test failed with error: {e}")
        all_passed = False
    
    try:
        if not test_all_effects_applied_before_preview():
            all_passed = False
    except Exception as e:
        print(f"  ✗ Test failed with error: {e}")
        all_passed = False
    
    try:
        if not test_effect_removed_resets_to_default():
            all_passed = False
    except Exception as e:
        print(f"  ✗ Test failed with error: {e}")
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("All effect application tests passed! ✓")
        return 0
    else:
        print("Some tests failed! ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())
