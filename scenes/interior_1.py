"""Interior_1 - Advanced stealth interior with procedural spawning"""

import pygame
import random
import math
from game import Scene
from game_objects import Wall, Child, Present, Tree
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


# Constants for tree and present spawning
TREE_WIDTH = 140
TREE_HEIGHT = 180
PRESENT_SIZE = 40
TREE_MARGIN = 40
TREE_MIN_RADIUS = max(TREE_WIDTH, TREE_HEIGHT) // 6 + TREE_MARGIN  # ~130px
TREE_MAX_RADIUS = TREE_MIN_RADIUS + 30  # ~160px
TREE_MIN_SEPARATION = 30


class Interior_1(Scene):
    """Advanced interior scene with procedural enemy, tree, and present spawning"""
    
    def __init__(self, walls, enemy_spawn_areas, tree_spawn_areas, 
                 num_enemies, num_presents, num_trees, level=None, name="Interior 1"):
        """Initialize Interior_1 with spawn configuration
        
        Args:
            walls: List of Wall objects
            enemy_spawn_areas: List of (x, y, w, h) tuples for enemy spawn zones
            tree_spawn_areas: List of (x, y, w, h) tuples for tree spawn zones
            num_enemies: Number of enemies to spawn
            num_presents: Target number of presents (will spawn around trees)
            num_trees: Number of trees to spawn
            level: Reference to parent level for tracking state
            name: Scene name
        """
        super().__init__(name)
        self.level = level
        self.background_color = (50, 50, 50)  # Dark grey
        
        # Store spawn configuration
        self.walls = walls
        self.enemy_spawn_areas = enemy_spawn_areas
        self.tree_spawn_areas = tree_spawn_areas
        self.num_enemies = num_enemies
        self.num_presents = num_presents
        self.num_trees = num_trees
        
        # Player spawn and door
        self.player_spawn = (630, 550)
        self.door = pygame.Rect(640, 695, 50, 30)
        
        # Game state
        self.game_state = 'PLAYING'  # PLAYING, CAUGHT, GAME_OVER, OUTSIDE
        self.kickout_timer = 0
        self.kickout_duration = 120  # 2 seconds at 60 FPS
        self.game_over_timer = 0
        self.game_over_duration = 180  # 3 seconds at 60 FPS
        
        # Player reference
        self.player = None
        
        # Game objects (will be populated by spawning)
        self.enemies = []
        self.trees = []
        self.presents = []
        
        # Add walls to scene
        for wall in self.walls:
            self.add_game_object(wall)
        
        # Spawn trees first (they define where presents go)
        self.trees = self.spawn_trees()
        for tree in self.trees:
            self.add_game_object(tree)
        
        # Spawn enemies (don't add to game_objects - we'll update them manually)
        self.enemies = self.spawn_enemies()
        
        # Spawn presents around trees (don't add to game_objects - we'll update them manually)
        self.presents = self.spawn_presents_around_trees()
        
        print(f"🏠 Interior_1 created: {len(self.enemies)} enemies, {len(self.trees)} trees, {len(self.presents)} presents")
    
    def set_player(self, player):
        """Set the player for this interior
        
        Args:
            player: Player object
        """
        self.player = player
        if self.player:
            # Reset player to spawn position
            self.player.reset_for_new_round(self.player_spawn[0], self.player_spawn[1])
            # Add player to game objects
            self.add_game_object(self.player)
    
    def random_point_in_area(self, area, obj_width, obj_height, margin=0):
        """Get a random point within a spawn area
        
        Args:
            area: (x, y, w, h) tuple defining the spawn area
            obj_width: Width of object to spawn
            obj_height: Height of object to spawn
            margin: Safety margin from edges
            
        Returns:
            (px, py) tuple or None if area is too small
        """
        x, y, w, h = area
        min_x = x + margin
        min_y = y + margin
        max_x = x + w - obj_width - margin
        max_y = y + h - obj_height - margin
        
        if max_x < min_x or max_y < min_y:
            return None
        
        px = random.randint(min_x, max_x)
        py = random.randint(min_y, max_y)
        return (px, py)
    
    def spawn_enemies(self):
        """Spawn Child enemies in designated spawn areas
        
        Returns:
            List of Child enemy objects
        """
        enemies = []
        for _ in range(self.num_enemies):
            area = random.choice(self.enemy_spawn_areas)
            pt = self.random_point_in_area(area, Child.CHILD_WIDTH, Child.CHILD_HEIGHT, margin=8)
            if pt:
                px, py = pt
                enemies.append(Child(px, py, speed=100))
        
        print(f"👶 Spawned {len(enemies)} Child enemies")
        return enemies
    
    def spawn_trees(self):
        """Spawn trees in designated areas with minimum separation
        
        Returns:
            List of Tree objects
        """
        trees = []
        solids_for_trees = list(self.walls)
        attempts_per_tree = 200
        
        for _ in range(self.num_trees):
            success = False
            for _attempt in range(attempts_per_tree):
                area = random.choice(self.tree_spawn_areas)
                pt = self.random_point_in_area(area, TREE_WIDTH, TREE_HEIGHT, margin=8)
                
                if pt is None:
                    continue
                
                px, py = pt
                candidate = Tree(px, py)
                
                # Create inflated rect for minimum separation check
                candidate_buffer_rect = candidate.rect.inflate(
                    TREE_MIN_SEPARATION * 2,
                    TREE_MIN_SEPARATION * 2
                )
                
                # Check overlap with existing solids
                overlap = False
                for solid in solids_for_trees:
                    if isinstance(solid, Tree):
                        # Check trees with buffer
                        if candidate_buffer_rect.colliderect(solid.rect):
                            overlap = True
                            break
                    else:
                        # Check walls normally
                        if candidate.rect.colliderect(solid.rect):
                            overlap = True
                            break
                
                if not overlap:
                    trees.append(candidate)
                    solids_for_trees.append(candidate)
                    success = True
                    break
            
            if not success:
                print(f"⚠️ Could not place tree after {attempts_per_tree} attempts")
        
        print(f"🎄 Spawned {len(trees)} trees")
        return trees
    
    def spawn_presents_around_trees(self):
        """Spawn presents in a radius around each tree
        
        Returns:
            List of Present objects
        """
        presents = []
        if not self.trees:
            print("⚠️ No trees to spawn presents around")
            return presents
        
        solids = list(self.walls) + list(self.trees)
        
        for tree in self.trees:
            # Spawn 1-4 presents per tree
            presents_for_this_tree = random.randint(1, 4)
            attempts = 300
            placed = 0
            
            tree_center = tree.get_full_sprite_center()
            
            while placed < presents_for_this_tree and attempts > 0:
                attempts -= 1
                
                # Random angle and radius
                angle = random.random() * math.pi * 2
                radius = random.randint(TREE_MIN_RADIUS, TREE_MAX_RADIUS)
                
                cx = tree_center[0] + int(radius * math.cos(angle))
                cy = tree_center[1] + int(radius * math.sin(angle))
                
                px = cx - PRESENT_SIZE // 2
                py = cy - PRESENT_SIZE // 2
                
                body = pygame.Rect(px, py, PRESENT_SIZE, PRESENT_SIZE)
                
                # Interaction bubble check
                interaction = pygame.Rect(0, 0, 90, 90)
                interaction.center = body.center
                
                # Must be fully on screen
                if not (0 < body.left and body.right < SCREEN_WIDTH and
                        0 < body.top and body.bottom < SCREEN_HEIGHT):
                    continue
                
                # Must not overlap walls, trees, or existing presents
                blocked = False
                for solid in solids:
                    if body.colliderect(solid.rect) or interaction.colliderect(solid.rect):
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
                
                # Prevent presents from being visually hidden by tree canopy
                if body.bottom < tree.rect.top:
                    blocked = True
                
                if blocked:
                    continue
                
                # Valid placement
                new_present = Present(px, py)
                presents.append(new_present)
                solids.append(new_present)
                placed += 1
        
        print(f"🎁 Spawned {len(presents)} presents around trees")
        return presents
    
    def handle_event(self, event):
        """Handle scene-specific events
        
        Args:
            event: Pygame event
        """
        if self.game_state != 'PLAYING':
            return
        
        # Handle E key for present collection
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e and self.player:
            # Find presents in range
            overlapping_presents = [
                p for p in self.presents 
                if p.check_interaction_proximity(self.player) and not p.is_collected
            ]
            
            if overlapping_presents:
                # Choose closest present
                chosen = min(overlapping_presents, key=lambda p: self.player.get_distance(p))
                
                # Check line of sight (not blocked by walls/trees)
                walls_for_los = self.walls + self.trees
                blocked = False
                for wall in walls_for_los:
                    if wall.rect.clipline(self.player.rect.center, chosen.rect.center):
                        blocked = True
                        break
                
                if not blocked:
                    # Cancel other collections
                    for p in overlapping_presents:
                        if p is not chosen:
                            p.cancel_collection()
                    
                    # Start collection
                    chosen.start_collection()
    
    def update(self, dt):
        """Update interior logic
        
        Args:
            dt: Delta time in seconds
        """
        if self.game_state == 'PLAYING':
            # Handle player input
            if self.player:
                keys = pygame.key.get_pressed()
                self.player.handle_input(keys)
                
                # Boost player velocity in debug mode (after input is processed)
                if self.level and hasattr(self.level, 'debug_mode') and self.level.debug_mode:
                    self.player.velocity_x *= 3  # 3x speed in debug mode
                    self.player.velocity_y *= 3
            
            # Update all presents
            for present in self.presents:
                if not present.is_collected:
                    present.update(dt, self.player if self.player else None)
                    
                    # Check if collected
                    if present.is_collected and self.level:
                        self.level.collect_present()
                        print(f"✅ Present collected!")
            
            # Remove collected presents
            self.presents = [p for p in self.presents if not p.is_collected]
            
            # Build solids list for collision
            walls_for_los = self.walls + self.trees
            static_solids = walls_for_los + self.presents
            all_obstacles = static_solids + self.enemies
            
            # Update player
            if self.player:
                # Check if caught by any enemy
                if not self.player.is_caught:
                    for enemy in self.enemies:
                        if enemy.is_player_detected(self.player, walls_for_los):
                            if self.player.got_caught():
                                # Check if player is out of lives
                                if self.player.lives <= 0:
                                    print("💀 GAME OVER! Out of lives!")
                                    self.game_state = 'GAME_OVER'
                                    self.game_over_timer = self.game_over_duration
                                else:
                                    print("🚨 PLAYER CAUGHT!")
                                    self.game_state = 'CAUGHT'
                                    self.kickout_timer = self.kickout_duration
                
                # Check door collision
                if self.player.rect.colliderect(self.door):
                    print("🚪 Player reached door - exiting interior")
                    self.game_state = 'OUTSIDE'
                    if self.level:
                        self.level.exit_interior()
                    return
            
            # Update enemies
            for enemy in self.enemies:
                enemy.update(dt, all_obstacles)
        
        elif self.game_state == 'CAUGHT':
            # Countdown kickout timer
            self.kickout_timer -= 1
            if self.kickout_timer <= 0:
                print("⏱️ Kickout complete - returning to outdoor scene")
                if self.level:
                    self.level.exit_interior()
                self.game_state = 'OUTSIDE'
        
        elif self.game_state == 'GAME_OVER':
            # Countdown game over timer
            self.game_over_timer -= 1
            if self.game_over_timer <= 0:
                print("🔄 Restarting game...")
                if self.level:
                    # Restart the game by resetting the level
                    self.level.restart_game()
        
        # Always update base scene
        super().update(dt)
    
    def render(self, screen):
        """Render interior with Z-ordering
        
        Args:
            screen: Pygame screen surface
        """
        # Fill background
        screen.fill(self.background_color)
        
        if self.game_state == 'PLAYING':
            # Render walls
            for wall in self.walls:
                wall.render(screen)
            
            # Render door
            pygame.draw.rect(screen, (0, 0, 255), self.door)
            
            # Z-ordering: Sort all objects by rect.bottom
            render_objects = []
            if self.player:
                render_objects.append(self.player)
            render_objects.extend(self.enemies)
            render_objects.extend(self.presents)
            render_objects.extend(self.trees)
            
            render_objects.sort(key=lambda obj: obj.rect.bottom)
            
            # Render sorted objects
            walls_for_los = self.walls + self.trees
            for obj in render_objects:
                if isinstance(obj, Child):
                    obj.render(screen, walls_for_los)
                elif isinstance(obj, Present):
                    obj.render(screen, self.player if self.player else obj)
                elif isinstance(obj, Tree):
                    obj.render(screen)
                else:
                    obj.render(screen)
        
        elif self.game_state == 'CAUGHT':
            # Draw black screen with message
            pygame.draw.rect(screen, (0, 0, 0), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            
            font = pygame.font.Font(None, 72)
            msg = font.render("CAUGHT! KICKED OUT.", True, (255, 0, 0))
            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, 
                            SCREEN_HEIGHT // 2 - msg.get_height() // 2))
        
        elif self.game_state == 'GAME_OVER':
            # Draw black screen with game over message
            pygame.draw.rect(screen, (0, 0, 0), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            
            font_large = pygame.font.Font(None, 72)
            font_small = pygame.font.Font(None, 48)
            
            msg1 = font_large.render("GAME OVER", True, (255, 0, 0))
            msg2 = font_small.render("You ran out of lives", True, (255, 255, 255))
            
            screen.blit(msg1, (SCREEN_WIDTH // 2 - msg1.get_width() // 2, 
                              SCREEN_HEIGHT // 2 - 60))
            screen.blit(msg2, (SCREEN_WIDTH // 2 - msg2.get_width() // 2, 
                              SCREEN_HEIGHT // 2 + 20))

