from pytmx import load_pygame
from game_objects.mWall import CollisionWall

def load_collision_walls(scene, tmx_path):
    """
    Reads the 'Collision' tile layer from a TMX map and generates CollisionWall objects.
    """
    tmx_data = load_pygame(tmx_path)
    try:
        collision_layer = tmx_data.get_layer_by_name("Collisions Layer")
    except ValueError:
        print(f"No layer named 'Collision' in {tmx_path}")
        return

    tile_w = tmx_data.tilewidth
    tile_h = tmx_data.tileheight

    for x, y, gid in collision_layer:
        if gid != 0:
            wall = CollisionWall(x*tile_w, y*tile_h, tile_w, tile_h)
            scene.add_game_object(wall)
