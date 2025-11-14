# Project Structure Guide

This document explains the recommended file structure for organizing your game code.

## Directory Structure

```
.
├── game/                  # Core framework (don't modify)
│   ├── __init__.py
│   ├── entity.py
│   ├── game_object.py
│   ├── ui_element.py
│   ├── scene.py
│   ├── level.py
│   └── game.py
│
├── game_objects/          # All interactive game entities
│   ├── __init__.py        # Import all game objects here
│   ├── example.py         # Example template
│   ├── player.py          # Player character
│   ├── enemy.py           # Enemy entities
│   ├── item.py            # Collectible items
│   └── ...                # Add more as needed
│
├── ui_elements/           # All UI components
│   ├── __init__.py        # Import all UI elements here
│   ├── example.py         # Example template
│   ├── button.py          # Button components
│   ├── text.py            # Text displays
│   ├── hud.py             # Heads-up display
│   └── ...                # Add more as needed
│
├── scenes/                # All game scenes
│   ├── __init__.py        # Import all scenes here
│   ├── example_scene.py   # Example template
│   ├── main_menu.py       # Main menu scene
│   ├── gameplay.py        # Main gameplay scene
│   ├── pause.py           # Pause menu scene
│   └── ...                # Add more as needed
│
├── levels/                # All game levels
│   ├── __init__.py        # Import all levels here
│   ├── example_level.py   # Example template
│   ├── level1.py          # Level 1 definition
│   ├── level2.py          # Level 2 definition
│   └── ...                # Add more as needed
│
├── config/                # Configuration and settings
│   ├── __init__.py
│   └── settings.py        # Game settings (screen size, FPS, etc.)
│
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── helpers.py         # Helper functions
│   └── ...                # Add more as needed
│
├── assets/                 # Game assets (images, sounds, fonts)
│   ├── images/
│   ├── sounds/
│   ├── fonts/
│   └── ...
│
├── main.py                 # Main entry point (keep this simple!)
├── requirements.txt
└── README.md
```

## Organization Principles

### 1. **Separation of Concerns**
- **game_objects/**: All interactive entities (players, enemies, items, projectiles, etc.)
- **ui_elements/**: All UI components (buttons, text, HUD, menus, etc.)
- **scenes/**: Scene definitions that combine objects and UI
- **levels/**: Level definitions that combine scenes

### 2. **One Class Per File**
Each game object, UI element, scene, and level should have its own file for easy navigation.

### 3. **Inheritance (Recommended Approach)**
Scenes and levels should inherit from `Scene` and `Level` respectively, and set up in their `__init__()` methods. This is the recommended approach for consistency and flexibility.

### 4. **Keep main.py Simple**
`main.py` should only:
- Initialize the game
- Load the starting level
- Run the game loop

## Example: Adding a New Game Object

1. Create a new file: `game_objects/player.py`
   ```python
   from game import GameObject
   import pygame
   
   class Player(GameObject):
       def __init__(self, x, y):
           super().__init__(x, y)
           # Initialize player properties
       
       def update(self, dt):
           # Update player logic
           super().update(dt)
       
       def render(self, screen):
           # Render player
           pass
   ```

2. Add to `game_objects/__init__.py`:
   ```python
   from game_objects.player import Player
   __all__ = ['Player']
   ```

3. Use in a scene:
   ```python
   from game_objects import Player
   player = Player(100, 100)
   scene.add_game_object(player)
   ```

## Example: Adding a New Scene

1. Create `scenes/gameplay.py`:
   ```python
   from game import Scene
   from game_objects.player import Player
   from ui_elements.hud import HUD
   
   class GameplayScene(Scene):
       def __init__(self):
           super().__init__("Gameplay")
           self.background_color = (0, 0, 0)
           
           # Add game objects
           player = Player(400, 300)
           self.add_game_object(player)
           
           # Add UI
           hud = HUD()
           self.add_ui_element(hud)
   ```

2. Add to `scenes/__init__.py`:
   ```python
   from scenes.gameplay import GameplayScene
   __all__ = ['GameplayScene']
   ```

3. Use in a level:
   ```python
   from scenes import GameplayScene
   scene = GameplayScene()
   level.add_scene(scene)
   ```

## Benefits of This Structure

✅ **Scalable**: Easy to add new objects, scenes, and levels  
✅ **Organized**: Everything has a clear place  
✅ **Maintainable**: Easy to find and modify code  
✅ **Reusable**: Objects can be easily reused across scenes  
✅ **Testable**: Each component is isolated and testable  

## Tips

- Use descriptive file names: `player.py`, not `p.py`
- Keep files focused: One main class per file
- Use inheritance for scenes/levels (recommended approach)
- Import from package `__init__.py` files for cleaner imports
- Store constants in `config/settings.py`
- Put reusable helper functions in `utils/`

