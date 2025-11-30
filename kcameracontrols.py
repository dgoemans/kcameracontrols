#!/usr/bin/env python3
"""
KCamera Controls - Main application entry point.

A camera controls pipeline for KDE Plasma on Linux.
"""

import sys
import os

# Add installation directory to Python path if installed system-wide
# This allows importing ui and backend modules when the script is in /usr/local/bin
# but the modules are in /usr/local/share/kcameracontrols
script_dir = os.path.dirname(os.path.abspath(__file__))
# Check if we're running from /usr/local/bin (system installation)
if script_dir == "/usr/local/bin":
    install_dir = "/usr/local/share/kcameracontrols"
    if os.path.isdir(install_dir) and install_dir not in sys.path:
        sys.path.insert(0, install_dir)

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow
from ui.system_tray import SystemTray


class KCameraControlsApp:
    """Main application class."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("KCamera Controls")
        self.app.setOrganizationName("KCameraControls")
        
        # Prevent app from quitting when last window closes
        self.app.setQuitOnLastWindowClosed(False)
        
        # Note: High DPI support is automatic in Qt6/PyQt6, no need to set AA_UseHighDpiPixmaps
        
        # Main window
        self.main_window = MainWindow()
        
        # System tray
        self.system_tray = SystemTray()
        self.system_tray.open_requested.connect(self.show_main_window)
        self.system_tray.about_requested.connect(self.show_about)
        self.system_tray.quit_requested.connect(self.quit_application)
        
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("Warning: System tray is not available on this system")
        
        self.system_tray.show()
        
        # Show main window on startup
        self.main_window.show()
    
    def show_main_window(self):
        """Show the main window."""
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
    
    def show_about(self):
        """Show the about dialog."""
        self.main_window.show_about_dialog()
    
    def quit_application(self):
        """Quit the application."""
        self.system_tray.hide()
        self.app.quit()
    
    def run(self):
        """Run the application."""
        return self.app.exec()


def main():
    """Main entry point."""
    app = KCameraControlsApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
