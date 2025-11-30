"""
Effects panel UI component.

Displays and manages the effects pipeline.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QScrollArea, QFrame, QLabel, QMenu, QStyle, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QPoint
from PyQt6.QtGui import QIcon, QAction, QDrag
from backend.effects import Effect, EffectType, EffectsPipeline


class EffectRow(QFrame):
    """A single effect row in the pipeline."""
    
    # Signals
    configure_requested = pyqtSignal(int)  # Effect index
    delete_requested = pyqtSignal(int)     # Effect index
    move_requested = pyqtSignal(int, int)  # from_index, to_index
    
    def __init__(self, effect: Effect, index: int, parent=None):
        super().__init__(parent)
        self.effect = effect
        self.index = index
        self.drag_start_position = None
        
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setAcceptDrops(True)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI for the effect row."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Drag handle (visual indicator)
        drag_label = QLabel("☰")
        drag_label.setStyleSheet("color: #7f8c8d; font-size: 16px;")
        drag_label.setToolTip("Drag to reorder")
        layout.addWidget(drag_label)
        
        # Effect title
        title_label = QLabel(self.effect.name)
        title_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Config button with text instead of emoji for accessibility
        config_btn = QPushButton("Configure")
        config_btn.setToolTip("Configure effect")
        config_btn.clicked.connect(lambda: self.configure_requested.emit(self.index))
        layout.addWidget(config_btn)
        
        # Delete button with text instead of emoji for accessibility
        delete_btn = QPushButton("Remove")
        delete_btn.setToolTip("Remove effect")
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.index))
        layout.addWidget(delete_btn)
    
    def mousePressEvent(self, event):
        """Handle mouse press for drag initiation."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for drag operation."""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        
        if self.drag_start_position is None:
            return
        
        # Check if we've moved far enough to start a drag
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
        
        # Start drag operation
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(str(self.index))
        drag.setMimeData(mime_data)
        
        # Perform drag
        drag.exec(Qt.DropAction.MoveAction)
    
    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Handle drop event."""
        if event.mimeData().hasText():
            from_index = int(event.mimeData().text())
            to_index = self.index
            
            if from_index != to_index:
                self.move_requested.emit(from_index, to_index)
            
            event.acceptProposedAction()


class EffectsPanel(QWidget):
    """Panel for managing the effects pipeline."""
    
    # Signals
    effect_added = pyqtSignal(EffectType)
    effect_removed = pyqtSignal(int, Effect)  # Pass index and the effect being removed
    effect_configured = pyqtSignal(int)
    
    def __init__(self, pipeline: EffectsPipeline, parent=None):
        super().__init__(parent)
        self.pipeline = pipeline
        self.effect_rows = []
        self.available_controls = set()  # Track available camera controls
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI for the effects panel."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Add effect button with dropdown
        header_layout = QHBoxLayout()
        
        add_btn = QPushButton("+ Add Effect")
        add_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #3daee9;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45b8f3;
            }
        """)
        add_btn.clicked.connect(self.show_add_effect_menu)
        header_layout.addWidget(add_btn)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Scroll area for effects list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.effects_container = QWidget()
        self.effects_layout = QVBoxLayout(self.effects_container)
        self.effects_layout.setContentsMargins(0, 5, 0, 5)
        self.effects_layout.addStretch()
        
        scroll.setWidget(self.effects_container)
        layout.addWidget(scroll)
    
    def show_add_effect_menu(self):
        """Show menu to add a new effect."""
        menu = QMenu(self)
        
        # Add all available effect types
        for effect_type in EffectType:
            action = QAction(effect_type.value.replace('_', ' ').title(), menu)
            
            # Disable if control is not available for the camera
            if self.available_controls and effect_type.value not in self.available_controls:
                action.setEnabled(False)
                action.setToolTip("Not available for this camera")
            
            action.triggered.connect(lambda checked, et=effect_type: self.add_effect(et))
            menu.addAction(action)
        
        # Show menu at button position
        sender = self.sender()
        menu.exec(sender.mapToGlobal(sender.rect().bottomLeft()))
    
    def set_available_controls(self, controls):
        """Update the list of available camera controls."""
        if controls:
            self.available_controls = set(controls.keys())
        else:
            self.available_controls = set()
    
    def add_effect(self, effect_type: EffectType):
        """Add a new effect to the pipeline."""
        effect = Effect(effect_type)
        self.pipeline.add_effect(effect)
        self.refresh_effects()
        self.effect_added.emit(effect_type)
    
    def remove_effect(self, index: int):
        """Remove an effect from the pipeline."""
        # Get the effect before removing it
        effect = self.pipeline.get_effect(index)
        if effect and self.pipeline.remove_effect(index):
            self.refresh_effects()
            self.effect_removed.emit(index, effect)
    
    def configure_effect(self, index: int):
        """Open configuration dialog for an effect."""
        self.effect_configured.emit(index)
    
    def refresh_effects(self):
        """Refresh the effects list display."""
        # Clear existing effect rows
        for row in self.effect_rows:
            row.deleteLater()
        self.effect_rows.clear()
        
        # Add current effects
        effects = self.pipeline.get_all_effects()
        for i, effect in enumerate(effects):
            row = EffectRow(effect, i)
            row.configure_requested.connect(self.configure_effect)
            row.delete_requested.connect(self.remove_effect)
            row.move_requested.connect(self.move_effect)
            
            # Insert before the stretch
            self.effects_layout.insertWidget(i, row)
            self.effect_rows.append(row)
    
    def move_effect(self, from_index: int, to_index: int):
        """Move an effect to a new position."""
        if self.pipeline.move_effect(from_index, to_index):
            self.refresh_effects()
