import pygame
import math
import random
import os

from pygame.sprite import collide_rect

# --- Pygame Setup Constants ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
PRESENT_COLLECTION_VALUE = 100  # Score value for collecting a present
KICKOUT_DURATION = FPS * 2  # 2 seconds of black screen duration
NUM_PRESENTS = 5  # Number of presents to spawn

SPRITE_SCALE_FACTOR = 4
SPRITE_WIDTH_ON_SHEET_GRINCH = 18
SPRITE_HEIGHT_ON_SHEET = 32
SPRITE_WIDTH_ON_SHEET_ENEMY = 16
SPRITE_SHEET_PATH = 'character.png'
grinch_sheet_path = 'grinch_spread.png'

PLAYER_WIDTH = SPRITE_WIDTH_ON_SHEET_GRINCH * SPRITE_SCALE_FACTOR  # 72
PLAYER_HEIGHT = SPRITE_HEIGHT_ON_SHEET * SPRITE_SCALE_FACTOR  # 128
ENEMY_WIDTH = SPRITE_WIDTH_ON_SHEET_ENEMY * SPRITE_SCALE_FACTOR  # 64
ENEMY_HEIGHT = SPRITE_HEIGHT_ON_SHEET * SPRITE_SCALE_FACTOR  # 128

# Define colors for Pygame
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'PLAYER_GREEN': (100, 200, 100),
    'ENEMY_RED': (200, 50, 50),
    'DARK_GRAY': (50, 50, 50),
    'YELLOW': (255, 255, 0),
    'PRESENT_BLUE': (100, 150, 255),
    'METER_BG': (30, 30, 30),
    'METER_FILL': (0, 200, 0),
    'SIGHT_CONE': (255, 100, 50, 50),  # Translucent Red-Orange
    'RED': (255, 0, 0),
    'WALL_COLOR': (100, 100, 100),  # New color for walls
    'LOS_BLOCKED': (255, 0, 0, 100),  # Debug color for blocked LOS
    'LOS_CLEAR': (0, 255, 0, 100),  # Debug color for clear LOS
}


# --- Sprite Sheet Loading and Splitting ---

def load_and_split_sprites(path, sprite_w, sprite_h, scale):
    """
    Loads a sprite sheet, splits it into individual frames, and scales them.
    The function handles the image loading error gracefully.
    """
    try:
        # Load the image and convert it for faster blitting
        sheet = pygame.image.load(path).convert_alpha()
    except pygame.error as e:
        # Standard error handling for missing/corrupt image file in local execution
        print(f"Error loading sprite sheet: {path}. Please ensure the file is in the script's directory. {e}")
        return None

    # Calculate the number of sprites horizontally
    sheet_width = sheet.get_width()
    sheet_height = sheet.get_height()

    # --- DEBUGGING OUTPUT ---
    print(f"--- Loading {path} (Expected Frame: {sprite_w}x{sprite_h}) ---")
    print(f"Sheet dimensions: {sheet_width}x{sheet_height}")

    # Assuming the sheet is a single row of sprites
    num_sprites = sheet_width // sprite_w

    print(f"Calculated number of sprites: {num_sprites}")
    # --- END DEBUGGING OUTPUT ---

    sprites = []
    for i in range(num_sprites):
        # Create a new surface for the individual sprite (18x32)
        frame = pygame.Surface((sprite_w, sprite_h), pygame.SRCALPHA)
        # Blit the section of the sheet onto the new surface
        frame.blit(sheet, (0, 0), (i * sprite_w, 0, sprite_w, sprite_h))
        # Scale the frame up for in-game display (4x scale)
        scaled_frame = pygame.transform.scale(frame, (sprite_w * scale, sprite_h * scale))
        sprites.append(scaled_frame)

    return sprites


