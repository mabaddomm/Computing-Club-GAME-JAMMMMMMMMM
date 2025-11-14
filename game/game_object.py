"""Game object class for interactive game entities"""

import pygame
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

