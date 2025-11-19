"""Mock Interior - test version of Christmas Interior for development"""

import pygame
from scenes.christmas_interior import ChristmasInterior


class MockInterior(ChristmasInterior):
    """Mock interior for testing stealth mechanics - accessible from any door"""
    
    def __init__(self, level=None):
        super().__init__(name="Mock Interior (Test)", level=level)
        # Inherits all the stealth gameplay from ChristmasInterior
        # This is just a wrapper to make it easier to test
        
        print("=== MOCK INTERIOR LOADED ===")
        print(f"  Enemies: {len(self.enemies)}")
        print(f"  Presents: {len(self.presents)}")
        print(f"  Walls: {len(self.walls)}")
        print("  Controls:")
        print("    - WASD/Arrows: Move")
        print("    - E: Hold to collect presents")
        print("    - SPACE: Exit interior")
        print("  Avoid enemy sight cones!")
        print("============================")

