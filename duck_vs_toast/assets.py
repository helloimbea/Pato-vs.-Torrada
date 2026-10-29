"""Loading images and sounds.

Images can be drawn two ways:
- on a full 1280x720 canvas, in the spot where they go on screen (the old way); or
- cropped to just the drawing, with its position in assets/images/positions.json.

`python -m tools.crop_images` turns the first kind into the second. In the game both look
the same: every image becomes a Sprite (the drawing plus where it goes).
"""
import json
import os
from dataclasses import dataclass

import pygame

from . import config, i18n


def load_image(category, name):
    path = os.path.join(config.IMAGES_DIR, category, name)
    return pygame.image.load(path).convert_alpha()


def load_positions():
    try:
        with open(config.POSITIONS_FILE) as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


@dataclass
class Sprite:
    image: pygame.Surface
    pos: tuple  # where its top-left corner goes on screen

    @property
    def rect(self):
        return self.image.get_rect(topleft=self.pos)

    def draw(self, screen):
        screen.blit(self.image, self.pos)


def make_sprite(image, key, positions):
    """Turn a loaded image into a Sprite. Full-screen drawings are cropped to the drawing itself."""
    if image.get_size() == (config.SCREEN_WIDTH, config.SCREEN_HEIGHT):
        area = image.get_bounding_rect()
        return Sprite(image.subsurface(area).copy(), area.topleft)
    if key not in positions:
        raise ValueError(
            f'{key}.png is smaller than the screen, so the game needs to know where it goes. '
            f'Draw it on a 1280x720 canvas, or add "{key}": [x, y] to assets/images/positions.json.')
    return Sprite(image, tuple(positions[key]))


def load_folder(category, positions):
    """Load every .png image in a folder as Sprites.

    Returns a dict {file_name_without_extension: sprite}.
    To add a new image, just drop the file in the right folder.
    """
    folder = os.path.join(config.IMAGES_DIR, category)
    sprites = {}
    for file_name in sorted(os.listdir(folder)):
        name, extension = os.path.splitext(file_name)
        if extension.lower() == '.png':
            image = load_image(category, file_name)
            sprites[name] = make_sprite(image, f'{category}/{name}', positions)
    return sprites


class GameFont(pygame.font.Font):
    """A font that also knows how far to move its texts down (nudge) to sit like the default font."""
    nudge = 0


def digit_box(font):
    return font.render('0', True, (0, 0, 0)).get_bounding_rect()


def load_font(size, name=None):
    """The game's text font (config.TEXT_FONT) at about the same size as Pygame's default font.

    Fonts draw letters of different sizes and heights, so the size is adjusted until a digit
    is as tall as in the default font, and texts are moved to sit at the same height;
    changing fonts then keeps texts in their boxes.
    """
    file_name = config.FONTS.get(name or config.TEXT_FONT)
    path = os.path.join(config.FONTS_DIR, file_name) if file_name else None
    if path is None or not os.path.exists(path):
        return pygame.font.SysFont(None, size)
    default = digit_box(pygame.font.SysFont(None, size))
    height = max(digit_box(GameFont(path, size)).height, 1)
    font = GameFont(path, max(1, round(size * default.height / height)))
    font.nudge = default.top - digit_box(font).top
    return font


def crop_with_margin(image, margin=0.08):
    """Crop a drawing to itself, leaving a small see-through margin around it.

    Without the margin, shrinking the drawing trims the soft edge of its outline where it
    touches the border (the hand's thumb and fingertip looked cut off).
    """
    area = image.get_bounding_rect()
    pad = max(2, round(max(area.size) * margin))
    cropped = pygame.Surface((area.width + 2 * pad, area.height + 2 * pad), pygame.SRCALPHA)
    cropped.blit(image, (pad, pad), area)
    return cropped


