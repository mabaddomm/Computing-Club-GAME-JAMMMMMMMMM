"""Child enemy - smaller variant using character.png sprite"""

import pygame
import math
import os
from game_objects.enemy import Enemy


class Child(Enemy):
    """Child enemy - smaller and uses different sprite than base Enemy"""
    
    # Override sprite configuration for smaller size
    SPRITE_SCALE_FACTOR = 3  # Smaller than Enemy's 4
    SPRITE_WIDTH_ON_SHEET = 16
    SPRITE_HEIGHT_ON_SHEET = 32
    CHILD_WIDTH = SPRITE_WIDTH_ON_SHEET * SPRITE_SCALE_FACTOR  # 48px
    CHILD_HEIGHT = SPRITE_HEIGHT_ON_SHEET * SPRITE_SCALE_FACTOR  # 96px
    
    def __init__(self, x, y, speed=100):
        """Initialize child enemy at position
        
        Args:
            x: X position
            y: Y position
            speed: Movement speed (pixels per second)
        """
        # Call GameObject's __init__ directly to avoid Enemy's __init__
        from game import GameObject
        GameObject.__init__(self, x, y)
        
        self.speed = speed
        self.width = self.CHILD_WIDTH
        self.height = self.CHILD_HEIGHT
        
        # Load child sprite animations (character.png)
        self.sprite_sheet = self._load_sprite_sheet()
        self.current_state = 'walk_down'
        self.current_animation = self.sprite_sheet.get(self.current_state, [])
        
        # Animation state
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_interval = 10
        
        # Collision rect - much smaller for child (at feet)
        # Width: 70% of sprite, Height: 20% of sprite
        collision_width = int(self.CHILD_WIDTH * 0.7)  # ~34px
        self.collision_height = int(self.CHILD_HEIGHT * 0.2)  # ~19px
        
        # Position collision rect at feet
        self.x_offset = int(self.CHILD_WIDTH * 0.25)  # Recenter horizontally
        self.y_offset = int(self.CHILD_HEIGHT * 0.65)  # Position at feet
        
        self.rect = pygame.Rect(
            int(self.x) + self.x_offset,
            int(self.y) + self.y_offset,
            collision_width,
            self.collision_height
        )
        
        # Sight cone properties (slightly longer than base Enemy)
        self.sight_range = 180  # Longer than Enemy's 150
        self.field_of_view = math.radians(60)  # 60 degree cone
        self.facing_angle = 0.0  # Radians
        
        # Movement AI
        self.move_timer = 0
        self.move_interval = 90  # Change direction every 1.5 seconds at 60 FPS
        self.last_moving_dx = 1
        self.last_moving_dy = 0
        
        # Set initial random direction
        self.set_random_direction()
        
        # Debug
        self.debug_los_clear = False
    
    def _load_sprite_sheet(self):
        """Load child sprite sheet from character.png"""
        try:
            # Load from assets/character.png (root assets folder)
            assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
            sprite_path = os.path.join(assets_dir, 'character.png')
            
            sheet = pygame.image.load(sprite_path).convert_alpha()
            sheet_width = sheet.get_width()
            num_sprites = sheet_width // self.SPRITE_WIDTH_ON_SHEET
            
            print(f"✅ Child sprite sheet loaded: {num_sprites} frames at {self.CHILD_WIDTH}x{self.CHILD_HEIGHT}")
            
            # Split sprite sheet into individual frames
            sprites = []
            for i in range(num_sprites):
                frame = pygame.Surface(
                    (self.SPRITE_WIDTH_ON_SHEET, self.SPRITE_HEIGHT_ON_SHEET),
                    pygame.SRCALPHA
                )
                frame.blit(
                    sheet,
                    (0, 0),
                    (i * self.SPRITE_WIDTH_ON_SHEET, 0, 
                     self.SPRITE_WIDTH_ON_SHEET, self.SPRITE_HEIGHT_ON_SHEET)
                )
                # Scale up
                scaled_frame = pygame.transform.scale(
                    frame,
                    (self.CHILD_WIDTH, self.CHILD_HEIGHT)
                )
                sprites.append(scaled_frame)
            
            # Map sprites to animation states
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
                # Fallback
                return self._create_fallback_sprites()
                
        except Exception as e:
            print(f"⚠️ Failed to load child sprites: {e}")
            return self._create_fallback_sprites()
    
    def _create_fallback_sprites(self):
        """Create fallback colored rectangles for child sprites"""
        fallback = pygame.Surface((self.CHILD_WIDTH, self.CHILD_HEIGHT))
        fallback.fill((200, 100, 100))  # Reddish color
        
        return {
            'idle_down': [fallback],
            'walk_down': [fallback],
            'idle_up': [fallback],
            'walk_up': [fallback],
            'idle_right': [fallback],
            'walk_right': [fallback],
            'idle_left': [fallback],
            'walk_left': [fallback]
        }
    
    def render(self, screen, walls):
        """Render child with sight cone (override to adjust for smaller size)"""
        # Draw sight cone first
        center = self.rect.center
        half_fov = self.field_of_view / 2
        
        start_angle = self.facing_angle - half_fov
        end_angle = self.facing_angle + half_fov
        
        point_a_x = center[0] + self.sight_range * math.cos(start_angle)
        point_a_y = center[1] + self.sight_range * math.sin(start_angle)
        point_b_x = center[0] + self.sight_range * math.cos(end_angle)
        point_b_y = center[1] + self.sight_range * math.sin(end_angle)
        
        current_point_a = (point_a_x, point_a_y)
        current_point_b = (point_b_x, point_b_y)
        
        # Clip sight cone by walls
        p1 = center
        p2_a = current_point_a
        p2_b = current_point_b
        
        for wall in walls:
            wall_rect = wall.rect
            
            # Clip line A
            clip_a = wall_rect.clipline(p1, p2_a)
            if clip_a:
                dist_sq_0 = (clip_a[0][0] - center[0]) ** 2 + (clip_a[0][1] - center[1]) ** 2
                dist_sq_1 = (clip_a[1][0] - center[0]) ** 2 + (clip_a[1][1] - center[1]) ** 2
                
                intersection_point_a = clip_a[0] if dist_sq_0 < dist_sq_1 else clip_a[1]
                
                current_dist_sq = (current_point_a[0] - center[0]) ** 2 + (current_point_a[1] - center[1]) ** 2
                intersect_dist_sq = (intersection_point_a[0] - center[0]) ** 2 + (intersection_point_a[1] - center[1]) ** 2
                
                if intersect_dist_sq < current_dist_sq:
                    current_point_a = intersection_point_a
            
            # Clip line B
            clip_b = wall_rect.clipline(p1, p2_b)
            if clip_b:
                dist_sq_0 = (clip_b[0][0] - center[0]) ** 2 + (clip_b[0][1] - center[1]) ** 2
                dist_sq_1 = (clip_b[1][0] - center[0]) ** 2 + (clip_b[1][1] - center[1]) ** 2
                
                intersection_point_b = clip_b[0] if dist_sq_0 < dist_sq_1 else clip_b[1]
                
                current_dist_sq = (current_point_b[0] - center[0]) ** 2 + (current_point_b[1] - center[1]) ** 2
                intersect_dist_sq = (intersection_point_b[0] - center[0]) ** 2 + (intersection_point_b[1] - center[1]) ** 2
                
                if intersect_dist_sq < current_dist_sq:
                    current_point_b = intersection_point_b
        
        # Draw sight cone
        cone_points = [center, current_point_a, current_point_b]
        s = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        pygame.draw.polygon(s, (255, 100, 50, 50), cone_points)  # Translucent red-orange
        screen.blit(s, (0, 0))
        
        # Draw child sprite (adjusted for smaller size)
        if self.current_animation:
            current_frame = self.current_animation[self.frame_index]
            frame_rect = current_frame.get_rect()
            frame_rect.midbottom = self.rect.midbottom
            screen.blit(current_frame, frame_rect.topleft)
        
        # Debug LOS indicator
        if self.debug_los_clear:
            line_color = (0, 255, 0, 100)  # Green
            line_end_x = center[0] + 50 * math.cos(self.facing_angle)
            line_end_y = center[1] + 50 * math.sin(self.facing_angle)
            pygame.draw.line(screen, line_color, center, (line_end_x, line_end_y), 2)

