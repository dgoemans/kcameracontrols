# KCameraControls

A camera controls pipeline application for KDE Plasma on Linux, providing a system tray interface for managing camera settings and effects.

## Features

- **System Tray Integration**: Lives in the KDE Plasma system tray
- **Camera Pipeline**: Configure and manage camera effects pipeline
- **Effects Support**: Add, remove, and reorder camera effects (similar to EasyEffects for audio)
- **Camera Controls**: Adjust lighting, zoom, exposure, and other camera settings
- **KDE Native**: Designed to feel native to the KDE Plasma environment

## Requirements

- Python 3.8+
- PyQt6 or PySide6
- v4l2-ctl (for camera detection and control) - install via `sudo apt install v4l-utils`
- Linux with V4L2 support
- X11 or Wayland display server (for GUI)
- KDE Plasma desktop environment (recommended)

## Installation

### Flatpak (Recommended)

The easiest way to install KCamera Controls is via Flatpak:

```bash
# Install the flatpak (after downloading from releases or building locally)
flatpak install kcameracontrols.flatpak

# Run the application
flatpak run com.davidgoemans.KCameraControls
```

### Quick Start (for development)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install v4l-utils
# On Debian/Ubuntu:
sudo apt install v4l-utils

# On Fedora/RHEL:
sudo dnf install v4l-utils

# Run the application
python3 kcameracontrols.py
```

### System-wide Installation

The installation script automatically detects your Linux distribution and installs dependencies accordingly.

**Supported distributions:**
- Debian/Ubuntu (using apt)
- Fedora/RHEL/CentOS (using dnf)

```bash
# Run the installation script
./install.sh
```

This will:
- Detect your Linux distribution
- Install Python 3 if not present
- Install pip3 if not present
- Install v4l-utils (provides v4l2-ctl) using the appropriate package manager
- Install Python dependencies
- Copy application files to `/usr/local/share/kcameracontrols`
- Create desktop entry for KDE application menu
- Make the application available system-wide

## Usage

1. The application icon appears in your system tray
2. **Left-click** the icon to open the main control window
3. **Right-click** the icon for quick actions (Open, About, Quit)
4. Select your camera from the input dropdown
5. Add effects using the + button
6. Configure each effect by clicking the config icon
7. Remove effects using the trash icon
8. Reorder effects by dragging them

## Development

This project is built with Python and Qt to provide a native KDE Plasma experience.

### Project Structure

```
kcameracontrols/
├── kcameracontrols.py      # Main application entry point
├── ui/                      # UI components
│   ├── main_window.py      # Main control window
│   ├── effects_panel.py    # Effects pipeline UI
│   └── system_tray.py      # System tray integration
├── backend/                 # Camera and effects backend
│   ├── camera.py           # Camera detection and control
│   └── effects.py          # Effects management
├── resources/               # Icons and assets
├── demo.py                  # Backend functionality demo
├── test_components.py       # Component tests
└── install.sh              # Installation script
```

### Testing

Run the backend demo to see the effects pipeline in action:
```bash
python3 demo.py
```

Run component tests:
```bash
python3 test_components.py
```

⚠️ **Testing Status**: This application has been developed but NOT fully tested in a real environment. Testing needed:
- Real V4L2 cameras
- Actual KDE Plasma system tray
- Visual UI verification
- End-to-end user workflows

Contributions for testing on real systems are welcome!

### Documentation

- [DEVELOPER.md](DEVELOPER.md) - Developer documentation and architecture
- [SCREENSHOTS.md](SCREENSHOTS.md) - UI screenshots and documentation
- [UI_MOCKUP.md](UI_MOCKUP.md) - Detailed UI mockup and design specs

## Troubleshooting

### Control sliders don't respond across the full range

Some camera controls (especially zoom) may report a range like 100-500, but only respond to values up to 200. **This is normal** and is due to hardware limitations, not a software issue.

- V4L2 drivers report theoretical maximum values
- Camera hardware may not use the full theoretical range
- Different camera models have different effective ranges
- The application displays the full V4L2-reported range for transparency

**Solution:** Adjust the slider to find the effective range for your camera. The actual useful range varies by camera model.

### Camera controls not available

If a control (like zoom or focus) isn't available in the "Add Effect" menu:

- Your camera doesn't support that control
- The control isn't exposed via V4L2
- Install `v4l2-ctl` and run `v4l2-ctl -d /dev/video0 --list-ctrls` to see available controls

### Preview doesn't open

The preview feature requires one of these video players:
- mpv (recommended)
- ffplay
- VLC
- Cheese
- guvcview

Install one using your package manager: `sudo apt install mpv`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See [LICENSE](LICENSE) file for details