def load_cursor(name):
    """A mouse cursor drawn by the owner (assets/images/cursors/<name>.png), or None if missing.

    The drawing is cropped and made CURSOR_SIZE big. The spot that clicks is the tip of the
    pointing finger for 'pointer' (the drawing's highest point) and the middle for 'grab'.
    """
    path = os.path.join(config.CURSORS_DIR, name + '.png')
    if not os.path.exists(path):
        return None
    image = pygame.image.load(path).convert_alpha()
    image = crop_with_margin(image)
    scale = config.CURSOR_SIZE / max(image.get_size())
    image = pygame.transform.smoothscale(
        image, (max(1, round(image.get_width() * scale)), max(1, round(image.get_height() * scale))))
    if name == 'pointer':
        width = image.get_width()
        top_row = next(y for y in range(image.get_height())
                       if any(image.get_at((x, y)).a > 128 for x in range(width)))
        tip = [x for x in range(width) if image.get_at((x, top_row)).a > 128]
        hotspot = (tip[len(tip) // 2], top_row)
    else:
        hotspot = (image.get_width() // 2, image.get_height() // 2)
    return pygame.cursors.Cursor(hotspot, image)


def load_icon(name, size):
    """A small drawing from assets/images/icons, cropped and made `size` pixels big (its longest side)."""
    image = load_image('icons', name + '.png')
    image = crop_with_margin(image)
    scale = size / max(image.get_size())
    return pygame.transform.smoothscale(
        image, (max(1, round(image.get_width() * scale)), max(1, round(image.get_height() * scale))))


def is_bread(color):
    """Bread and crust are warm colors; the sky and floor are blue; the gold coin has little blue."""
    return color.r > color.b + 25 and color.b > 95


def erase_bread(game_map):
    """Erase the bread slice painted on the old map: each toast drawing has its own bread now.

    The hole is filled with the sky and floor, blending the colors at both sides of each row.
    A map drawn without the bread is returned as it is.
    """
    width, height = game_map.get_size()
    start = pygame.Rect(config.TOAST_RECT).center
    bread = pygame.mask.Mask((width, height))
    to_visit = [start]
    while to_visit:  # flood fill: every bread-colored pixel connected to the middle of the slice
        x, y = to_visit.pop()
        if 0 <= x < width and 0 <= y < height and not bread.get_at((x, y)) \
                and is_bread(game_map.get_at((x, y))):
            bread.set_at((x, y))
            to_visit += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    if bread.count() < 1000:  # no bread painted here
        return game_map

    # Grow the shape a little so the soft edge of the crust goes too
    grown = pygame.mask.Mask((width, height))
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            grown.draw(bread, (dx, dy))
    box = grown.get_bounding_rects()[0]

    background = game_map.copy()
    left_x, right_x = box.left - 1, box.right
    for y in range(box.top, box.bottom):
        left, right = game_map.get_at((left_x, y)), game_map.get_at((right_x, y))
        for x in range(box.left, box.right):
            if not grown.get_at((x, y)):
                continue
            color = game_map.get_at((x, y))
            if color.r > color.b + 25 and not is_bread(color):  # the reward coin drawn over the bread
                continue
            t = (x - left_x) / (right_x - left_x)
            background.set_at((x, y), left.lerp(right, t))
    return background


def differs(color, background, threshold=24):
    return abs(color.r - background.r) + abs(color.g - background.g) + abs(color.b - background.b) > threshold


def cut_out(game_map, area, reference_x):
    """Take a drawing out of the map: every pixel in `area` that isn't the background.

    The background of each row is the color at x = reference_x on that row (a spot next to
    the drawing). Returns (map without the drawing, Sprite of the drawing); the hole is
    painted with the background.
    """
    area = pygame.Rect(area)
    inside = pygame.mask.Mask(area.size)
    for y in range(area.top, area.bottom):
        background = game_map.get_at((reference_x, y))
        for x in range(area.left, area.right):
            if differs(game_map.get_at((x, y)), background):
                inside.set_at((x - area.left, y - area.top))
    grown = pygame.mask.Mask(area.size)  # a little bigger, to catch the soft edges
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            grown.draw(inside, (dx, dy))
    piece = pygame.Surface(area.size, pygame.SRCALPHA)
    without = game_map.copy()
    for y in range(area.top, area.bottom):
        background = game_map.get_at((reference_x, y))
        for x in range(area.left, area.right):
            if grown.get_at((x - area.left, y - area.top)):
                piece.set_at((x - area.left, y - area.top), game_map.get_at((x, y)))
                without.set_at((x, y), background)
    return without, Sprite(piece, area.topleft)


def is_box_blue(color):
    """The blue paint of the stats boxes (not their icons, not see-through edges)."""
    return color.a > 0 and color.b > color.r + 12 and color.b > 120


def erase_icons(panel, areas, panel_pos):
    """Paint the old icons in the stats boxes over with the box's own blue (row by row)."""
    for area in areas:
        area = pygame.Rect(area).move(-panel_pos[0], -panel_pos[1])
        for y in range(area.top, area.bottom):
            paint = None
            for x in range(max(area.left - 6, 0), area.right):
                color = panel.get_at((x, y))
                if x < area.left:
                    if is_box_blue(color):
                        paint = color
                elif is_box_blue(color):
                    paint = color
                elif paint is not None and color.a > 0:
                    panel.set_at((x, y), paint)


def recolor(image, target):
    """Paint the blue of a drawing with `target`, keeping its brush strokes (lighter and darker spots)."""
    blues = [image.get_at((x, y)) for x in range(0, image.get_width(), 3)
             for y in range(0, image.get_height(), 3) if is_box_blue(image.get_at((x, y)))]
    if not blues:
        return
    middle = sum(color.r + color.g + color.b for color in blues) / len(blues)
    for x in range(image.get_width()):
        for y in range(image.get_height()):
            color = image.get_at((x, y))
            if is_box_blue(color):
                light = (color.r + color.g + color.b) / middle
                image.set_at((x, y), tuple(min(255, round(part * light)) for part in target) + (color.a,))


def cut_stats_panel(game_map):
    """Take the Duckcoins, DPS and damage boxes out of the map, so they can stay in the corner.

    Their old coin and sword icons are erased (the game draws the new coin and the mouse
    drawing there) and their blue is painted with the palette's panel color.
    Returns (map without the boxes, boxes Sprite).
    """
    area = pygame.Rect(config.STATS_BOXES[0]).unionall(config.STATS_BOXES)
    panel = pygame.Surface(area.size, pygame.SRCALPHA)
    for box in config.STATS_BOXES:
        game_map, piece = cut_out(game_map, box, area.right + 15)
        panel.blit(piece.image, (piece.pos[0] - area.left, piece.pos[1] - area.top))
    erase_icons(panel, config.OLD_ICON_AREAS, area.topleft)
    recolor(panel, config.PANEL)
    return game_map, Sprite(panel, area.topleft)


def cut_portraits(game_map):
    """The round duck portraits of the map's old shop, for the new shop: {duck name: Sprite}."""
    portraits = {}
    for name, (x, y, diameter) in config.SHOP_PORTRAITS.items():
        # Exactly the round portrait (its old soft shadow is left behind; the shop draws one)
        size = round(diameter) + 2
        area = pygame.Rect(round(x - size / 2), round(y - size / 2), size, size)
        circle = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(circle, (255, 255, 255, 255), (size / 2, size / 2), diameter / 2)
        portrait = pygame.Surface((size, size), pygame.SRCALPHA)
        portrait.blit(game_map, (0, 0), area)
        portrait.blit(circle, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)  # keep only the circle
        portraits[name] = Sprite(portrait, area.topleft)
    return portraits


def split_map(game_map):
    """Split the map in the parts the game uses (see MapParts)."""
    game_map = erase_bread(game_map)
    game_map, heart = cut_out(game_map, config.HEART_RECT, config.HEART_RECT[0] - 6)
    badge = config.REWARD_BADGE_RECT
    game_map, _ = cut_out(game_map, badge, badge[0] - 6)  # the old "+ coin" (drawn by the game now)
    game_map, stats_panel = cut_stats_panel(game_map)
    portraits = cut_portraits(game_map)

    width = game_map.get_width()
    background = game_map.subsurface((0, 0, width, config.SHOP_TOP)).copy()
    floor_row = background.subsurface((0, config.SHOP_TOP - 1, width, 1)).copy()
    return MapParts(background, floor_row, stats_panel, heart, portraits)


def localized(sprites, name):
    """The drawing for the current language: "<name>_en" in English when it exists.

    The drawings as they are now are the Portuguese ones (see i18n.py).
    """
    if i18n.language != 'pt' and f'{name}_{i18n.language}' in sprites:
        return sprites[f'{name}_{i18n.language}']
    return sprites.get(name)


@dataclass
class MapParts:
    """The map split so each part can follow its edge of the window (see layout.py)."""
    background: pygame.Surface   # sky and floor (the bread and the drawings below are erased)
    floor_row: pygame.Surface    # the floor's last line, repeated down to the bottom
    stats_panel: Sprite          # the Duckcoins, DPS and damage boxes
    heart: Sprite                # the heart next to the toast's health
    portraits: dict              # the round duck portraits for the shop


class Assets:
    """Holds every image and sound in the game.

    Must be created after pygame.display.set_mode().
    """

    def __init__(self):
        positions = load_positions()
        self.ducks = load_folder('ducks', positions)
        self.toasts = load_folder('toasts', positions)
        self.ui = load_folder('ui', positions)
        self.coin = load_icon('coin', config.COIN_SIZE)  # the flying coins
        self.coin_icons = {}  # the coin at other sizes, made when first needed
        self.maps = {'pt': split_map(self.load_map('map1.png'))}  # one per language, when needed
        self.cursors = {name: load_cursor(name) for name in ('pointer', 'grab')}
        self.click_sound = None  # stays None when there is no audio device (e.g. Codespaces)
        if pygame.mixer.get_init():
            self.click_sound = pygame.mixer.Sound(os.path.join(config.SOUNDS_DIR, 'quack.wav'))

    def coin_icon(self, size):
        if size not in self.coin_icons:
            self.coin_icons[size] = load_icon('coin', size)
        return self.coin_icons[size]

    @staticmethod
    def load_map(file_name):
        game_map = load_image('maps', file_name)
        return pygame.transform.scale(game_map, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

    def map_parts(self):
        """The map for the current language: maps/map1_en.png in English, when it exists."""
        language = i18n.language
        if language not in self.maps:
            path = os.path.join(config.IMAGES_DIR, 'maps', f'map1_{language}.png')
            self.maps[language] = split_map(self.load_map(os.path.basename(path))) \
                if os.path.exists(path) else self.maps['pt']
        return self.maps[language]
