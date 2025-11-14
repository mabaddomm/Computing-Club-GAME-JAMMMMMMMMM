"""Example of using inheritance for a simple level """

from game import Level
from scenes.example_scene import create_example_scene


class Level_1_1(Level):
    """Level 1-1 using inheritance"""
    
    def __init__(self):
        # Call parent constructor
        super().__init__("Level 1-1")
        
        # Setup scenes (same as factory function would do)
        scene = create_example_scene()
        self.add_scene(scene)
        
        # You could add more setup here if needed
        # self.difficulty = "easy"
        # self.max_enemies = 5

# Usage:
# level = Level_1_1()  # Just like factory function!

