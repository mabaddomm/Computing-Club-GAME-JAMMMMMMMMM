"""Christmas level - manages chunks and interiors for the Christmas game"""

import pygame
import random
import os
from game import Level
from scenes import Chunk, Interior, Interior_1, ChristmasInterior
from game_objects import Player, Wall
from ui_elements import PresentCounter
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, L1_PRESENT_ITEM_GOAL


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
            8: {'top': False, 'bottom': True, 'left': False, 'right': False}   # Goal chunk (one entrance from bottom)
        }
        
        # Chunk unlock status
        # Chunks 0-7 are unlocked by default (basic winter maps)
        # Chunk 8 is the goal chunk (unlocks after collecting presents)
        self.chunk_unlocked = {
            0: True,
            1: True,
            2: True,
            3: True,
            4: True,
            5: True,
            6: True,
            7: True,
            8: False  # Goal chunk (unlocks after collecting L1_PRESENT_ITEM_GOAL presents)
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
        
        # Debug mode
        self.debug_mode = False
        
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
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, speed=200)
        
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
        
        # Check if we've reached the goal and should unlock the goal chunk
        if self.presents_collected >= self.present_goal and not self.chunk_unlocked[8]:
            self.unlock_chunk(8)
            print(f"🎄 You've collected enough presents! The goal chunk is now unlocked!")
    
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
            # Start with all unlocked maps only (including goal chunk if unlocked)
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
        
        # Create chunk with coordinates and map_id
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
    
    def _create_interior_1(self):
        """Create an Interior_1 instance with level configuration
        
        Returns:
            Interior_1 scene
        """
        # Define wall layout (border walls + some interior walls)
        walls = [
            Wall(0, 0, SCREEN_WIDTH, 20),  # Top
            Wall(0, 0, 20, SCREEN_HEIGHT),  # Left
            Wall(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20),  # Bottom
            Wall(SCREEN_WIDTH - 20, 0, 20, SCREEN_HEIGHT),  # Right
            Wall(300, 200, 400, 20),  # Interior wall 1
            Wall(300, 200, 20, 300),  # Interior wall 2
        ]
        
        # Define spawn areas (x, y, width, height)
        enemy_spawn_areas = [
            (100, 100, 200, 200),  # Top left area
            (800, 150, 300, 250),  # Top right area
        ]
        
        tree_spawn_areas = [
            (400, 400, 200, 300),  # Bottom middle-left
            (900, 500, 250, 300),  # Bottom right
        ]
        
        # Create Interior_1 with configuration
        interior = Interior_1(
            walls=walls,
            enemy_spawn_areas=enemy_spawn_areas,
            tree_spawn_areas=tree_spawn_areas,
            num_enemies=3,
            num_presents=8,  # Target (actual number depends on tree placement)
            num_trees=3,
            level=self,
            name="Interior 1"
        )
        
        return interior
    
    def enter_interior(self):
        """Enter an interior area"""
        if self.is_in_interior:
            return
        
        # Store door entry position
        self.door_entry_x = self.player.x
        self.door_entry_y = self.player.y
        self.door_entry_chunk_pos = self.current_chunk_pos
        
        # Check if this is the goal chunk
        current_map_id = self.generated_chunks.get(self.current_chunk_pos, 0)
        is_goal_chunk = (current_map_id == 8)
        
        # Create interior
        if is_goal_chunk:
            # Special Christmas stealth interior with enemies and presents!
            interior = ChristmasInterior("Goal Interior - Christmas Challenge", level=self)
            print("🎄 You've entered the GOAL CHUNK - Stealth Challenge!")
            print("   Collect presents while avoiding enemies!")
            
            # Position player near middle bottom of screen
            self.player.x = SCREEN_WIDTH // 2 - self.player.width // 2
            self.player.y = SCREEN_HEIGHT - self.player.height - 50
            
            interior.set_player(self.player)
        else:
            # Regular interior using Interior_1 with procedural spawning
            interior = self._create_interior_1()
            print("🏠 Entering Interior_1 - Advanced stealth challenge")
            
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
        
        # Return to the chunk we were in
        self.is_in_interior = False
        self.current_interior = None
        
        # Restore chunk at the saved coordinates
        self.current_chunk_pos = self.door_entry_chunk_pos
        self.create_chunk(self.door_entry_chunk_pos[0], self.door_entry_chunk_pos[1])
        
        # Reset player position and state (clears caught status, velocities, etc.)
        self.player.reset_for_new_round(self.door_entry_x, self.door_entry_y + 45)
    
    def restart_game(self):
        """Request game restart from main Game class"""
        if self.game:
            self.game.request_restart()
        else:
            print("⚠️ Cannot restart - no game reference")
    
    def handle_event(self, event):
        """Handle pygame events
        
        Args:
            event: pygame.Event to handle
        """
        # Toggle debug mode with backslash key
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSLASH:
                self.debug_mode = not self.debug_mode
                print(f"Debug mode: {'ON' if self.debug_mode else 'OFF'}")
            # TEST: Press P to collect a present (for testing)
            elif event.key == pygame.K_p:
                self.collect_present()
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
        if not self.is_in_interior:
            # Check for chunk switching
            scene = self.get_current_scene()
            if isinstance(scene, Chunk):
                direction, new_x, new_y = scene.check_edge_exit()
                if direction and new_x is not None and new_y is not None:
                    self.switch_chunk(new_x, new_y, direction)
                
                # Check for door entry
                if scene.check_door_enter():
                    # Check for input to enter
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_e]:  # Press E to enter
                        self.enter_interior()
        else:
            # In interior - check for exit
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:  # Press SPACE to exit
                self.exit_interior()
        
        # Update UI elements
        for ui_element in self.ui_elements:
            ui_element.update(dt)
        
        # Update current scene (base class handles fade effect)
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

