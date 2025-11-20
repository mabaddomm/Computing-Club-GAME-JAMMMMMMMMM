"""Lives tracker UI element - displays player's remaining lives as present icons"""

import pygame
from game import UIElement


class LivesTracker(UIElement):
    """UI element that displays player lives as present icons"""
    
    def __init__(self, x, y, max_lives=3, icon_size=50, spacing=10):
        """Initialize the lives tracker
        
        Args:
            x: X position (left edge)
            y: Y position (top edge)
            max_lives: Maximum number of lives to display
            icon_size: Size of each life icon (width and height)
            spacing: Space between icons
        """
        super().__init__(x, y)
        self.max_lives = max_lives
        self.current_lives = max_lives
        self.icon_size = icon_size
        self.spacing = spacing
        
        # Font for "Lives:" label
        self.font = pygame.font.Font(None, 36)  # Medium font size to match smaller icons
        self.label_text = "Lives:"
        self.label_color = (0, 0, 0)  # Black
        
        # Render the label once
        self.label_surface = self.font.render(self.label_text, True, self.label_color)
        self.label_width = self.label_surface.get_width()
        self.label_offset = 10  # Space between label and icons
        
        # Load and scale the present icon
        self.life_icon = self._load_icon()
        
        # Total width for positioning (label + icons)
        self.width = self.label_width + self.label_offset + (self.icon_size * self.max_lives) + (self.spacing * (self.max_lives - 1))
        self.height = max(self.icon_size, self.label_surface.get_height())
    
    def _load_icon(self):
        """Load and scale the lives icon
        
        Returns:
            pygame.Surface: Scaled lives icon
        """
        try:
            icon = pygame.image.load('assets/images/christmas/presents/lives.png').convert_alpha()
            # Scale to desired size
            icon = pygame.transform.scale(icon, (self.icon_size, self.icon_size))
            return icon
        except pygame.error as e:
            print(f"⚠️ Error loading life icon: {e}")
            # Fallback: red square
            fallback = pygame.Surface((self.icon_size, self.icon_size))
            fallback.fill((255, 0, 0))
            return fallback
    
    def set_lives(self, lives):
        """Update the number of lives displayed
        
        Args:
            lives: Current number of lives (0 to max_lives)
        """
        self.current_lives = max(0, min(lives, self.max_lives))
    
    def update(self, dt):
        """Update the lives tracker
        
        Args:
            dt: Delta time in seconds
        """
        # Lives tracker is static, no updates needed
        pass
    
    def render(self, screen):
        """Render the lives tracker
        
        Args:
            screen: pygame screen surface
        """
        if not self.visible:
            return
        
        # Render "Lives:" label
        # Center the label vertically with the icons
        label_y = self.y + (self.icon_size // 2) - (self.label_surface.get_height() // 2)
        screen.blit(self.label_surface, (self.x, label_y))
        
        # Calculate starting x position for icons (after label)
        icons_start_x = self.x + self.label_width + self.label_offset
        
        # Render each life icon
        for i in range(self.max_lives):
            icon_x = icons_start_x + (i * (self.icon_size + self.spacing))
            icon_y = self.y
            
            if i < self.current_lives:
                # Render filled icon (has life)
                screen.blit(self.life_icon, (icon_x, icon_y))
            else:
                # Render empty/grayed out icon (lost life)
                # Create a darkened version
                dark_icon = self.life_icon.copy()
                dark_icon.set_alpha(80)  # Make it semi-transparent
                screen.blit(dark_icon, (icon_x, icon_y))

