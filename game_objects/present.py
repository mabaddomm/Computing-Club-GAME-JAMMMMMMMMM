"""Present collectible game object with interaction mechanics"""

import pygame
import random
import os
from game import GameObject


# Present image paths
PRESENT_IMAGE_PATHS = ['prez1.png', 'prez2.png']
PRESENT_SIZE = 40  # Size to scale present images to


class Present(GameObject):
    """Collectible present that requires holding E to collect"""
    
    # Class variable for caching loaded present images
    PRESENT_IMAGES = None
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.width = PRESENT_SIZE
        self.height = PRESENT_SIZE
        
        # Load present images if not cached
        if Present.PRESENT_IMAGES is None:
            Present.PRESENT_IMAGES = self._load_present_images()
        
        # Randomly select a present image
        if Present.PRESENT_IMAGES:
            self.image = random.choice(Present.PRESENT_IMAGES)
        else:
            # Fallback image
            self.image = pygame.Surface((PRESENT_SIZE, PRESENT_SIZE), pygame.SRCALPHA)
            self.image.fill((100, 150, 255))
        
        # Collision rect
        self.rect = pygame.Rect(int(x), int(y), self.width, self.height)
        
        # Interaction zone (smaller for tighter gameplay)
        self.interaction_range = 45
        interact_size = self.interaction_range * 2
        self.interaction_rect = pygame.Rect(0, 0, interact_size, interact_size)
        self.interaction_rect.center = self.rect.center
        
        # Collection state
        self.is_collected = False
        self.is_collecting = False
        self.collection_progress = 0
        self.max_collection_time = 150  # 2.5 seconds at 60 FPS
        
        # UI
        self.font_medium = pygame.font.Font(None, 24)
        
        # Colors (updated interaction opacity to 20)
        self.present_color = (100, 150, 255)
        self.interaction_color = (100, 150, 255, 20)  # More transparent
        self.meter_bg_color = (30, 30, 30)
        self.meter_fill_color = (0, 200, 0)
        self.prompt_color = (255, 255, 0)
        self.bg_color = (0, 0, 0)
        self.white = (255, 255, 255)
    
    def _load_present_images(self):
        """Load present images from assets/images/christmas/presents/"""
        images = []
        assets_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'assets', 'images', 'christmas', 'presents'
        )
        
        for path in PRESENT_IMAGE_PATHS:
            try:
                full_path = os.path.join(assets_dir, path)
                raw_image = pygame.image.load(full_path).convert_alpha()
                scaled_image = pygame.transform.scale(raw_image, (PRESENT_SIZE, PRESENT_SIZE))
                images.append(scaled_image)
                print(f"✅ Loaded present image: {path}")
            except Exception as e:
                print(f"⚠️ Failed to load {path}: {e}")
                # Create fallback
                fallback = pygame.Surface((PRESENT_SIZE, PRESENT_SIZE), pygame.SRCALPHA)
                fallback.fill((100, 150, 255))
                pygame.draw.line(fallback, (255, 255, 255), (PRESENT_SIZE // 2, 0),
                                (PRESENT_SIZE // 2, PRESENT_SIZE), 3)
                pygame.draw.line(fallback, (255, 255, 255), (0, PRESENT_SIZE // 2),
                                (PRESENT_SIZE, PRESENT_SIZE // 2), 3)
                images.append(fallback)
        
        return images if images else None
    
    def check_interaction_proximity(self, player):
        """Check if player is within interaction range"""
        return self.interaction_rect.colliderect(player.rect)
    
    def start_collection(self):
        """Begin collection process"""
        if not self.is_collecting:
            self.is_collecting = True
            self.collection_progress = 0
    
    def cancel_collection(self):
        """Cancel collection process"""
        self.is_collecting = False
        self.collection_progress = 0
    
    def update(self, dt, player):
        """Update present collection state
        
        Args:
            dt: Delta time
            player: Player object
        """
        if not self.active or self.is_collected:
            return
        
        in_range = self.check_interaction_proximity(player)
        
        if self.is_collecting:
            if in_range:
                self.collection_progress += 1
                
                if self.collection_progress >= self.max_collection_time:
                    self.is_collected = True
                    self.is_collecting = False
            else:
                # Player moved away - cancel collection
                self.cancel_collection()
    
    def render(self, screen, player):
        """Render present with UI overlay
        
        Args:
            screen: Pygame screen surface
            player: Player object (to check proximity)
        """
        if not self.visible or self.is_collected:
            return
        
        # Draw interaction bubble (transparent)
        interaction_surface = pygame.Surface((self.interaction_range * 2, self.interaction_range * 2), 
                                            pygame.SRCALPHA)
        pygame.draw.circle(interaction_surface, self.interaction_color, 
                          (self.interaction_range, self.interaction_range), self.interaction_range)
        screen.blit(interaction_surface, self.interaction_rect.topleft)
        
        # Draw present image
        screen.blit(self.image, self.rect.topleft)
        
        # Draw UI based on state
        if self.check_interaction_proximity(player):
            if not self.is_collecting:
                # Show interaction prompt
                interact_text = self.font_medium.render("PRESS E TO COLLECT", True, self.prompt_color)
                text_rect = interact_text.get_rect(center=(self.rect.centerx, self.rect.top - 40))
                bg_rect = text_rect.inflate(10, 5)
                pygame.draw.rect(screen, self.bg_color, bg_rect, border_radius=3)
                screen.blit(interact_text, text_rect)
        
        # Draw collection meter
        if self.is_collecting:
            meter_width = 80
            meter_height = 15
            meter_x = self.rect.centerx - meter_width // 2
            meter_y = self.rect.top - 65
            
            # Background
            bg_rect = pygame.Rect(meter_x, meter_y, meter_width, meter_height)
            pygame.draw.rect(screen, self.meter_bg_color, bg_rect, border_radius=3)
            
            # Fill
            progress_ratio = self.collection_progress / self.max_collection_time
            fill_width = int(meter_width * progress_ratio)
            fill_rect = pygame.Rect(meter_x, meter_y, fill_width, meter_height)
            pygame.draw.rect(screen, self.meter_fill_color, fill_rect, border_radius=3)
            
            # Border
            pygame.draw.rect(screen, self.white, bg_rect, 1, border_radius=3)

