"""Enemy game object with sight cone detection and patrol AI"""

import pygame
import math
import random
import os
from game import GameObject


class Enemy(GameObject):
    """Enemy with directional sight cone and random patrol movement"""
    
    # Sprite configuration
    SPRITE_SCALE_FACTOR = 4
    SPRITE_WIDTH_ON_SHEET = 16
    SPRITE_HEIGHT_ON_SHEET = 32
    ENEMY_WIDTH = SPRITE_WIDTH_ON_SHEET * SPRITE_SCALE_FACTOR  # 64
    ENEMY_HEIGHT = SPRITE_HEIGHT_ON_SHEET * SPRITE_SCALE_FACTOR  # 128
    
    def __init__(self, x, y, speed=100):
        super().__init__(x, y)
        self.speed = speed
        self.width = self.ENEMY_WIDTH
        self.height = self.ENEMY_HEIGHT
        
        # Load sprite animations
        self.sprite_sheet = self._load_sprite_sheet()
        self.current_state = 'walk_down'
        self.current_animation = self.sprite_sheet.get(self.current_state, [])
        
        # Animation state
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_interval = 10
        
        # Collision rect (smaller, for lower body)
        self.collision_height = int(self.ENEMY_HEIGHT * 0.5)
        self.rect = pygame.Rect(int(self.x), int(self.y) + (self.ENEMY_HEIGHT - self.collision_height),
                                self.width, self.collision_height)
        
        # Sight cone properties
        self.sight_range = 150
        self.field_of_view = math.radians(60)  # 60 degree cone
        self.facing_angle = 0.0  # Radians
        
        # Movement AI
        self.move_timer = 0
        self.move_interval = 90  # Change direction every 1.5 seconds at 60 FPS
        self.last_moving_dx = 1
        self.last_moving_dy = 0
        
        # Debug
        self.debug_los_clear = False
        
        # Set initial random direction
        self.set_random_direction()
    
    def _load_sprite_sheet(self):
        """Load enemy sprites or use placeholder"""
        try:
            assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                     'assets', 'images', 'christmas')
            sheet_path = os.path.join(assets_dir, 'character.png')
            
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
                scaled_frame = pygame.transform.scale(frame, (self.ENEMY_WIDTH, self.ENEMY_HEIGHT))
                sprites.append(scaled_frame)
            
            # Map sprites to animations
            if len(sprites) >= 16:
                return {
                    'idle': [sprites[0]],
                    'walk_down': [sprites[0], sprites[1]],
                    'walk_up': [sprites[4], sprites[5]],
                    'walk_right': [sprites[12], sprites[13]],
                    'walk_left': [sprites[8], sprites[9]]
                }
            else:
                raise Exception("Not enough sprites")
        
        except Exception as e:
            print(f"Failed to load enemy sprites: {e}. Using placeholder box.")
            # Create placeholder box
            placeholder = pygame.Surface((self.ENEMY_WIDTH, self.ENEMY_HEIGHT), pygame.SRCALPHA)
            placeholder.fill((200, 50, 50))
            # Draw face/eyes
            pygame.draw.circle(placeholder, (255, 255, 255), (20, 40), 8)
            pygame.draw.circle(placeholder, (255, 255, 255), (44, 40), 8)
            pygame.draw.circle(placeholder, (0, 0, 0), (20, 40), 4)
            pygame.draw.circle(placeholder, (0, 0, 0), (44, 40), 4)
            
            return {
                'idle': [placeholder],
                'walk_down': [placeholder],
                'walk_up': [placeholder],
                'walk_right': [placeholder],
                'walk_left': [placeholder]
            }
    
    def set_state(self, new_state):
        """Change animation state"""
        if new_state in self.sprite_sheet and self.current_state != new_state:
            self.current_state = new_state
            self.current_animation = self.sprite_sheet[new_state]
            self.frame_index = 0
            
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
    
    def set_random_direction(self):
        """Set a random movement direction"""
        while True:
            # Random direction
            angle = random.random() * 2 * math.pi
            dx = math.cos(angle) * self.speed
            dy = math.sin(angle) * self.speed
            
            if abs(dx) > 10 or abs(dy) > 10:  # Ensure some movement
                self.velocity_x = dx
                self.velocity_y = dy
                self.facing_angle = math.atan2(dy, dx)
                break
    
    def update(self, dt, obstacles):
        """Update enemy AI, movement, and animation
        
        Args:
            dt: Delta time in seconds
            obstacles: List of game objects to collide with
        """
        if not self.active:
            return
        
        # Update move timer
        self.move_timer += 1
        if self.move_timer >= self.move_interval:
            self.set_random_direction()
            self.move_timer = 0
        
        # Update facing direction based on movement
        if self.velocity_x != 0 or self.velocity_y != 0:
            self.facing_angle = math.atan2(self.velocity_y, self.velocity_x)
            self.last_moving_dx = self.velocity_x
            self.last_moving_dy = self.velocity_y
        elif self.last_moving_dx != 0 or self.last_moving_dy != 0:
            self.facing_angle = math.atan2(self.last_moving_dy, self.last_moving_dx)
        
        # Set animation state
        if self.velocity_x == 0 and self.velocity_y == 0:
            self.set_state('idle')
        elif abs(self.velocity_x) > abs(self.velocity_y):
            if self.velocity_x > 0:
                self.set_state('walk_right')
            else:
                self.set_state('walk_left')
        else:
            if self.velocity_y > 0:
                self.set_state('walk_down')
            else:
                self.set_state('walk_up')
        
        # Store old position
        old_x = self.x
        old_y = self.y
        
        # Update position
        super().update(dt)
        
        # Update collision rect
        self.rect.x = int(self.x)
        self.rect.y = int(self.y) + (self.ENEMY_HEIGHT - self.collision_height)
        
        # Check collisions
        for obstacle in obstacles:
            if obstacle is self:
                continue
            if hasattr(obstacle, 'rect') and self.rect.colliderect(obstacle.rect):
                # Collision detected - revert and change direction
                self.x = old_x
                self.y = old_y
                self.rect.x = int(self.x)
                self.rect.y = int(self.y) + (self.ENEMY_HEIGHT - self.collision_height)
                self.velocity_x = 0
                self.velocity_y = 0
                self.set_random_direction()
                break
        
        # Animate
        self.animate()
    
    def is_player_detected(self, player, walls):
        """Check if player is in sight cone with line-of-sight check
        
        Args:
            player: Player object
            walls: List of wall objects that block sight
            
        Returns:
            True if player is detected, False otherwise
        """
        # Distance check
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > self.sight_range:
            self.debug_los_clear = False
            return False
        
        # Angle check
        angle_to_player = math.atan2(dy, dx)
        angle_diff = (angle_to_player - self.facing_angle + math.pi) % (2 * math.pi) - math.pi
        
        if abs(angle_diff) <= self.field_of_view / 2:
            # Line of sight check
            p1 = self.rect.center
            p2 = player.rect.center
            
            for wall in walls:
                if wall.rect.clipline(p1, p2):
                    self.debug_los_clear = False
                    return False
            
            self.debug_los_clear = True
            return True
        
        self.debug_los_clear = False
        return False
    
    def render(self, screen, walls=None, debug=False):
        """Render enemy with sight cone
        
        Args:
            screen: Pygame screen surface
            walls: List of wall objects (for clipping sight cone)
            debug: If True, draw debug info
        """
        if not self.visible:
            return
        
        # Draw sight cone
        center = self.rect.center
        half_fov = self.field_of_view / 2
        
        start_angle = self.facing_angle - half_fov
        end_angle = self.facing_angle + half_fov
        
        # Calculate cone edge points
        point_a_x = center[0] + self.sight_range * math.cos(start_angle)
        point_a_y = center[1] + self.sight_range * math.sin(start_angle)
        point_b_x = center[0] + self.sight_range * math.cos(end_angle)
        point_b_y = center[1] + self.sight_range * math.sin(end_angle)
        
        current_point_a = (point_a_x, point_a_y)
        current_point_b = (point_b_x, point_b_y)
        
        # Clip sight cone by walls
        if walls:
            for wall in walls:
                # Clip ray A
                clip_a = wall.rect.clipline(center, current_point_a)
                if clip_a:
                    dist_sq_0 = (clip_a[0][0] - center[0]) ** 2 + (clip_a[0][1] - center[1]) ** 2
                    dist_sq_1 = (clip_a[1][0] - center[0]) ** 2 + (clip_a[1][1] - center[1]) ** 2
                    intersection = clip_a[0] if dist_sq_0 < dist_sq_1 else clip_a[1]
                    
                    current_dist_sq = (current_point_a[0] - center[0]) ** 2 + (current_point_a[1] - center[1]) ** 2
                    intersect_dist_sq = (intersection[0] - center[0]) ** 2 + (intersection[1] - center[1]) ** 2
                    
                    if intersect_dist_sq < current_dist_sq:
                        current_point_a = intersection
                
                # Clip ray B
                clip_b = wall.rect.clipline(center, current_point_b)
                if clip_b:
                    dist_sq_0 = (clip_b[0][0] - center[0]) ** 2 + (clip_b[0][1] - center[1]) ** 2
                    dist_sq_1 = (clip_b[1][0] - center[0]) ** 2 + (clip_b[1][1] - center[1]) ** 2
                    intersection = clip_b[0] if dist_sq_0 < dist_sq_1 else clip_b[1]
                    
                    current_dist_sq = (current_point_b[0] - center[0]) ** 2 + (current_point_b[1] - center[1]) ** 2
                    intersect_dist_sq = (intersection[0] - center[0]) ** 2 + (intersection[1] - center[1]) ** 2
                    
                    if intersect_dist_sq < current_dist_sq:
                        current_point_b = intersection
        
        # Draw sight cone
        cone_points = [center, current_point_a, current_point_b]
        s = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        pygame.draw.polygon(s, (255, 100, 50, 50), cone_points)
        screen.blit(s, (0, 0))
        
        # Draw enemy sprite
        current_frame = self.get_current_frame()
        if current_frame:
            frame_rect = current_frame.get_rect()
            frame_rect.midbottom = self.rect.midbottom
            screen.blit(current_frame, frame_rect.topleft)
        
        # Debug: draw line of sight
        if debug and self.debug_los_clear:
            line_end_x = center[0] + 50 * math.cos(self.facing_angle)
            line_end_y = center[1] + 50 * math.sin(self.facing_angle)
            pygame.draw.line(screen, (0, 255, 0, 100), center, (line_end_x, line_end_y), 2)

