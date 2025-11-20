"""Static present game object - just displays a present sprite"""

import pygame
import random
from game import GameObject


class StaticPresent(GameObject):
    """A present that just sits there looking pretty"""
    
    # Available present sprites
    PRESENT_IMAGES = [
        'assets/images/christmas/presents/present_1.png',
        'assets/images/christmas/presents/present_2.png',
        'assets/images/christmas/presents/present_3.png',
        'assets/images/christmas/presents/present_4.png',
    ]
    
    def __init__(self, x, y, size=64):
        """Initialize static present
        
        Args:
            x: X position
            y: Y position
            size: Size to scale present to (default 64x64)
        """
        super().__init__(x, y)
        self.size = size
        
        # Load random present sprite
        self.sprite = self._load_sprite()
        
        # Set up rect
        self.rect = pygame.Rect(int(x), int(y), self.size, self.size)
    
    def _load_sprite(self):
        """Load a random present sprite
        
        Returns:
            pygame.Surface: Present sprite scaled to size
        """
        try:
            # Pick random present
            image_path = random.choice(self.PRESENT_IMAGES)
            sprite = pygame.image.load(image_path).convert_alpha()
            
            # Scale to desired size
            sprite = pygame.transform.scale(sprite, (self.size, self.size))
            
            return sprite
        except pygame.error as e:
            print(f"⚠️ Error loading present sprite: {e}")
            # Fallback to colored square
            fallback = pygame.Surface((self.size, self.size))
            fallback.fill((200, 50, 50))  # Red
            return fallback
    
    def update(self, dt):
        """Update (does nothing for static present)
        
        Args:
            dt: Delta time in seconds
        """
        # Static - no updates
        pass
    
    def render(self, screen, debug=False):
        """Render the static present
        
        Args:
            screen: pygame screen surface
            debug: If True, show hitbox
        """
        if self.visible and self.sprite:
            screen.blit(self.sprite, (int(self.x), int(self.y)))
            
            if debug:
                pygame.draw.rect(screen, (255, 215, 0), self.rect, 2)

