"""Base entity class for all game entities"""

from abc import ABC, abstractmethod


class Entity(ABC):
    """Base class for all game entities (GameObjects and UIElements)"""
    
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.active = True
        self.visible = True
    
    @abstractmethod
    def update(self, dt):
        """Update entity logic
        
        Args:
            dt: Delta time in seconds since last update
        """
        pass
    
    @abstractmethod
    def render(self, screen):
        """Render entity to screen
        
        Args:
            screen: pygame.Surface to render to
        """
        pass

