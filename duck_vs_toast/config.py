"""General game settings: screen, colors, positions, timings and balancing.

Almost every "magic number" in the game lives here, so it is easy to tweak.
"""
import os

# --- Folders ---
GAME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(GAME_DIR, 'assets', 'images')
SOUNDS_DIR = os.path.join(GAME_DIR, 'assets', 'sounds')
FONTS_DIR = os.path.join(GAME_DIR, 'assets', 'fonts')
CURSORS_DIR = os.path.join(IMAGES_DIR, 'cursors')  # pointer.png (always) and grab.png (holding a duck)
CURSOR_SIZE = 44  # the cursor drawings are made this big (their longest side, in pixels)
POSITIONS_FILE = os.path.join(IMAGES_DIR, 'positions.json')  # where each cropped image goes

# --- Screen ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)  # the size the art is drawn at
FONT_SIZE = 48
SMALL_FONT_SIZE = 28  # tooltips
FPS = 30  # frame rate limit

# --- Fonts ---
# Texts are written with TEXT_FONT, and the big numbers (health, Duckcoins, level) with the
# chunkier NUMBER_FONT. All are in assets/fonts and free to use (see the -OFL.txt next to
# each). To compare the text fonts: python -m tools.preview_fonts
FONTS = {
    'patrick_hand': 'PatrickHand-Regular.ttf',
    'itim': 'Itim-Regular.ttf',
    'indie_flower': 'IndieFlower-Regular.ttf',
    'mali': 'Mali-Bold.ttf',
    'short_stack': 'ShortStack-Regular.ttf',
    'lilita_one': 'LilitaOne-Regular.ttf',
}
TEXT_FONT = 'patrick_hand'
NUMBER_FONT = 'lilita_one'

# --- Colors: the game's palette. Each color means one thing, everywhere ---
PANEL = (252, 248, 240)        # boxes, the shop, menus and tooltips: cream, like paper
PANEL_EDGE = (214, 198, 172)   # their border
INK = (66, 66, 72)             # texts: dark gray, like the pencil of the drawings
INK_SOFT = (120, 112, 104)     # less important texts
GOLD = (245, 180, 40)          # Duckcoins (and only Duckcoins)
GOLD_DARK = (140, 86, 10)      # the outline of gold numbers
HEALTH_RED = (232, 78, 94)     # health and danger
HEALTH_RED_DARK = (150, 38, 52)
HEALTH_TRACK = (240, 226, 222)  # the empty part of the health bar
GREEN = (84, 170, 106)         # gains
GREEN_DARK = (34, 96, 52)
SHADE = (95, 100, 120)         # ducks the player can't buy yet are darkened with this
RED = HEALTH_RED               # damage numbers
TIMER_BLUE = (108, 137, 244)   # damage numbers of the DPS ducks
TOOLTIP_BACKGROUND = PANEL
BOOST_COLOR = (240, 170, 50)   # numbers boosted by the Bourgeois Duck

# --- Resizable window (see layout.py) ---
# The map is split in parts that follow the window's edges:
SHOP_TOP = 472                     # the old shop panel of the map starts here (it isn't drawn)
# The Duckcoins, DPS and damage boxes (x, y, width, height), stuck to the top left
STATS_BOXES = [(26, 6, 316, 112), (26, 116, 240, 88), (26, 206, 140, 86)]
# When the window is wider, the background keeps its left and right ends at the window's
# edges and stretches the plain part between these x positions
BACKGROUND_STRETCH = (260, 1080)
CENTER_DROP = 90                   # the toast and the ducks are this much lower than in the map,
                                   # to make room for the level buttons above the toast's name

# --- Toast (in the toast's part of the screen, before CENTER_DROP) ---
TOAST_RECT = (510, 201, 260, 242)  # x, y, width, height: where clicks hit the toast
TOAST_TITLE_CENTER = (640, 68)     # the toast's name, above it
TOAST_TITLE_SIZE = 56
TOAST_TITLE_MAX_WIDTH = 400        # longer names are made smaller (the ducks are beside it)
HEALTH_TEXT_CENTER = (652, 112)    # "3.3 K / 4.4 K", with the heart before it
HEALTH_TEXT_SIZE = 40
HEALTH_BAR = (515, 140, 250, 24)   # x, y, width, height (it has round ends)
HEART_RECT = (480, 108, 55, 48)    # the heart drawn on the map, moved next to the health
BOSS_TIMER_CENTER = (500, 152)     # the boss's countdown, in a circle at the bar's left end
BOSS_TIMER_RADIUS = 30             # (ui/boss_timer.png, when drawn, is used instead of the circle)
BOSS_TIMER_HURRY = 3               # the last seconds are red and the circle pulses
BOSS_TAG_ANGLE = 12                # the "BOSS" label on the toast's name is tilted this much
REWARD_CENTER = (640, 470)         # "+ (coin) 1.2 K" under the toast
REWARD_BADGE_RECT = (495, 430, 115, 60)  # the old "+ coin" drawn on the map (erased)

# --- Stats (top left) ---
DUCKCOINS_ICON_POS = (82, 61)      # center of the coin in the Duckcoins box
DUCKCOINS_ICON_SIZE = 62
DAMAGE_ICON_POS = (55, 249)        # center of the click-damage icon (the mouse drawing)
DAMAGE_ICON_SIZE = 46
OLD_ICON_AREAS = [(46, 26, 74, 72), (28, 220, 52, 58)]  # the old coin and sword, erased
DUCKCOINS_TEXT_LEFT = (128, 62)    # left end and middle height of the numbers
DPS_TEXT_LEFT = (110, 161)
DAMAGE_TEXT_LEFT = (88, 250)
DUCKCOINS_TEXT_SIZE = 52
STAT_TEXT_SIZE = 40

# --- Level buttons (top center) ---
LEVEL_ADVANCE_BUTTON_POS = (640, 109)  # the lock under the level: farm the same level or advance
LEVEL_ADVANCE_BUTTON_RADIUS = 24
PREVIOUS_LEVEL_BUTTON_POS = (566, 61)
NEXT_LEVEL_BUTTON_POS = (722, 61)
LEVEL_ARROW_RADIUS = 24
LEVEL_TEXT_CENTER = (640, 64)
LEVEL_TEXT_SIZE = 52

# --- Settings (top right) ---
GEAR_POS = (1240, 38)          # the gear button opens a menu with the sound and language buttons
GEAR_RADIUS = 26
MENU_STEP = 52                 # from one button of the menu to the next
MENU_BUTTON_RADIUS = 22

# --- Shop (bottom): a panel that slides up when its button is clicked ---
SHOP_PANEL = (24, 572, 1232, 140)  # x, y, width, height when open
SHOP_PORTRAIT_Y = 68               # the ducks' middle, from the top of the panel
SHOP_TAB_SIZE = (170, 46)          # the shop's button
SHOP_TAB_TEXT_SIZE = 36
SHOP_SLIDE_TIME = 260
SHOP_HOP_EVERY = 1600              # ducks the player can buy hop (and glow) every 1.6 s
SHOP_HOP_HEIGHT = 10
COUNT_BADGE_RADIUS = 14            # the bubble with how many of a duck were bought
# The round duck portraits drawn on the map's old shop: (center x, center y, diameter).
# They are cut out of the map and shown in the new shop, in this order from left to right.
SHOP_PORTRAITS = {
    'siamese_duck': (155.5, 617, 86),
    'double_duck': (398.5, 614, 85),
    'muscular_duck': (643.5, 611, 83),
    'realistic_duck': (882.5, 608.5, 79),
    'bourgeois_duck': (1125.5, 613.5, 81),
}

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
