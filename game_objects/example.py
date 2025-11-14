"""Example game object - can be used as a template"""

from game import GameObject
import pygame


class SimpleGameObject(GameObject):
    """A simple example game object"""
    
    def __init__(self, x, y, color=(255, 0, 0), size=20):
        super().__init__(x, y)
        self.color = color
        self.size = size
    
    def render(self, screen):
        if self.visible:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

