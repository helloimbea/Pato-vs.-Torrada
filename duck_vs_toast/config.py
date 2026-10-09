"""General game settings: screen, colors, positions, timings and balancing.

Almost every "magic number" in the game lives here, so it is easy to tweak.
"""
import os

# --- Folders ---
GAME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(GAME_DIR, 'assets', 'images')
SOUNDS_DIR = os.path.join(GAME_DIR, 'assets', 'sounds')
POSITIONS_FILE = os.path.join(IMAGES_DIR, 'positions.json')  # where each cropped image goes

# --- Screen ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TITLE = 'Duck vs. Toast'
FONT_SIZE = 48
SMALL_FONT_SIZE = 28  # purchase counters and tooltips
FPS = 30  # frame rate limit

# --- Colors ---
RED = (234, 95, 112)
BLUE = (121, 161, 191)
LIGHT_BLUE = (207, 228, 245)
GREEN = (114, 167, 139)
TIMER_BLUE = (108, 137, 244)
DARK_BLUE = (62, 84, 110)
TOOLTIP_BACKGROUND = (240, 246, 252)

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
NEXT_LEVEL_BUTTON_POS = (1203, 79)
NEXT_LEVEL_BUTTON_RADIUS = 20
SOUND_BUTTON_POS = (1252, 26)
SOUND_BUTTON_RADIUS = 18
SHOP_BUTTON_RADIUS = 40

# --- Shop extras ---
PURCHASE_COUNT_OFFSET = (48, -12)  # where "x3" is written, relative to each buy button's center
BOURGEOIS_BUTTON_POS = (1125, 603)

# --- Text positions ---
HEALTH_TEXT_POS = (541, 115)
DUCKCOINS_TEXT_POS = (130, 45)
DPS_TEXT_POS = (110, 145)
DAMAGE_TEXT_POS = (72, 235)
REWARD_TEXT_POS = (610, 448)
BOSS_TIMER_TEXT_POS = (711, 114)
LEVEL_TEXT_POS = (1100, 68)

# --- Animations (times in milliseconds) ---
DAMAGE_NUMBER_DURATION = 800   # how long a damage number stays on screen
DAMAGE_NUMBER_RISE = 70        # how many pixels it floats up
MAX_DAMAGE_NUMBERS = 25        # older numbers disappear when there are more than this
SHAKE_DURATION = 150           # how long the toast shakes after a hit
SHAKE_STRENGTH = 5             # how many pixels it moves while shaking
SQUISH_DURATION = 180          # how long the toast flinches (squashes) after a hit
SQUISH_WIDTH = 0.08            # at most 8% wider...
SQUISH_HEIGHT = 0.14           # ...and 14% shorter
HURT_DURATION = 300            # how long the pained face stays
HURT_TINT = (255, 205, 205)    # reddish tint used while a toast has no "_hurt" drawing yet
REWARD_BADGE_RECT = (495, 430, 115, 60)  # the "+ coin" under the toast, drawn in front of it
TOAST_TITLE_BOTTOM = 95        # the toast images have their name above this line; it doesn't squish
COINS_PER_DEFEAT = 6
COIN_DELAY = 60                # coins leave the toast one after another
COIN_BURST_TIME = 250          # coins pop out of the toast...
COIN_FLIGHT_TIME = 550         # ...then fly to the Duckcoins counter
COIN_SIZE = 34
DUCKCOINS_ICON_POS = (82, 61)  # center of the coin drawn in the Duckcoins box (map image)
DUCKCOINS_ICON_RADIUS = 28

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
