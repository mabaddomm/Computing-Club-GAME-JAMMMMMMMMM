"""Chunk scene for topdown game - handles map rendering and collision"""

import pygame
import os
from game import Scene
from game_objects import Player
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Chunk(Scene):
    """A chunk represents a map area at grid coordinates with a specific map"""
    
    def __init__(self, chunk_x, chunk_y, map_id, maps_dict):
        super().__init__(f"Chunk ({chunk_x}, {chunk_y})")
        self.chunk_x = chunk_x
        self.chunk_y = chunk_y
        self.map_id = map_id
        self.maps_dict = maps_dict
        
        # Map surfaces
        self.map_bottom = None
        self.map_top = None
        self.walls = None
        self.collision_rects = []
        self.door_rects = []
        
        # Player reference (will be set by level)
        self.player = None
        
        # Load the map
        self.load_map(map_id)
        self.generate_collisions()
        self.setup_doors()
    
    def load_map(self, map_id):
        """Load map images for this chunk
        
        Args:
            map_id: ID of the map to load (0-7)
        """
        if map_id not in self.maps_dict:
            print(f"Warning: Map {map_id} not found in maps_dict")
            return
        
        map_files = self.maps_dict[map_id]
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        
        # Load bottom layer
        bottom_path = os.path.join(assets_dir, map_files[0])
        if os.path.exists(bottom_path):
            self.map_bottom = pygame.image.load(bottom_path).convert_alpha()
            self.map_bottom = pygame.transform.scale(self.map_bottom, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            print(f"Warning: {bottom_path} not found")
            self.map_bottom = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.map_bottom.fill((100, 100, 100))
        
        # Load top layer
        top_path = os.path.join(assets_dir, map_files[1])
        if os.path.exists(top_path):
            self.map_top = pygame.image.load(top_path).convert_alpha()
            self.map_top = pygame.transform.scale(self.map_top, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.map_top = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.map_top.set_alpha(0)
        
        # Load walls for collision
        walls_path = os.path.join(assets_dir, map_files[2])
        if os.path.exists(walls_path):
            self.walls = pygame.image.load(walls_path).convert_alpha()
            self.walls = pygame.transform.scale(self.walls, (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.walls = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.walls.set_alpha(0)
    
    def generate_collisions(self):
        """Generate collision rectangles from walls surface"""
        if self.walls is None:
            return
        
        # Create mask from walls surface
        mask = pygame.mask.from_surface(self.walls)
        # Get bounding rects from mask
        self.collision_rects = mask.get_bounding_rects()
    
    def setup_doors(self):
        """Setup door rectangles for this chunk based on map appearance"""
        self.door_rects = []
        
        # Define doors for specific map types (based on map_id)
        if self.map_id == 1:
            self.door_rects.append(pygame.Rect(540, 540, 70, 32))
        elif self.map_id == 2:
            self.door_rects.append(pygame.Rect(930, 540, 70, 32))
        elif self.map_id == 5:
            self.door_rects.append(pygame.Rect(950, 535, 70, 32))
        elif self.map_id == 6:
            self.door_rects.append(pygame.Rect(252, 381, 70, 32))  # Adjusted based on player position (287, 397)
    
    def check_edge_exit(self):
        """Check if player is exiting through an edge
        
        Returns:
            Tuple of (direction, new_x, new_y) or (None, None, None)
        """
        if self.player is None:
            return None, None, None
        
        # Check top edge - Y decreases in pygame coordinates
        if self.player.rect.top < 0:
            return 'top', self.chunk_x, self.chunk_y - 1
        
        # Check bottom edge - Y increases
        elif self.player.rect.bottom > SCREEN_HEIGHT:
            return 'bottom', self.chunk_x, self.chunk_y + 1
        
        # Check left edge - X decreases
        elif self.player.rect.left < 0:
            return 'left', self.chunk_x - 1, self.chunk_y
        
        # Check right edge - X increases
        elif self.player.rect.right > SCREEN_WIDTH:
            return 'right', self.chunk_x + 1, self.chunk_y
        
        return None, None, None
    
    def check_door_enter(self):
        """Check if player is entering a door
        
        Returns:
            True if player is on a door, False otherwise
        """
        if self.player is None:
            return False
        
        for door in self.door_rects:
            if self.player.rect.colliderect(door):
                return True
        return False
    
    def set_player(self, player):
        """Set the player reference for this chunk
        
        Args:
            player: Player game object
        """
        self.player = player
        if player not in self.game_objects:
            self.add_game_object(player)
    
    def update(self, dt):
        """Update chunk logic"""
        # Handle player input first (before updating positions)
        if self.player:
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
        
        # Update all game objects (this will apply velocities)
        super().update(dt)
        
        # Check collision and resolve after movement
        if self.player:
            if self.player.check_collision(self.collision_rects):
                self.player.resolve_collision(self.collision_rects, dt)
    
    def render(self, screen, debug=False):
        """Render the chunk
        
        Args:
            screen: pygame.Surface to render to
            debug: If True, render collision and door rects
        """
        # Render map bottom layer
        if self.map_bottom:
            screen.blit(self.map_bottom, (0, 0))
        
        # Render game objects (player, etc.)
        for obj in self.game_objects:
            if obj.visible:
                obj.render(screen)
        
        # Render map top layer (overlay)
        if self.map_top:
            screen.blit(self.map_top, (0, 0))
        
        # Render UI elements
        for ui in self.ui_elements:
            if ui.visible:
                ui.render(screen)
        
        # Debug mode: Render collision rects
        if debug:
            for rect in self.collision_rects:
                pygame.draw.rect(screen, (255, 0, 0), rect, 2)
            
            # Debug mode: Render door rects
            for door in self.door_rects:
                pygame.draw.rect(screen, (148, 87, 235), door, 3)
            
            # Debug mode: Render player hitbox
            if self.player:
                pygame.draw.rect(screen, (0, 255, 0), self.player.rect, 2)

