"""Present collectible game object with interaction mechanics"""

import pygame
from game import GameObject


class Present(GameObject):
    """Collectible present that requires holding E to collect"""
    
    def __init__(self, x, y):
        super().__init__(x, y)
        self.width = 35
        self.height = 35
        
        # Collision rect
        self.rect = pygame.Rect(int(x), int(y), self.width, self.height)
        
        # Interaction zone
        self.interaction_range = 50
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
        
        # Colors
        self.present_color = (100, 150, 255)
        self.interaction_color = (100, 150, 255, 60)
        self.meter_bg_color = (30, 30, 30)
        self.meter_fill_color = (0, 200, 0)
        self.prompt_color = (255, 255, 0)
        self.bg_color = (0, 0, 0)
        self.white = (255, 255, 255)
    
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
        
        # Draw present body (simple blue box with white ribbon)
        pygame.draw.rect(screen, self.present_color, self.rect)
        # Vertical ribbon
        pygame.draw.line(screen, self.white, 
                        (self.rect.centerx, self.rect.top), 
                        (self.rect.centerx, self.rect.bottom), 3)
        # Horizontal ribbon
        pygame.draw.line(screen, self.white, 
                        (self.rect.left, self.rect.centery), 
                        (self.rect.right, self.rect.centery), 3)
        
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

