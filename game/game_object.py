"""Game object class for interactive game entities"""

import pygame
import math
from game.entity import Entity


class GameObject(Entity):
    """Interactive game objects (players, enemies, items, etc.)"""
    
    def __init__(self, x=0, y=0):
        super().__init__(x, y)
        self.velocity_x = 0
        self.velocity_y = 0
    
    def update(self, dt):
        """Update position based on velocity"""
        if self.active:
            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt
    
    def render(self, screen):
        """Override in subclasses to implement rendering"""
        if self.visible:
            pass  # Implement rendering in subclasses
    
    def get_distance(self, other):
        """Calculate Euclidean distance to another game object
        
        Args:
            other: Another GameObject with a rect attribute
            
        Returns:
            float: Distance between centers of the two objects
        """
        if not hasattr(self, 'rect') or not hasattr(other, 'rect'):
            return float('inf')
        
        center_x1, center_y1 = self.rect.center
        center_x2, center_y2 = other.rect.center
        return math.sqrt((center_x2 - center_x1) ** 2 + (center_y2 - center_y1) ** 2)

