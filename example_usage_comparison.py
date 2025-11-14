"""Example showing inheritance approach for levels"""

from game import Game
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE

# Recommended: Use inheritance classes
from levels.example_level import ExampleLevel


def main():
    """Example using inheritance - recommended approach"""
    game = Game(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE)
    
    # Create instance of inherited class
    level = ExampleLevel()
    game.set_level(level)
    
    game.run()


if __name__ == "__main__":
    main()

