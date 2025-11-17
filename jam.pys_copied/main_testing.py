from all_functions import *

pygame.init()
sw = 1280
sh = 720
screen = pygame.display.set_mode((sw, sh))

# GAME STATES:
RUNNING = 0
FADE_OUT = 1
LEVEL_LOADED = 2
PAUSED = 3
current_state = RUNNING
fade_alpha = 0
fade_speed = 8
font = pygame.font.Font(None, 36)



maps = {0: ["0_winter.png", "0_winter_top.png", "0_walls.png"],
        1: ["1_winter.png", "1_winter_top.png", "1_walls.png"],
        2: ["2_winter.png", "2_winter_top.png", "2_walls.png"],
        3: ["3_winter.png", "3_winter_top.png", "3_walls.png"],
        4: ["4_winter.png", "4_winter_top.png", "4_walls.png"],
        5: ["5_winter.png", "5_winter_top.png", "5_walls.png"],
        6: ["6_winter.png", "6_winter_top.png", "6_walls.png"],
        7: ["7_winter.png", "7_winter_top.png", "7_walls.png"]}


neighbors = {
    0: {
    'top': [1, 5],
    'bottom': [3],
    'left': [5, 7],
    'right': [2, 4, 5]
},
    1: {
        'top': [7],
        'bottom': [0],
        'left': [7],
        'right': [7]
},
    2: {
        'top': [7],
        'bottom': [7],
        'left': [0, 3, 4],
        'right': [7]
},
    3: {
        'top': [0],
        'bottom': [5, 4, 7],
        'left': [5, 7],
        'right': [2, 4, 5]
},
    4: {
        'top': [3, 7],
        'bottom': [5, 7],
        'left': [0, 3, 6],
        'right': [2, 5]
},
    5: {
        'top': [3, 4, 7],
        'bottom': [0],
        'left': [0, 3, 4, 6],
        'right': [0, 3, 7]
},
    6: {
        'top': [7],
        'bottom': [7],
        'left': [7],
        'right': [4, 5]
},
    7: {
        'top': [2, 3, 4, 6],
        'bottom': [1, 2, 4, 5, 6],
        'left': [1, 2, 5,],
        'right': [0, 1, 3, 4, 6]
    }
}



player = pygame.Rect(50, 50, 32, 32)
player_speed = 3
player.x = 545
player.y = 365

