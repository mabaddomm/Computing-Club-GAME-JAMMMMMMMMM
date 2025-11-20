import pygame
import math
import random

# --- Pygame Setup Constants ---

current_track = None

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
PRESENT_COLLECTION_VALUE = 1  # Score value for collecting a present
KICKOUT_DURATION = FPS * 2  # 2 seconds of black screen duration

SPRITE_SCALE_FACTOR = 3
SPRITE_WIDTH_ON_SHEET_GRINCH = 18
SPRITE_HEIGHT_ON_SHEET = 32
SPRITE_WIDTH_ON_SHEET_ENEMY = 16
SPRITE_SHEET_PATH = 'character.png'
grinch_sheet_path = 'grinch_spread.png'

PLAYER_WIDTH = SPRITE_WIDTH_ON_SHEET_GRINCH * SPRITE_SCALE_FACTOR  # 72
PLAYER_HEIGHT = SPRITE_HEIGHT_ON_SHEET * SPRITE_SCALE_FACTOR  # 128
ENEMY_WIDTH = SPRITE_WIDTH_ON_SHEET_ENEMY * SPRITE_SCALE_FACTOR  # 64
ENEMY_HEIGHT = SPRITE_HEIGHT_ON_SHEET * SPRITE_SCALE_FACTOR  # 128

PLAYER_SPAWN_IN_LEVEL = (630, 550)
DOOR_RECT = (640, 695, 50, 30)  # x, y, w, h

# New sizes requested
TREE_WIDTH = 110
TREE_HEIGHT = 150
PRESENT_SIZE = 40

# --- PRESENT SPAWN CONSTANTS (REVISED) ---
TREE_MARGIN = 40  # Minimum distance from tree's collision box
# TREE_HEIGHT // 2 is 90. min_radius is 90 + 40 = 130
TREE_MIN_RADIUS = max(TREE_WIDTH, TREE_HEIGHT) // 6 + TREE_MARGIN
# Tighter band: 130 + 30 = 160 (was 170)
TREE_MAX_RADIUS = TREE_MIN_RADIUS + 30

# --- PRESENT IMAGE CONSTANTS ---
PRESENT_IMAGE_PATHS = ['prez1.png', 'prez2.png']  # Assuming the user meant 'image1.png' and 'image2.png'

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
    'WALL_COLOR': (50, 20, 20),  # New color for walls
    'FLOOR_COLOR': (152, 116, 86),
    'LOS_BLOCKED': (255, 0, 0, 100),  # Debug color for blocked LOS
    'LOS_CLEAR': (0, 255, 0, 100),  # Debug color for clear LOS
    'DEBUG_RANGE': (255, 255, 100, 50),  # Light Yellow Translucent
}


# --- Sprite Sheet Loading and Splitting ---

# ... load_and_split_sprites (unchanged) ...
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
        surf = pygame.Surface([width, height], pygame.SRCALPHA)
        surf.fill(color)
        font = pygame.font.Font(None, 16)
        text_surf = font.render(label[:4], True, COLORS['BLACK'])
        surf.blit(text_surf, (2, 2))
        return surf

    if type_key == 'player':
        all_sprites = load_and_split_sprites(grinch_sheet_path, SPRITE_WIDTH_ON_SHEET_GRINCH, SPRITE_HEIGHT_ON_SHEET,
                                             SPRITE_SCALE_FACTOR)

        if all_sprites and len(all_sprites) >= 12:
            sheet['idle_down'] = [all_sprites[0]]
            sheet['walk_down'] = [all_sprites[1], all_sprites[2]]
            sheet['idle_up'] = [all_sprites[3]]
            sheet['walk_up'] = [all_sprites[4], all_sprites[5]]
            sheet['idle_right'] = [all_sprites[6]]
            sheet['walk_right'] = [all_sprites[7], all_sprites[6], all_sprites[8]]
            sheet['idle_left'] = [all_sprites[9]]
            sheet['walk_left'] = [all_sprites[10], all_sprites[9], all_sprites[11]]
        else:
            print("Failed to load or split Player (Grinch) sprites. Using placeholder.")
            sheet['idle'] = [create_frame(COLORS['PLAYER_GREEN'], 'idle')]
            sheet['walk_down'] = [create_frame(COLORS['PLAYER_GREEN'], 'down')] * 2
            sheet['walk_up'] = [create_frame(COLORS['PLAYER_GREEN'], 'up')] * 2
            sheet['walk_right'] = [create_frame(COLORS['PLAYER_GREEN'], 'right')] * 2
            sheet['walk_left'] = [create_frame(COLORS['PLAYER_GREEN'], 'left')] * 2

    # --- REMOVED PRESENT PLACEHOLDER LOGIC ---
    # elif type_key == 'present':
    #     present_surf = pygame.Surface([width, height], pygame.SRCALPHA)
    #     present_surf.fill(COLORS['PRESENT_BLUE'])
    #     pygame.draw.line(present_surf, COLORS['WHITE'], (width // 2, 0), (width // 2, height), 3)
    #     pygame.draw.line(present_surf, COLORS['WHITE'], (0, height // 2), (width, height // 2), 3)
    #     sheet['idle'] = [present_surf]

    elif type_key == 'wall':
        wall_surf = pygame.Surface([width, height], pygame.SRCALPHA)
        wall_surf.fill(COLORS['WALL_COLOR'])
        sheet['idle'] = [wall_surf]

    elif type_key == 'enemy':
        all_sprites = load_and_split_sprites(SPRITE_SHEET_PATH, SPRITE_WIDTH_ON_SHEET_ENEMY, SPRITE_HEIGHT_ON_SHEET,
                                             SPRITE_SCALE_FACTOR)

        if all_sprites and len(all_sprites) >= 16:
            sheet['idle'] = [all_sprites[0]]
            sheet['walk_down'] = [all_sprites[0], all_sprites[1]]
            sheet['walk_up'] = [all_sprites[4], all_sprites[5]]
            sheet['walk_right'] = [all_sprites[12], all_sprites[13]]  # Swapped Left
            sheet['walk_left'] = [all_sprites[8], all_sprites[9]]  # Swapped Right
        else:
            print("Failed to load or split enemy sprites. Using placeholder.")
            sheet['idle'] = [create_frame(COLORS['ENEMY_RED'], 'ERR')]
            sheet['walk_down'] = [create_frame(COLORS['ENEMY_RED'], 'E-D')] * 2
            sheet['walk_up'] = [create_frame(COLORS['ENEMY_RED'], 'E-U')] * 2
            sheet['walk_right'] = [create_frame(COLORS['ENEMY_RED'], 'E-R')] * 2
            sheet['walk_left'] = [create_frame(COLORS['ENEMY_RED'], 'E-L')] * 2

    return sheet


