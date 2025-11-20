"""Main menu scene with start button"""

import pygame
from game import Scene


class Menu(Scene):
    """Main menu screen with background and start button"""
    
    def __init__(self, name="Main Menu"):
        super().__init__(name)
        
        # Screen dimensions
        self.screen_width = 1280
        self.screen_height = 720
        
        # Load background image
        try:
            self.background_image = pygame.image.load('assets/Title_Screen.png').convert()
            self.background_image = pygame.transform.scale(
                self.background_image, 
                (self.screen_width, self.screen_height)
            )
            print("✅ Title screen loaded successfully")
        except pygame.error as e:
            print(f"⚠️ Error loading assets/Title_Screen.png: {e}. Using fallback.")
            self.background_image = pygame.Surface((self.screen_width, self.screen_height))
            self.background_image.fill((255, 255, 255))
        
        # Define the clickable START button area
        BUTTON_WIDTH = 250
        BUTTON_HEIGHT = 80
        BUTTON_X = (self.screen_width // 2) - (BUTTON_WIDTH // 2)  # Center horizontally
        BUTTON_Y = 500  # Lower-middle of screen
        self.start_button_rect = pygame.Rect(BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        
        # State
        self.start_clicked = False
    
    def handle_event(self, event):
        """Handle mouse clicks on the start button
        
        Args:
            event: pygame event
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if click is within start button
            if self.start_button_rect.collidepoint(event.pos):
                print("🎮 Start button clicked!")
                self.start_clicked = True
    
    def update(self, dt):
        """Update menu logic
        
        Args:
            dt: Delta time in seconds
        """
        # Menu is static, nothing to update
        pass
    
    def render(self, screen):
        """Render the menu
        
        Args:
            screen: pygame screen surface
        """
        # Draw background image
        screen.blit(self.background_image, (0, 0))
        
        # DEBUG: Uncomment to see the clickable button area
        # pygame.draw.rect(screen, (255, 0, 0), self.start_button_rect, 2)
    
    def reset(self):
        """Reset menu state for returning to menu"""
        self.start_clicked = False

