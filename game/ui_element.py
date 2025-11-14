"""UI element class for user interface components"""

import pygame
from game.entity import Entity


class UIElement(Entity):
    """UI elements (buttons, text, HUD, etc.)"""
    
    def __init__(self, x=0, y=0):
        super().__init__(x, y)
    
    def update(self, dt):
        """UI elements typically don't need physics updates"""
        if self.active:
            pass  # Handle UI logic in subclasses
    
    def render(self, screen):
        """Override in subclasses to implement rendering"""
        if self.visible:
            pass  # Implement rendering in subclasses
    
    def handle_event(self, event):
        """Handle pygame events (clicks, hover, etc.)
        
        Args:
            event: pygame.Event to handle
        """
        pass