# --- Core GameObject Class (unchanged) ---
# ... GameObject (unchanged) ...
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
        self.current_animation = self.sprite_sheet.get(initial_state, [default_surface])

        self.rect = pygame.Rect(x, y, width, height)

        self.dx = 0  # Velocity X
        self.dy = 0  # Velocity Y

        # Animation State Management
        self.frame_x = 0
        self.frame_timer = 0
        self.frame_interval = 10  # Control speed of animation (lower = faster)

    def set_state(self, new_state):
        """Changes the current animation state if different from the current one."""
        if new_state not in self.sprite_sheet:
            if new_state != 'idle':
                return self.set_state('idle')
            return

        if self.current_state != new_state:
            self.current_state = new_state
            self.current_animation = self.sprite_sheet[new_state]
            self.frame_x = 0

            if len(self.current_animation) <= 1:
                self.frame_interval = 1000
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
        frame_rect = current_frame.get_rect(center=self.rect.center)
        screen.blit(current_frame, frame_rect.topleft)

    def check_collision(self, other):
        """Checks for collision using Pygame's built-in Rect collision detection."""
        return self.rect.colliderect(other.rect)

    def get_distance(self, other):
        """Calculates the Euclidean distance to the center of another object."""
        center_x1, center_y1 = self.rect.center
        center_x2, center_y2 = other.rect.center
        return math.sqrt((center_x2 - center_x1) ** 2 + (center_y2 - center_y1) ** 2)


# --- Player Class (unchanged) ---
# ... Player (unchanged) ...
class Player(GameObject):

    def __init__(self, x, y):
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

        self.rect.y = y + (PLAYER_HEIGHT - self.collision_height)

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
            current_state = self.current_state

            if 'down' in current_state:
                self.set_state('idle_down')
            elif 'up' in current_state:
                self.set_state('idle_up')
            elif 'right' in current_state:
                self.set_state('idle_right')
            elif 'left' in current_state:
                self.set_state('idle_left')
            else:
                self.set_state('idle_down')

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

    def got_caught(self):
        if self.is_vulnerable and self.lives > 0:
            self.lives -= 1
            self.is_vulnerable = False
            self.invuln_timer = self.max_invuln_time

            self.is_caught = True
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

        # 2. Apply solid collision and movement against all solid objects (Walls + Presents + Trees)
        self._attempt_move(solids)

        # 3. Handle Invulnerability Timer
        if not self.is_vulnerable:
            self.invuln_timer -= 1
            if self.invuln_timer <= 0:
                self.is_vulnerable = True

        # 4. Caught Logic: Check if any enemy has the player in sight
        if self.lives > 0 and not self.is_caught:
            for enemy in enemies:
                # PASS combined walls (walls + trees) for Line-of-Sight check
                if enemy.is_player_detected(self, walls):
                    self.got_caught()

    def render(self, screen):
        """Custom player render, handling flashing when invulnerable."""
        if not self.is_vulnerable and self.invuln_timer % 10 < 5:
            pass
        else:
            current_frame = self.get_current_frame()
            frame_rect = current_frame.get_rect()
            frame_rect.midbottom = self.rect.midbottom
            screen.blit(current_frame, frame_rect.topleft)

        lives_text = self.font.render(f"Lives: {self.lives}", True, COLORS['YELLOW'])
        screen.blit(lives_text, (self.rect.x, self.rect.y - 20))


