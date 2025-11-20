"""Present Counter UI Element - displays present collection progress"""

import pygame
import os
from game import UIElement


class PresentCounter(UIElement):
    """UI element that displays a present icon and collection count"""
    
    def __init__(self, x, y, presents_collected=0, present_goal=10):
        """Initialize the present counter
        
        Args:
            x: X position (typically top-right corner)
            y: Y position
            presents_collected: Current number of presents collected
            present_goal: Total presents needed
        """
        super().__init__(x, y)
        
        self.presents_collected = presents_collected
        self.present_goal = present_goal
        
        # UI styling
        self.icon_size = 82  # Large icon size
        self.font = pygame.font.Font(None, 48)
        self.text_color = (0, 0, 0)  # Black
        self.text_offset_x = 0  # Offset from icon to text (increased to prevent overlap with large icon)
        self.text_offset_y = 60  # Vertical alignment adjustment (centers text with icon)
        
        # Container/background settings
        self.container_width = 200
        self.container_height = 120
        
        # Load present icon and background
        self._load_background()
        self._load_icon()
    
    def _load_background(self):
        """Load the candy cane pattern background"""
        try:
            # Get the path to the pre-cropped candy cane pattern
            assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'images')
            bg_path = os.path.join(assets_dir, 'candy_cane_pattern_ui.png')
            
            # Load the background (already sized to 200x120, no scaling needed)
            self.background = pygame.image.load(bg_path).convert_alpha()
            print("✅ Candy cane pattern background loaded successfully (pre-cropped)")
        except Exception as e:
            print(f"⚠️ Failed to load candy cane pattern: {e}")
            # Create a fallback background (light colored rectangle)
            self.background = pygame.Surface((self.container_width, self.container_height))
            self.background.fill((200, 200, 200))  # Light gray fallback
    
    def _load_icon(self):
        """Load the present icon image"""
        try:
            # Get the path to the present icon
            assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'images', 'christmas', 'presents')
            icon_path = os.path.join(assets_dir, 'topdownTile_50.png')
            
            # Load and scale the icon
            self.icon = pygame.image.load(icon_path).convert_alpha()
            self.icon = pygame.transform.scale(self.icon, (self.icon_size, self.icon_size))
            print("✅ Present counter icon loaded successfully")
        except Exception as e:
            print(f"⚠️ Failed to load present counter icon: {e}")
            # Create a fallback icon (simple colored rectangle)
            self.icon = pygame.Surface((self.icon_size, self.icon_size))
            self.icon.fill((100, 150, 255))  # Blue present color
    
    def update_count(self, presents_collected, present_goal=None):
        """Update the present count display
        
        Args:
            presents_collected: New number of presents collected
            present_goal: Optional new goal value
        """
        self.presents_collected = presents_collected
        if present_goal is not None:
            self.present_goal = present_goal
    
    def update(self, dt):
        """Update logic (present counter is mostly static)"""
        if not self.active:
            return
        # No animation or update logic needed for static counter
    
    def render(self, screen):
        """Render the present icon and count text
        
        Args:
            screen: pygame.Surface to render to
        """
        if not self.visible:
            return
        
        # Draw the candy cane pattern background (behind everything)
        bg_x = self.x - 10  # Slight offset for padding
        bg_y = self.y - 10
        screen.blit(self.background, (bg_x, bg_y))
        
        # Draw the present icon (on top of background)
        screen.blit(self.icon, (self.x, self.y))
        
        # Draw the count text (X / Goal format, on top of background)
        count_text = f"{self.presents_collected} / {self.present_goal}"
        text_surface = self.font.render(count_text, True, self.text_color)
        
        # Position text to the right of the icon
        text_x = self.x + self.text_offset_x
        text_y = self.y + self.text_offset_y
        screen.blit(text_surface, (text_x, text_y))

