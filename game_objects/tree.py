"""Tree game object - decorative obstacle with present spawning"""

import pygame
import os
from game import GameObject


class Tree(GameObject):
    """Christmas tree obstacle with collision box at base"""
    
    # Tree dimensions
    TREE_WIDTH = 140
    TREE_HEIGHT = 180
    TREE_IMAGE = None  # Class variable for cached image
    
    def __init__(self, x, y):
        """Initialize tree at position (x, y) for top-left of full sprite
        
        Args:
            x: X position of top-left corner of full 140x180 sprite
            y: Y position of top-left corner of full 140x180 sprite
        """
        super().__init__(x, y)
        
        # Store the full sprite position
        self.full_x = x
        self.full_y = y
        
        # Load the tree image (cached)
        if Tree.TREE_IMAGE is None:
            Tree.TREE_IMAGE = self._load_tree_image()
        
        self.image = Tree.TREE_IMAGE
        self.width = self.TREE_WIDTH
        self.height = self.TREE_HEIGHT
        
        # Create smaller collision box at base of tree (40% width x 30% height)
        collision_width = int(self.TREE_WIDTH * 0.4)  # 56px
        collision_height = int(self.TREE_HEIGHT * 0.3)  # 54px
        
        # Calculate offsets to center collision box at base
        x_offset = (self.TREE_WIDTH - collision_width) // 2
        y_offset = self.TREE_HEIGHT - collision_height
        
        # Set collision rect at base of tree
        self.rect = pygame.Rect(
            x + x_offset,
            y + y_offset,
            collision_width,
            collision_height
        )
    
    def _load_tree_image(self):
        """Load and scale the christmas tree image"""
        try:
            assets_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'assets', 'images', 'christmas'
            )
            tree_path = os.path.join(assets_dir, 'christmas_tree.png')
            
            raw_image = pygame.image.load(tree_path).convert_alpha()
            scaled_image = pygame.transform.scale(
                raw_image,
                (self.TREE_WIDTH, self.TREE_HEIGHT)
            )
            print(f"✅ Tree image loaded: {self.TREE_WIDTH}x{self.TREE_HEIGHT}")
            return scaled_image
            
        except Exception as e:
            print(f"⚠️ Failed to load tree image: {e}")
            # Fallback: green rectangle
            fallback = pygame.Surface((self.TREE_WIDTH, self.TREE_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(fallback, (30, 150, 30), fallback.get_rect())
            return fallback
    
    def get_full_sprite_center(self):
        """Get the center point of the full 140x180 tree sprite
        
        Returns:
            tuple: (center_x, center_y) of full sprite
        """
        return (
            self.full_x + self.TREE_WIDTH // 2,
            self.full_y + self.TREE_HEIGHT // 2
        )
    
    def update(self, dt):
        """Trees don't need updates (static objects)"""
        pass
    
    def render(self, screen):
        """Render the full tree sprite at its original position"""
        # Draw the full 140x180 tree image
        screen.blit(self.image, (self.full_x, self.full_y))
    
    def render_spawn_range(self, screen, min_radius, max_radius):
        """Debug visualization: render present spawn range circles
        
        Args:
            screen: Surface to draw on
            min_radius: Minimum spawn radius
            max_radius: Maximum spawn radius
        """
        center_x, center_y = self.rect.center
        
        # Create translucent surface
        debug_surface = pygame.Surface(
            (screen.get_width(), screen.get_height()),
            pygame.SRCALPHA
        )
        
        # Draw spawn range circles
        debug_color = (255, 255, 100, 50)  # Light yellow translucent
        
        # Draw filled max radius circle
        pygame.draw.circle(debug_surface, debug_color, (center_x, center_y), max_radius, 0)
        
        # Draw outlines
        pygame.draw.circle(debug_surface, debug_color, (center_x, center_y), max_radius, 2)
        pygame.draw.circle(debug_surface, debug_color, (center_x, center_y), min_radius, 2)
        
        screen.blit(debug_surface, (0, 0))

