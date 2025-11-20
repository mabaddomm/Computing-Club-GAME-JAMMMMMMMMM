"""Ending scene - Final special chunk where Grinch returns presents to children"""

import pygame
import random
from game import Scene
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from game_objects import PassiveChild, StaticPresent
from utils.audio import play_music


# Child positions based on singing_tree_childrenblocks.png
# Positions arranged in a circle around the singing tree
# Circle is positioned 150 pixels above the bottom of the screen (720 - 150 = 570)
CHILD_POSITIONS = {
    # Format: (x, y, direction) - direction faces toward center
    # Circle center: (640, 470), radius: ~100 pixels
    
    # Top arc (facing down toward center)
    'child_1': (490, 380, 'down'),
    'child_2': (560, 360, 'down'),
    'child_3': (640, 350, 'down'),
    'child_4': (720, 360, 'down'),
    'child_5': (790, 380, 'down'),
    
    # Right arc (facing left toward center)
    'child_6': (860, 430, 'left'),
    'child_7': (900, 470, 'left'),
    'child_8': (860, 510, 'left'),
    
    # Bottom arc (facing up toward center)
    'child_9': (790, 560, 'up'),
    'child_10': (720, 580, 'up'),
    'child_11': (640, 590, 'up'),
    'child_12': (560, 580, 'up'),
    'child_13': (490, 560, 'up'),
    
    # Left arc (facing right toward center)
    'child_14': (420, 510, 'right'),
    'child_15': (380, 470, 'right'),
    'child_16': (420, 430, 'right'),
    
    # Additional positions to complete circle (18 total)
    'child_17': (540, 410, 'down'),
    'child_18': (740, 410, 'down'),
}


class EndingScene(Scene):
    """Special ending scene with CPU-controlled player and present spawning"""
    
    def __init__(self, player, name="Ending Scene"):
        """Initialize the ending scene
        
        Args:
            player: Player object to control via CPU
            name: Scene name
        """
        super().__init__(name)
        
        # Background
        self.background_color = (240, 250, 255)  # Light winter blue
        self.background_image = self._load_background()
        
        # Player (CPU controlled)
        self.player = player
        self.cpu_control_active = True
        self.player_movement_timer = 0
        self.player_movement_duration = 1.0  # Walk for 1 second
        self.player_stopped = False
        
        # Player spawns on right side
        self.player.x = SCREEN_WIDTH - 150
        self.player.y = SCREEN_HEIGHT // 2
        self.player.velocity_x = -75  # Half of 150 speed (half of normal)
        self.player.velocity_y = 0
        self.player.set_state('walk_left')
        
        # Add player to scene
        self.add_game_object(self.player)
        
        # Create passive children
        self.children = []
        self._create_children()
        
        # Present spawning
        self.presents = []
        self.present_spawn_timer = 0
        self.present_spawn_delay = 10.0  # Wait 10 seconds after player stops
        self.present_spawn_started = False
        self.present_spawn_interval = 0.5  # Spawn a present every 0.5 seconds
        self.present_spawn_counter = 0
        self.max_presents = 20  # Total presents to spawn
        
        print("🎄 ENDING SCENE LOADED - The Grinch returns!")
    
    def _load_background(self):
        """Load the singing tree background
        
        Returns:
            pygame.Surface or None: Background image
        """
        try:
            bg = pygame.image.load('assets/singing_tree.png').convert_alpha()
            # Scale to screen size
            bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            print("✅ Singing tree background loaded")
            return bg
        except pygame.error as e:
            print(f"⚠️ Error loading singing tree background: {e}")
            return None
    
    def _create_children(self):
        """Create passive children at predefined positions"""
        for child_id, (x, y, direction) in CHILD_POSITIONS.items():
            child = PassiveChild(x, y, direction)
            self.children.append(child)
            self.add_game_object(child)
        
        print(f"👶 Created {len(self.children)} passive children")
    
    def update(self, dt):
        """Update the ending scene with CPU-controlled player and present spawning
        
        Args:
            dt: Delta time in seconds
        """
        # Play children singing music during ending
        play_music("assets/sounds/children_singing.mp3")
        
        # === Phase 1: CPU-controlled player movement ===
        if self.cpu_control_active and not self.player_stopped:
            self.player_movement_timer += dt
            
            if self.player_movement_timer >= self.player_movement_duration:
                # Stop the player
                self.player.velocity_x = 0
                self.player.velocity_y = 0
                self.player.set_state('idle_left')
                self.player_stopped = True
                print("🎅 Grinch stopped - preparing to return presents...")
        
        # === Phase 2: Wait before spawning presents ===
        if self.player_stopped and not self.present_spawn_started:
            self.present_spawn_timer += dt
            
            if self.present_spawn_timer >= self.present_spawn_delay:
                self.present_spawn_started = True
                print("🎁 Starting present spawning!")
        
        # === Phase 3: Spawn presents ===
        if self.present_spawn_started and len(self.presents) < self.max_presents:
            self.present_spawn_counter += dt
            
            if self.present_spawn_counter >= self.present_spawn_interval:
                self._spawn_present()
                self.present_spawn_counter = 0
        
        # Update all game objects
        for obj in self.game_objects:
            if obj.active:
                obj.update(dt)
        
        # Update presents
        for present in self.presents:
            if present.active:
                present.update(dt)
    
    def _spawn_present(self):
        """Spawn a present at a random location"""
        # Random position (avoid edges and center tree area)
        x = random.randint(100, SCREEN_WIDTH - 164)
        y = random.randint(100, SCREEN_HEIGHT - 164)
        
        # Avoid spawning in center tree area (rough estimate)
        if 450 < x < 830 and 220 < y < 500:
            # Move to side
            if x < SCREEN_WIDTH // 2:
                x = random.randint(100, 400)
            else:
                x = random.randint(880, SCREEN_WIDTH - 164)
        
        present = StaticPresent(x, y, size=64)
        self.presents.append(present)
        self.add_game_object(present)
        
        print(f"🎁 Spawned present #{len(self.presents)} at ({x}, {y})")
    
    def render(self, screen, debug=False):
        """Render the ending scene
        
        Args:
            screen: pygame screen surface
            debug: If True, show debug info
        """
        # Draw background
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill(self.background_color)
        
        # Sort game objects by y-position for depth (render bottom objects last)
        sorted_objects = sorted(
            [obj for obj in self.game_objects if obj.visible],
            key=lambda obj: obj.rect.bottom if hasattr(obj, 'rect') else obj.y
        )
        
        # Render all game objects (children, player, presents)
        for obj in sorted_objects:
            obj.render(screen, debug=debug)
        
        # Render presents separately if needed
        for present in self.presents:
            if present.visible:
                present.render(screen, debug=debug)
        
        # Debug info
        if debug:
            font = pygame.font.Font(None, 30)
            status = "Moving" if not self.player_stopped else "Stopped"
            spawn_status = f"Spawning ({len(self.presents)}/{self.max_presents})" if self.present_spawn_started else "Waiting"
            
            debug_text = font.render(f"Player: {status} | Presents: {spawn_status}", True, (255, 255, 0))
            screen.blit(debug_text, (10, 10))
        
        # Render UI elements
        for ui in self.ui_elements:
            if ui.visible:
                ui.render(screen)
    
    def handle_event(self, event):
        """Handle events (disabled during ending scene)
        
        Args:
            event: pygame.Event
        """
        # No input during ending scene
        pass

