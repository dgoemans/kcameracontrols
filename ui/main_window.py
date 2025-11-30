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
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
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
                form_layout.addRow(QLabel(f"Control '{control_name}' not available for this camera"))
        else:
            form_layout.addRow(QLabel("No camera selected"))
        
        layout.addLayout(form_layout)
        
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
        
        self.setup_ui()
        self.refresh_cameras()
    
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
        
        # Refresh button
        refresh_btn = QPushButton("🔄")
        refresh_btn.setToolTip("Refresh camera list")
        refresh_btn.setFixedSize(30, 30)
        refresh_btn.clicked.connect(self.refresh_cameras)
        input_layout.addWidget(refresh_btn)
        
        layout.addLayout(input_layout)
        
        # Effects panel
        self.effects_panel = EffectsPanel(self.effects_pipeline)
        self.effects_panel.effect_configured.connect(self.configure_effect)
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
            self.camera_backend.get_camera_controls(camera)
        else:
            self.current_camera = None
    
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
