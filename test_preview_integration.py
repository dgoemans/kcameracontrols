#!/usr/bin/env python3
"""
Integration test for preview window effects application.

This test simulates the complete flow of adding effects and ensuring
they are applied before opening the preview window.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.camera import CameraDevice
from backend.effects import Effect, EffectType, EffectsPipeline


class MockCameraBackend:
    """Mock camera backend for integration testing."""
    
    def __init__(self):
        self.applied_controls = {}  # Track which controls are applied
    
    def set_camera_control(self, camera, control_name, value):
        """Apply a control to the camera."""
        self.applied_controls[control_name] = value
        print(f"    Applied {control_name} = {value}")
        return True
    
    def get_camera_control_value(self, camera, control_name):
        """Get current value of a control."""
        # Return the applied value if it exists, otherwise a default
        return self.applied_controls.get(control_name, 128)


def simulate_user_workflow():
    """Simulate the complete user workflow."""
    print("\n" + "=" * 60)
    print("Integration Test: Preview Window with Effects")
    print("=" * 60)
    
    # Setup
    backend = MockCameraBackend()
    pipeline = EffectsPipeline()
    
    # Create a mock camera with controls
    camera = CameraDevice('/dev/video0', 'Test Webcam')
    camera.controls = {
        'brightness': {'min': 0, 'max': 255, 'default': 128, 'value': 128},
        'contrast': {'min': 0, 'max': 255, 'default': 128, 'value': 150},
        'saturation': {'min': 0, 'max': 255, 'default': 128, 'value': 100}
    }
    
    print("\n1. User selects camera:", camera)
    
    # User adds effects to pipeline
    print("\n2. User adds effects to pipeline:")
    effects_to_add = [
        EffectType.BRIGHTNESS,
        EffectType.CONTRAST,
        EffectType.SATURATION
    ]
    
    for effect_type in effects_to_add:
        effect = Effect(effect_type)
        pipeline.add_effect(effect)
        print(f"  + Added {effect.name}")
        
        # Simulate on_effect_added: apply current value
        control_name = effect_type.value
        if control_name in camera.controls:
            current_value = backend.get_camera_control_value(camera, control_name)
            backend.set_camera_control(camera, control_name, current_value)
    
    # User configures one effect
    print("\n3. User configures Brightness to 200:")
    brightness_effect = pipeline.get_effect(0)
    backend.set_camera_control(camera, 'brightness', 200)
    
    # User opens preview
    print("\n4. User opens preview - applying all enabled effects:")
    effects = pipeline.get_all_effects()
    for effect in effects:
        if effect.enabled:
            control_name = effect.effect_type.value
            if control_name in camera.controls:
                current_value = backend.get_camera_control_value(camera, control_name)
                backend.set_camera_control(camera, control_name, current_value)
    
    # Verify all effects are applied
    print("\n5. Verification:")
    expected_controls = ['brightness', 'contrast', 'saturation']
    for control in expected_controls:
        if control in backend.applied_controls:
            print(f"  ✓ {control.title()} is applied (value: {backend.applied_controls[control]})")
        else:
            print(f"  ✗ {control.title()} is NOT applied")
            return False
    
    # Verify brightness has the configured value
    if backend.applied_controls['brightness'] == 200:
        print("\n  ✓ Configured brightness value (200) is applied")
    else:
        print(f"\n  ✗ Brightness should be 200, but is {backend.applied_controls['brightness']}")
        return False
    
    print("\n6. Preview window would now show camera feed with all effects applied")
    
    print("\n" + "=" * 60)
    print("Integration test passed! ✓")
    print("=" * 60)
    
    return True


def test_disabled_effect_not_applied():
    """Test that disabled effects are not applied."""
    print("\n" + "=" * 60)
    print("Test: Disabled effects are not applied")
    print("=" * 60)
    
    backend = MockCameraBackend()
    pipeline = EffectsPipeline()
    
    camera = CameraDevice('/dev/video0', 'Test Webcam')
    camera.controls = {
        'brightness': {'min': 0, 'max': 255, 'default': 128},
        'contrast': {'min': 0, 'max': 255, 'default': 128}
    }
    
    # Add two effects
    pipeline.add_effect(Effect(EffectType.BRIGHTNESS))
    pipeline.add_effect(Effect(EffectType.CONTRAST))
    
    # Disable contrast
    pipeline.toggle_effect(1)
    print("\n  Disabled Contrast effect")
    
    # Apply all effects (like before preview)
    print("\n  Applying all enabled effects:")
    effects = pipeline.get_all_effects()
    for effect in effects:
        if effect.enabled:
            control_name = effect.effect_type.value
            if control_name in camera.controls:
                current_value = backend.get_camera_control_value(camera, control_name)
                backend.set_camera_control(camera, control_name, current_value)
    
    # Verify
    if 'brightness' in backend.applied_controls and 'contrast' not in backend.applied_controls:
        print("\n  ✓ Only enabled effects (Brightness) were applied")
        print("  ✓ Disabled effect (Contrast) was NOT applied")
        print("\n" + "=" * 60)
        print("Test passed! ✓")
        print("=" * 60)
        return True
    else:
        print("\n  ✗ Test failed")
        return False


def main():
    """Run all integration tests."""
    all_passed = True
    
    try:
        if not simulate_user_workflow():
            all_passed = False
    except Exception as e:
        print(f"\n✗ Integration test failed with error: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    try:
        if not test_disabled_effect_not_applied():
            all_passed = False
    except Exception as e:
        print(f"\n✗ Disabled effect test failed with error: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
