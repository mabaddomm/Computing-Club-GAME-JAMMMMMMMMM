"""Wall game object - static obstacle"""

import pygame
from game import GameObject


class Wall(GameObject):
    """Static wall obstacle for level design"""
    
    def __init__(self, x, y, width, height):
        super().__init__(x, y)
        self.width = width
        self.height = height
        
        # Collision rect
        self.rect = pygame.Rect(int(x), int(y), width, height)
        
        # Visual
        self.color = (50, 20, 20)  # Dark reddish brown
    
    def update(self, dt):
        """Walls don't move or update"""
        pass
    
    def render(self, screen):
        """Render the wall"""
        if self.visible:
            pygame.draw.rect(screen, self.color, self.rect)

