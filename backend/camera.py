"""
Camera detection and control backend.

This module provides functionality to detect V4L2 cameras and retrieve their controls.
"""

import subprocess
import re
import shutil
from typing import List, Dict, Optional, Any


# Control types that should have min/max validation
INTEGER_CONTROL_TYPES = ('int', 'integer', 'int64')


class CameraDevice:
    """Represents a V4L2 camera device."""
    
    def __init__(self, device_path: str, name: str):
        self.device_path = device_path
        self.name = name
        self.controls: Dict[str, Dict[str, Any]] = {}
    
    def __str__(self):
        return f"{self.name} ({self.device_path})"
    
    def __repr__(self):
        return f"CameraDevice(device_path='{self.device_path}', name='{self.name}')"


class CameraBackend:
    """Backend for detecting and controlling V4L2 cameras."""
    
    def __init__(self):
        self.cameras: List[CameraDevice] = []
        self._v4l2_ctl_path = None
    
    def _get_v4l2_ctl_path(self) -> Optional[str]:
        """
        Get the path to v4l2-ctl executable.
        
        Returns:
            Path to v4l2-ctl or None if not found
        """
        if self._v4l2_ctl_path is None:
            self._v4l2_ctl_path = shutil.which('v4l2-ctl')
        return self._v4l2_ctl_path
    
    def detect_cameras(self) -> List[CameraDevice]:
        """
        Detect all available V4L2 camera devices.
        
        Returns:
            List of CameraDevice objects
        """
        cameras = []
        
        # Get v4l2-ctl path
        v4l2_ctl = self._get_v4l2_ctl_path()
        if not v4l2_ctl:
            print("Warning: v4l2-ctl not found. Cannot detect cameras.")
            self.cameras = cameras
            return cameras
        
        try:
            # List all video devices
            result = subprocess.run(
                [v4l2_ctl, '--list-devices'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse the output to extract device paths and names
                lines = result.stdout.strip().split('\n')
                current_name = None
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Device name lines don't start with /
                    if not line.startswith('/'):
                        # Remove trailing colon if present
                        current_name = line.rstrip(':')
                    else:
                        # This is a device path
                        if current_name and '/dev/video' in line:
                            device_path = line.strip()
                            camera = CameraDevice(device_path, current_name)
                            cameras.append(camera)
        
        except subprocess.TimeoutExpired:
            print("Warning: Camera detection timed out.")
        except Exception as e:
            print(f"Error detecting cameras: {e}")
        
        self.cameras = cameras
        return cameras
    
    def get_camera_controls(self, camera: CameraDevice) -> Dict[str, Dict[str, Any]]:
        """
        Get available controls for a camera.
        
        Args:
            camera: The camera device to query
            
        Returns:
            Dictionary of control name to control properties
        """
        controls = {}
        
        # Get v4l2-ctl path
        v4l2_ctl = self._get_v4l2_ctl_path()
        if not v4l2_ctl:
            return controls
        
        try:
            result = subprocess.run(
                [v4l2_ctl, '-d', camera.device_path, '--list-ctrls'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse control information
                # Example line: brightness 0x00980900 (int)    : min=0 max=255 step=1 default=128 value=128
                for line in result.stdout.strip().split('\n'):
                    # Skip empty lines
                    if not line.strip():
                        continue
                    
                    match = re.match(
                        r'^\s*(\w+)\s+0x[0-9a-f]+\s+\((\w+)\)\s*:\s*(.+)$',
                        line,
                        re.IGNORECASE
                    )
                    if match:
                        name = match.group(1)
                        ctrl_type = match.group(2)
                        params = match.group(3)
                        
                        control = {
                            'type': ctrl_type,
                            'name': name
                        }
                        
                        # Parse min, max, step, default, value
                        for param_match in re.finditer(r'(\w+)=(-?\d+)', params):
                            param_name = param_match.group(1)
                            param_value = int(param_match.group(2))
                            control[param_name] = param_value
                        
                        # Validate that we have at least min and max for integer controls
                        if ctrl_type.lower() in INTEGER_CONTROL_TYPES:
                            if 'min' not in control or 'max' not in control:
                                print(f"Warning: Control '{name}' is missing min/max values, skipping")
                                continue
                            
                            # Ensure min <= max
                            if control['min'] > control['max']:
                                print(f"Warning: Control '{name}' has min > max, swapping values")
                                control['min'], control['max'] = control['max'], control['min']
                        
                        controls[name] = control
        
        except Exception as e:
            print(f"Error getting camera controls: {e}")
        
        camera.controls = controls
        return controls
    
    def set_camera_control(self, camera: CameraDevice, control_name: str, value: int) -> bool:
        """
        Set a camera control value.
        
        Args:
            camera: The camera device
            control_name: Name of the control to set
            value: New value for the control
            
        Returns:
            True if successful, False otherwise
        """
        # Get v4l2-ctl path
        v4l2_ctl = self._get_v4l2_ctl_path()
        if not v4l2_ctl:
            return False
        
        try:
            result = subprocess.run(
                [v4l2_ctl, '-d', camera.device_path, '--set-ctrl', f'{control_name}={value}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error setting camera control: {e}")
            return False
    
    def get_camera_control_value(self, camera: CameraDevice, control_name: str) -> Optional[int]:
        """
        Get current value of a camera control.
        
        Args:
            camera: The camera device
            control_name: Name of the control
            
        Returns:
            Current value or None if not available
        """
        # Get v4l2-ctl path
        v4l2_ctl = self._get_v4l2_ctl_path()
        if not v4l2_ctl:
            return None
        
        try:
            result = subprocess.run(
                [v4l2_ctl, '-d', camera.device_path, '--get-ctrl', control_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse output like "brightness: 128"
                match = re.search(r':\s*(-?\d+)', result.stdout)
                if match:
                    return int(match.group(1))
        
        except Exception as e:
            print(f"Error getting camera control value: {e}")
        
        return None
