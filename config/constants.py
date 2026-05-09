# Game configuration constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# Tile and grid
TILE_SIZE = 16

# Movement speeds (tiles per second)
PLAYER_TPS = 8    # tiles per second for player (faster due to smaller tiles)
ENEMY_TPS = 5     # tiles per second for enemies

# Colors (R,G,B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (100, 100, 100)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Asset placeholders (can be replaced with image file paths later)
ASSETS = {
    'player_skins': [None, None, None],  # placeholders for different player skins
    'enemy_skins': [None]*5,
}

# Display mode
FULLSCREEN = True