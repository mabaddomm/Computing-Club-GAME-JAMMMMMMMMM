"""Example UI element - can be used as a template"""

from game import UIElement
import pygame


class SimpleText(UIElement):
    """A simple text UI element"""
    
    def __init__(self, x, y, text, font_size=24, color=(255, 255, 255)):
        super().__init__(x, y)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.color = color
    
    def render(self, screen):
        if self.visible:
            text_surface = self.font.render(self.text, True, self.color)
            screen.blit(text_surface, (self.x, self.y))

