"""Scene class for managing game objects and UI elements"""

import pygame
from typing import List
from game.game_object import GameObject
from game.ui_element import UIElement


class Scene:
    """A scene contains game objects and UI elements"""
    
    def __init__(self, name: str):
        self.name = name
        self.game_objects: List[GameObject] = []
        self.ui_elements: List[UIElement] = []
        self.background_color = (0, 0, 0)
        self.active = True
    
    def add_game_object(self, obj: GameObject):
        """Add a game object to the scene
        
        Args:
            obj: GameObject instance to add
        """
        self.game_objects.append(obj)
    
    def add_ui_element(self, element: UIElement):
        """Add a UI element to the scene
        
        Args:
            element: UIElement instance to add
        """
        self.ui_elements.append(element)
    
    def remove_game_object(self, obj: GameObject):
        """Remove a game object from the scene
        
        Args:
            obj: GameObject instance to remove
        """
        if obj in self.game_objects:
            self.game_objects.remove(obj)
    
    def remove_ui_element(self, element: UIElement):
        """Remove a UI element from the scene
        
        Args:
            element: UIElement instance to remove
        """
        if element in self.ui_elements:
            self.ui_elements.remove(element)
    
    def update(self, dt):
        """Update all entities in the scene
        
        Args:
            dt: Delta time in seconds since last update
        """
        if not self.active:
            return
        
        for obj in self.game_objects:
            obj.update(dt)
        
        for ui in self.ui_elements:
            ui.update(dt)
    
    def render(self, screen):
        """Render all entities in the scene
        
        Args:
            screen: pygame.Surface to render to
        """
        screen.fill(self.background_color)
        
        # Render game objects first (background layer)
        for obj in self.game_objects:
            if obj.visible:
                obj.render(screen)
        
        # Render UI elements on top (foreground layer)
        for ui in self.ui_elements:
            if ui.visible:
                ui.render(screen)
    
    def handle_event(self, event):
        """Pass events to UI elements
        
        Args:
            event: pygame.Event to handle
        """
        for ui in self.ui_elements:
            ui.handle_event(event)

