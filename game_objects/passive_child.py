"""Passive child game object - static sprite with no movement"""

import pygame
from game import GameObject


class PassiveChild(GameObject):
    """A child character that stands still - just a sprite"""
    
    def __init__(self, x, y, direction='down'):
        """Initialize passive child
        
        Args:
            x: X position
            y: Y position
            direction: Facing direction ('up', 'down', 'left', 'right')
        """
        super().__init__(x, y)
        self.direction = direction
        self.width = 48
        self.height = 96
        
        # Load sprite sheet
        self.sprite_sheet = self._load_sprite_sheet()
        self.current_frame = self._get_idle_frame()
        
        # Set up rect
        self.rect = pygame.Rect(int(x), int(y), self.width, self.height)
    
    def _load_sprite_sheet(self):
        """Load and split the child sprite sheet
        
        Returns:
            dict: Dictionary of animation frames by state
        """
        try:
            sheet = pygame.image.load('assets/character.png').convert_alpha()
            
            # Frame dimensions on sheet
            frame_width = 12
            frame_height = 24
            scale_factor = 4  # Scale up to 48x96
            
            # Extract idle frames for each direction
            frames = {
                'idle_down': self._extract_frame(sheet, 0, 0, frame_width, frame_height, scale_factor),
                'idle_up': self._extract_frame(sheet, 0, 3, frame_width, frame_height, scale_factor),
                'idle_left': self._extract_frame(sheet, 0, 2, frame_width, frame_height, scale_factor),
                'idle_right': self._extract_frame(sheet, 0, 1, frame_width, frame_height, scale_factor),
            }
            
            return frames
        except pygame.error as e:
            print(f"⚠️ Error loading child sprite: {e}")
            # Return empty surface as fallback
            fallback = pygame.Surface((self.width, self.height))
            fallback.fill((100, 150, 200))  # Light blue placeholder
            return {
                'idle_down': fallback,
                'idle_up': fallback,
                'idle_left': fallback,
                'idle_right': fallback,
            }
    
    def _extract_frame(self, sheet, col, row, frame_w, frame_h, scale):
        """Extract and scale a single frame from sprite sheet
        
        Args:
            sheet: Source sprite sheet surface
            col: Column index
            row: Row index
            frame_w: Frame width on sheet
            frame_h: Frame height on sheet
            scale: Scale factor
            
        Returns:
            pygame.Surface: Scaled frame
        """
        frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), (col * frame_w, row * frame_h, frame_w, frame_h))
        return pygame.transform.scale(frame, (frame_w * scale, frame_h * scale))
    
    def _get_idle_frame(self):
        """Get the idle frame for current direction
        
        Returns:
            pygame.Surface: Frame to display
        """
        state_key = f'idle_{self.direction}'
        return self.sprite_sheet.get(state_key, self.sprite_sheet.get('idle_down'))
    
    def update(self, dt):
        """Update (does nothing for passive child)
        
        Args:
            dt: Delta time in seconds
        """
        # Passive - no updates needed
        pass
    
    def render(self, screen, debug=False):
        """Render the passive child
        
        Args:
            screen: pygame screen surface
            debug: If True, show hitbox
        """
        if self.visible and self.current_frame:
            screen.blit(self.current_frame, (int(self.x), int(self.y)))
            
            if debug:
                pygame.draw.rect(screen, (255, 255, 0), self.rect, 2)

