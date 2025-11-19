"""Player game object for topdown movement"""

import pygame
from game import GameObject


class Player(GameObject):
    """Player character with topdown movement controls"""
    
    def __init__(self, x=0, y=0, speed=200):
        super().__init__(x, y)
        self.speed = speed  # Pixels per second
        self.width = 32
        self.height = 32
        self.color = (255, 0, 0)
        
        # Collision rect for collision detection
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def handle_input(self, keys):
        """Handle keyboard input for movement
        
        Args:
            keys: pygame.key.get_pressed() result
        """
        dx = 0
        dy = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
        
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.707  # 1/sqrt(2) for diagonal
            dy *= 0.707
        
        self.velocity_x = dx * self.speed
        self.velocity_y = dy * self.speed
    
    def update(self, dt):
        """Update player position"""
        if self.active:
            super().update(dt)
            
            # Update collision rect
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)
    
    def check_collision(self, collision_rects):
        """Check if player collides with any collision rect
        
        Args:
            collision_rects: List of pygame.Rect objects
            
        Returns:
            True if colliding, False otherwise
        """
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                return True
        return False
    
    def resolve_collision(self, collision_rects, dt):
        """Resolve collision by moving player back
        
        Args:
            collision_rects: List of pygame.Rect objects
            dt: Delta time
        """
        # Try moving back in X
        test_x = self.x - self.velocity_x * dt
        test_rect_x = pygame.Rect(int(test_x), int(self.y), self.width, self.height)
        if not any(test_rect_x.colliderect(rect) for rect in collision_rects):
            self.x = test_x
        else:
            self.velocity_x = 0
        
        # Try moving back in Y
        test_y = self.y - self.velocity_y * dt
        test_rect_y = pygame.Rect(int(self.x), int(test_y), self.width, self.height)
        if not any(test_rect_y.colliderect(rect) for rect in collision_rects):
            self.y = test_y
        else:
            self.velocity_y = 0
        
        # Update rect
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def render(self, screen):
        """Render the player"""
        if self.visible:
            pygame.draw.rect(screen, self.color, self.rect)