# --- Enemy Class (unchanged) ---
# ... Enemy (unchanged) ...
class Enemy(GameObject):
    """
    A specialized GameObject for enemies with directional sight.
    Now uses the loaded and scaled sprites.
    """

    def __init__(self, x, y):
        enemy_sheet = create_placeholder_sprite_sheet(ENEMY_WIDTH, ENEMY_HEIGHT, 'enemy')
        super().__init__(x, y, ENEMY_WIDTH, ENEMY_HEIGHT, sprite_sheet=enemy_sheet, speed=2)

        self.sight_range = 130
        self.field_of_view = math.radians(60)
        self.facing_angle = 0.0
        self.move_timer = 0
        self.move_interval = FPS * 1.5
        self.last_moving_dx = 1
        self.last_moving_dy = 0
        self.set_random_direction()

        # Collision box sizing for feet
        self.collision_height = int(ENEMY_HEIGHT * 0.5)

        # Make physical collision smaller (narrow and low)
        self.rect.width = int(self.rect.width * 0.7)
        self.rect.height = int(self.rect.height * 0.2)
        self.rect.x += ENEMY_WIDTH * 0.25  # recenter horizontally
        self.rect.y += ENEMY_HEIGHT * 0.65

        self.set_state('walk_down')
        self.debug_los_clear = False

    def set_random_direction(self):
        """Sets a random velocity for the enemy, avoiding zero movement."""
        while True:
            self.dx = (random.random() - 0.5) * 2 * self.speed
            self.dy = (random.random() - 0.5) * 2 * self.speed
            if abs(self.dx) > 0.1 or abs(self.dy) > 0.1:
                break

        if self.dx != 0 or self.dy != 0:
            self.facing_angle = math.atan2(self.dy, self.dx)

    def update(self, obstacles, player=None):
        """Enemy update logic, including movement AI, solid collision, and setting animation state."""
        self.move_timer += 1

        if self.move_timer >= self.move_interval:
            self.set_random_direction()
            self.move_timer = 0

        if self.dx != 0 or self.dy != 0:
            self.facing_angle = math.atan2(self.dy, self.dx)
            self.last_moving_dx = self.dx
            self.last_moving_dy = self.dy
        elif self.last_moving_dx != 0 or self.last_moving_dy != 0:
            self.facing_angle = math.atan2(self.last_moving_dy, self.last_moving_dx)

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

        self._attempt_move(obstacles)
        self.animate()

        if self.dx == 0 and self.dy == 0 and self.move_timer < self.move_interval:
            self.set_random_direction()

    def is_player_detected(self, player, walls):
        player_full_rect = pygame.Rect(
            player.rect.x,
            player.rect.y - (PLAYER_HEIGHT - player.rect.height),
            PLAYER_WIDTH,
            PLAYER_HEIGHT
        )

        player_hit_rect = player.rect

        p1 = self.rect.center
        p2 = player_full_rect.center

        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        distance = math.hypot(dx, dy)

        if distance > self.sight_range:
            self.debug_los_clear = False
            return False

        angle_to_player = math.atan2(dy, dx)
        angle_diff = (angle_to_player - self.facing_angle + math.pi) % (2 * math.pi) - math.pi

        if abs(angle_diff) > self.field_of_view / 2:
            self.debug_los_clear = False
            return False

        # Wall obstruction check (walls param includes trees when passed correctly)
        for wall in walls:
            if wall.rect.clipline(p1, p2):
                self.debug_los_clear = False
                return False

        hits_full = player_full_rect.clipline(p1, p2)
        hits_feet = player_hit_rect.clipline(p1, p2)

        if hits_full or hits_feet:
            self.debug_los_clear = True
            return True

        self.debug_los_clear = False
        return False

    def render(self, screen, walls):
        """Custom enemy render, including the directional sight cone and LOS debug."""
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

        p1 = center
        p2_a = current_point_a
        p2_b = current_point_b

        for wall in walls:
            wall_rect = wall.rect

            clip_a = wall_rect.clipline(p1, p2_a)
            if clip_a:
                dist_sq_0 = (clip_a[0][0] - center[0]) ** 2 + (clip_a[0][1] - center[1]) ** 2
                dist_sq_1 = (clip_a[1][0] - center[0]) ** 2 + (clip_a[1][1] - center[1]) ** 2

                if dist_sq_0 < dist_sq_1:
                    intersection_point_a = clip_a[0]
                else:
                    intersection_point_a = clip_a[1]

                current_dist_sq = (current_point_a[0] - center[0]) ** 2 + (current_point_a[1] - center[1]) ** 2
                intersect_dist_sq = (intersection_point_a[0] - center[0]) ** 2 + (
                        intersection_point_a[1] - center[1]) ** 2

                if intersect_dist_sq < current_dist_sq:
                    current_point_a = intersection_point_a

            clip_b = wall_rect.clipline(p1, p2_b)
            if clip_b:
                dist_sq_0 = (clip_b[0][0] - center[0]) ** 2 + (clip_b[0][1] - center[1]) ** 2
                dist_sq_1 = (clip_b[1][0] - center[0]) ** 2 + (clip_b[1][1] - center[1]) ** 2

                if dist_sq_0 < dist_sq_1:
                    intersection_point_b = clip_b[0]
                else:
                    intersection_point_b = clip_b[1]

                current_dist_sq = (current_point_b[0] - center[0]) ** 2 + (current_point_b[1] - center[1]) ** 2
                intersect_dist_sq = (intersection_point_b[0] - center[0]) ** 2 + (
                        intersection_point_b[1] - center[1]) ** 2

                if intersect_dist_sq < current_dist_sq:
                    current_point_b = intersection_point_b

        cone_points = [center, current_point_a, current_point_b]

        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(s, COLORS['SIGHT_CONE'], cone_points)
        screen.blit(s, (0, 0))

        super().render(screen)

        if self.debug_los_clear:
            line_color = COLORS['LOS_CLEAR']
            line_end_x = center[0] + 50 * math.cos(self.facing_angle)
            line_end_y = center[1] + 50 * math.sin(self.facing_angle)
            pygame.draw.line(screen, line_color, center, (line_end_x, line_end_y), 2)


