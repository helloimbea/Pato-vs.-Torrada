"""General game settings: screen, colors, positions, timings and balancing.

Almost every "magic number" in the game lives here, so it is easy to tweak.
"""
import os

# --- Folders ---
GAME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(GAME_DIR, 'assets', 'images')
SOUNDS_DIR = os.path.join(GAME_DIR, 'assets', 'sounds')
FONTS_DIR = os.path.join(GAME_DIR, 'assets', 'fonts')
POSITIONS_FILE = os.path.join(IMAGES_DIR, 'positions.json')  # where each cropped image goes

# --- Screen ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)  # the size the art is drawn at
FONT_SIZE = 48
SMALL_FONT_SIZE = 28  # purchase counters and tooltips

# --- Text font ---
# Every text in the game is written with this font (in assets/fonts; all are free to use,
# see the -OFL.txt file next to each). To compare them: python -m tools.preview_fonts
FONTS = {
    'patrick_hand': 'PatrickHand-Regular.ttf',
    'itim': 'Itim-Regular.ttf',
    'indie_flower': 'IndieFlower-Regular.ttf',
    'mali': 'Mali-Bold.ttf',
    'short_stack': 'ShortStack-Regular.ttf',
}
TEXT_FONT = 'patrick_hand'
INK = (66, 66, 72)               # dark gray, like the pencil of the drawings
TOAST_TITLE_CENTER = (640, 52)   # the toast's name, above it
TOAST_TITLE_SIZE = 56
TOAST_TITLE_MAX_WIDTH = 400     # longer names are made smaller (the ducks are beside it)
SHOP_TITLE_TOP = 503             # the ducks' names in the shop, above their portraits...
SHOP_TITLE_SIZE = 32
SHOP_TITLE_LINE = 1.4            # from one line of a name to the next, in capital letters' heights
SHOP_TITLE_MAX_WIDTH = 200
SHOP_TITLE_AREA = (497, 568)     # ...where the old handwritten names are erased from the map
FPS = 30  # frame rate limit

# --- Resizable window (see layout.py) ---
# The map is split in parts that follow the window's edges:
SHOP_TOP = 472                     # the shop panel starts at this line, stuck to the bottom
# The Duckcoins, DPS and damage boxes (x, y, width, height), stuck to the top left
STATS_BOXES = [(26, 6, 316, 112), (26, 116, 240, 88), (26, 206, 140, 86)]
# When the window is wider, the background and shop keep their left and right ends at the
# window's edges and stretch the plain part between these x positions
BACKGROUND_STRETCH = (260, 1080)
SHOP_STRETCH = (40, 1240)

# --- Colors ---
RED = (234, 95, 112)
BLUE = (121, 161, 191)
LIGHT_BLUE = (207, 228, 245)
GREEN = (114, 167, 139)
TIMER_BLUE = (108, 137, 244)
DARK_BLUE = (62, 84, 110)
TOOLTIP_BACKGROUND = (240, 246, 252)
BOOST_COLOR = (240, 170, 50)  # numbers boosted by the Bourgeois Duck

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
LANGUAGE_BUTTON_POS = (1252, 70)
LANGUAGE_BUTTON_RADIUS = 18
SHOP_BUTTON_RADIUS = 40

# --- Shop extras ---
PURCHASE_COUNT_OFFSET = (48, -12)  # where "x3" is written, relative to each buy button's center
BOURGEOIS_BUTTON_POS = (1125, 603)

