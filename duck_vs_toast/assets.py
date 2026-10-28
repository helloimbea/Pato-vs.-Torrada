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


def is_ink(color):
    """The dark gray pencil of the handwritten texts (not the colorful drawings)."""
    brightest, darkest = max(color.r, color.g, color.b), min(color.r, color.g, color.b)
    return brightest < 150 and brightest - darkest < 40


def erase_shop_titles(game_map):
    """Erase the ducks' handwritten names from the shop; the game writes them with the font now.

    The pencil strokes (and their soft edges) are painted over with the panel's color.
    """
    top, bottom = config.SHOP_TITLE_AREA
    area = pygame.Rect(0, top, config.SCREEN_WIDTH, bottom - top)
    pencil = pygame.mask.Mask(area.size)
    for x in range(area.left, area.right):
        for y in range(area.top, area.bottom):
            if is_ink(game_map.get_at((x, y))):
                pencil.set_at((x, y - area.top))
    grown = pygame.mask.Mask(area.size)  # a little bigger, for the soft edges
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            grown.draw(pencil, (dx, dy))
    erased = game_map.copy()
    for y in range(area.top, area.bottom):
        paper = None
        for x in range(area.left, area.right):
            if not grown.get_at((x, y - area.top)):
                paper = game_map.get_at((x, y))  # the last panel color seen on this row
            elif paper is not None:
                erased.set_at((x, y), paper)
    return erased


def load_cursor(name):
    """A mouse cursor drawn by the owner (assets/images/cursors/<name>.png), or None if missing.

    The drawing is cropped and made CURSOR_SIZE big. The spot that clicks is the tip of the
    pointing finger for 'pointer' (the drawing's highest point) and the middle for 'grab'.
    """
    path = os.path.join(config.CURSORS_DIR, name + '.png')
    if not os.path.exists(path):
        return None
    image = pygame.image.load(path).convert_alpha()
    image = image.subsurface(image.get_bounding_rect()).copy()
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


def cut_coin(game_map):
    """Copy the Duckcoin drawn on the map (top left), for the flying-coin animation."""
    radius = config.DUCKCOINS_ICON_RADIUS
    x, y = config.DUCKCOINS_ICON_POS
    coin = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA)
    mask = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (radius, radius), radius)
    coin.blit(game_map, (0, 0), (x - radius, y - radius, 2 * radius, 2 * radius))
    coin.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)  # keep only the round part
    return pygame.transform.smoothscale(coin, (config.COIN_SIZE, config.COIN_SIZE))


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


def cut_reward_badge(game_map):
    """Copy the green "+" and the coin under the toast, so they stay in front of the bread."""
    badge = pygame.Surface(game_map.get_size(), pygame.SRCALPHA)
    area = pygame.Rect(config.REWARD_BADGE_RECT)
    for x in range(area.left, area.right):
        for y in range(area.top, area.bottom):
            color = game_map.get_at((x, y))
            # Not the blue background and not the bread: the plus sign or the coin
            if (color.r > color.b or color.g > color.b + 20) and not is_bread(color):
                badge.set_at((x, y), color)
    # The coin's face has bread-like colors; take whatever is enclosed by the coin's rim too
    outside = pygame.mask.from_surface(badge.subsurface(area))
    outside.invert()
    for hole in outside.connected_components():
        box = hole.get_bounding_rects()[0]
        if box.left > 0 and box.top > 0 and box.right < area.width and box.bottom < area.height:
            for x in range(box.left, box.right):
                for y in range(box.top, box.bottom):
                    if hole.get_at((x, y)):
                        position = (area.left + x, area.top + y)
                        badge.set_at(position, game_map.get_at(position))
    return make_sprite(badge, 'reward_badge', {})


