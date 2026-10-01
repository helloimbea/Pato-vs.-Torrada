"""General game settings: screen, colors, positions, timings and balancing.

Almost every "magic number" in the game lives here, so it is easy to tweak.
"""
import os

# --- Folders ---
GAME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(GAME_DIR, 'assets', 'images')
SOUNDS_DIR = os.path.join(GAME_DIR, 'assets', 'sounds')

# --- Screen ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TITLE = 'Duck vs. Toast'
FONT_SIZE = 48
FPS = 30  # frame rate limit (the game has no animations yet)

# --- Colors ---
RED = (234, 95, 112)
BLUE = (121, 161, 191)
LIGHT_BLUE = (207, 228, 245)
GREEN = (114, 167, 139)
TIMER_BLUE = (108, 137, 244)

# --- Toast (clickable area) ---
TOAST_RECT = (510, 201, 260, 242)  # x, y, width, height

# --- Toast health bar ---
HEALTH_BAR_POS = (518, 160)
HEALTH_BAR_WIDTH = 243
HEALTH_BAR_HEIGHT = 20

# --- Round buttons (center position and radius) ---
LEVEL_ADVANCE_BUTTON_POS = (1121, 127)
LEVEL_ADVANCE_BUTTON_RADIUS = 40
PREVIOUS_LEVEL_BUTTON_POS = (1047, 79)
PREVIOUS_LEVEL_BUTTON_RADIUS = 20
SHOP_BUTTON_RADIUS = 40

# --- Text positions ---
HEALTH_TEXT_POS = (541, 115)
DUCKCOINS_TEXT_POS = (130, 45)
DPS_TEXT_POS = (110, 145)
DAMAGE_TEXT_POS = (72, 235)
REWARD_TEXT_POS = (610, 448)
BOSS_TIMER_TEXT_POS = (711, 114)
LEVEL_TEXT_POS = (1100, 68)

# --- Timings (in milliseconds) ---
DPS_INTERVAL = 1000                  # how often DPS damage is applied (1000 = once per second)
AUTO_CLICK_INTERVAL_START = 2000     # starting auto-click interval (muscular duck)
AUTO_CLICK_INTERVAL_MIN = 200        # the interval never goes below this
AUTO_CLICK_INTERVAL_STEP = 50        # how much the interval drops per purchase
BOSS_TIME_LIMIT = 10000

# --- Balancing ---
STARTING_DAMAGE = 1
STARTING_DPS_BASE = 12.5  # DPS added by each Siamese duck
BOSS_EVERY_N_LEVELS = 5

# --- Developer mode ---
# Turn on while developing: enables the P cheat and prints where the mouse clicked
# (handy for placing things on screen). Keep it False for players.
DEV_MODE = False
CHEAT_DUCKCOINS = 1000000000000  # amount gained when pressing P (dev mode only)
