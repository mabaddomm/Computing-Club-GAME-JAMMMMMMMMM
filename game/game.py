"""Main game engine class"""

import pygame
from typing import Optional
from game.level import Level


class Game:
    """Main game engine that manages levels and the game loop"""
    
    def __init__(self, width: int = 800, height: int = 600, title: str = "Game"):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_level: Optional[Level] = None
        self.fps = 60
        self.width = width
        self.height = height
    
    def set_level(self, level: Level):
        """Set the current level
        
        Args:
            level: Level instance to set as current
        """
        self.current_level = level
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Pass events to current level/scene
            if self.current_level:
                self.current_level.handle_event(event)
    
    def update(self, dt):
        """Update game logic
        
        Args:
            dt: Delta time in seconds since last update
        """
        if self.current_level:
            self.current_level.update(dt)
    
    def render(self):
        """Render everything"""
        if self.current_level:
            self.current_level.render(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0  # Delta time in seconds
            
            self.handle_events()
            self.update(dt)
            self.render()
        
        pygame.quit()

