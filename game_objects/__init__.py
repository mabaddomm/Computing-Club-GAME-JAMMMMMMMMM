"""Game objects package - contains all interactive game entities"""

# Import all game objects here for easy access
from game_objects.player import Player
from game_objects.enemy import Enemy
from game_objects.child import Child
from game_objects.passive_child import PassiveChild
from game_objects.present import Present
from game_objects.static_present import StaticPresent
from game_objects.wall import Wall
from game_objects.tree import Tree
from game_objects.example import SimpleGameObject

__all__ = ['Player', 'Enemy', 'Child', 'PassiveChild', 'Present', 'StaticPresent', 'Wall', 'Tree', 'SimpleGameObject']

