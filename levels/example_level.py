"""Example level - demonstrates both factory function and inheritance approaches"""

from game import Level
from scenes.example_scene import create_example_scene, ExampleScene


# ============================================================================
# APPROACH 1: Factory Function (Alternative approach)
# ============================================================================

def create_example_level() -> Level:
    """Factory function to create and configure an example level
    
    This is an alternative approach. Inheritance (Approach 2) is recommended.
    """
    level = Level("Example Level")
    
    # Add scenes to the level (using factory function)
    scene = create_example_scene()
    level.add_scene(scene)
    
    return level


# ============================================================================
# APPROACH 2: Inheritance (Recommended)
# ============================================================================

class ExampleLevel(Level):
    """Example level using inheritance - recommended approach
    
    Inherit from Level and set up in __init__(). You can override 
    update(), render(), etc. as needed for custom behavior.
    """
    
    def __init__(self):
        super().__init__("Example Level")
        self.level_start_time = 0
        self.level_complete = False
        
        # Add scenes to the level
        # You can use either factory function or inheritance for scenes
        scene = create_example_scene()  # Using factory function
        # OR: scene = ExampleScene()  # Using inheritance
        self.add_scene(scene)
    
    def update(self, dt):
        """Override update to add custom level logic"""
        # Call parent update first
        super().update(dt)
        
        # Custom behavior: track level time
        self.level_start_time += dt
        
        # Example: Check win condition
        if not self.level_complete:
            # Your custom win condition logic here
            # if self.check_win_condition():
            #     self.on_level_complete()
            pass
    
    def check_win_condition(self):
        """Custom method to check if level is complete"""
        # Example: Check if all enemies defeated, items collected, etc.
        return False
    
    def on_level_complete(self):
        """Called when level is completed"""
        self.level_complete = True
        print(f"Level {self.name} completed!")
        # Could switch to next level or show victory screen
        # self.set_scene(1)  # Switch to victory scene
    def render(self, screen):
        """Render the level"""
        super.render(screen)


# ============================================================================
# Usage Examples:
# ============================================================================
# 
# Recommended: Use inheritance
#   level = ExampleLevel()
#
# Alternative: Factory function
#   level = create_example_level()

