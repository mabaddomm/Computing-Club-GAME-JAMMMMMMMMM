"""Main entry point for the game"""

from game import Game
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
from levels.christmas_level import ChristmasLevel


def main():
    """Initialize and run the game"""
    # Create the game with settings from config
    game = Game(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE)
    
    # Create and set the starting level (using inheritance - recommended)
    level = ChristmasLevel()
    game.set_level(level)
    
    # Run the game
    game.run()


if __name__ == "__main__":
    main()

