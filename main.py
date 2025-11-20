"""Main entry point for the game"""

from game import Game
from config.settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
from levels.christmas_level import ChristmasLevel
from scenes import Menu


def main():
    """Initialize and run the game"""
    # Create the game with settings from config
    game = Game(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE)
    
    # Create and set the menu
    menu = Menu()
    game.set_menu(menu)
    
    # Store the level class (will be instantiated when start button is clicked)
    game.initial_level_class = ChristmasLevel
    
    # Run the game (starts in menu)
    game.run()


if __name__ == "__main__":
    main()

