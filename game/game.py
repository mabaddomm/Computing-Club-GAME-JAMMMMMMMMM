"""Main game engine class"""

import pygame
from typing import Optional
from game.level import Level
from game.scene import Scene


class Game:
    """Main game engine that manages levels and the game loop"""
    
    def __init__(self, width: int = 800, height: int = 600, title: str = "Game"):
        pygame.init()
        pygame.mixer.init()  # Initialize audio mixer
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_level: Optional[Level] = None
        self.fps = 60
        self.width = width
        self.height = height
        self.restart_requested = False
        self.return_to_menu_requested = False
        self.initial_level_class = None  # Store level class for restart
        
        # Menu state
        self.menu_scene: Optional[Scene] = None
        self.game_state = 'MENU'  # MENU or PLAYING
    
    def set_menu(self, menu_scene: Scene):
        """Set the menu scene
        
        Args:
            menu_scene: Menu scene instance
        """
        self.menu_scene = menu_scene
        self.game_state = 'MENU'
        print("📋 Menu scene loaded")
    
    def set_level(self, level: Level):
        """Set the current level
        
        Args:
            level: Level instance to set as current
        """
        self.current_level = level
        # Set game reference on level
        level.game = self
        # Store the level class for restart functionality
        self.initial_level_class = level.__class__
    
    def start_game(self):
        """Transition from menu to game"""
        if self.initial_level_class:
            print("🎮 Starting game...")
            self.current_level = self.initial_level_class()
            self.current_level.game = self
            self.game_state = 'PLAYING'
            print("✅ Game started!")
    
    def request_return_to_menu(self):
        """Request return to main menu (called by level on game over)"""
        self.return_to_menu_requested = True
        print("🔙 Return to menu requested...")
    
    def return_to_menu(self):
        """Return to main menu"""
        print("📋 Returning to main menu...")
        if self.menu_scene:
            self.menu_scene.reset()  # Reset menu state
        self.current_level = None
        self.game_state = 'MENU'
        self.return_to_menu_requested = False
        print("✅ Returned to menu!")
    
    def request_restart(self):
        """Request a game restart (called by level when game over)"""
        self.restart_requested = True
        print("🔄 Game restart requested...")
    
    def restart_game(self):
        """Restart the game by creating a fresh level instance"""
        if self.initial_level_class:
            print("🎮 Restarting game from scratch...")
            # Create a completely new level instance
            self.current_level = self.initial_level_class()
            self.restart_requested = False
            print("✅ Game restarted successfully!")
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # ESC key to quit game
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            
            # Pass events to current scene/level based on state
            if self.game_state == 'MENU' and self.menu_scene:
                self.menu_scene.handle_event(event)
            elif self.game_state == 'PLAYING' and self.current_level:
                self.current_level.handle_event(event)
    
    def update(self, dt):
        """Update game logic
        
        Args:
            dt: Delta time in seconds since last update
        """
        # Check if return to menu was requested
        if self.return_to_menu_requested:
            self.return_to_menu()
            return
        
        # Check if restart was requested (legacy, now returns to menu)
        if self.restart_requested:
            self.return_to_menu()
            self.restart_requested = False
            return
        
        if self.game_state == 'MENU':
            # Update menu
            if self.menu_scene:
                self.menu_scene.update(dt)
                
                # Check if start button was clicked
                if hasattr(self.menu_scene, 'start_clicked') and self.menu_scene.start_clicked:
                    self.start_game()
        
        elif self.game_state == 'PLAYING':
            # Update game level
            if self.current_level:
                self.current_level.update(dt)
    
    def render(self):
        """Render everything"""
        if self.game_state == 'MENU' and self.menu_scene:
            self.menu_scene.render(self.screen)
        elif self.game_state == 'PLAYING' and self.current_level:
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

