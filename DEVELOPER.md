# KCamera Controls - Developer Documentation

## Architecture

### Overview

KCamera Controls is built with a clean separation between backend logic and UI:

```
┌─────────────────────────────────────────┐
│          Application Layer              │
│    (kcameracontrols.py)                │
└─────────────────────────────────────────┘
           │                    │
           ▼                    ▼
┌──────────────────┐  ┌──────────────────┐
│   UI Layer       │  │  Backend Layer   │
│   (PyQt6)        │  │  (Pure Python)   │
├──────────────────┤  ├──────────────────┤
│ • SystemTray     │  │ • CameraBackend  │
│ • MainWindow     │  │ • EffectsPipeline│
│ • EffectsPanel   │  │ • Effect         │
│ • EffectRow      │  │                  │
└──────────────────┘  └──────────────────┘
           │                    │
           └────────┬───────────┘
                    ▼
         ┌──────────────────┐
         │  V4L2 (v4l2-ctl) │
         │  System Cameras  │
         └──────────────────┘
```

## Components

### Backend (`backend/`)

#### `camera.py`
- **CameraDevice**: Represents a V4L2 camera
- **CameraBackend**: Handles camera detection and control
  - `detect_cameras()`: Discovers available cameras
  - `get_camera_controls()`: Retrieves available controls for a camera
  - `set_camera_control()`: Sets a control value
  - `get_camera_control_value()`: Gets current control value

#### `effects.py`
- **EffectType**: Enum of available effect types
- **Effect**: Represents a single effect
- **EffectsPipeline**: Manages the effects chain
  - `add_effect()`: Adds effect to pipeline
  - `remove_effect()`: Removes effect by index
  - `move_effect()`: Reorders effects
  - `toggle_effect()`: Enables/disables effect

### UI (`ui/`)

#### `system_tray.py`
- **SystemTray**: System tray integration
  - Signals: `open_requested`, `about_requested`, `quit_requested`
  - Context menu: Open, About, Quit

#### `main_window.py`
- **MainWindow**: Main application window
  - Camera input selector (dropdown)
  - Effects panel integration
  - KDE Breeze styling
- **EffectConfigDialog**: Configure individual effect parameters
  - Dynamic slider based on V4L2 control ranges
  - Real-time control updates

#### `effects_panel.py`
- **EffectsPanel**: Effects pipeline UI
  - Add button with dropdown menu
  - Scrollable effects list
- **EffectRow**: Individual effect row
  - Title, configure button, delete button
  - Signals for user actions

## V4L2 Integration

The application uses the `v4l2-ctl` command-line tool to interact with cameras:

### Camera Detection
```bash
v4l2-ctl --list-devices
```

### Control Listing
```bash
v4l2-ctl -d /dev/video0 --list-ctrls
```

### Setting Controls
```bash
v4l2-ctl -d /dev/video0 --set-ctrl brightness=128
```

### Getting Controls
```bash
v4l2-ctl -d /dev/video0 --get-ctrl brightness
```

## Supported Camera Controls

The application supports these V4L2 controls (when available on the camera):

- **brightness**: Image brightness adjustment
- **contrast**: Image contrast adjustment
- **saturation**: Color saturation
- **hue**: Color hue shift
- **sharpness**: Image sharpness
- **gamma**: Gamma correction
- **zoom_absolute**: Digital/optical zoom
- **exposure_absolute**: Exposure time
- **gain**: Sensor gain/ISO
- **white_balance_temperature**: White balance in Kelvin
- **focus_absolute**: Focus distance
- **backlight_compensation**: Backlight compensation

Not all cameras support all controls. The application dynamically detects available controls.

## UI Design

The UI follows KDE Breeze design guidelines:

### Color Palette
- Primary: `#3daee9` (Blue)
- Background: `#eff0f1` (Light gray)
- Text: `#31363b` (Dark gray)
- Borders: `#bdc3c7` (Medium gray)
- Hover: `#45b8f3` (Lighter blue)

### Components
- Rounded corners (3-4px)
- Subtle shadows on panels
- Icon buttons (30x30px)
- Clear visual hierarchy

## Adding New Effects

To add a new effect type:

1. Add to `EffectType` enum in `backend/effects.py`:
   ```python
   class EffectType(Enum):
       NEW_EFFECT = "v4l2_control_name"
   ```

2. The effect will automatically appear in the "Add Effect" dropdown

3. Ensure the V4L2 control name matches the camera's control

## Testing

### Component Tests
```bash
python3 test_components.py
```

### Backend Demo
```bash
python3 demo.py
```

### Running the Application
```bash
python3 kcameracontrols.py
```

## Dependencies

### Runtime Dependencies
- Python 3.8+
- PyQt6 >= 6.4.0
- v4l-utils (provides v4l2-ctl)

### System Requirements
- Linux with V4L2 support
- X11 or Wayland
- KDE Plasma (recommended, but works on any DE)

## Future Enhancements

Potential features for future development:

1. **Camera Preview**: Live camera feed in the UI
2. **Pipeline Presets**: Save/load effect configurations
3. **Per-Application Profiles**: Different settings for different apps
4. **Drag-and-Drop Reordering**: Visual effect reordering
5. **Advanced Effects**: Custom processing beyond V4L2 controls
6. **Multi-Camera Support**: Switch between multiple cameras
7. **Hotkey Support**: Global shortcuts for quick adjustments
8. **Tray Notifications**: Status updates and warnings
9. **Auto-Start**: Automatic launch on login
10. **Export/Import Settings**: Share configurations

## Contributing

When contributing:

1. Follow PEP 8 style guide
2. Add docstrings to new functions/classes
3. Test with real cameras when possible
4. Maintain separation between UI and backend
5. Keep KDE design guidelines in mind

## License

MIT License - See LICENSE file for details
