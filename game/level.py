"""Level class for managing multiple scenes"""

from typing import List, Optional
from game.scene import Scene


class Level:
    """A level contains multiple scenes"""
    
    def __init__(self, name: str):
        self.name = name
        self.scenes: List[Scene] = []
        self.current_scene_index = 0
    
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
    
    def update(self, dt):
        """Update the current scene
        
        Args:
            dt: Delta time in seconds since last update
        """
        scene = self.get_current_scene()
        if scene:
            scene.update(dt)
    
    def render(self, screen):
        """Render the current scene
        
        Args:
            screen: pygame.Surface to render to
        """
        scene = self.get_current_scene()
        if scene:
            scene.render(screen)
    
    def handle_event(self, event):
        """Pass events to the current scene
        
        Args:
            event: pygame.Event to handle
        """
        scene = self.get_current_scene()
        if scene:
            scene.handle_event(event)

