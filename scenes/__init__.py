"""Scenes package - contains all game scenes"""

# Import all scene classes here for easy access
# Recommended: Use inheritance classes
from scenes.chunk import Chunk
from scenes.interior import Interior
from scenes.christmas_interior import ChristmasInterior
from scenes.mock_interior import MockInterior

__all__ = ['Chunk', 'Interior', 'ChristmasInterior', 'MockInterior']

