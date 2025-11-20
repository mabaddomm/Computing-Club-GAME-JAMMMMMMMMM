"""Level class for managing multiple scenes"""

import pygame
from typing import List, Optional
from game.scene import Scene


class Level:
    """A level contains multiple scenes"""
    
    def __init__(self, name: str):
        self.name = name
        self.scenes: List[Scene] = []
        self.current_scene_index = 0
        self.game = None  # Reference to parent Game instance (set by Game.set_level)
        
        # Fade to black effect state
        self.is_fading = False
        self.fade_alpha = 0  # 0 = fully visible, 255 = fully black
        self.fade_speed = 3  # Alpha change per frame (same for both directions)
        self.fade_direction = 1  # 1 = fading to black, -1 = fading from black
        self.last_fade_speed = 3  # Remember last fade speed for matching
        self.fade_surface = None  # Will be initialized when we know screen size
        self.fade_initialized = False
    
    def add_scene(self, scene: Scene):
        """Add a scene to the level
        
        Args:
            scene: Scene instance to add
        """
        self.scenes.append(scene)
    
    def get_current_scene(self) -> Optional[Scene]:
        """Get the currently active scene
        
        Returns:
            Current Scene instance or None if no scenes exist
        """
        if 0 <= self.current_scene_index < len(self.scenes):
            return self.scenes[self.current_scene_index]
        return None
    
    def set_scene(self, index: int):
        """Switch to a different scene
        
        Args:
            index: Index of the scene to switch to
        """
        if 0 <= index < len(self.scenes):
            self.current_scene_index = index
    
    def fade_to_black(self, speed=3):
        """Start a fade to black effect over the current scene
        
        Args:
            speed: How fast to fade (alpha increase per frame, default 3)
                  Both fade directions use the same speed value for symmetry.
        """
        self.is_fading = True
        self.fade_alpha = 0
        self.fade_speed = speed
        self.fade_direction = 1  # Fading TO black
        self.last_fade_speed = speed  # Remember for matching fade in
        print(f"🎬 Fade to black started (speed: {speed})")
    
    def fade_in_from_black(self, speed=3):
        """Start a fade in from black effect (revealing the scene)
        
        Args:
            speed: How fast to fade (alpha decrease per frame, default 3 to match fade out)
                  Lower speed = slower, more dramatic fade in
        """
        self.is_fading = True
        self.fade_alpha = 255  # Start fully black
        self.fade_speed = speed
        self.fade_direction = -1  # Fading FROM black
        self.last_fade_speed = speed  # Remember for future fades
        print(f"🎬 Fade in from black started (speed: {speed})")
    
    def reset_fade(self):
        """Reset the fade effect back to fully visible"""
        self.is_fading = False
        self.fade_alpha = 0
        print("🎬 Fade reset")
    
    def update(self, dt):
        """Update the current scene
        
        Args:
            dt: Delta time in seconds since last update
        """
        # Update fade effect
        if self.is_fading:
            self.fade_alpha += self.fade_speed * self.fade_direction
            
            if self.fade_direction == 1:  # Fading TO black
                if self.fade_alpha >= 255:
                    self.fade_alpha = 255
                    print("🎬 Fade to black complete!")
                    # Optionally stop fading once complete
                    # self.is_fading = False
            else:  # Fading FROM black (fade_direction == -1)
                if self.fade_alpha <= 0:
                    self.fade_alpha = 0
                    print("🎬 Fade in complete!")
                    # Optionally stop fading once complete
                    # self.is_fading = False
        
        scene = self.get_current_scene()
        if scene:
            scene.update(dt)
    
    def _render_fade_overlay(self, screen):
        """Render the fade to black overlay (internal method)
        
        Args:
            screen: pygame.Surface to render to
        """
        # Initialize fade surface on first render (when we know screen size)
        if not self.fade_initialized:
            screen_size = screen.get_size()
            self.fade_surface = pygame.Surface(screen_size)
            self.fade_surface.fill((0, 0, 0))  # Black surface
            self.fade_initialized = True
        
        # Draw fade to black overlay (if fading)
        if self.fade_alpha > 0 and self.fade_surface:
            self.fade_surface.set_alpha(int(self.fade_alpha))
            screen.blit(self.fade_surface, (0, 0))
    
    def render(self, screen):
        """Render the current scene
        
        Args:
            screen: pygame.Surface to render to
        """
        scene = self.get_current_scene()
        if scene:
            scene.render(screen)
        
        # Render fade overlay on top
        self._render_fade_overlay(screen)
    
    def handle_event(self, event):
        """Pass events to the current scene
        
        Args:
            event: pygame.Event to handle
        """
        scene = self.get_current_scene()
        if scene:
            scene.handle_event(event)

