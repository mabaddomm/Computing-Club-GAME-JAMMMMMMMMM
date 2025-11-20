import pygame
import sys

# --- Constants & Initialization ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
FPS = 60

# Game States
MENU = 'MENU'
PLAYING = 'PLAYING'
game_state = MENU

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("The Present Thief - Menu")
clock = pygame.time.Clock()

# --- Asset Loading ---
try:
    # Load and scale the background image
    background_image = pygame.image.load('Title_Screen.png').convert()
    background_image = pygame.transform.scale(background_image, SCREEN_SIZE)
except pygame.error as e:
    print(f"Error loading Title_Screen.png: {e}. Using fallback screen.")
    background_image = pygame.Surface(SCREEN_SIZE)
    background_image.fill(WHITE)

# Define the clickable area for the 'START' button on the image
# (Adjust these values if the click area doesn't perfectly match the image)
BUTTON_WIDTH = 250
BUTTON_HEIGHT = 80
BUTTON_X = (SCREEN_WIDTH // 2) - (BUTTON_WIDTH // 2)  # Center horizontally
BUTTON_Y = 500  # Position lower-middle of the 720px screen
START_BUTTON_RECT = pygame.Rect(BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)

# Font for the Playing screen
font_big = pygame.font.Font(None, 74)

# --- Main Game Loop ---
running = True
while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        if game_state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if the mouse click is within the button's clickable rectangle
                if START_BUTTON_RECT.collidepoint(event.pos):
                    print("Start button clicked!")
                    game_state = PLAYING

    # 2. Rendering
    screen.fill(BLACK)

    if game_state == MENU:
        # Draw the background image
        screen.blit(background_image, (0, 0))

        # DEBUG: Uncomment the line below to see the clickable area outline
        # pygame.draw.rect(screen, (255, 0, 0, 100), START_BUTTON_RECT, 2)

    elif game_state == PLAYING:
        # This is your game's main screen placeholder
        screen.fill(WHITE)
        msg = font_big.render("GAME IS NOW PLAYING!", True, BLACK)
        screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

pygame.quit()
sys.exit()