# The round duck portraits drawn on the shop: (center x, center y, diameter).
# The "locked" sign (ui/locked.png) was drawn over the Siamese duck's portrait; on the
# others it is resized and moved to fit their circle. A duck missing here uses the
# Siamese size, centered on its buy button.
SHOP_PORTRAITS = {
    'siamese_duck': (155.5, 617, 86),
    'double_duck': (398.5, 614, 85),
    'muscular_duck': (643.5, 611, 83),
    'realistic_duck': (882.5, 608.5, 79),
    'bourgeois_duck': (1125.5, 613.5, 81),
}

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
# How strongly the toast reacts to each kind of hit (1 = the full reaction to a click):
# the shake, the squash and how long the pained face stays all get this much smaller.
HIT_STRENGTH = {'click': 1.0, 'auto': 0.6, 'dps': 0.4, 'smack': 1.5, 'smack_crit': 2.0}
AUTO_CLICK_TIP = (738, 355)    # tip of the muscular duck's pointer: its damage numbers pop up here
REWARD_BADGE_RECT = (495, 430, 115, 60)  # the "+ coin" under the toast, drawn in front of it
TOAST_TITLE_BOTTOM = 130       # the toast images have their name above this line; it doesn't squish
DEATH_DURATION = 220           # a beaten toast shrinks away this fast
DEATH_TINT = (165, 165, 175)   # grayish tint used while a toast has no "_dead" drawing yet
SPAWN_DELAY = 180              # the next toast pops up this long after the old one starts shrinking
SPAWN_DURATION = 300           # how long the next toast takes to pop up
DUCK_POP_DURATION = 500        # a duck stretches and squashes for this long when bought
DUCK_POP_STRETCH = 0.25        # at most 25% taller (and a bit thinner), then shorter and wider
DUCK_GROW_TIME = 200           # a duck bought for the first time grows from nothing this fast
COINS_PER_DEFEAT = 6
COIN_DELAY = 60                # coins leave the toast one after another
COIN_BURST_TIME = 250          # coins pop out of the toast...
COIN_FLIGHT_TIME = 550         # ...then fly to the Duckcoins counter
COIN_SIZE = 34
COUNTER_SPEED = 150            # the Duckcoins counter rolls up to new Duckcoins (smaller = faster)
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

# --- Bourgeois Duck ---
BOURGEOIS_COST = 10_000_000          # fixed price (it doesn't go up)
BOURGEOIS_DURATION = 60_000          # the boost lasts 1 minute...
BOURGEOIS_COOLDOWN = 600_000         # ...and it can be bought again 10 minutes after buying
BOURGEOIS_DAMAGE_MULTIPLIER = 2      # all damage (clicks, DPS, muscular duck) while boosted
BOURGEOIS_REWARD_MULTIPLIER = 2      # Duckcoins from each toast while boosted
BOURGEOIS_COST_TEXT_POS = (1105, 675)

# --- Smacking with the muscular duck (a secret: nothing in the game tells about it) ---
SMACK_DAMAGE = 5               # a smack does 5 times the click damage...
SMACK_CRIT_CHANCE = 0.15       # ...and 15% of the smacks are critical hits...
SMACK_CRIT_MULTIPLIER = 5      # ...that do 5 times more (25 clicks)
SMACKS_BEFORE_REST = 5         # after this many smacks the duck goes away to rest...
MUSCULAR_REST = 120_000        # ...for 2 minutes, and does no damage meanwhile
SMACK_MARGIN = 20              # the duck has to go this far into the toast to smack it
GRAB_ALPHA = 60                # only grab the duck by its drawing, not its see-through corners
HELD_LIFT = 1.08               # the held duck looks a bit bigger, as if picked up
RETURN_TIME = 450              # how long the duck takes to hop back to its spot when let go
RETURN_ARC = 60                # how high it hops on the way back
RESTING_TINT = (170, 170, 180)  # a resting duck is grayish...
RESTING_ALPHA = 140            # ...and see-through (0 = invisible, 255 = solid)
CRIT_COLOR = (240, 170, 50)    # critical hit numbers
SCREEN_SHAKE = {'smack': 7, 'smack_crit': 16}  # how many pixels the whole screen shakes
SCREEN_SHAKE_DURATION = 280
GRAB_CURSOR_FILE = os.path.join(IMAGES_DIR, 'cursors', 'grab.png')  # optional drawing
GRAB_CURSOR_HOTSPOT = (16, 16)  # the spot of the cursor that points (from its top-left corner)

# --- Saving and offline earnings ---
SAVE_FILE = os.path.join(os.path.expanduser('~'), '.duck_vs_toast', 'save.json')
AUTOSAVE_INTERVAL = 30_000           # the game also saves when it is closed
OFFLINE_LIMIT_HOURS = 8              # Duckcoins are earned for at most this long while closed
OFFLINE_MINIMUM_SECONDS = 60         # shorter breaks don't show the "welcome back" message

# --- Screens ---
TITLE_FONT_SIZE = 80
OVERLAY_COLOR = (40, 55, 80, 150)    # darkens the game behind the start/pause/victory screens

# --- Developer mode ---
# Turn on while developing: enables the P cheat and prints where the mouse clicked
# (handy for placing things on screen). Keep it False for players.
DEV_MODE = False
CHEAT_DUCKCOINS = 1000000000000  # amount gained when pressing P (dev mode only)
