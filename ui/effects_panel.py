"""
Effects panel UI component.

Displays and manages the effects pipeline.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QScrollArea, QFrame, QLabel, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction
from backend.effects import Effect, EffectType, EffectsPipeline


class EffectRow(QFrame):
    """A single effect row in the pipeline."""
    
    # Signals
    configure_requested = pyqtSignal(int)  # Effect index
    delete_requested = pyqtSignal(int)     # Effect index
    
    def __init__(self, effect: Effect, index: int, parent=None):
        super().__init__(parent)
        self.effect = effect
        self.index = index
        
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI for the effect row."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Effect title
        title_label = QLabel(self.effect.name)
        title_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Config button
        config_btn = QPushButton("⚙")  # Settings icon
        config_btn.setToolTip("Configure effect")
        config_btn.setFixedSize(30, 30)
        config_btn.clicked.connect(lambda: self.configure_requested.emit(self.index))
        layout.addWidget(config_btn)
        
        # Delete button
        delete_btn = QPushButton("🗑")  # Trash icon
        delete_btn.setToolTip("Remove effect")
        delete_btn.setFixedSize(30, 30)
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.index))
        layout.addWidget(delete_btn)


class EffectsPanel(QWidget):
    """Panel for managing the effects pipeline."""
    
    # Signals
    effect_added = pyqtSignal(EffectType)
    effect_removed = pyqtSignal(int)
    effect_configured = pyqtSignal(int)
    
    def __init__(self, pipeline: EffectsPipeline, parent=None):
        super().__init__(parent)
        self.pipeline = pipeline
        self.effect_rows = []
        
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
            action.triggered.connect(lambda checked, et=effect_type: self.add_effect(et))
            menu.addAction(action)
        
        # Show menu at button position
        sender = self.sender()
        menu.exec(sender.mapToGlobal(sender.rect().bottomLeft()))
    
    def add_effect(self, effect_type: EffectType):
        """Add a new effect to the pipeline."""
        effect = Effect(effect_type)
        self.pipeline.add_effect(effect)
        self.refresh_effects()
        self.effect_added.emit(effect_type)
    
    def remove_effect(self, index: int):
        """Remove an effect from the pipeline."""
        if self.pipeline.remove_effect(index):
            self.refresh_effects()
            self.effect_removed.emit(index)
    
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
            
            # Insert before the stretch
            self.effects_layout.insertWidget(i, row)
            self.effect_rows.append(row)
