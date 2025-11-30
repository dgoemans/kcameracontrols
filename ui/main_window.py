"""
Main window UI for KCameraControls.

Provides the main interface for camera controls and effects management.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QPushButton, QMessageBox,
    QDialog, QDialogButtonBox, QFormLayout, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
import os

from backend.camera import CameraBackend, CameraDevice
from backend.effects import EffectsPipeline
from ui.effects_panel import EffectsPanel


class EffectConfigDialog(QDialog):
    """Dialog for configuring an effect's parameters."""
    
    def __init__(self, effect, camera, camera_backend, parent=None):
        super().__init__(parent)
        self.effect = effect
        self.camera = camera
        self.camera_backend = camera_backend
        
        self.setWindowTitle(f"Configure {effect.name}")
        self.setModal(True)
        self.setMinimumSize(400, 150)  # Set minimum size to ensure slider is visible
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  # Add padding
        layout.setSpacing(10)
        
        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(10)
        
        if self.camera:
            # Get the control for this effect
            control_name = self.effect.effect_type.value
            controls = self.camera.controls
            
            if control_name in controls:
                control = controls[control_name]
                
                # Create slider for the control
                slider = QSlider(Qt.Orientation.Horizontal)
                slider.setMinimum(control.get('min', 0))
                slider.setMaximum(control.get('max', 100))
                slider.setMinimumWidth(250)  # Ensure slider is wide enough
                
                # Get current value
                current_value = self.camera_backend.get_camera_control_value(
                    self.camera, control_name
                )
                if current_value is not None:
                    slider.setValue(current_value)
                else:
                    slider.setValue(control.get('default', 0))
                
                # Value label
                value_label = QLabel(str(slider.value()))
                value_label.setMinimumWidth(40)
                slider.valueChanged.connect(lambda v: value_label.setText(str(v)))
                slider.valueChanged.connect(
                    lambda v: self.camera_backend.set_camera_control(
                        self.camera, control_name, v
                    )
                )
                
                control_layout = QHBoxLayout()
                control_layout.addWidget(slider)
                control_layout.addWidget(value_label)
                
                form_layout.addRow(f"{control_name.replace('_', ' ').title()}:", control_layout)
            else:
                label = QLabel(f"Control '{control_name}' not available for this camera")
                label.setWordWrap(True)
                form_layout.addRow(label)
        else:
            form_layout.addRow(QLabel("No camera selected"))
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Backend
        self.camera_backend = CameraBackend()
        self.effects_pipeline = EffectsPipeline()
        self.current_camera = None
        
        # UI setup
        self.setWindowTitle("KCamera Controls")
        self.setMinimumSize(600, 500)
        
        # Set window icon
        icon_path = self._get_icon_path()
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setup_ui()
        self.refresh_cameras()
    
    def _get_icon_path(self):
        """Get the path to the application icon."""
        # Try multiple locations
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'kcameracontrols.svg'),
            '/usr/local/share/kcameracontrols/resources/kcameracontrols.svg',
            '/usr/share/icons/hicolor/scalable/apps/kcameracontrols.svg',
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def setup_ui(self):
        """Set up the main window UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Camera input selector
        input_layout = QHBoxLayout()
        input_label = QLabel("Input:")
        input_label.setStyleSheet("font-weight: bold;")
        input_layout.addWidget(input_label)
        
        self.camera_combo = QComboBox()
        self.camera_combo.currentIndexChanged.connect(self.on_camera_changed)
        input_layout.addWidget(self.camera_combo)
        
        # Refresh button with text instead of emoji
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setToolTip("Refresh camera list")
        refresh_btn.clicked.connect(self.refresh_cameras)
        input_layout.addWidget(refresh_btn)
        
        layout.addLayout(input_layout)
        
        # Effects panel
        self.effects_panel = EffectsPanel(self.effects_pipeline)
        self.effects_panel.effect_configured.connect(self.configure_effect)
        self.effects_panel.effect_removed.connect(self.on_effect_removed)
        layout.addWidget(self.effects_panel)
        
        # Apply Breeze-style theme
        self.apply_kde_style()
    
    def apply_kde_style(self):
        """Apply KDE Breeze-inspired styling."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #eff0f1;
            }
            QLabel {
                color: #31363b;
            }
            QComboBox {
                padding: 5px;
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
            }
            QComboBox:hover {
                border: 1px solid #3daee9;
            }
            QComboBox::drop-down {
                border: none;
            }
            QPushButton {
                background-color: #fcfcfc;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #e3e5e7;
                border: 1px solid #3daee9;
            }
            QPushButton:pressed {
                background-color: #d0d1d2;
            }
            QFrame {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
    
    def refresh_cameras(self):
        """Refresh the list of available cameras."""
        cameras = self.camera_backend.detect_cameras()
        
        self.camera_combo.clear()
        
        if cameras:
            for camera in cameras:
                self.camera_combo.addItem(str(camera), camera)
        else:
            self.camera_combo.addItem("No cameras detected", None)
    
    def on_camera_changed(self, index):
        """Handle camera selection change."""
        camera = self.camera_combo.itemData(index)
        
        if camera:
            self.current_camera = camera
            # Get camera controls
            controls = self.camera_backend.get_camera_controls(camera)
            # Update effects panel with available controls
            self.effects_panel.set_available_controls(controls)
        else:
            self.current_camera = None
            self.effects_panel.set_available_controls(None)
    
    def configure_effect(self, effect_index):
        """Open configuration dialog for an effect."""
        effect = self.effects_pipeline.get_effect(effect_index)
        
        if effect:
            dialog = EffectConfigDialog(
                effect, 
                self.current_camera, 
                self.camera_backend,
                self
            )
            dialog.exec()
    
    def on_effect_removed(self, effect_index, effect):
        """Handle effect removal by resetting its control to default."""
        if self.current_camera and effect:
            control_name = effect.effect_type.value
            controls = self.current_camera.controls
            
            if control_name in controls:
                # Reset to default value
                default_value = controls[control_name].get('default', 0)
                self.camera_backend.set_camera_control(
                    self.current_camera, control_name, default_value
                )
    
    def show_about_dialog(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About KCamera Controls",
            "<h3>KCamera Controls</h3>"
            "<p>A camera controls pipeline for KDE Plasma on Linux.</p>"
            "<p>Version 1.0.0</p>"
            "<p>Provides system tray integration and camera effects management.</p>"
        )
