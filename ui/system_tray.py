"""
System tray integration for KCameraControls.

Provides a system tray icon with context menu.
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QStyle, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal
import os


class SystemTray(QObject):
    """System tray icon with context menu."""
    
    # Signals
    open_requested = pyqtSignal()
    about_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    
    def __init__(self, icon_path: str = None):
        super().__init__()
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon()
        
        # Set icon
        if icon_path and os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # Try to find the icon in standard locations
            found_icon = False
            possible_paths = [
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'kcameracontrols.svg'),
                '/usr/local/share/kcameracontrols/resources/kcameracontrols.svg',
                '/usr/share/icons/hicolor/scalable/apps/kcameracontrols.svg',
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    self.tray_icon.setIcon(QIcon(path))
                    found_icon = True
                    break
            
            if not found_icon:
                # Use a built-in camera icon as fallback
                style = QApplication.style()
                icon = style.standardIcon(QStyle.StandardPixmap.SP_DriveDVD)  # Camera-like icon
                self.tray_icon.setIcon(icon)
        
        self.tray_icon.setToolTip("KCamera Controls")
        
        # Create context menu
        self.create_context_menu()
        
        # Connect signals
        self.tray_icon.activated.connect(self.on_tray_activated)
    
    def create_context_menu(self):
        """Create the context menu for the system tray icon."""
        menu = QMenu()
        
        # Open action
        open_action = QAction("Open", menu)
        open_action.triggered.connect(self.open_requested.emit)
        menu.addAction(open_action)
        
        menu.addSeparator()
        
        # About action
        about_action = QAction("About", menu)
        about_action.triggered.connect(self.about_requested.emit)
        menu.addAction(about_action)
        
        menu.addSeparator()
        
        # Quit action
        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(self.quit_requested.emit)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Left click
            self.open_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.Context:
            # Right click (context menu is shown automatically)
            pass
    
    def show(self):
        """Show the system tray icon."""
        self.tray_icon.show()
    
    def hide(self):
        """Hide the system tray icon."""
        self.tray_icon.hide()
    
    def show_message(self, title: str, message: str, icon=QSystemTrayIcon.MessageIcon.Information, duration: int = 3000):
        """
        Show a notification message.
        
        Args:
            title: Message title
            message: Message body
            icon: Message icon type
            duration: Duration in milliseconds
        """
        self.tray_icon.showMessage(title, message, icon, duration)
