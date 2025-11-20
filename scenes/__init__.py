"""Scenes package - contains all game scenes"""

# Import all scene classes here for easy access
# Recommended: Use inheritance classes
from scenes.menu import Menu
from scenes.chunk import Chunk
from scenes.interior import Interior
from scenes.interior_1 import Interior_1
from scenes.christmas_interior import ChristmasInterior

__all__ = ['Menu', 'Chunk', 'Interior', 'Interior_1', 'ChristmasInterior']

