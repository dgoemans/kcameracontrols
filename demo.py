#!/usr/bin/env python3
"""
Demo script showing KCamera Controls backend functionality.

This script demonstrates the camera and effects backend without requiring a GUI.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.camera import CameraBackend, CameraDevice
from backend.effects import Effect, EffectType, EffectsPipeline


def print_separator():
    """Print a separator line."""
    print("=" * 60)


def demo_camera_detection():
    """Demonstrate camera detection."""
    print_separator()
    print("CAMERA DETECTION DEMO")
    print_separator()
    
    backend = CameraBackend()
    cameras = backend.detect_cameras()
    
    if cameras:
        print(f"\nFound {len(cameras)} camera(s):\n")
        for i, camera in enumerate(cameras, 1):
            print(f"  {i}. {camera}")
    else:
        print("\nNo cameras detected.")
        print("Note: This requires v4l2-ctl to be installed and cameras to be connected.")
    
    return cameras


def demo_camera_controls(cameras):
    """Demonstrate camera controls."""
    print_separator()
    print("CAMERA CONTROLS DEMO")
    print_separator()
    
    if not cameras:
        print("\nNo cameras available for controls demo.")
        return
    
    backend = CameraBackend()
    camera = cameras[0]
    
    print(f"\nRetrieving controls for: {camera.name}\n")
    controls = backend.get_camera_controls(camera)
    
    if controls:
        print(f"Found {len(controls)} control(s):\n")
        for name, control in list(controls.items())[:5]:  # Show first 5
            print(f"  • {name.replace('_', ' ').title()}")
            print(f"    Type: {control['type']}")
            if 'min' in control and 'max' in control:
                print(f"    Range: {control['min']} - {control['max']}")
            if 'value' in control:
                print(f"    Current: {control['value']}")
            print()
        
        if len(controls) > 5:
            print(f"  ... and {len(controls) - 5} more controls")
    else:
        print("No controls available for this camera.")


def demo_effects_pipeline():
    """Demonstrate effects pipeline."""
    print_separator()
    print("EFFECTS PIPELINE DEMO")
    print_separator()
    
    pipeline = EffectsPipeline()
    
    print("\nCreating effects pipeline...")
    
    # Add some effects
    effects_to_add = [
        EffectType.BRIGHTNESS,
        EffectType.CONTRAST,
        EffectType.SATURATION,
        EffectType.ZOOM
    ]
    
    for effect_type in effects_to_add:
        effect = Effect(effect_type)
        pipeline.add_effect(effect)
        print(f"  + Added: {effect.name}")
    
    print(f"\nPipeline now has {len(pipeline.get_all_effects())} effects:\n")
    for i, effect in enumerate(pipeline.get_all_effects(), 1):
        status = "✓ Enabled" if effect.enabled else "✗ Disabled"
        print(f"  {i}. {effect.name} ({status})")
    
    # Demonstrate moving effects
    print("\nMoving 'Zoom' from position 4 to position 1...")
    pipeline.move_effect(3, 0)
    
    print("\nUpdated pipeline order:\n")
    for i, effect in enumerate(pipeline.get_all_effects(), 1):
        print(f"  {i}. {effect.name}")
    
    # Demonstrate toggling
    print("\nToggling effect at position 2...")
    pipeline.toggle_effect(1)
    
    print("\nPipeline status:\n")
    for i, effect in enumerate(pipeline.get_all_effects(), 1):
        status = "✓ Enabled" if effect.enabled else "✗ Disabled"
        print(f"  {i}. {effect.name} ({status})")
    
    # Demonstrate removal
    print("\nRemoving effect at position 1...")
    pipeline.remove_effect(0)
    
    print(f"\nFinal pipeline ({len(pipeline.get_all_effects())} effects):\n")
    for i, effect in enumerate(pipeline.get_all_effects(), 1):
        print(f"  {i}. {effect.name}")


def demo_available_effects():
    """Show all available effect types."""
    print_separator()
    print("AVAILABLE EFFECTS")
    print_separator()
    
    print("\nThe following camera effects are available:\n")
    
    for i, effect_type in enumerate(EffectType, 1):
        name = effect_type.value.replace('_', ' ').title()
        print(f"  {i:2d}. {name}")
        print(f"      V4L2 Control: {effect_type.value}")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "KCamera Controls Backend Demo" + " " * 19 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Run demos
    demo_available_effects()
    cameras = demo_camera_detection()
    demo_camera_controls(cameras)
    demo_effects_pipeline()
    
    print_separator()
    print("Demo completed!")
    print_separator()
    print()


if __name__ == "__main__":
    main()