def create_placeholder_sprite_sheet(width, height, type_key):
    """
    Generates a dictionary of Pygame Surfaces to simulate a loaded sprite sheet
    or loads the actual sprite sheet data for the enemy.
    """
    sheet = {}

    # Define a function to create a single animated frame (Surface)
    def create_frame(color, label=""):
        # Use SRCALPHA for transparency support in placeholder surfaces
        surf = pygame.Surface([width, height], pygame.SRCALPHA)
        surf.fill(color)

        # Add text for debugging
        font = pygame.font.Font(None, 16)
        text_surf = font.render(label[:4], True, COLORS['BLACK'])
        surf.blit(text_surf, (2, 2))

        return surf

    if type_key == 'player':
        # Load Grinch sprites using 18x32 dimensions
        all_sprites = load_and_split_sprites(grinch_sheet_path, SPRITE_WIDTH_ON_SHEET_GRINCH, SPRITE_HEIGHT_ON_SHEET,
                                             SPRITE_SCALE_FACTOR)

        if all_sprites and len(all_sprites) >= 12:
            # Re-verify Grinch sprite mapping (using first frame for idle and direction fallbacks)
            sheet['idle_down'] = [all_sprites[0]]
            sheet['walk_down'] = [all_sprites[1], all_sprites[2]]
            sheet['idle_up'] = [all_sprites[3]]
            sheet['walk_up'] = [all_sprites[4], all_sprites[5]]
            sheet['idle_right'] = [all_sprites[6]]
            sheet['walk_right'] = [all_sprites[7], all_sprites[6], all_sprites[8]]
            sheet['idle_left'] = [all_sprites[9]]
            sheet['walk_left'] = [all_sprites[10], all_sprites[9], all_sprites[11]]
        else:
            # Fallback to a placeholder using the correct PLAYER_WIDTH/HEIGHT
            print("Failed to load or split Player (Grinch) sprites. Using placeholder.")
            sheet['idle'] = [create_frame(COLORS['PLAYER_GREEN'], 'idle')]
            sheet['walk_down'] = [create_frame(COLORS['PLAYER_GREEN'], 'down')] * 2
            sheet['walk_up'] = [create_frame(COLORS['PLAYER_GREEN'], 'up')] * 2
            sheet['walk_right'] = [create_frame(COLORS['PLAYER_GREEN'], 'right')] * 2
            sheet['walk_left'] = [create_frame(COLORS['PLAYER_GREEN'], 'left')] * 2


    elif type_key == 'present':
        # Present placeholder (using 35x35 placeholder size)
        present_surf = pygame.Surface([width, height], pygame.SRCALPHA)
        present_surf.fill(COLORS['PRESENT_BLUE'])
        pygame.draw.line(present_surf, COLORS['WHITE'], (width // 2, 0), (width // 2, height), 3)
        pygame.draw.line(present_surf, COLORS['WHITE'], (0, height // 2), (width, height // 2), 3)
        sheet['idle'] = [present_surf]

    elif type_key == 'wall':
        # Wall placeholder (using dynamic width/height placeholder size)
        wall_surf = pygame.Surface([width, height], pygame.SRCALPHA)
        wall_surf.fill(COLORS['WALL_COLOR'])
        sheet['idle'] = [wall_surf]

    elif type_key == 'enemy':
        # Load the actual sprites using the correct Enemy constants
        all_sprites = load_and_split_sprites(SPRITE_SHEET_PATH, SPRITE_WIDTH_ON_SHEET_ENEMY, SPRITE_HEIGHT_ON_SHEET,
                                             SPRITE_SCALE_FACTOR)

        # Check if loading and splitting was successful and we have enough frames
        if all_sprites and len(all_sprites) >= 16:
            # Enemy sprite mapping:
            sheet['idle'] = [all_sprites[0]]
            sheet['walk_down'] = [all_sprites[0], all_sprites[1]]
            sheet['walk_up'] = [all_sprites[4], all_sprites[5]]
            sheet['walk_right'] = [all_sprites[12], all_sprites[13]]  # Swapped Left
            sheet['walk_left'] = [all_sprites[8], all_sprites[9]]  # Swapped Right
        else:
            # Fallback for error loading image or if sprite count is wrong
            print("Failed to load or split enemy sprites. Using placeholder.")
            placeholder_width = ENEMY_WIDTH
            placeholder_height = ENEMY_HEIGHT

            sheet['idle'] = [create_frame(COLORS['ENEMY_RED'], 'ERR')]
            sheet['walk_down'] = [create_frame(COLORS['ENEMY_RED'], 'E-D')] * 2
            sheet['walk_up'] = [create_frame(COLORS['ENEMY_RED'], 'E-U')] * 2
            sheet['walk_right'] = [create_frame(COLORS['ENEMY_RED'], 'E-R')] * 2
            sheet['walk_left'] = [create_frame(COLORS['ENEMY_RED'], 'E-L')] * 2

    return sheet


# --- Core GameObject Class ---
class GameObject:
    """
    Base class for all interactive entities in the game.
    Handles sprite sheet-based animation, movement, and solid collision.
    """

    def __init__(self, x, y, width, height, sprite_sheet, speed=3, initial_state='idle'):
        self.width = width
        self.height = height
        self.speed = speed

        # Sprite Sheet Management
        self.sprite_sheet = sprite_sheet
        self.current_state = initial_state
        default_surface = pygame.Surface([width, height], pygame.SRCALPHA)
        default_surface.fill(COLORS['WALL_COLOR'])
        # Use the provided sprite sheet, falling back to a dummy surface if the sheet is empty
        self.current_animation = self.sprite_sheet.get(initial_state, [default_surface])

        # Pygame Rect handles positioning and collision boundaries
        self.rect = pygame.Rect(x, y, width, height)

        self.dx = 0  # Velocity X
        self.dy = 0  # Velocity Y

        # Animation State Management
        self.frame_x = 0
        self.frame_timer = 0
        self.frame_interval = 10  # Control speed of animation (lower = faster)

    def set_state(self, new_state):
        """Changes the current animation state if different from the current one."""
        # Ensure the state exists in the loaded sheet
        if new_state not in self.sprite_sheet:
            if new_state != 'idle':
                return self.set_state('idle')
            return

        if self.current_state != new_state:
            self.current_state = new_state
            self.current_animation = self.sprite_sheet[new_state]
            self.frame_x = 0  # Reset animation when state changes

            # Adjust interval based on animation length
            if len(self.current_animation) <= 1:
                self.frame_interval = 1000  # Effectively stop animation
            else:
                self.frame_interval = 10

    def animate(self):
        """Cycles through frames in the current animation list."""
        self.frame_timer += 1
        if self.frame_timer >= self.frame_interval:
            self.frame_x = (self.frame_x + 1) % len(self.current_animation)
            self.frame_timer = 0

    def get_current_frame(self):
        """Retrieves the current sprite frame."""
        return self.current_animation[self.frame_x]

    def _attempt_move(self, obstacles):
        """
        Moves the object, checking for collisions with a list of static obstacles
        and resolving them.
        """
        if self.dx == 0 and self.dy == 0:
            return

        # 1. Attempt X movement
        self.rect.x += self.dx

        # Check and resolve horizontal collision
        for obstacle in obstacles:
            # Skip checking against self
            if obstacle is self:
                continue

            if self.rect.colliderect(obstacle.rect):
                if self.dx > 0:
                    self.rect.right = obstacle.rect.left
                elif self.dx < 0:
                    self.rect.left = obstacle.rect.right

                self.dx = 0
                break

        # 2. Attempt Y movement
        self.rect.y += self.dy

        # Check and resolve vertical collision
        for obstacle in obstacles:
            # Skip checking against self
            if obstacle is self:
                continue

            if self.rect.colliderect(obstacle.rect):
                if self.dy > 0:
                    self.rect.bottom = obstacle.rect.top
                elif self.dy < 0:
                    self.rect.top = obstacle.rect.bottom

                self.dy = 0
                break

        # 3. Boundary checking: Keep object within screen bounds
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)

    def update(self):
        """Updates the object's state, only handling animation in the base class."""
        self.animate()

    def render(self, screen):
        """Draws the current frame of the object's animation."""
        current_frame = self.get_current_frame()
        # Center the sprite frame within the collision rect
        frame_rect = current_frame.get_rect(center=self.rect.center)
        screen.blit(current_frame, frame_rect.topleft)
        # Optional: Draw collision box for debugging
        # pygame.draw.rect(screen, COLORS['WHITE'], self.rect, 1)

    def check_collision(self, other):
        """Checks for collision using Pygame's built-in Rect collision detection."""
        return self.rect.colliderect(other.rect)

    def get_distance(self, other):
        """Calculates the Euclidean distance to the center of another object."""
        center_x1, center_y1 = self.rect.center
        center_x2, center_y2 = other.rect.center
        return math.sqrt((center_x2 - center_x1) ** 2 + (center_x2 - center_y2) ** 2)


# --- Player Class ---
class Player(GameObject):
    """
    A specialized GameObject for the user-controlled player (The Grinch).
    """

    def __init__(self, x, y):
        # FIX: Use the calculated Player dimensions (72x128)
        player_sheet = create_placeholder_sprite_sheet(PLAYER_WIDTH, PLAYER_HEIGHT, 'player')
        super().__init__(x, y, PLAYER_WIDTH, PLAYER_HEIGHT, sprite_sheet=player_sheet, speed=5)
        self.lives = 3
        self.is_vulnerable = True
        self.invuln_timer = 0
        self.max_invuln_time = FPS * 2
        self.font = pygame.font.Font(None, 24)
        self.is_caught = False

        self.collision_height = int(PLAYER_HEIGHT * 0.75)
        self.rect.height = self.collision_height

        self.rect.y = PLAYER_HEIGHT - self.collision_height

    def handle_input_and_set_state(self, keys):
        """Calculates velocity and sets the correct animation state."""
        self.dx = 0
        self.dy = 0

        if self.is_caught or self.lives <= 0:
            self.set_state('idle')
            return

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.dy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.dy = self.speed
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.dx = self.speed

        # Diagonal movement correction
        if self.dx != 0 and self.dy != 0:
            self.dx *= 0.707
            self.dy *= 0.707

        if self.dx == 0 and self.dy == 0:
            # Determine which directional idle state to use based on the last movement
            current_state = self.current_state  # Get current state before setting new one

            if 'down' in current_state:
                self.set_state('idle_down')
            elif 'up' in current_state:
                self.set_state('idle_up')
            elif 'right' in current_state:
                self.set_state('idle_right')
            elif 'left' in current_state:
                self.set_state('idle_left')
            else:
                self.set_state('idle_down')  # Default to down if no previous walk state

        elif abs(self.dx) > abs(self.dy):
            if self.dx > 0:
                self.set_state('walk_right')
            else:
                self.set_state('walk_left')
        else:
            if self.dy > 0:
                self.set_state('walk_down')
            else:
                self.set_state('walk_up')

    def lose_life(self):
        """Attempts to lose a life if the player is vulnerable (standard life loss)."""
        if self.is_vulnerable and self.lives > 0:
            self.lives -= 1
            self.is_vulnerable = False
            self.invuln_timer = self.max_invuln_time
            print(f"*** PLAYER HIT (Physical)! Lives remaining: {self.lives} ***")
            return True
        return False

    def got_caught(self):
        """
        Deducts one life and sets the 'is_caught' flag to trigger the transient
        'kicked out' scene and subsequent reset.
        """
        if self.is_vulnerable and self.lives > 0:
            self.lives -= 1
            self.is_vulnerable = False
            self.invuln_timer = self.max_invuln_time

            self.is_caught = True
            print(f"*** PLAYER CAUGHT by ENEMY SIGHT! KICKED OUT. (Lives left: {self.lives}) ***")
            return True
        return False

    def reset_for_new_round(self, x, y):
        """Resets position and caught state after a round loss/kickout."""
        self.rect.x = x
        self.rect.y = y
        self.is_caught = False
        self.dx = 0
        self.dy = 0

        # FIX: Recalculate y based on the large sprite height and collision height
        self.rect.y += PLAYER_HEIGHT - self.collision_height

    def update(self, enemies, solids, walls):
        """
        Player update logic, including invulnerability, solid collision, and enemy sight check.
        """
        self.animate()

        # 2. Apply solid collision and movement against all solid objects (Walls + Presents)
        self._attempt_move(solids)

        # 3. Handle Invulnerability Timer
        if not self.is_vulnerable:
            self.invuln_timer -= 1
            if self.invuln_timer <= 0:
                self.is_vulnerable = True

        # 4. Caught Logic: Check if any enemy has the player in sight
        if self.lives > 0 and not self.is_caught:
            for enemy in enemies:
                # PASS WALLS for Line-of-Sight check
                if enemy.is_player_detected(self, walls):
                    self.got_caught()

    def render(self, screen):
        """Custom player render, handling flashing when invulnerable."""
        # Only render if not currently in a flash cycle when invulnerable
        if not self.is_vulnerable and self.invuln_timer % 10 < 5:
            pass
        else:
            # Custom rendering logic for Player only: align sprite bottom to rect bottom
            current_frame = self.get_current_frame()
            frame_rect = current_frame.get_rect()
            frame_rect.midbottom = self.rect.midbottom
            screen.blit(current_frame, frame_rect.topleft)

        lives_text = self.font.render(f"Lives: {self.lives}", True, COLORS['YELLOW'])
        screen.blit(lives_text, (self.rect.x, self.rect.y - 20))


# --- Enemy Class ---
class Enemy(GameObject):
    """
    A specialized GameObject for enemies with directional sight.
    Now uses the loaded and scaled sprites.
    """

    def __init__(self, x, y):
        # Enemy now uses the custom sprite size (64x128)
        enemy_sheet = create_placeholder_sprite_sheet(ENEMY_WIDTH, ENEMY_HEIGHT, 'enemy')
        super().__init__(x, y, ENEMY_WIDTH, ENEMY_HEIGHT, sprite_sheet=enemy_sheet, speed=2)

        self.sight_range = 100
        self.field_of_view = math.radians(60)
        self.facing_angle = 0.0
        self.move_timer = 0
        self.move_interval = FPS * 1.5
        self.last_moving_dx = 1
        self.last_moving_dy = 0
        self.set_random_direction()

        # Adjust rect height for collision, as the sprite is tall (128)
        # Collision box is 50% of sprite height for the feet/lower body (128 * 0.5 = 64)
        self.collision_height = int(ENEMY_HEIGHT * 0.5)
        self.rect.height = self.collision_height
        # Shift the collision box down to align with the bottom of the sprite (128 - 64 = 64 pixels)
        self.rect.y += ENEMY_HEIGHT - self.collision_height

        self.set_state('walk_down')  # Set an initial animation
        # Debugging variable to draw the LOS line
        self.debug_los_clear = False

    def set_random_direction(self):
        """Sets a random velocity for the enemy, avoiding zero movement."""
        while True:
            # Generate random movement between -speed and +speed
            self.dx = (random.random() - 0.5) * 2 * self.speed
            self.dy = (random.random() - 0.5) * 2 * self.speed
            if abs(self.dx) > 0.1 or abs(self.dy) > 0.1:
                break  # Ensure some movement is chosen

        if self.dx != 0 or self.dy != 0:
            # Update facing angle based on the new movement direction
            self.facing_angle = math.atan2(self.dy, self.dx)

    def update(self, obstacles, player=None):
        """Enemy update logic, including movement AI, solid collision, and setting animation state."""

        self.move_timer += 1

        if self.move_timer >= self.move_interval:
            self.set_random_direction()
            self.move_timer = 0

        # 1. Update facing direction based on movement
        if self.dx != 0 or self.dy != 0:
            self.facing_angle = math.atan2(self.dy, self.dx)
            self.last_moving_dx = self.dx
            self.last_moving_dy = self.dy
        elif self.last_moving_dx != 0 or self.last_moving_dy != 0:
            # If stopped, maintain the last direction for sight cone
            self.facing_angle = math.atan2(self.last_moving_dy, self.last_moving_dx)

        # 2. Set Animation State based on direction
        if self.dx == 0 and self.dy == 0:
            self.set_state('idle')
        elif abs(self.dx) > abs(self.dy):
            if self.dx > 0:
                self.set_state('walk_right')
            else:
                self.set_state('walk_left')
        else:
            if self.dy > 0:
                self.set_state('walk_down')
            else:
                self.set_state('walk_up')

        # 3. Apply movement and collision
        self._attempt_move(obstacles)

        # 4. Animate
        self.animate()

        # 5. Handle stuck state by resetting direction immediately
        if self.dx == 0 and self.dy == 0 and self.move_timer < self.move_interval:
            self.set_random_direction()

    def is_player_detected(self, player, walls):
        """Checks if the player is within the sight cone AND the line of sight is clear."""

        # 1. Distance Check
        distance = self.get_distance(player)
        if distance > self.sight_range:
            self.debug_los_clear = False
            return False

        # 2. Angle Check (Is player within the field of view)
        dx_to_player = player.rect.centerx - self.rect.centerx
        dy_to_player = player.rect.centery - self.rect.centery
        angle_to_player = math.atan2(dy_to_player, dx_to_player)
        # Normalize angle difference to be between -pi and pi
        angle_diff = (angle_to_player - self.facing_angle + math.pi) % (2 * math.pi) - math.pi

        if abs(angle_diff) <= self.field_of_view / 2:

            # --- 3. Line of Sight (LOS) Obstruction Check ---
            p1 = self.rect.center  # Ray origin (enemy center)
            p2 = player.rect.center  # Ray target (player center)

            path_blocked = False
            for wall in walls:
                # clipline returns a tuple if the line segment (p1, p2) intersects the rect
                if wall.rect.clipline(p1, p2):
                    path_blocked = True
                    break

            self.debug_los_clear = not path_blocked
            return not path_blocked

        self.debug_los_clear = False
        return False

    def render(self, screen, walls):
        """Custom enemy render, including the directional sight cone and LOS debug."""

        # 1. Calculate the base sight cone points (without wall obstruction)
        center = self.rect.center
        half_fov = self.field_of_view / 2

        start_angle = self.facing_angle - half_fov
        end_angle = self.facing_angle + half_fov

        # Calculate the two far points at the edge of the range
        point_a_x = center[0] + self.sight_range * math.cos(start_angle)
        point_a_y = center[1] + self.sight_range * math.sin(start_angle)

        point_b_x = center[0] + self.sight_range * math.cos(end_angle)
        point_b_y = center[1] + self.sight_range * math.sin(end_angle)

        # Store the current outer points (will be clipped)
        current_point_a = (point_a_x, point_a_y)
        current_point_b = (point_b_x, point_b_y)

        # --- 2. Wall Collision Check and Clipping ---

        # Ray 1: Edge from center to point A
        p1 = center
        p2_a = current_point_a

        # Ray 2: Edge from center to point B
        p2_b = current_point_b

        for wall in walls:
            wall_rect = wall.rect

            # Check and clip Ray 1 (Center to Point A)
            clip_a = wall_rect.clipline(p1, p2_a)
            if clip_a:
                # Find the intersection point CLOSER to the enemy's center (p1)
                dist_sq_0 = (clip_a[0][0] - center[0]) ** 2 + (clip_a[0][1] - center[1]) ** 2
                dist_sq_1 = (clip_a[1][0] - center[0]) ** 2 + (clip_a[1][1] - center[1]) ** 2

                if dist_sq_0 < dist_sq_1:
                    intersection_point_a = clip_a[0]
                else:
                    intersection_point_a = clip_a[1]

                # Only clip the point if the intersection is CLOSER than the current point A
                current_dist_sq = (current_point_a[0] - center[0]) ** 2 + (current_point_a[1] - center[1]) ** 2
                intersect_dist_sq = (intersection_point_a[0] - center[0]) ** 2 + (
                        intersection_point_a[1] - center[1]) ** 2

                if intersect_dist_sq < current_dist_sq:
                    current_point_a = intersection_point_a

            # Check and clip Ray 2 (Center to Point B)
            clip_b = wall_rect.clipline(p1, p2_b)
            if clip_b:
                # Find the intersection point CLOSER to the enemy's center (p1)
                dist_sq_0 = (clip_b[0][0] - center[0]) ** 2 + (clip_b[0][1] - center[1]) ** 2
                dist_sq_1 = (clip_b[1][0] - center[0]) ** 2 + (clip_b[1][1] - center[1]) ** 2

                if dist_sq_0 < dist_sq_1:
                    intersection_point_b = clip_b[0]
                else:
                    intersection_point_b = clip_b[1]

                # Only clip the point if the intersection is CLOSER than the current point B
                current_dist_sq = (current_point_b[0] - center[0]) ** 2 + (current_point_b[1] - center[1]) ** 2
                intersect_dist_sq = (intersection_point_b[0] - center[0]) ** 2 + (
                        intersection_point_b[1] - center[1]) ** 2

                if intersect_dist_sq < current_dist_sq:
                    current_point_b = intersection_point_b

        # 3. Final Cone Points using the clipped edges
        cone_points = [center, current_point_a, current_point_b]

        # Draw the translucent cone onto a separate surface first
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(s, COLORS['SIGHT_CONE'], cone_points)
        screen.blit(s, (0, 0))

        # 4. Draw Enemy body (uses the correctly sized and scaled sprite)
        super().render(screen)

        # 5. Debugging: Draw the line of sight status if the path is clear
        if self.debug_los_clear:
            line_color = COLORS['LOS_CLEAR']
            # For demonstration, we'll just draw a short line in the facing direction
            line_end_x = center[0] + 50 * math.cos(self.facing_angle)
            line_end_y = center[1] + 50 * math.sin(self.facing_angle)
            pygame.draw.line(screen, line_color, center, (line_end_x, line_end_y), 2)


# --- Present Class ---
class Present(GameObject):
    """
    A collectible object that requires the player to interact to collect it.
    It acts as a solid obstacle until collected.
    """

    def __init__(self, x, y):
        present_sheet = create_placeholder_sprite_sheet(35, 35, 'present')
        super().__init__(x, y, 35, 35, sprite_sheet=present_sheet, speed=0, initial_state='idle')

        self.interaction_range = 50
        interact_size = self.interaction_range * 2
        # Pre-calculate the interaction rect based on the center of the body rect
        self.interaction_rect = pygame.Rect(0, 0, interact_size, interact_size)
        self.interaction_rect.center = self.rect.center

        self.is_collected = False
        self.is_collecting = False
        self.collection_progress = 0
        self.max_collection_time = FPS * 2.5

        self.font_medium = pygame.font.Font(None, 24)

    def check_interaction_proximity(self, player):
        """Checks if the player is within the interaction bubble."""
        return self.interaction_rect.colliderect(player.rect)

    def start_collection(self):
        """Begins the collection process if not already collecting."""
        if not self.is_collecting:
            self.is_collecting = True
            self.collection_progress = 0

    def cancel_collection(self):
        """Stops the collection process."""
        self.is_collecting = False
        self.collection_progress = 0

    def update(self, player):
        """Present update logic, handling collection progress."""
        super().update()

        in_range = self.check_interaction_proximity(player)

        if self.is_collecting:
            if in_range:
                self.collection_progress += 1

                if self.collection_progress >= self.max_collection_time:
                    self.is_collected = True
                    self.is_collecting = False
            else:
                self.cancel_collection()

    def render(self, screen, player):
        """Custom present render, including UI overlay."""
        # 1. Draw the interaction bubble (transparent)
        interaction_surface = pygame.Surface((self.interaction_range * 2, self.interaction_range * 2), pygame.SRCALPHA)
        # Transparent blue circle
        pygame.draw.circle(interaction_surface, (100, 150, 255, 60), (self.interaction_range, self.interaction_range),
                           self.interaction_range)
        screen.blit(interaction_surface, self.interaction_rect.topleft)

        # 2. Draw the Present body
        super().render(screen)

        # 3. Draw UI based on state

        # A. Interaction prompt
        if self.check_interaction_proximity(player) and not self.is_collecting:
            interact_text = self.font_medium.render("PRESS E TO INTERACT", True, COLORS['YELLOW'])
            text_rect = interact_text.get_rect(center=(self.rect.centerx, self.rect.top - 40))
            bg_rect = text_rect.inflate(10, 5)
            pygame.draw.rect(screen, COLORS['BLACK'], bg_rect, border_radius=3)
            screen.blit(interact_text, text_rect)

        # B. Collection Meter
        if self.is_collecting:
            meter_width = 80
            meter_height = 15
            meter_x = self.rect.centerx - meter_width // 2
            meter_y = self.rect.top - 65

            bg_rect = pygame.Rect(meter_x, meter_y, meter_width, meter_height)
            pygame.draw.rect(screen, COLORS['METER_BG'], bg_rect, border_radius=3)

            progress_ratio = self.collection_progress / self.max_collection_time
            fill_width = int(meter_width * progress_ratio)
            fill_rect = pygame.Rect(meter_x, meter_y, fill_width, meter_height)
            pygame.draw.rect(screen, COLORS['METER_FILL'], fill_rect, border_radius=3)

            pygame.draw.rect(screen, COLORS['WHITE'], bg_rect, 1, border_radius=3)


# --- Wall Class ---
class Wall(GameObject):
    """
    A non-interactive, solid barrier for level design.
    """

    def __init__(self, x, y, width, height):
        # Wall uses a generic placeholder sprite sheet
        wall_sheet = create_placeholder_sprite_sheet(width, height, 'wall')
        super().__init__(x, y, width, height, sprite_sheet=wall_sheet, speed=0, initial_state='idle')

    def render(self, screen):
        """
        Draws the wall. Overriding the super method to ensure the wall is drawn
        to match its exact rect dimensions, as it's a structural element.
        """
        pygame.draw.rect(screen, COLORS['WALL_COLOR'], self.rect)

    def update(self, *args):
        """Walls do not move or animate."""
        pass


# --- Game Helper Functions ---

def is_valid_spawn_location(rect_body, rect_interaction, solids):
    """Checks if a location for a Present (both body and interaction zone) is clear of all existing solids."""
    # Check bounds first
    if not (0 < rect_body.left and rect_body.right < SCREEN_WIDTH and
            0 < rect_body.top and rect_body.bottom < SCREEN_HEIGHT):
        return False

    for solid in solids:
        # Check collision with the main body
        if rect_body.colliderect(solid.rect):
            return False

        # Check collision with the interaction zone
        if rect_interaction.colliderect(solid.rect):
            return False

    return True


# --- Main Game Execution ---
def run_game():
    """Initializes Pygame, sets up objects, and runs the main game loop."""
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pygame Stealth Game")

    clock = pygame.time.Clock()

    ui_font = pygame.font.Font(None, 36)
    game_over_font = pygame.font.Font(None, 72)

    global score
    score = 0
    game_state = 'PLAYING'
    kickout_timer = 0

    player_start_x = SCREEN_WIDTH // 4
    player_start_y = SCREEN_HEIGHT // 2

    # --- Define Room Separating Walls ---
    wall_objects = [
        # Horizontal barrier near the top
        Wall(x=50, y=100, width=700, height=20),
        # Vertical room divider in the middle (creating two halves)
        Wall(x=SCREEN_WIDTH // 2 - 10, y=150, width=20, height=350),
        # Small corner wall
        Wall(x=600, y=450, width=100, height=100),
    ]

    # Initialize Enemies
    enemies = [
        Enemy(x=SCREEN_WIDTH * 0.75, y=SCREEN_HEIGHT * 0.25),
        Enemy(x=SCREEN_WIDTH * 0.5 - 100, y=SCREEN_HEIGHT * 0.75)
    ]

    # --- Dynamic Present Spawning (Avoiding Walls) ---
    present_objects = []
    attempts = 0
    max_attempts = 100

    while len(present_objects) < NUM_PRESENTS and attempts < max_attempts:
        # Pick a random position
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(50, SCREEN_HEIGHT - 50)

        temp_present = Present(x, y)

        # Check validity against existing walls AND presents
        if is_valid_spawn_location(temp_present.rect, temp_present.interaction_rect, wall_objects + present_objects):
            present_objects.append(temp_present)

        attempts += 1

    print(f"--- Spawned {len(present_objects)} out of {NUM_PRESENTS} presents. ---")

    # Initialize Player
    player = Player(x=player_start_x, y=player_start_y)

    running = True
    print("--- Pygame Game Started (Stealth Mode) ---")

    while running:
        e_pressed = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_e:
                    e_pressed = True

        # --- State Transitions ---
        if game_state == 'PLAYING' and player.is_caught:
            if player.lives <= 0:
                game_state = 'GAME_OVER'
            else:
                game_state = 'CAUGHT'
                kickout_timer = KICKOUT_DURATION

        keys = pygame.key.get_pressed()

        # Only allow input handling if we are actively playing
        if game_state == 'PLAYING':
            player.handle_input_and_set_state(keys)
        else:
            player.handle_input_and_set_state({})

        # --- Update All Objects ---
        if game_state == 'PLAYING':

            # Solids that *don't* move (Walls and Presents)
            static_solids = wall_objects + present_objects

            # ALL_OBSTACLES is the complete list of objects any moving entity should check against
            # This includes static solids AND other enemies (because enemies collide with each other)
            ALL_OBSTACLES = static_solids + enemies

            # 1. Update Player (pass ALL_OBSTACLES for movement collision, and wall_objects for LOS check)
            player.update(enemies, ALL_OBSTACLES, wall_objects)

            # 2. Update and check present collection
            for present in present_objects:
                if e_pressed and present.check_interaction_proximity(player):
                    present.start_collection()

                present.update(player)

                if present.is_collected:
                    score += PRESENT_COLLECTION_VALUE
                    print(f"Score increased! New Score: {score}")

            # Remove collected presents
            present_objects = [p for p in present_objects if not p.is_collected]

            # 3. Update enemies
            for enemy in enemies:
                # Enemies collide with ALL_OBSTACLES (Walls, Presents, other Enemies)
                enemy.update(ALL_OBSTACLES, player)

            # 4. Collision
            for enemy in enemies:
                if player.lives > 0 and player.check_collision(enemy):
                    if player.lose_life():
                        # Push the player away from the enemy on physical collision
                        push_factor = 40
                        direction_x = player.rect.centerx - enemy.rect.centerx
                        direction_y = player.rect.centery - enemy.rect.centery
                        distance = player.get_distance(enemy)

                        if distance > 0:
                            player.rect.x += direction_x / distance * push_factor
                            player.rect.y += direction_y / distance * push_factor

                        # Resolve any new collisions from the push
                        player.update(enemies, static_solids, wall_objects)

                        # --- Rendering ---
        screen.fill(COLORS['DARK_GRAY'])

        if game_state == 'PLAYING':
            # Draw game objects
            for wall in wall_objects:
                wall.render(screen)
            for present in present_objects:
                present.render(screen, player)
            for enemy in enemies:
                enemy.render(screen, wall_objects)
            player.render(screen)

            # COLLISION BOX FOR TESTING - DELETE LATER
            for enemy in enemies:
                pygame.draw.rect(screen, COLORS['RED'], enemy.rect, 1)
            pygame.draw.rect(screen, COLORS['YELLOW'], player.rect, 1)

            # Draw score UI
            score_text = ui_font.render(f"Score: {score}", True, COLORS['WHITE'])
            screen.blit(score_text, (10, 10))

        elif game_state == 'CAUGHT':
            # Draw black screen during kickout timer
            pygame.draw.rect(screen, COLORS['BLACK'], (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 0)

            msg = game_over_font.render("CAUGHT! KICKED OUT.", True, COLORS['RED'])
            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - msg.get_height() // 2))

            kickout_timer -= 1
            if kickout_timer <= 0:
                # Reset player position and return to playing state
                player.reset_for_new_round(player_start_x, player_start_y)
                game_state = 'PLAYING'
                print("--- RESUMING GAME ---")

        elif game_state == 'GAME_OVER':
            # Draw black screen for game over
            pygame.draw.rect(screen, COLORS['BLACK'], (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 0)

            msg = game_over_font.render("GAME OVER", True, COLORS['RED'])
            sub_msg = ui_font.render(f"Final Score: {score} | Close the window to exit", True, COLORS['WHITE'])

            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - msg.get_height() // 2))
            screen.blit(sub_msg, (SCREEN_WIDTH // 2 - sub_msg.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    print("--- Pygame Game Ended ---")


if __name__ == '__main__':
    run_game()
