"""
Effects pipeline management.

This module manages the effects pipeline for camera processing.
"""

from typing import List, Dict, Any, Optional
from enum import Enum


class EffectType(Enum):
    """Types of available camera effects."""
    BRIGHTNESS = "brightness"
    CONTRAST = "contrast"
    SATURATION = "saturation"
    HUE = "hue"
    SHARPNESS = "sharpness"
    GAMMA = "gamma"
    ZOOM = "zoom_absolute"
    EXPOSURE = "exposure_absolute"
    GAIN = "gain"
    WHITE_BALANCE = "white_balance_temperature"
    FOCUS = "focus_absolute"
    BACKLIGHT_COMPENSATION = "backlight_compensation"


class Effect:
    """Represents a single effect in the pipeline."""
    
    def __init__(self, effect_type: EffectType, name: str = None):
        self.effect_type = effect_type
        self.name = name or effect_type.value.replace('_', ' ').title()
        self.enabled = True
        self.parameters: Dict[str, Any] = {}
    
    def __repr__(self):
        return f"Effect(type={self.effect_type.name}, name='{self.name}', enabled={self.enabled})"


class EffectsPipeline:
    """Manages the effects pipeline for a camera."""
    
    def __init__(self):
        self.effects: List[Effect] = []
    
    def add_effect(self, effect: Effect) -> None:
        """Add an effect to the pipeline."""
        self.effects.append(effect)
    
    def remove_effect(self, index: int) -> bool:
        """
        Remove an effect from the pipeline.
        
        Args:
            index: Index of the effect to remove
            
        Returns:
            True if successful, False otherwise
        """
        if 0 <= index < len(self.effects):
            self.effects.pop(index)
            return True
        return False
    
    def move_effect(self, from_index: int, to_index: int) -> bool:
        """
        Move an effect to a new position in the pipeline.
        
        Args:
            from_index: Current index of the effect
            to_index: Target index for the effect
            
        Returns:
            True if successful, False otherwise
        """
        if 0 <= from_index < len(self.effects) and 0 <= to_index < len(self.effects):
            effect = self.effects.pop(from_index)
            self.effects.insert(to_index, effect)
            return True
        return False
    
    def toggle_effect(self, index: int) -> bool:
        """
        Toggle an effect's enabled state.
        
        Args:
            index: Index of the effect to toggle
            
        Returns:
            True if successful, False otherwise
        """
        if 0 <= index < len(self.effects):
            self.effects[index].enabled = not self.effects[index].enabled
            return True
        return False
    
    def get_effect(self, index: int) -> Optional[Effect]:
        """Get an effect by index."""
        if 0 <= index < len(self.effects):
            return self.effects[index]
        return None
    
    def clear(self) -> None:
        """Remove all effects from the pipeline."""
        self.effects.clear()
    
    def get_all_effects(self) -> List[Effect]:
        """Get all effects in the pipeline."""
        return self.effects.copy()
