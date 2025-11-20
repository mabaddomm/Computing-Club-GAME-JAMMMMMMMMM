from game import Scene
from pytmx import load_pygame
from levels.CollasionLevel import load_collision_walls
from game_objects.player import Player

def draw_tile_layer(screen, tmx_data, layer_name):
    """Draws a single tile layer"""
    layer = tmx_data.get_layer_by_name(layer_name)
    for x, y, gid in layer:
        tile_image = tmx_data.get_tile_image_by_gid(gid)
        if tile_image:
            screen.blit(tile_image, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

class houseUno(Scene):
    def __init__(self, tmx_path):
        super().__init__("GameplayScene")
        self.tmx_data = load_pygame(tmx_path)

        # Load collision walls
        load_collision_walls(self, tmx_path)

        # Add player
        self.player = Player(50, 50)
        self.add_game_object(self.player)

    def render(self, screen):
        # Draw layers in order
        draw_tile_layer(screen, self.tmx_data, "Red_walls_cyan")     # bottom     # behind player

        super().render(screen)  # draw player and any visible objects

        draw_tile_layer(screen, self.tmx_data, "Furniture") # top layer
