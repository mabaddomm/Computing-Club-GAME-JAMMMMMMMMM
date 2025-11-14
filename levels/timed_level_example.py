"""Example of using inheritance for a level with custom behavior"""

from game import Level
from scenes.example_scene import create_example_scene


class TimedLevel(Level):
    """Level with a time limit - demonstrates inheritance approach"""
    
    def __init__(self, time_limit=60):
        super().__init__("Timed Level")
        self.time_limit = time_limit
        self.time_remaining = time_limit
        self.level_complete = False
        
        # Setup the level using factory function
        scene = create_example_scene()
        self.add_scene(scene)
    
    def update(self, dt):
        """Override update to add custom timer logic"""
        # Call parent update first
        super().update(dt)
        
        # Custom: Countdown timer
        if not self.level_complete:
            self.time_remaining -= dt
            if self.time_remaining <= 0:
                self.on_time_up()
    
    def on_time_up(self):
        """Custom behavior when time runs out"""
        self.level_complete = True
        print(f"Time's up! Level: {self.name}")
        # You could switch to a game over scene here
        # self.set_scene(1)  # If you had a game over scene
    
    def get_time_remaining(self):
        """Get remaining time"""
        return max(0, self.time_remaining)