current_map_key = 0
map_bottom, top, walls = make_map(current_map_key, maps, (sw, sh))
collisions = generate_collision_rects(walls)
door_rect = []


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if current_state == RUNNING:
        dx = dy = 0
        if keys[pygame.K_LEFT]: dx -= player_speed
        if keys[pygame.K_RIGHT]: dx += player_speed
        if keys[pygame.K_UP]: dy -= player_speed
        if keys[pygame.K_DOWN]: dy += player_speed

        magnitude = (dx ** 2 + dy ** 2) ** 0.5
        if magnitude > 0:
            scale_factor = player_speed / magnitude
            dx *= scale_factor
            dy *= scale_factor

        new_x = player.x + dx
        new_y = player.y + dy

        temp_rect_x = pygame.Rect(new_x, player.y, player.width, player.height)
        if not check_collision(temp_rect_x, collisions):
            player.x = new_x

        temp_rect_y = pygame.Rect(player.x, new_y, player.width, player.height)
        if not check_collision(temp_rect_y, collisions):
            player.y = new_y

        for door in door_rect:
            if player.colliderect(door):
                entered_x = player.x
                entered_y = player.y
                entered_map = current_map_key
                current_state = FADE_OUT
                print("Door activated! Starting fade out.")
                break
        if keys[pygame.K_p]:
            current_state = PAUSED

        current_neighbors = neighbors[current_map_key]
        if player.top < 0:
            # Moving off the top edge
            possible_maps = current_neighbors.get('top')
            if possible_maps is not None:
                # Randomly select the next map ID from the list
                next_map_key = random.choice(possible_maps)
                current_map_key, map_bottom, top, walls, collisions, door_rect = switch_map(next_map_key, 'top', player, maps)
            else:
                player.top = 0  # Prevent moving past the screen edge
        elif player.bottom > sh:
            # Moving off the bottom edge
            possible_maps = current_neighbors.get('bottom', player)
            if possible_maps is not None:
                # Randomly select the next map ID from the list
                next_map_key = random.choice(possible_maps)
                current_map_key, map_bottom, top, walls, collisions, door_rect = switch_map(next_map_key, 'bottom', player, maps)
            else:
                player.bottom = sh
        elif player.left < 0:
            # Moving off the left edge
            possible_maps = current_neighbors.get('left')
            if possible_maps is not None:
                # Randomly select the next map ID from the list
                next_map_key = random.choice(possible_maps)
                current_map_key, map_bottom, top, walls, collisions, door_rect = switch_map(next_map_key, 'left', player, maps)
            else:
                player.left = 0
        elif player.right > sw:
            # Moving off the right edge
            possible_maps = current_neighbors.get('right')
            if possible_maps is not None:
                # Randomly select the next map ID from the list
                next_map_key = random.choice(possible_maps)
                current_map_key, map_bottom, top, walls, collisions, door_rect = switch_map(next_map_key, 'right', player, maps)
            else:
                player.right = sw

        #draw collision behind the map to hide it
        for rect in collisions:
            pygame.draw.rect(screen, (255, 0, 0), rect, 1)

        for door in door_rect:
            pygame.draw.rect(screen, (148, 87, 235), door, 10)

        screen.blit(map_bottom, (0, 0))


        pygame.draw.rect(screen, (255, 0, 0), player)

        screen.blit(top, (0,0))


        font = pygame.font.Font(None, 36)
        text_map = font.render(f"Map: {current_map_key}", True, (148, 87, 235))
        screen.blit(text_map, (10, 10))

        # 6. Show player coordinates (NEW FEATURE)
        player_coords_text = f"Coords: (X:{player.x}, Y:{player.y})"
        text_coords = font.render(player_coords_text, True, (148, 87, 235))
        # Place it right below the Map ID text at position (10, 40)
        screen.blit(text_coords, (10, 40))


    elif current_state == FADE_OUT:
        # Increment alpha until fully black
        fade_alpha += fade_speed
        if fade_alpha >= 255:
            fade_alpha = 255
            current_state = LEVEL_LOADED

        # Redraw the RUNNING state elements (needed if the fade surface is translucent)
        screen.blit(map_bottom, (0, 0))
        pygame.draw.rect(screen, (0, 255, 0), player)
        screen.blit(top, (0, 0))

        # Create and draw the transparent black surface
        fade_surface = pygame.Surface((sw, sh))
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))

        # --- State: LEVEL_LOADED ---
    elif current_state == LEVEL_LOADED:
        # Draw pure black background
        screen.fill((0, 0, 0))
        level_text = font.render("Level 1: Interior (Placeholder)", True, (255, 255, 255))
        text_rect = level_text.get_rect(center=(sw // 2, sh // 2))
        screen.blit(level_text, text_rect)

        return_text = font.render("Press SPACE to return OUTSIDE", True, (150, 150, 150))
        return_rect = return_text.get_rect(center=(sw // 2, sh // 2 + 50))
        screen.blit(return_text, return_rect)

        # Check for return input
        if keys[pygame.K_SPACE]:
            current_state = RUNNING
            fade_alpha = 0
            # Force player to respawn near the door location on map 0
            current_map_key, map_bottom, top, walls, collisions, door_rect = switch_map(entered_map, 'door', player, maps, player_x=entered_x, player_y=(entered_y))

    elif current_state == PAUSED:
        screen.fill((0, 0, 0))
        level_text = font.render("PAUSED ------ press c to continue", True, (255, 255, 255))
        text_rect = level_text.get_rect(center=(sw // 2, sh // 2))
        screen.blit(level_text, text_rect)
        if keys[pygame.K_c]: current_state = RUNNING


    pygame.display.update()

pygame.quit()

