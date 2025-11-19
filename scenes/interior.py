"""Interior scene for topdown game - represents interior areas"""

import pygame
from game import Scene
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Interior(Scene):
    """An interior area - has one chunk, game objects, and UI elements"""
    
    def __init__(self, name="Interior"):
        super().__init__(name)
        self.background_color = (50, 50, 50)  # Dark grey background
        
        # Interior has one chunk (as a scene)
        self.chunk = None
        
        # Player reference
        self.player = None
    
    def set_chunk(self, chunk):
        """Set the chunk for this interior
        
        Args:
            chunk: Chunk scene instance
        """
        self.chunk = chunk
    
    def set_player(self, player):
        """Set the player reference for this interior
        
        Args:
            player: Player game object
        """
        self.player = player
        
        # Add player to interior's game objects
        if player not in self.game_objects:
            self.add_game_object(player)
        
        # Also set player in chunk if chunk exists
        if self.chunk:
            self.chunk.set_player(player)
    
    def update(self, dt):
        """Update interior logic"""
        # Update chunk if it exists
        if self.chunk:
            self.chunk.update(dt)
        else:
            # No chunk - handle player input directly
            if self.player:
                keys = pygame.key.get_pressed()
                self.player.handle_input(keys)
        
        # Update interior's own game objects
        for obj in self.game_objects:
            if obj.active:
                obj.update(dt)
    
    def render(self, screen, debug=False):
        """Render the interior
        
        Args:
            screen: pygame.Surface to render to
            debug: If True, pass debug mode to chunk
        """
        # Render chunk if it exists (pass debug mode)
        if self.chunk:
            self.chunk.render(screen, debug=debug)
        else:
            # No chunk: render background and game objects
            screen.fill(self.background_color)
            
            # Render game objects (including player)
            for obj in self.game_objects:
                if obj.visible:
                    obj.render(screen)
        
        # Render UI elements
        for ui in self.ui_elements:
            if ui.visible:
                ui.render(screen)
    
    def handle_event(self, event):
        """Handle events"""
        # Pass to chunk first
        if self.chunk:
            self.chunk.handle_event(event)
        
        # Then to UI elements
        super().handle_event(event)