# --- Tree Class (REVISED) ---
class Tree(GameObject):
    TREE_IMAGE = None  # cached to avoid reloading every tree
    def __init__(self, x, y):
        # The (x, y) passed is the top-left of the full sprite (140x180)
        self.full_x = x
        self.full_y = y

        # load image once
        if Tree.TREE_IMAGE is None:
            try:
                raw = pygame.image.load("christmas_tree.png").convert_alpha()
            except:
                print("ERROR: tree.png missing, using fallback rectangle.")
                raw = pygame.Surface((TREE_WIDTH, TREE_HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(raw, (30, 150, 30), raw.get_rect())

            Tree.TREE_IMAGE = pygame.transform.scale(raw, (TREE_WIDTH, TREE_HEIGHT))

        self.image = Tree.TREE_IMAGE

        collision_width = TREE_WIDTH * 0.4  # e.g., 56
        collision_height = TREE_HEIGHT * 0.3  # e.g., 54

        # Calculate offsets to center the collision box at the base of the sprite
        x_offset = (TREE_WIDTH - collision_width) // 2
        y_offset = TREE_HEIGHT - collision_height

        # The actual collision rect position
        super().__init__(x + x_offset, y + y_offset, collision_width, collision_height,
                         sprite_sheet={"idle": [self.image]},
                         speed=0, initial_state='idle')
        # -----------------------------

    def get_full_sprite_center(self):
        """Calculates the center of the full TREE_WIDTH x TREE_HEIGHT sprite."""
        # The full sprite position is (self.full_x, self.full_y)
        return self.full_x + TREE_WIDTH // 2, self.full_y + TREE_HEIGHT // 2

    def render(self, screen):
        # draw full PNG sprite using the stored original coordinates
        screen.blit(self.image, (self.full_x, self.full_y))

    def render_spawn_range(self, screen):
        """Renders the debug circle for the present spawn range."""
        center_x, center_y = self.rect.center

        # Create a surface for translucent drawing
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # Draw the ring area (max_r filled, then min_r filled with a hole)
        # We will draw a translucent filled circle for the max radius...
        pygame.draw.circle(s, COLORS['DEBUG_RANGE'], (center_x, center_y), TREE_MAX_RADIUS, 0)

        pygame.draw.circle(s, COLORS['DEBUG_RANGE'], (center_x, center_y), TREE_MAX_RADIUS, 2)
        # Draw the outline of the inner limit
        pygame.draw.circle(s, COLORS['DEBUG_RANGE'], (center_x, center_y), TREE_MIN_RADIUS, 2)

        screen.blit(s, (0, 0))


# --- Present Class (unchanged) ---
# ... Present (unchanged) ...
class Present(GameObject):

    PRESENT_IMAGES = None  # Cache for loaded present images

    def __init__(self, x, y):
        # --- NEW IMAGE LOADING LOGIC ---
        if Present.PRESENT_IMAGES is None:
            Present.PRESENT_IMAGES = []
            for path in PRESENT_IMAGE_PATHS:
                try:
                    raw = pygame.image.load(path).convert_alpha()
                    image = pygame.transform.scale(raw, (PRESENT_SIZE, PRESENT_SIZE))
                    Present.PRESENT_IMAGES.append(image)
                except pygame.error:
                    print(f"ERROR: {path} missing, using fallback rectangle.")
                    fallback = pygame.Surface((PRESENT_SIZE, PRESENT_SIZE), pygame.SRCALPHA)
                    fallback.fill(COLORS['PRESENT_BLUE'])
                    pygame.draw.line(fallback, COLORS['WHITE'], (PRESENT_SIZE // 2, 0),
                                     (PRESENT_SIZE // 2, PRESENT_SIZE), 3)
                    pygame.draw.line(fallback, COLORS['WHITE'], (0, PRESENT_SIZE // 2),
                                     (PRESENT_SIZE, PRESENT_SIZE // 2), 3)
                    Present.PRESENT_IMAGES.append(fallback)

        # Randomly select a loaded image
        if Present.PRESENT_IMAGES:
            self.image = random.choice(Present.PRESENT_IMAGES)
        else:
            # Should only happen if all images failed to load
            self.image = pygame.Surface((PRESENT_SIZE, PRESENT_SIZE), pygame.SRCALPHA)
            self.image.fill(COLORS['PRESENT_BLUE'])

        # Create a basic sprite sheet containing the single image
        present_sheet = {"idle": [self.image]}
        # -------------------------------

        super().__init__(x, y, PRESENT_SIZE, PRESENT_SIZE, sprite_sheet=present_sheet, speed=0, initial_state='idle')

        # Interaction
        self.interaction_range = 45  # a little smaller but still comfortable
        interact_size = self.interaction_range * 2
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
        if not self.is_collecting:
            self.is_collecting = True
            self.collection_progress = 0

    def cancel_collection(self):
        self.is_collecting = False
        self.collection_progress = 0

    def update(self, player):
        super().update()

        # Keep the interaction rect centered on the present
        self.interaction_rect.center = self.rect.center

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
        # Draw interaction bubble with more opacity (user requested more opaque)
        interaction_surface = pygame.Surface((self.interaction_range * 2, self.interaction_range * 2), pygame.SRCALPHA)
        pygame.draw.circle(interaction_surface, (100, 150, 255, 20), (self.interaction_range, self.interaction_range),
                           self.interaction_range)
        screen.blit(interaction_surface, self.interaction_rect.topleft)

        # Draw the Present body
        super().render(screen)

        # UI
        if self.check_interaction_proximity(player) and not self.is_collecting:
            interact_text = self.font_medium.render("PRESS E TO INTERACT", True, COLORS['WHITE'])
            text_rect = interact_text.get_rect(center=(self.rect.centerx, self.rect.top - 40))
            #bg_rect = text_rect.inflate(10, 5)
            #pygame.draw.rect(screen, COLORS['BLACK'], bg_rect, border_radius=1)
            screen.blit(interact_text, text_rect)

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


# --- Wall Class (unchanged) ---
# ... Wall (unchanged) ...
class Wall(GameObject):

    def __init__(self, x, y, width, height):
        wall_sheet = create_placeholder_sprite_sheet(width, height, 'wall')
        super().__init__(x, y, width, height, sprite_sheet=wall_sheet, speed=0, initial_state='idle')

    def render(self, screen):
        pygame.draw.rect(screen, COLORS['WALL_COLOR'], self.rect)

    def update(self, *args):
        pass


class Level:
    # ... Level (unchanged) ...
    def __init__(self, walls, enemy_spawn_areas, tree_spawn_areas, num_enemies, num_presents, num_trees):
        """
        walls - list of Wall()
        enemy_spawn_areas - list of (x,y,w,h)
        tree_spawn_areas - list of (x,y,w,h)
        """
        self.walls = walls
        self.enemy_spawn_areas = enemy_spawn_areas
        self.tree_spawn_areas = tree_spawn_areas
        self.tree_spawn_areas = tree_spawn_areas  # tree spawn zones = present zones as requested
        self.num_enemies = num_enemies
        self.num_presents = num_presents
        self.num_trees = num_trees

        self.door = pygame.Rect(DOOR_RECT)
        DOOR_INTERACT_SIZE = 100
        self.door_interaction_rect = self.door.inflate(DOOR_INTERACT_SIZE, DOOR_INTERACT_SIZE)


        self.player_spawn_x = PLAYER_SPAWN_IN_LEVEL[0]
        self.player_spawn_y = PLAYER_SPAWN_IN_LEVEL[1]

        # Spawn trees first (they define where presents go)
        self.trees = self.spawn_trees()
        self.enemies = self.spawn_enemies()
        self.presents = self.spawn_presents_around_trees()

    def check_door_proximity(self, player):
        """Checks if the player is within the door's interaction bubble."""
        return self.door_interaction_rect.colliderect(player.rect)

    def render_door_ui(self, screen, ui_font):
        """Renders the interaction prompt for the door."""
        # Draw interaction bubble
        door_interact_color = (255, 200, 100, 30)
        door_interact_surface = pygame.Surface(self.door_interaction_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(door_interact_surface, door_interact_color, door_interact_surface.get_rect(), border_radius=5)
        screen.blit(door_interact_surface, self.door_interaction_rect.topleft)

        # Draw prompt text
        interact_text = ui_font.render("PRESS E TO LEAVE", True, COLORS['WHITE'])
        text_rect = interact_text.get_rect(center=(self.door.centerx, self.door.top - 20))
        #bg_rect = text_rect.inflate(10, 5)
        #pygame.draw.rect(screen, COLORS['BLACK'], bg_rect, border_radius=1)
        screen.blit(interact_text, text_rect)


    def random_point_in_area(self, area, obj_width, obj_height, margin=0):
        x, y, w, h = area
        min_x = x + margin
        min_y = y + margin
        max_x = x + w - obj_width - margin
        max_y = y + h - obj_height - margin
        if max_x < min_x or max_y < min_y:
            return None
        px = random.randint(min_x, max_x)
        py = random.randint(min_y, max_y)
        return px, py

    def spawn_enemies(self):
        enemies = []
        for _ in range(self.num_enemies):
            area = random.choice(self.enemy_spawn_areas)
            pt = self.random_point_in_area(area, ENEMY_WIDTH, ENEMY_HEIGHT, margin=8)
            if pt:
                px, py = pt
                enemies.append(Enemy(px, py))
        return enemies

    def spawn_trees(self):
        """Place multiple trees inside tree_spawn_areas, non-overlapping and not touching walls."""
        trees = []
        # solids_for_trees starts with walls and will accumulate newly placed trees.
        solids_for_trees = list(self.walls)

        # New constant for the minimum separation distance between tree collision rects
        TREE_MIN_MARGIN = 50

        attempts_per_tree = 200
        placed = 0

        for _ in range(self.num_trees):
            success = False
            for _a in range(attempts_per_tree):
                area = random.choice(self.tree_spawn_areas)
                # Note: The margin=8 here is for screen boundary and general area margin
                pt = self.random_point_in_area(area, TREE_WIDTH, TREE_HEIGHT, margin=8)
                if pt is None:
                    continue

                # We need to pass the initial (x, y) for the full sprite to the Tree constructor,
                # which then calculates the offset for the smaller collision rect.
                px, py = pt
                candidate = Tree(px, py)

                # Create an inflated rect for the candidate tree to enforce the 30px margin.
                # Inflating by 2*MARGIN ensures the centers are at least 30px + half_width_A + half_width_B apart.
                candidate_buffer_rect = candidate.rect.inflate(TREE_MIN_MARGIN * 2, TREE_MIN_MARGIN * 2)

                # Check overlap with existing solids (walls and previous trees)
                overlap = False
                for s in solids_for_trees:

                    if isinstance(s, Tree):
                        # Check against existing Tree objects using the inflated rect for margin enforcement.
                        if candidate_buffer_rect.colliderect(s.rect):
                            overlap = True
                            break
                    else:  # Must be a Wall (or other non-tree solid)
                        # Check against walls normally (no margin enforcement needed).
                        if candidate.rect.colliderect(s.rect):
                            overlap = True
                            break

                if overlap:
                    continue

                # valid position
                trees.append(candidate)
                # Append the newly placed tree's SMALLER collision rect to the solids list for future checks
                solids_for_trees.append(candidate)
                success = True
                placed += 1
                break

            if not success:
                # couldn't place this tree after attempts; skip it
                continue

        return trees

    def spawn_presents_around_trees(self):
        presents = []
        if not self.trees:
            return presents

        solids = list(self.walls) + list(self.trees)

        for tree in self.trees:
            presents_for_this_tree = random.randint(1, 4)
            attempts = 300
            placed = 0

            min_radius = TREE_MIN_RADIUS
            max_radius = TREE_MAX_RADIUS
            tree_center = tree.get_full_sprite_center()

            while placed < presents_for_this_tree and attempts > 0:
                attempts -= 1

                angle = random.random() * math.pi * 2
                radius = random.randint(min_radius, max_radius)

                cx = tree_center[0] + int(radius * math.cos(angle))
                cy = tree_center[1] + int(radius * math.sin(angle))

                px = cx - PRESENT_SIZE // 2
                py = cy - PRESENT_SIZE // 2

                body = pygame.Rect(px, py, PRESENT_SIZE, PRESENT_SIZE)

                # interaction bubble check:
                interaction = pygame.Rect(0, 0, 90, 90)
                interaction.center = body.center

                # Must be fully on screen
                if not (0 < body.left and body.right < SCREEN_WIDTH and
                        0 < body.top and body.bottom < SCREEN_HEIGHT):
                    continue

                # Must NOT overlap walls, trees, or existing presents
                blocked = False
                for s in solids:
                    if body.colliderect(s.rect) or interaction.colliderect(s.rect):
                        blocked = True
                        break
                if blocked:
                    continue

                for p in presents:
                    if body.colliderect(p.rect) or interaction.colliderect(p.interaction_rect):
                        blocked = True
                        break
                if blocked:
                    continue

                # --- NEW: Prevent Presents from being visually hidden by the tree's canopy ---
                # Tree.full_y is the top of the 180px tree image.
                # If the present's bottom is above the tree's collision rect top, it's visually behind the trunk.
                # If the present's body is too high (close to tree's full_y), it's visually in the canopy.

                # Use the tree's full visual top to prevent present from being visually embedded in the canopy
                tree_full_top = tree.full_y

                # If the present's top edge is above the halfway point of the tree image,
                # it's likely too far into the canopy. Let's use a simpler rule:
                # The present's bottom should be below the top of the tree's collision rect (trunk).
                if body.bottom < tree.rect.top:
                    blocked = True

                if blocked:
                    continue

                # Valid → place present
                new_present = Present(px, py)
                presents.append(new_present)
                solids.append(new_present)
                placed += 1

        return presents


# --- Game Helper Functions (unchanged) ---
# ... Game Helper Functions (unchanged) ...
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


def line_blocked_by_walls(p1, p2, walls):
    """Returns True if any wall blocks a line between p1 and p2."""
    for wall in walls:
        if wall.rect.clipline(p1, p2):
            return True
    return False

def play_music(track):
    global current_track
    if current_track == track:
        return
    current_track = track
    pygame.mixer.music.load(track)
    pygame.mixer.music.play(-1)


# --- Main Game Execution (REVISED FOR Z-ORDERING) ---
def run_game():
    """Initializes Pygame, sets up objects, and runs the main game loop."""
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pygame Stealth Game")

    clock = pygame.time.Clock()
    collect_sound = pygame.mixer.Sound("present_collected.mp3")

    ui_font = pygame.font.Font(None, 24)
    game_over_font = pygame.font.Font(None, 72)

    global score
    score = 0
    game_state = 'PLAYING'
    kickout_timer = 0

    LEVELS = {
        "level1": {
            "walls": [Wall(0, 0, 1280, 20),
                      Wall(0, 0, 20, 720),
                      Wall(0, 700, 1280, 20),
                      Wall(1260, 0, 20, 720),

                      Wall(0, 350, 180, 20),
                      Wall(300, 350, 220, 20),
                      Wall(520, 350, 20, 100),
                      Wall(520, 600, 20, 200),

                      Wall(780, 0, 20, 500)
                      ],
            "enemy_areas": [(270, 400, 200, 200),
                            (810, 300, 440, 300)],

            "tree_areas": [(30, 380, 150, 310),
                           (30, 30, 500, 170),
                           (810, 30, 440, 300)]},

        "level2": {
            "walls": [Wall(0, 0, 1280, 20),
                      Wall(0, 0, 20, 720),
                      Wall(0, 700, 1280, 20),
                      Wall(1260, 0, 20, 720),

                      Wall(655, 150, 20, 400),
                      Wall(300, 340, 700, 20),
                      Wall(0, 340, 150, 20),
                      Wall(1150, 340, 200, 20)
                      ],
            "enemy_areas": [(380, 30, 150, 300),
                            (850, 30, 150, 300),
                            (900, 400, 200, 200),
                            (200, 400, 200, 200)
                            ],
            "tree_areas": [(30, 30, 130, 300),
                           (1120, 30, 130, 300),
                           (30, 520, 130, 170),
                           (1120, 520, 130, 170)]}
    }

    def load_random_level():
        key = random.choice(list(LEVELS.keys()))
        data = LEVELS[key]

        return Level(
            walls=data["walls"],
            enemy_spawn_areas=data["enemy_areas"],
            tree_spawn_areas=data["tree_areas"],
            num_enemies=3,
            num_presents=8,  # example number; adjust per level by changing LEVELS if desired
            num_trees=3
        )

    level = load_random_level()

    # Initialize Player
    player = Player(level.player_spawn_x, level.player_spawn_y)

    # For LOS and collision, treat walls + trees as blockers
    walls_for_los = level.walls + level.trees
    walls_render = level.walls
    trees = level.trees

    enemies = level.enemies
    present_objects = level.presents

    door_ready_to_exit = False

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

        if game_state == 'PLAYING':
            player.handle_input_and_set_state(keys)

        # --- Update All Objects ---
        if game_state == 'PLAYING':
            # adds in music here
            play_music("inside_music.mp3")

            # Solids that *don't* move (Walls, Trees, Presents)
            static_solids = walls_for_los + present_objects  # walls_for_los already includes trees

            # ALL_OBSTACLES is the complete list of objects any moving entity should check against
            ALL_OBSTACLES = static_solids + enemies

            # 1. Update Player (pass ALL_OBSTACLES for movement collision, and walls_for_los for LOS check)
            player.update(enemies, ALL_OBSTACLES, walls_for_los)

            door_ready_to_exit = level.check_door_proximity(player)

            # 2. Update and check present collection
            if e_pressed:
                overlapping_presents = [p for p in present_objects if p.check_interaction_proximity(player)]
                if overlapping_presents:
                    # choose the closest present to player's center
                    chosen = min(overlapping_presents, key=lambda p: player.get_distance(p))
                    # ensure not blocked by walls (trees + walls)
                    if not line_blocked_by_walls(player.rect.center, chosen.rect.center, walls_for_los):
                        for p in overlapping_presents:
                            if p is not chosen:
                                p.cancel_collection()
                        chosen.start_collection()

            for present in present_objects:
                present.update(player)
                if present.is_collected:
                    collect_sound.play()
                    score += PRESENT_COLLECTION_VALUE
                    print(f"Score increased! New Score: {score}")

            # Player uses the exit door
            if door_ready_to_exit and e_pressed:  # Check for proximity AND 'E' press
                game_state = 'OUTSIDE'
                # finish the frame early to avoid using corrupted input later
                screen.fill((255, 255, 255))
                msg = game_over_font.render("OUTSIDE", True, (0, 0, 0))
                screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - msg.get_height() // 2))
                pygame.display.flip()
                pygame.event.clear()
                continue

            # Remove collected presents
            present_objects = [p for p in present_objects if not p.is_collected]

            # 3. Update enemies
            for enemy in enemies:
                # Enemies collide with ALL_OBSTACLES (Walls, Trees, Presents, other Enemies)
                enemy.update(ALL_OBSTACLES, player)

        # --- Rendering (REVISED FOR Z-ORDERING) ---
        screen.fill(COLORS['FLOOR_COLOR'])

        if game_state == 'PLAYING':
            # 1. Draw non-sorted objects (Walls, Door)
            for wall in walls_render:
                wall.render(screen)
            pygame.draw.rect(screen, (255,228,196), level.door)

            if door_ready_to_exit:
                level.render_door_ui(screen, ui_font)

            # 2. Prepare for depth sorting (Z-ordering)
            all_render_objects = (
                    [player] +
                    enemies +
                    present_objects +
                    trees
            )

            # Sort by the bottom edge of the collision box. Objects with smaller rect.bottom are drawn first ("further back").
            all_render_objects.sort(key=lambda obj: obj.rect.bottom)

            # 3. Draw sorted objects
            for obj in all_render_objects:
                if isinstance(obj, Player):
                    obj.render(screen)
                elif isinstance(obj, Enemy):
                    # Enemy needs walls_for_los for the sight cone calculation
                    obj.render(screen, walls_for_los)
                elif isinstance(obj, Tree):
                    # Tree is rendered, which includes the full 180px image
                    obj.render(screen)
                    # Draw the debug spawn range circle *over* the tree.
                    obj.render_spawn_range(screen)
                elif isinstance(obj, Present):
                    # Present needs player for interaction UI
                    obj.render(screen, player)

                    # DEBUG: boxes (delete later)
            for enemy in enemies:
                pygame.draw.rect(screen, COLORS['RED'], enemy.rect, 1)
            pygame.draw.rect(screen, COLORS['YELLOW'], player.rect, 1)

            # Debug outlines for spawn areas
            for area in level.enemy_spawn_areas:
                pygame.draw.rect(screen, COLORS['WHITE'], pygame.Rect(area), 1)
            for area in level.tree_spawn_areas:
                pygame.draw.rect(screen, COLORS['YELLOW'], pygame.Rect(area), 1)

            # Draw score UI
            score_text = ui_font.render(f"Presents Collected: {score}", True, COLORS['WHITE'])
            screen.blit(score_text, (10, 10))

        elif game_state == 'CAUGHT':
            #ADD MUSIC SOUND EFFECT
            play_music("player_caught.mp3")
            # Draw black screen during kickout timer
            pygame.draw.rect(screen, COLORS['BLACK'], (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 0)

            msg = game_over_font.render("CAUGHT! KICKED OUT.", True, COLORS['RED'])
            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - msg.get_height() // 2))

            kickout_timer -= 1
            if kickout_timer <= 0:
                game_state = 'OUTSIDE'
                print("--- RESUMING GAME ---")

        elif game_state == 'OUTSIDE':
            #ADD MUSIC
            play_music("outside_music.mp3")

            screen.fill((255, 255, 255))  # white background

            msg = game_over_font.render("OUTSIDE", True, (0, 0, 0))
            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - msg.get_height() // 2))
            pygame.display.update()
            pygame.event.clear()

        elif game_state == 'GAME_OVER':
            pygame.draw.rect(screen, COLORS['BLACK'], (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 0)
            play_music("game-over.mp3")
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