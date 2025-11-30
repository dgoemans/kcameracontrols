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

### Control Ranges and Effective Values

**Important Note about Control Ranges:**

Camera controls report min/max ranges via V4L2, but the effective range (values that actually change camera behavior) may be smaller than the reported range. This is a hardware limitation, not a software issue.

For example:
- A camera may report `zoom_absolute: min=100, max=500`
- But the camera hardware may only respond to values up to 200
- Values from 200-500 are accepted but have no additional effect

**Why this happens:**
1. V4L2 drivers report theoretical maximum values from firmware
2. Camera hardware may not utilize the full theoretical range
3. Different camera models have different effective ranges
4. There's no standard V4L2 mechanism to query "effective" ranges

**What the application does:**
- Uses V4L2-reported ranges (device-specific, driver-provided)
- Validates ranges are sensible (min < max, both values exist)
- Displays full range to users with informational text
- Skips controls with invalid or missing range data

**For users:**
If a control doesn't seem to respond across its full range, this is normal camera behavior. Adjust the slider to find the effective range for your specific camera model.

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

### Supported Distributions
The installation script supports the following distributions:
- **Debian/Ubuntu**: Uses `apt` package manager
- **Fedora/RHEL/CentOS**: Uses `dnf` package manager

The script automatically:
- Detects the distribution
- Installs Python 3 if needed
- Installs pip3 if needed
- Installs v4l-utils using the appropriate package manager

## Building Flatpak

### Prerequisites
```bash
# Install flatpak and flatpak-builder
sudo dnf install flatpak flatpak-builder  # Fedora
sudo apt install flatpak flatpak-builder  # Debian/Ubuntu

# Add Flathub repository
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# Install KDE runtime and SDK
flatpak install flathub org.kde.Platform//6.8 org.kde.Sdk//6.8
```

### Local Build
```bash
# Build the flatpak
flatpak-builder --force-clean --install-deps-from=flathub build-dir com.davidgoemans.KCameraControls.yml

# Install locally
flatpak-builder --user --install --force-clean build-dir com.davidgoemans.KCameraControls.yml

# Run the installed flatpak
flatpak run com.davidgoemans.KCameraControls
```

### Export as Bundle
```bash
# Build and export as a single-file bundle
flatpak-builder --repo=repo --force-clean build-dir com.davidgoemans.KCameraControls.yml
flatpak build-bundle repo kcameracontrols.flatpak com.davidgoemans.KCameraControls

# Install the bundle
flatpak install kcameracontrols.flatpak
```

### CI/CD Pipeline
The project includes a GitHub Actions workflow (`.github/workflows/flatpak.yml`) that:
- Automatically builds flatpak on every push to main
- Creates flatpak bundles for releases (tagged commits)
- Uploads artifacts for testing

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
