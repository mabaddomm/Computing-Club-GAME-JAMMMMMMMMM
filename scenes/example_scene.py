"""Example scene - demonstrates both factory function and inheritance approaches"""

from game import Scene
from game_objects.example import SimpleGameObject
from ui_elements.example import SimpleText


# ============================================================================
# APPROACH 1: Factory Function (Alternative approach)
# ============================================================================

def create_example_scene() -> Scene:
    """Factory function to create and configure an example scene
    
    This is an alternative approach. Inheritance (Approach 2) is recommended.
    """
    scene = Scene("Example Scene")
    scene.background_color = (50, 50, 50)  # Dark gray background
    
    # Add game objects
    obj1 = SimpleGameObject(100, 100, color=(255, 0, 0), size=30)
    obj1.velocity_x = 50  # Move right
    scene.add_game_object(obj1)
    
    obj2 = SimpleGameObject(200, 200, color=(0, 255, 0), size=25)
    obj2.velocity_y = 50  # Move down
    scene.add_game_object(obj2)
    
    # Add UI elements
    title = SimpleText(10, 10, "Game Framework Example", font_size=32)
    scene.add_ui_element(title)
    
    fps_text = SimpleText(10, 50, "FPS: 60", font_size=20, color=(200, 200, 200))
    scene.add_ui_element(fps_text)
    
    return scene


# ============================================================================
# APPROACH 2: Inheritance (Recommended)
# ============================================================================

class ExampleScene(Scene):
    """Example scene using inheritance - recommended approach
    
    Inherit from Scene and set up in __init__(). You can override 
    update(), render(), etc. as needed for custom behavior.
    """
    
    def __init__(self):
        super().__init__("Example Scene")
        self.background_color = (50, 50, 50)
        self.frame_count = 0
        
        # Add game objects
        self.obj1 = SimpleGameObject(100, 100, color=(255, 0, 0), size=30)
        self.obj1.velocity_x = 50
        self.add_game_object(self.obj1)
        
        self.obj2 = SimpleGameObject(200, 200, color=(0, 255, 0), size=25)
        self.obj2.velocity_y = 50
        self.add_game_object(self.obj2)
        
        # Add UI elements
        self.title = SimpleText(10, 10, "Game Framework Example", font_size=32)
        self.add_ui_element(self.title)
        
        self.fps_text = SimpleText(10, 50, "FPS: 60", font_size=20, color=(200, 200, 200))
        self.add_ui_element(self.fps_text)
    
    def update(self, dt):
        """Override update to add custom scene logic"""
        # Call parent update first
        super().update(dt)
        
        # Custom behavior: track frame count
        self.frame_count += 1
        
        # Example: Change background color every 60 frames
        if self.frame_count % 60 == 0:
            # Cycle through colors
            colors = [(50, 50, 50), (60, 50, 50), (50, 60, 50), (50, 50, 60)]
            self.background_color = colors[(self.frame_count // 60) % len(colors)]
    
    def on_enter(self):
        """Called when scene becomes active (if you add this to Scene class)"""
        print(f"Entering {self.name}")
    
    def on_exit(self):
        """Called when scene becomes inactive (if you add this to Scene class)"""
        print(f"Exiting {self.name}")


# ============================================================================
# Usage Examples:
# ============================================================================
# 
# Recommended: Use inheritance
#   scene = ExampleScene()
#
# Alternative: Factory function
#   scene = create_example_scene()

