import pygame
import sys
import random

def load_png(image, size):
    png = pygame.image.load(image).convert_alpha()
    return pygame.transform.scale(png, (size))

def make_map(key, maps, size):
    list = maps[key]
    map_bottom = load_png(list[0], size)
    top = load_png(list[1], size)
    walls = load_png(list[2], size)
    return map_bottom, top, walls

def generate_collision_rects(surface):
    mask = pygame.mask.from_surface(surface)
    local_rects = mask.get_bounding_rects()
    return local_rects

def check_collision(player_rect, collision_list):
    for rect in collision_list:
        if player_rect.colliderect(rect):
            return True
    return False


def resolve_spawn_collision_advanced(player, collisions, max_radius=120, step=4):
    """
    Expands in circles around spawn until a free position is found.
    Guarantees escape from diagonal, tight, or edge-wrapped collisions.
    """

    # If already safe, we’re done
    if not any(player.colliderect(c) for c in collisions):
        return

    original_x, original_y = player.x, player.y

    # Try increasing radius
    for radius in range(0, max_radius, step):
        for angle in range(0, 360, 15):
            rad = angle * 3.14159 / 180

            new_x = original_x + int(radius * pygame.math.cos(rad))
            new_y = original_y + int(radius * pygame.math.sin(rad))

            player.x = new_x
            player.y = new_y

            if not any(player.colliderect(c) for c in collisions):
                return  # FOUND VALID SPOT

    # Give up (extremely unlikely)
    print("WARNING: Could not find safe spawn!")
    player.x, player.y = original_x, original_y



def switch_map(new_map_key, entry_side, player,  maps, sw=1280, sh=720, player_x=0, player_y=0):
    current_map_key = new_map_key
    map_bottom, top, walls = make_map(current_map_key, maps, (sw, sh))
    collisions = generate_collision_rects(walls)
    door_rect = make_door(current_map_key)
    resolve_spawn_collision_advanced(player, collisions)

    padding = 2
    if entry_side == 'top':
        player.y = sh - player.height - padding
        player.x = max(padding, min(player.x, sw - player.width - padding))
    elif entry_side == 'bottom':
        player.y = padding
        player.x = max(padding, min(player.x, sw - player.width - padding))
    elif entry_side == 'left':
        player.x = sw - player.width - padding
        player.y =  max(padding, min(player.y, sh - player.height - padding))
    elif entry_side == 'right':
        player.x = padding
        player.y =  max(padding, min(player.y, sh - player.height - padding))
    elif entry_side == 'door':
        player.x = player_x
        player.y = player_y + 45

    return map_bottom, top, walls, collisions, door_rect


def make_door(current_map_key):
    door = []
    if current_map_key == 1:
        door.append(pygame.Rect(540, 540, 70, 32))
    elif current_map_key == 2:
        door.append(pygame.Rect(930, 540, 70, 32))
    elif current_map_key == 5:
        door.append(pygame.Rect(950, 535, 70, 32))
    elif current_map_key == 6:
        door.append(pygame.Rect(960, 500, 70, 32))
    return door