def cut_stats_panel(game_map):
    """Take the Duckcoins, DPS and damage boxes out of the map, so they can stay in the corner.

    Returns (map without the boxes, boxes Sprite). The hole is filled with the sky or floor
    color of each row, taken just right of the boxes.
    """
    area = pygame.Rect(config.STATS_BOXES[0]).unionall(config.STATS_BOXES)
    reference_x = area.right + 15
    panel = pygame.Surface(area.size, pygame.SRCALPHA)
    without_boxes = game_map.copy()
    for box in config.STATS_BOXES:
        box = pygame.Rect(box)
        inside = pygame.mask.Mask(box.size)  # what differs from the sky or floor around it
        for y in range(box.top, box.bottom):
            background = game_map.get_at((reference_x, y))
            for x in range(box.left, box.right):
                color = game_map.get_at((x, y))
                if abs(color.r - background.r) + abs(color.g - background.g) \
                        + abs(color.b - background.b) > 24:
                    inside.set_at((x - box.left, y - box.top))
        grown = pygame.mask.Mask(box.size)  # a little bigger, to catch the soft edges
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                grown.draw(inside, (dx, dy))
        for y in range(box.top, box.bottom):
            background = game_map.get_at((reference_x, y))
            for x in range(box.left, box.right):
                if grown.get_at((x - box.left, y - box.top)):
                    panel.set_at((x - area.left, y - area.top), game_map.get_at((x, y)))
                    without_boxes.set_at((x, y), background)
    return without_boxes, Sprite(panel, area.topleft)


def split_map(game_map, reward_badge):
    """Split the map in the background (sky and floor) and the shop panel at the bottom.

    The "+ coin" under the toast is taken out of the shop, because it goes with the toast
    (reward_badge draws it). Returns (background, shop Sprite, floor row): the floor row is
    the background's last line without the "+ coin", repeated down when the window is taller.
    """
    width, height = game_map.get_size()
    shop = game_map.subsurface((0, config.SHOP_TOP, width, height - config.SHOP_TOP)).copy()
    badge = reward_badge.rect.inflate(4, 4)
    shape = pygame.mask.Mask(badge.size)  # a little bigger than the badge, for its soft edges
    for dx in range(5):
        for dy in range(5):
            shape.draw(pygame.mask.from_surface(reward_badge.image), (dx, dy))
    for y in range(config.SHOP_TOP, badge.bottom):
        fill = game_map.get_at((badge.left - 10, y))
        for x in range(badge.left, badge.right):
            if shape.get_at((x - badge.left, y - badge.top)):
                shop.set_at((x, y - config.SHOP_TOP), fill)

    background = game_map.subsurface((0, 0, width, config.SHOP_TOP)).copy()
    floor_row = background.subsurface((0, config.SHOP_TOP - 1, width, 1)).copy()
    floor_row.fill(game_map.get_at((badge.left - 10, config.SHOP_TOP - 1)),
                   (badge.left - 5, 0, badge.width + 10, 1))
    return background, Sprite(shop, (0, config.SHOP_TOP)), floor_row


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
    background: pygame.Surface
    shop: Sprite
    floor_row: pygame.Surface
    stats_panel: Sprite


class Assets:
    """Holds every image and sound in the game.

    Must be created after pygame.display.set_mode().
    """

    def __init__(self):
        positions = load_positions()
        self.ducks = load_folder('ducks', positions)
        self.toasts = load_folder('toasts', positions)
        self.ui = load_folder('ui', positions)
        game_map = self.load_map('map1.png')
        self.reward_badge = cut_reward_badge(game_map)
        self.coin = cut_coin(game_map)
        self.maps = {'pt': self.split(game_map)}  # one per language, made when first needed
        self.cursors = {name: load_cursor(name) for name in ('pointer', 'grab')}
        self.click_sound = None  # stays None when there is no audio device (e.g. Codespaces)
        if pygame.mixer.get_init():
            self.click_sound = pygame.mixer.Sound(os.path.join(config.SOUNDS_DIR, 'quack.wav'))

    @staticmethod
    def load_map(file_name):
        game_map = load_image('maps', file_name)
        return pygame.transform.scale(game_map, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

    def split(self, game_map):
        game_map = erase_bread(game_map)
        game_map = erase_shop_titles(game_map)
        game_map, stats_panel = cut_stats_panel(game_map)
        background, shop, floor_row = split_map(game_map, self.reward_badge)
        return MapParts(background, shop, floor_row, stats_panel)

    def map_parts(self):
        """The map for the current language: maps/map1_en.png in English, when it exists."""
        language = i18n.language
        if language not in self.maps:
            path = os.path.join(config.IMAGES_DIR, 'maps', f'map1_{language}.png')
            self.maps[language] = self.split(self.load_map(os.path.basename(path))) \
                if os.path.exists(path) else self.maps['pt']
        return self.maps[language]
