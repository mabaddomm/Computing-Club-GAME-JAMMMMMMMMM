"""Christmas Interior - stealth minigame scene with presents to collect"""

import pygame
import random
from game import Scene
from game_objects import Enemy, Present, Wall


class ChristmasInterior(Scene):
    """Interior scene with stealth gameplay and present collection"""
    
    def __init__(self, name="Christmas Interior", level=None):
        super().__init__(name)
        self.background_color = (50, 50, 50)  # Dark grey background
        self.level = level  # Reference to parent level for tracking presents
        
        # Game state
        self.player = None
        self.enemies = []
        self.presents = []
        self.walls = []
        self.is_kickout_active = False
        self.kickout_timer = 0
        self.kickout_duration = 120  # 2 seconds at 60 FPS
        self.game_over_timer = 0
        self.game_over_duration = 180  # 3 seconds at 60 FPS
        self.game_over_active = False
        
        # Player spawn position (will be set when player is added)
        self.player_start_x = 640
        self.player_start_y = 640
        
        # Setup the interior layout
        self._setup_layout()
    
    def _setup_layout(self):
        """Create walls, enemies, and presents for the interior"""
        # Create room-dividing walls
        self.walls = [
            # Horizontal barrier near top
            Wall(50, 100, 700, 20),
            # Vertical room divider in middle
            Wall(640 - 10, 150, 20, 350),
            # Small corner wall
            Wall(600, 450, 100, 100)
        ]
        
        # Add walls to scene
        for wall in self.walls:
            self.add_game_object(wall)
        
        # Create enemies (2 patrolling guards)
        enemy1 = Enemy(960, 180, speed=80)
        enemy2 = Enemy(640 - 100, 540, speed=80)
        
        self.enemies = [enemy1, enemy2]
        for enemy in self.enemies:
            self.add_game_object(enemy)
        
        # Spawn presents randomly (avoiding walls)
        self._spawn_presents(5)
    
    def _is_valid_spawn_location(self, rect, interaction_rect):
        """Check if a location is valid for spawning (not overlapping obstacles)
        
        Args:
            rect: Body rect of the object
            interaction_rect: Interaction zone rect (for presents)
            
        Returns:
            True if valid, False otherwise
        """
        # Check screen bounds
        if not (0 < rect.left and rect.right < 1280 and 
                0 < rect.top and rect.bottom < 720):
            return False
        
        # Check collision with walls
        for wall in self.walls:
            if rect.colliderect(wall.rect) or interaction_rect.colliderect(wall.rect):
                return False
        
        # Check collision with other presents
        for present in self.presents:
            if rect.colliderect(present.rect) or interaction_rect.colliderect(present.rect):
                return False
        
        return True
    
    def _spawn_presents(self, count):
        """Spawn presents in random valid locations
        
        Args:
            count: Number of presents to spawn
        """
        attempts = 0
        max_attempts = 100
        
        while len(self.presents) < count and attempts < max_attempts:
            # Random position
            x = random.randint(50, 1280 - 50)
            y = random.randint(50, 720 - 50)
            
            temp_present = Present(x, y)
            
            # Check if location is valid
            if self._is_valid_spawn_location(temp_present.rect, temp_present.interaction_rect):
                self.presents.append(temp_present)
                self.add_game_object(temp_present)
            
            attempts += 1
        
        print(f"Spawned {len(self.presents)} presents in Christmas Interior")
    
    def set_player(self, player):
        """Set the player for this interior
        
        Args:
            player: Player game object
        """
        self.player = player
        
        # Add player to scene if not already added
        if player not in self.game_objects:
            self.add_game_object(player)
        
        # Store spawn position
        self.player_start_x = player.x
        self.player_start_y = player.y
    
    def update(self, dt):
        """Update interior logic including stealth mechanics"""
        # Handle game over state
        if self.game_over_active:
            self.game_over_timer -= 1
            if self.game_over_timer <= 0:
                print("🔄 Restarting game...")
                if self.level:
                    self.level.restart_game()
            return  # Don't update game during game over
        
        # Handle kickout state
        if self.is_kickout_active:
            self.kickout_timer -= 1
            if self.kickout_timer <= 0:
                # Reset player
                if self.player:
                    self.player.reset_for_new_round(self.player_start_x, self.player_start_y)
                self.is_kickout_active = False
            return  # Don't update game during kickout
        
        # Handle player input
        if self.player:
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
            
            # Boost player velocity in debug mode (after input is processed)
            if self.level and hasattr(self.level, 'debug_mode') and self.level.debug_mode:
                self.player.velocity_x *= 3  # 3x speed in debug mode
                self.player.velocity_y *= 3
        
        # Get all solid obstacles (walls + presents that haven't been collected)
        solid_obstacles = self.walls + [p for p in self.presents if not p.is_collected]
        
        # Update player
        if self.player:
            self.player.update(dt)
            
            # Check collisions
            if self.player.check_collision([obj.rect for obj in solid_obstacles]):
                self.player.resolve_collision([obj.rect for obj in solid_obstacles], dt)
            
            # Check if caught by enemy sight
            if self.player.lives > 0 and not self.player.is_caught:
                for enemy in self.enemies:
                    if enemy.is_player_detected(self.player, self.walls):
                        if self.player.got_caught():
                            self._trigger_kickout()
            
            # Check physical collision with enemies using collision_rect
            for enemy in self.enemies:
                if self.player.collision_rect.colliderect(enemy.rect):
                    if self.player.lose_life():
                        # Push player away
                        push_factor = 40
                        direction_x = self.player.rect.centerx - enemy.rect.centerx
                        direction_y = self.player.rect.centery - enemy.rect.centery
                        distance = ((direction_x ** 2) + (direction_y ** 2)) ** 0.5
                        
                        if distance > 0:
                            self.player.x += direction_x / distance * push_factor
                            self.player.y += direction_y / distance * push_factor
                            self.player.rect.x = int(self.player.x)
                            self.player.rect.y = int(self.player.y)
        
        # Update presents
        for present in self.presents:
            if not present.is_collected and self.player:
                present.update(dt, self.player)
                
                # Check if just collected
                if present.is_collected:
                    print(f"Present collected! Notifying level...")
                    # Notify level of collection
                    if self.level:
                        self.level.collect_present()
        
        # Remove collected presents
        self.presents = [p for p in self.presents if not p.is_collected]
        
        # Update enemies (with all solid obstacles)
        all_obstacles = solid_obstacles + self.enemies
        for enemy in self.enemies:
            enemy.update(dt, all_obstacles)
        
        # Update UI elements
        for ui in self.ui_elements:
            if ui.active:
                ui.update(dt)
    
    def _trigger_kickout(self):
        """Trigger the kickout state (caught by enemy)"""
        if self.player and self.player.lives <= 0:
            # Game over - player has no lives left
            print("💀 GAME OVER! Out of lives!")
            self.game_over_active = True
            self.game_over_timer = self.game_over_duration
        else:
            # Kickout state
            self.is_kickout_active = True
            self.kickout_timer = self.kickout_duration
    
    def handle_event(self, event):
        """Handle events like E key for collecting presents
        
        Args:
            event: pygame.Event
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e and self.player:
                # Check if player is near any present
                for present in self.presents:
                    if not present.is_collected and present.check_interaction_proximity(self.player):
                        present.start_collection()
        
        # Pass to parent
        super().handle_event(event)
    
    def render(self, screen, debug=False):
        """Render the interior scene
        
        Args:
            screen: Pygame screen surface
            debug: If True, render debug info
        """
        # Handle game over rendering
        if self.game_over_active:
            # Black screen during game over
            screen.fill((0, 0, 0))
            font_large = pygame.font.Font(None, 72)
            font_small = pygame.font.Font(None, 48)
            
            msg1 = font_large.render("GAME OVER", True, (255, 0, 0))
            msg2 = font_small.render("You ran out of lives", True, (255, 255, 255))
            
            screen.blit(msg1, (640 - msg1.get_width() // 2, 300))
            screen.blit(msg2, (640 - msg2.get_width() // 2, 380))
            return
        
        # Handle kickout rendering
        if self.is_kickout_active:
            # Black screen during kickout
            screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 72)
            msg = font.render("CAUGHT! KICKED OUT.", True, (255, 0, 0))
            screen.blit(msg, (640 - msg.get_width() // 2, 360 - msg.get_height() // 2))
            return
        
        # Normal rendering
        screen.fill(self.background_color)
        
        # Render walls
        for wall in self.walls:
            if wall.visible:
                wall.render(screen)
        
        # Render presents (with player reference)
        for present in self.presents:
            if present.visible and not present.is_collected and self.player:
                present.render(screen, self.player)
        
        # Render enemies (with walls for sight cone clipping)
        for enemy in self.enemies:
            if enemy.visible:
                enemy.render(screen, self.walls, debug=debug)
        
        # Render player
        if self.player and self.player.visible:
            self.player.render(screen, debug=debug)
            
            # Show lives
            if debug:
                font = pygame.font.Font(None, 24)
                lives_text = font.render(f"Lives: {self.player.lives}", True, (255, 255, 0))
                screen.blit(lives_text, (10, 10))
        
        # Debug: draw enemy collision boxes (player hitboxes are drawn in player.render())
        if debug:
            for enemy in self.enemies:
                pygame.draw.rect(screen, (255, 0, 0), enemy.rect, 1)
        
        # Render UI elements
        for ui in self.ui_elements:
            if ui.visible:
                ui.render(screen)

