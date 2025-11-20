"""Christmas level - manages chunks and interiors for the Christmas game"""

import pygame
import random
import os
from game import Level
from scenes import Chunk, Interior, Interior_1
from game_objects import Player, Wall
from ui_elements import PresentCounter, LivesTracker
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, L1_PRESENT_ITEM_GOAL
from utils import play_music


class InteriorState:
    """Stores the state of an interior for persistence"""
    def __init__(self, level_num, enemy_positions, present_data, tree_positions):
        self.level_num = level_num  # Which level configuration (1-4)
        self.enemy_positions = enemy_positions  # List of (x, y) positions
        self.present_data = present_data  # List of {'x': x, 'y': y, 'collected': bool}
        self.tree_positions = tree_positions  # List of (x, y) positions


class ChristmasLevel(Level):
    """Level that manages procedurally generated chunks on an infinite grid"""
    
    def __init__(self):
        super().__init__("Christmas Level")
        
        # Map data - 8 basic winter templates + 1 goal chunk
        self.maps = {
            0: ["0_winter.png", "0_winter_top.png", "0_walls.png"],
            1: ["1_winter.png", "1_winter_top.png", "1_walls.png"],
            2: ["2_winter.png", "2_winter_top.png", "2_walls.png"],
            3: ["3_winter.png", "3_winter_top.png", "3_walls.png"],
            4: ["4_winter.png", "4_winter_top.png", "4_walls.png"],
            5: ["5_winter.png", "5_winter_top.png", "5_walls.png"],
            6: ["6_winter.png", "6_winter_top.png", "6_walls.png"],
            7: ["7_winter.png", "7_winter_top.png", "7_walls.png"],
            8: ["0_winter.png", "0_winter_top.png", "0_walls.png"]  # Placeholder for goal chunk (using map 0 for now)
        }
        
        # Path configuration - defines which edges have paths for each map
        # True = has path on that edge, False = no path
        self.map_paths = {
            0: {'top': True, 'bottom': True, 'left': True, 'right': True},     # Crossroads
            1: {'top': True, 'bottom': True, 'left': False, 'right': False},   # Vertical path
            2: {'top': False, 'bottom': False, 'left': True, 'right': True},   # Horizontal path
            3: {'top': True, 'bottom': False, 'left': False, 'right': True},   # Top-right corner
            4: {'top': True, 'bottom': False, 'left': True, 'right': False},   # Top-left corner
            5: {'top': False, 'bottom': True, 'left': False, 'right': True},   # Bottom-right corner
            6: {'top': False, 'bottom': True, 'left': True, 'right': False},   # Bottom-left corner
            7: {'top': False, 'bottom': False, 'left': False, 'right': False}, # Dead end/clearing
            8: {'top': True, 'bottom': True, 'left': True, 'right': True}      # Goal chunk (crossroads - all directions)
        }
        
        # Chunk unlock status
        # Chunks 0-7 are unlocked by default (basic winter maps)
        # Chunk 8 is the ending scene (unlocks after collecting presents)
        self.chunk_unlocked = {
            0: True,
            1: True,
            2: True,
            3: True,
            4: True,
            5: True,
            6: True,
            7: True,
            8: False,  # Ending scene - The Grinch returns presents! (unlocks after collecting L1_PRESENT_ITEM_GOAL presents)
        }
        
        # Special/Unlockable chunks configuration
        # Format: chunk_id -> {unlock_requirements, accessible_from, path_config}
        self.special_chunks = {
            # Example: Boss/Goal chunk (ID 8)
            # 8: {
            #     'map_files': ["8_special.png", "8_special_top.png", "8_walls.png"],
            #     'accessible_from': [0],  # Only accessible from crossroads (map 0)
            #     'connection_direction': 'top',  # Can only be accessed from the top of map 0
            #     'paths': {'top': False, 'bottom': True, 'left': False, 'right': False}  # One-way entry
            # }
        }
        
        # Game state - present collection
        self.presents_collected = 0
        self.present_goal = L1_PRESENT_ITEM_GOAL  # Number of presents needed to unlock goal chunk
        
        # Valid neighbors based on path alignment
        # Only chunks with matching path edges can be neighbors
        self.valid_neighbors = self._build_valid_neighbors()
        
        # Procedural generation state
        self.generated_chunks = {}  # Dictionary mapping (x, y) -> map_id
        self.current_chunk_pos = (0, 0)  # Current chunk coordinates
        
        # Always start at (0, 0) with map 0
        self.generated_chunks[(0, 0)] = 0
        
        # Interior state
        self.current_interior = None
        self.is_in_interior = False
        self.door_entry_x = 0
        self.door_entry_y = 0
        self.door_entry_chunk_pos = (0, 0)
        
        # Interior persistence - store interior states by chunk coordinates
        # Format: {(chunk_x, chunk_y): InteriorState object}
        self.saved_interiors = {}
        
        # Debug mode
        self.debug_mode = False
        
        # Input tracking
        self.e_pressed = False
        
        # Audio
        try:
            self.collect_sound = pygame.mixer.Sound("assets/sounds/present_collected.mp3")
        except:
            print("⚠️ Could not load present collection sound")
            self.collect_sound = None
        
        # UI Elements list
        self.ui_elements = []
        
        # Create and add present counter UI
        self.present_counter = PresentCounter(
            x=SCREEN_WIDTH - 120,  # 100px width + 20px margin
            y=20,
            presents_collected=self.presents_collected,
            present_goal=self.present_goal
        )
        self.ui_elements.append(self.present_counter)
        
        # Create player
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, speed=150)
        
        # Create and add lives tracker UI
        self.lives_tracker = LivesTracker(
            x=20,  # Left side of screen
            y=20,  # Top of screen
            max_lives=3,
            icon_size=50,  # Small heart icons
            spacing=10
        )
        self.ui_elements.append(self.lives_tracker)
        
        # Create initial chunk at (0, 0)
        self.create_chunk(0, 0)
        
        # Track door entry state
        self.door_entry_x = 0
        self.door_entry_y = 0
        self.door_entry_chunk_pos = (0, 0)
    
    def collect_present(self):
        """Collect a present and check if goal chunk should be unlocked"""
        self.presents_collected += 1
        print(f"🎁 Present collected! ({self.presents_collected}/{self.present_goal})")
        
        # Update the UI counter
        self.present_counter.update_count(self.presents_collected, self.present_goal)
        
        # Check if we've reached the goal and should unlock the ending scene
        if self.presents_collected >= self.present_goal and not self.chunk_unlocked[8]:
            self.unlock_chunk(8)
            print(f"🎄✨ You've collected enough presents! The ENDING SCENE is now unlocked!")
            print(f"🎵 Listen... the children are singing!")
    
    def unlock_chunk(self, chunk_id):
        """Unlock a chunk, making it available for generation
        
        Args:
            chunk_id: ID of the chunk to unlock
        """
        if chunk_id not in self.chunk_unlocked:
            # Add new chunk to the unlocked dictionary
            self.chunk_unlocked[chunk_id] = True
            print(f"🎁 Unlocked new chunk: {chunk_id}!")
        elif not self.chunk_unlocked[chunk_id]:
            # Unlock previously locked chunk
            self.chunk_unlocked[chunk_id] = True
            print(f"🎁 Unlocked chunk: {chunk_id}!")
        else:
            print(f"Chunk {chunk_id} is already unlocked.")
    
    def _build_valid_neighbors(self):
        """Build valid neighbor mappings based on path alignment
        
        Returns:
            Dictionary mapping map_id -> {direction: [valid_map_ids]}
        """
        neighbors = {}
        
        # Include goal chunk (map 8) in the neighbor calculation
        for map_id in range(9):  # Changed from range(8) to range(9)
            neighbors[map_id] = {
                'top': [],
                'bottom': [],
                'left': [],
                'right': []
            }
            
            # For each direction, find maps that can connect
            for other_id in range(9):  # Changed from range(8) to range(9)
                # Don't allow same map as neighbor
                if map_id == other_id:
                    continue
                
                # Top neighbor: current map's top must match other's bottom
                if self.map_paths[map_id]['top'] == self.map_paths[other_id]['bottom']:
                    neighbors[map_id]['top'].append(other_id)
                
                # Bottom neighbor: current map's bottom must match other's top
                if self.map_paths[map_id]['bottom'] == self.map_paths[other_id]['top']:
                    neighbors[map_id]['bottom'].append(other_id)
                
                # Left neighbor: current map's left must match other's right
                if self.map_paths[map_id]['left'] == self.map_paths[other_id]['right']:
                    neighbors[map_id]['left'].append(other_id)
                
                # Right neighbor: current map's right must match other's left
                if self.map_paths[map_id]['right'] == self.map_paths[other_id]['left']:
                    neighbors[map_id]['right'].append(other_id)
        
        return neighbors
    
    def _get_neighbor_map(self, direction, adjacent_chunk_pos):
        """Get a valid map for a new chunk based on neighboring chunks
        
        Args:
            direction: Direction the player is entering from ('top', 'bottom', 'left', 'right')
            adjacent_chunk_pos: Position of the chunk we're coming from
        
        Returns:
            Valid map_id that aligns with existing neighbors
        """
        # Get the adjacent chunk's map_id
        if adjacent_chunk_pos not in self.generated_chunks:
            # No adjacent chunk, return random valid map with path in that direction
            valid_maps = []
            opposite_dir = {'top': 'bottom', 'bottom': 'top', 'left': 'right', 'right': 'left'}[direction]
            for map_id in range(8):
                if self.map_paths[map_id][opposite_dir]:  # Must have path on the entering edge
                    valid_maps.append(map_id)
            return random.choice(valid_maps) if valid_maps else 0
        
        adjacent_map_id = self.generated_chunks[adjacent_chunk_pos]
        
        # Get valid neighbors for the adjacent chunk in the opposite direction
        opposite_dir = {'top': 'bottom', 'bottom': 'top', 'left': 'right', 'right': 'left'}[direction]
        valid_maps = self.valid_neighbors[adjacent_map_id][opposite_dir]
        
        if not valid_maps:
            # Fallback: just ensure we have a path on the entering edge
            valid_maps = []
            for map_id in range(8):
                if map_id != adjacent_map_id and self.map_paths[map_id][opposite_dir]:
                    valid_maps.append(map_id)
            return random.choice(valid_maps) if valid_maps else 0
        
        return random.choice(valid_maps)
    
    def create_chunk(self, chunk_x, chunk_y):
        """Create and set up a chunk at the given coordinates
        
        Args:
            chunk_x: X coordinate of the chunk
            chunk_y: Y coordinate of the chunk
        """
        # Check if chunk already exists
        if (chunk_x, chunk_y) in self.generated_chunks:
            map_id = self.generated_chunks[(chunk_x, chunk_y)]
        else:
            # Generate new chunk based on neighboring chunks
            # Check all four neighbors to find valid maps
            # Start with all unlocked maps only (including ending scene if unlocked)
            valid_maps = set([map_id for map_id in range(9) if self.chunk_unlocked.get(map_id, False)])
            
            # Check top neighbor (y-1)
            top_neighbor = (chunk_x, chunk_y - 1)
            if top_neighbor in self.generated_chunks:
                top_id = self.generated_chunks[top_neighbor]
                # New chunk's top must align with neighbor's bottom
                valid_from_top = set(self.valid_neighbors[top_id]['bottom'])
                valid_maps &= valid_from_top
            
            # Check bottom neighbor (y+1)
            bottom_neighbor = (chunk_x, chunk_y + 1)
            if bottom_neighbor in self.generated_chunks:
                bottom_id = self.generated_chunks[bottom_neighbor]
                # New chunk's bottom must align with neighbor's top
                valid_from_bottom = set(self.valid_neighbors[bottom_id]['top'])
                valid_maps &= valid_from_bottom
            
            # Check left neighbor (x-1)
            left_neighbor = (chunk_x - 1, chunk_y)
            if left_neighbor in self.generated_chunks:
                left_id = self.generated_chunks[left_neighbor]
                # New chunk's left must align with neighbor's right
                valid_from_left = set(self.valid_neighbors[left_id]['right'])
                valid_maps &= valid_from_left
            
            # Check right neighbor (x+1)
            right_neighbor = (chunk_x + 1, chunk_y)
            if right_neighbor in self.generated_chunks:
                right_id = self.generated_chunks[right_neighbor]
                # New chunk's right must align with neighbor's left
                valid_from_right = set(self.valid_neighbors[right_id]['left'])
                valid_maps &= valid_from_right
            
            # If no valid maps, use map 0 as fallback (should always be unlocked)
            if not valid_maps:
                map_id = 0
                print(f"WARNING: No valid unlocked maps for ({chunk_x}, {chunk_y}), using map 0")
            else:
                map_id = random.choice(list(valid_maps))
            
            self.generated_chunks[(chunk_x, chunk_y)] = map_id
            if len(valid_maps) > 1:
                print(f"Generated chunk at ({chunk_x}, {chunk_y}) with map {map_id} (from {len(valid_maps)} unlocked options)")
            else:
                print(f"Generated chunk at ({chunk_x}, {chunk_y}) with map {map_id} (only unlocked option)")
        
        # Special handling for chunk 8 (ending scene)
        if map_id == 8:
            from scenes import EndingScene
            ending_scene = EndingScene(self.player, name="The Grinch Returns")
            
            # Clear existing scenes and add ending scene
            self.scenes.clear()
            self.add_scene(ending_scene)
            self.current_scene_index = 0
            print("🎄🎁 ENDING SCENE ACTIVATED! The Grinch returns the presents to the children!")
        else:
            # Create regular chunk with coordinates and map_id
            chunk = Chunk(chunk_x, chunk_y, map_id, self.maps, level=self)
            chunk.set_player(self.player)
            
            # Clear existing scenes and add new chunk
            self.scenes.clear()
            self.add_scene(chunk)
            self.current_scene_index = 0
    
    def switch_chunk(self, new_x, new_y, entry_direction):
        """Switch to a different chunk at the given coordinates
        
        Args:
            new_x: X coordinate of the new chunk
            new_y: Y coordinate of the new chunk
            entry_direction: Direction player entered from ('top', 'bottom', 'left', 'right')
        """
        self.current_chunk_pos = (new_x, new_y)
        self.create_chunk(new_x, new_y)
        
        # Position player based on entry direction
        padding = 2
        if entry_direction == 'top':
            self.player.y = SCREEN_HEIGHT - self.player.height - padding
        elif entry_direction == 'bottom':
            self.player.y = padding
        elif entry_direction == 'left':
            self.player.x = SCREEN_WIDTH - self.player.width - padding
        elif entry_direction == 'right':
            self.player.x = padding
        
        # Clamp player position
        self.player.x = max(padding, min(self.player.x, SCREEN_WIDTH - self.player.width - padding))
        self.player.y = max(padding, min(self.player.y, SCREEN_HEIGHT - self.player.height - padding))
    
    def _get_interior_level_config(self, level_num):
        """Get the configuration for a specific interior level (1-2)
        
        Args:
            level_num: Interior level number (1 or 2)
            
        Returns:
            dict with 'walls', 'enemy_areas', 'tree_areas' lists
        """
        configs = {
            1: {  # Level 1 - Complex room divisions
                'walls': [
                    # Border walls
                    Wall(0, 0, 1280, 20), Wall(0, 0, 20, 720),
                    Wall(0, 700, 1280, 20), Wall(1260, 0, 20, 720),
                    # Interior walls
                    Wall(0, 350, 180, 20), Wall(300, 350, 220, 20),
                    Wall(520, 350, 20, 100), Wall(520, 600, 20, 200),
                    Wall(780, 0, 20, 500)
                ],
                'enemy_areas': [(270, 400, 200, 200), (810, 300, 440, 300)],
                'tree_areas': [(30, 380, 150, 310), (30, 30, 500, 170), (810, 30, 440, 300)]
            },
            2: {  # Level 2 - Multiple areas with central dividers
                'walls': [
                    # Border walls
                    Wall(0, 0, 1280, 20), Wall(0, 0, 20, 720),
                    Wall(0, 700, 1280, 20), Wall(1260, 0, 20, 720),
                    # Interior walls
                    Wall(655, 150, 20, 400),  # Central vertical divider
                    Wall(300, 340, 700, 20),  # Middle horizontal
                    Wall(0, 340, 150, 20),  # Left horizontal extension
                    Wall(1150, 340, 200, 20)  # Right horizontal extension
                ],
                'enemy_areas': [
                    (380, 30, 150, 300),  # Upper left-center
                    (850, 30, 150, 300),  # Upper right-center
                    (900, 400, 200, 200),  # Lower right
                    (200, 400, 200, 200)  # Lower left
                ],
                'tree_areas': [
                    (30, 30, 130, 300),  # Top left
                    (1120, 30, 130, 300),  # Top right
                    (30, 520, 130, 170),  # Bottom left
                    (1120, 520, 130, 170)  # Bottom right
                ]
            }
        }
        return configs.get(level_num, configs[1])  # Default to level 1 if invalid
    
    def _create_interior_1(self, level_num=None, saved_state=None):
        """Create an Interior_1 instance with level configuration
        
        Args:
            level_num: Which level to create (1 or 2). If None, randomly select
            saved_state: InteriorState object to restore from, or None for new interior
            
        Returns:
            Interior_1 scene
        """
        # Determine level number (only 2 levels available)
        if level_num is None:
            level_num = random.randint(1, 2)
        
        # Get level configuration
        config = self._get_interior_level_config(level_num)
        
        # Create Interior_1 with configuration
        interior = Interior_1(
            walls=config['walls'],
            enemy_spawn_areas=config['enemy_areas'],
            tree_spawn_areas=config['tree_areas'],
            num_enemies=3,
            num_presents=8,  # Target (actual number depends on tree placement)
            num_trees=3,
            level=self,
            name=f"Interior {level_num}",
            saved_state=saved_state  # Pass saved state for restoration
        )
        
        print(f"🏠 Created Interior Level {level_num}")
        return interior
    
    def enter_interior(self):
        """Enter an interior area"""
        if self.is_in_interior:
            return
        
        # Store door entry position
        self.door_entry_x = self.player.x
        self.door_entry_y = self.player.y
        self.door_entry_chunk_pos = self.current_chunk_pos
        
        # Create interior using Interior_1 with procedural spawning
        # Check if this chunk already has a saved interior
        saved_state = self.saved_interiors.get(self.current_chunk_pos)
        
        if saved_state:
            # Restore previous interior
            interior = self._create_interior_1(level_num=saved_state.level_num, saved_state=saved_state)
            print(f"🏠 Restoring Interior Level {saved_state.level_num}")
        else:
            # Create new random interior
            interior = self._create_interior_1()
            print("🏠 Entering new Interior - Stealth challenge!")
        
        interior.set_player(self.player)
        
        self.current_interior = interior
        self.is_in_interior = True
        
        # Switch to interior scene
        self.scenes.clear()
        self.add_scene(interior)
        self.current_scene_index = 0
    
    def exit_interior(self):
        """Exit the interior and return to the chunk"""
        if not self.is_in_interior:
            return
        
        # Save interior state before exiting (if it's an Interior_1)
        if isinstance(self.current_interior, Interior_1):
            self._save_interior_state(self.door_entry_chunk_pos, self.current_interior)
        
        # Return to the chunk we were in
        self.is_in_interior = False
        self.current_interior = None
        
        # Restore chunk at the saved coordinates
        self.current_chunk_pos = self.door_entry_chunk_pos
        self.create_chunk(self.door_entry_chunk_pos[0], self.door_entry_chunk_pos[1])
        
        # Reset player position and state (clears caught status, velocities, etc.)
        self.player.reset_for_new_round(self.door_entry_x, self.door_entry_y + 45)
    
    def _save_interior_state(self, chunk_pos, interior):
        """Save the state of an interior for later restoration
        
        Args:
            chunk_pos: (x, y) chunk coordinates
            interior: Interior_1 instance to save
        """
        # Extract level number from interior name
        level_num = interior.level_num if hasattr(interior, 'level_num') else 1
        
        # Save enemy positions
        enemy_positions = [(e.x, e.y) for e in interior.enemies]
        
        # Save present data (position and collected status)
        present_data = [
            {'x': p.x, 'y': p.y, 'collected': p.is_collected}
            for p in interior.presents
        ]
        
        # Save tree positions
        tree_positions = [(t.full_x, t.full_y) for t in interior.trees]
        
        # Create and store state
        state = InteriorState(level_num, enemy_positions, present_data, tree_positions)
        self.saved_interiors[chunk_pos] = state
        
        print(f"💾 Saved interior state for chunk {chunk_pos}: Level {level_num}, {len(enemy_positions)} enemies, {len(present_data)} presents")
    
    def restart_game(self):
        """Request return to main menu from Game class (on game over)"""
        if self.game:
            self.game.request_return_to_menu()
        else:
            print("⚠️ Cannot return to menu - no game reference")
    
    def handle_event(self, event):
        """Handle pygame events
        
        Args:
            event: pygame.Event to handle
        """
        # Handle key presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSLASH:
                self.debug_mode = not self.debug_mode
                print(f"Debug mode: {'ON' if self.debug_mode else 'OFF'}")
            elif event.key == pygame.K_e:
                self.e_pressed = True
            # TEST: Press P to collect 10 presents (for testing)
            elif event.key == pygame.K_p:
                for _ in range(10):
                    self.collect_present()
                print(f"🎁 Added 10 presents! Total: {self.presents_collected}/{self.present_goal}")
            # TEST: Press [ to trigger fade to black
            elif event.key == pygame.K_LEFTBRACKET:
                self.fade_to_black()
            # TEST: Press ] to trigger fade in from black
            elif event.key == pygame.K_RIGHTBRACKET:
                self.fade_in_from_black()
            # TEST: Press \ and R together to reset fade
            elif event.key == pygame.K_r and pygame.key.get_pressed()[pygame.K_BACKSLASH]:
                self.reset_fade()
        
        # Pass events to parent
        super().handle_event(event)
    
    def update(self, dt):
        """Update level logic"""
        # Store e_pressed for this frame, then reset
        e_pressed_this_frame = self.e_pressed
        self.e_pressed = False
        
        # Update lives tracker to match player's current lives
        if self.player and self.lives_tracker:
            self.lives_tracker.set_lives(self.player.lives)
        
        # Music management based on location
        if not self.is_in_interior:
            # Play special music when goal is reached
            if self.presents_collected >= self.present_goal:
                play_music("assets/sounds/children_singing.mp3")
            else:
                play_music("assets/sounds/outside_music.mp3")
            # Check for chunk switching
            scene = self.get_current_scene()
            if isinstance(scene, Chunk):
                direction, new_x, new_y = scene.check_edge_exit()
                if direction and new_x is not None and new_y is not None:
                    self.switch_chunk(new_x, new_y, direction)
                
                # Check for door entry
                if scene.check_door_enter():
                    # Check for input to enter
                    if e_pressed_this_frame:  # Press E to enter
                        self.enter_interior()
        
        # Update UI elements
        for ui_element in self.ui_elements:
            ui_element.update(dt)
        
        # Update current scene
        scene = self.get_current_scene()
        if scene:
            # For interiors, pass e_pressed parameter
            if isinstance(scene, Interior_1):
                scene.update(dt, e_pressed_this_frame)
            else:
                scene.update(dt)
        
        # Update fade effects (from Level base class)
        super().update(dt)
    
    def render(self, screen):
        """Render the level"""
        # Render scene (pass debug mode to chunk)
        scene = self.get_current_scene()
        if scene:
            if isinstance(scene, Chunk):
                scene.render(screen, debug=self.debug_mode)
            elif isinstance(scene, Interior):
                scene.render(screen, debug=self.debug_mode)
            else:
                scene.render(screen)
        
        # Only show HUD in debug mode
        if self.debug_mode:
            font = pygame.font.Font(None, 36)
            
            # Show current chunk/interior
            if self.is_in_interior:
                text = font.render("Interior - Press SPACE to exit", True, (255, 255, 255))
                screen.blit(text, (10, 10))
            else:
                # Show chunk ID (sprite/map number)
                current_map_id = self.generated_chunks.get(self.current_chunk_pos, 0)
                chunk_text = f"Chunk: {current_map_id}"
                text = font.render(chunk_text, True, (148, 87, 235))
                screen.blit(text, (10, 10))
                
                # Show chunk coordinates
                coords_chunk_text = f"Coords: ({self.current_chunk_pos[0]}, {self.current_chunk_pos[1]})"
                text_coords_chunk = font.render(coords_chunk_text, True, (148, 87, 235))
                screen.blit(text_coords_chunk, (10, 50))
            
            # Show player position
            player_pos_text = f"Player: (X:{int(self.player.x)}, Y:{int(self.player.y)})"
            text_player_pos = font.render(player_pos_text, True, (148, 87, 235))
            screen.blit(text_player_pos, (10, 90))
            
            # Show chunks explored count
            chunks_text = f"Chunks explored: {len(self.generated_chunks)}"
            text_chunks = font.render(chunks_text, True, (148, 87, 235))
            screen.blit(text_chunks, (10, 130))
            
            # Show presents collected
            presents_text = f"Presents: {self.presents_collected}/{self.present_goal}"
            text_presents = font.render(presents_text, True, (255, 215, 0))  # Gold color
            screen.blit(text_presents, (10, 170))
            
            # Debug mode indicator
            debug_text = font.render("DEBUG MODE (Press \\ to toggle)", True, (255, 255, 0))
            screen.blit(debug_text, (SCREEN_WIDTH - 500, 10))
        
        # === Render UI Elements (Always Visible) ===
        for ui_element in self.ui_elements:
            ui_element.render(screen)
        
        # Show door hint (always visible, not just in debug)
        if not self.is_in_interior:
            scene = self.get_current_scene()
            if isinstance(scene, Chunk) and scene.check_door_enter():
                font = pygame.font.Font(None, 36)
                hint_text = font.render("Press E to enter", True, (255, 255, 0))
                screen.blit(hint_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50))
        
        # Render fade overlay on top of everything (from base Level class)
        self._render_fade_overlay(screen)

