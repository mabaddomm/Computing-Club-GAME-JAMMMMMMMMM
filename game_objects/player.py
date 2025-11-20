"""Player game object with sprite animations and stealth mechanics"""

import pygame
import os
from game import GameObject


class Player(GameObject):
    """Player character with sprite animations, lives, and stealth mechanics"""
    
    # Sprite configuration
    SPRITE_SCALE_FACTOR = 4
    SPRITE_WIDTH_ON_SHEET = 18
    SPRITE_HEIGHT_ON_SHEET = 32
    PLAYER_WIDTH = SPRITE_WIDTH_ON_SHEET * SPRITE_SCALE_FACTOR  # 72
    PLAYER_HEIGHT = SPRITE_HEIGHT_ON_SHEET * SPRITE_SCALE_FACTOR  # 128
    
    def __init__(self, x=0, y=0, speed=200):
        super().__init__(x, y)
        self.speed = speed  # Pixels per second
        self.width = self.PLAYER_WIDTH
        self.height = self.PLAYER_HEIGHT
        
        # Load sprite animations
        self.sprite_sheet = self._load_sprite_sheet()
        self.current_state = 'idle_down'
        self.current_animation = self.sprite_sheet.get(self.current_state, [])
        
        # Animation state
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_interval = 10  # Frames between animation updates
        
        # Collision rect (smaller than sprite for feet/lower body)
        self.collision_height = int(self.PLAYER_HEIGHT * 0.75)
        self.rect = pygame.Rect(int(self.x), int(self.y) + (self.PLAYER_HEIGHT - self.collision_height), 
                                self.width, self.collision_height)
        
        # Lives and invulnerability (for stealth interiors)
        self.lives = 3
        self.is_vulnerable = True
        self.invuln_timer = 0
        self.max_invuln_time = 120  # 2 seconds at 60 FPS
        self.is_caught = False
        
        # Font for UI
        self.font = pygame.font.Font(None, 24)
    
    def _load_sprite_sheet(self):
        """Load and split the Grinch sprite sheet"""
        try:
            assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                     'assets', 'images', 'christmas')
            sheet_path = os.path.join(assets_dir, 'grinch_spread.png')
            
            sheet = pygame.image.load(sheet_path).convert_alpha()
            sheet_width = sheet.get_width()
            num_sprites = sheet_width // self.SPRITE_WIDTH_ON_SHEET
            
            # Split sprite sheet
            sprites = []
            for i in range(num_sprites):
                frame = pygame.Surface((self.SPRITE_WIDTH_ON_SHEET, self.SPRITE_HEIGHT_ON_SHEET), 
                                      pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), 
                          (i * self.SPRITE_WIDTH_ON_SHEET, 0, 
                           self.SPRITE_WIDTH_ON_SHEET, self.SPRITE_HEIGHT_ON_SHEET))
                scaled_frame = pygame.transform.scale(frame, (self.PLAYER_WIDTH, self.PLAYER_HEIGHT))
                sprites.append(scaled_frame)
            
            # Map sprites to animations
            if len(sprites) >= 12:
                return {
                    'idle_down': [sprites[0]],
                    'walk_down': [sprites[1], sprites[2]],
                    'idle_up': [sprites[3]],
                    'walk_up': [sprites[4], sprites[5]],
                    'idle_right': [sprites[6]],
                    'walk_right': [sprites[7], sprites[6], sprites[8]],
                    'idle_left': [sprites[9]],
                    'walk_left': [sprites[10], sprites[9], sprites[11]]
                }
            else:
                raise Exception("Not enough sprites")
        
        except Exception as e:
            print(f"Failed to load Grinch sprites: {e}. Using placeholder.")
            # Create placeholder
            placeholder = pygame.Surface((self.PLAYER_WIDTH, self.PLAYER_HEIGHT), pygame.SRCALPHA)
            placeholder.fill((100, 200, 100))
            return {
                'idle_down': [placeholder],
                'walk_down': [placeholder],
                'idle_up': [placeholder],
                'walk_up': [placeholder],
                'idle_right': [placeholder],
                'walk_right': [placeholder],
                'idle_left': [placeholder],
                'walk_left': [placeholder]
            }
    
    def set_state(self, new_state):
        """Change animation state"""
        if new_state in self.sprite_sheet and self.current_state != new_state:
            self.current_state = new_state
            self.current_animation = self.sprite_sheet[new_state]
            self.frame_index = 0
            
            # Adjust frame interval
            if len(self.current_animation) <= 1:
                self.frame_interval = 1000
            else:
                self.frame_interval = 10
    
    def animate(self):
        """Update animation frame"""
        self.frame_timer += 1
        if self.frame_timer >= self.frame_interval:
            self.frame_index = (self.frame_index + 1) % len(self.current_animation)
            self.frame_timer = 0
    
    def get_current_frame(self):
        """Get current sprite frame"""
        if self.current_animation:
            return self.current_animation[self.frame_index]
        return None
    
    def handle_input(self, keys):
        """Handle keyboard input and set animation state
        
        Args:
            keys: pygame.key.get_pressed() result
        """
        if self.is_caught or self.lives <= 0:
            self.set_state('idle_down')
            self.velocity_x = 0
            self.velocity_y = 0
            return
        
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
            dx *= 0.707
            dy *= 0.707
        
        self.velocity_x = dx * self.speed
        self.velocity_y = dy * self.speed
        
        # Set animation state based on movement
        if dx == 0 and dy == 0:
            # Idle - maintain direction
            if 'down' in self.current_state:
                self.set_state('idle_down')
            elif 'up' in self.current_state:
                self.set_state('idle_up')
            elif 'right' in self.current_state:
                self.set_state('idle_right')
            elif 'left' in self.current_state:
                self.set_state('idle_left')
            else:
                self.set_state('idle_down')
        elif abs(dx) > abs(dy):
            if dx > 0:
                self.set_state('walk_right')
            else:
                self.set_state('walk_left')
        else:
            if dy > 0:
                self.set_state('walk_down')
            else:
                self.set_state('walk_up')
    
    def update(self, dt):
        """Update player position and state"""
        if self.active:
            # Animate
            self.animate()
            
            # Update position
            super().update(dt)
            
            # Update collision rect (align with bottom of sprite)
            self.rect.x = int(self.x)
            self.rect.y = int(self.y) + (self.PLAYER_HEIGHT - self.collision_height)
            
            # Handle invulnerability timer
            if not self.is_vulnerable:
                self.invuln_timer -= 1
                if self.invuln_timer <= 0:
                    self.is_vulnerable = True
    
    def check_collision(self, collision_rects):
        """Check if player collides with any collision rect"""
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                return True
        return False
    
    def resolve_collision(self, collision_rects, dt):
        """Resolve collision by moving player back"""
        # Try moving back in X
        test_x = self.x - self.velocity_x * dt
        test_rect_x = pygame.Rect(int(test_x), self.rect.y, self.width, self.collision_height)
        if not any(test_rect_x.colliderect(rect) for rect in collision_rects):
            self.x = test_x
        else:
            self.velocity_x = 0
        
        # Try moving back in Y
        test_y = self.y - self.velocity_y * dt
        test_rect_y = pygame.Rect(int(self.x), int(test_y) + (self.PLAYER_HEIGHT - self.collision_height), 
                                   self.width, self.collision_height)
        if not any(test_rect_y.colliderect(rect) for rect in collision_rects):
            self.y = test_y
        else:
            self.velocity_y = 0
        
        # Update rect
        self.rect.x = int(self.x)
        self.rect.y = int(self.y) + (self.PLAYER_HEIGHT - self.collision_height)
    
    def lose_life(self):
        """Lose a life from physical collision"""
        if self.is_vulnerable and self.lives > 0:
            self.lives -= 1
            self.is_vulnerable = False
            self.invuln_timer = self.max_invuln_time
            print(f"*** PLAYER HIT! Lives remaining: {self.lives} ***")
            return True
        return False
    
    def reset_for_new_round(self, x, y):
        """Reset player position and state after being caught/kicked out
        
        Args:
            x: New X position
            y: New Y position
        """
        self.x = x
        self.y = y
        self.is_caught = False
        self.velocity_x = 0
        self.velocity_y = 0
        
        # Recalculate rect position based on collision height
        # The y position needs adjustment for the large sprite vs small collision box
        self.rect.x = int(self.x)
        self.rect.y = int(self.y) + (self.PLAYER_HEIGHT - self.collision_height)
        
        print(f"🔄 Player reset to position ({x}, {y})")
    
    def got_caught(self):
        """Get caught by enemy sight - triggers kickout"""
        if self.is_vulnerable and self.lives > 0:
            self.lives -= 1
            self.is_vulnerable = False
            self.invuln_timer = self.max_invuln_time
            self.is_caught = True
            print(f"*** PLAYER CAUGHT! Lives: {self.lives} ***")
            return True
        return False
    
    def reset_for_new_round(self, x, y):
        """Reset player after being caught"""
        self.x = x
        self.y = y
        self.is_caught = False
        self.velocity_x = 0
        self.velocity_y = 0
        self.rect.x = int(self.x)
        self.rect.y = int(self.y) + (self.PLAYER_HEIGHT - self.collision_height)
    
    def render(self, screen):
        """Render the player sprite"""
        if self.visible:
            # Flashing effect when invulnerable
            if not self.is_vulnerable and self.invuln_timer % 10 < 5:
                return
            
            current_frame = self.get_current_frame()
            if current_frame:
                # Align sprite bottom with rect bottom
                frame_rect = current_frame.get_rect()
                frame_rect.midbottom = self.rect.midbottom
                screen.blit(current_frame, frame_rect.topleft)

