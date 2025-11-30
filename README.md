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
- v4l2-ctl (for camera detection and control)
- Linux with V4L2 support

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python3 kcameracontrols.py
```

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
└── resources/               # Icons and assets
```

## License

MIT License
