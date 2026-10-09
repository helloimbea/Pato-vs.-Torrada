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

from . import config


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


def split_bread(game_map):
    """Take the bread slice out of the map, so it can squash when a toast is hit.

    Only used while there is no separate bread drawing (assets/images/toasts/bread.png):
    the old map has the bread painted on it, and each toast image only adds its face on top.
    Returns (map without the bread, bread Sprite).
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

    # Grow the shape a little so the soft edge of the crust comes along too
    grown = pygame.mask.Mask((width, height))
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            grown.draw(bread, (dx, dy))
    box = grown.get_bounding_rects()[0]

    bread_image = pygame.Surface((width, height), pygame.SRCALPHA)
    background = game_map.copy()
    left_x, right_x = box.left - 1, box.right
    for y in range(box.top, box.bottom):
        # Fill the hole with the background, blending the colors at both sides of the row
        left, right = game_map.get_at((left_x, y)), game_map.get_at((right_x, y))
        for x in range(box.left, box.right):
            if not grown.get_at((x, y)):
                continue
            color = game_map.get_at((x, y))
            if color.r > color.b + 25 and not is_bread(color):  # the reward coin drawn over the bread
                continue
            bread_image.set_at((x, y), color)
            t = (x - left_x) / (right_x - left_x)
            background.set_at((x, y), left.lerp(right, t))
    return background, make_sprite(bread_image, 'bread', {})


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


class Assets:
    """Holds every image and sound in the game.

    Must be created after pygame.display.set_mode().
    """

    def __init__(self):
        game_map = load_image('maps', 'map1.png')
        game_map = pygame.transform.scale(game_map, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        positions = load_positions()
        self.ducks = load_folder('ducks', positions)
        self.toasts = load_folder('toasts', positions)
        self.ui = load_folder('ui', positions)
        if 'bread' in self.toasts:  # the bread drawn on its own, with the map drawn without it
            self.bread = self.toasts.pop('bread')
            self.map = game_map
        else:
            self.map, self.bread = split_bread(game_map)
        self.reward_badge = cut_reward_badge(game_map)
        self.coin = cut_coin(game_map)
        # So each part can follow its edge of the window (see layout.py)
        self.map, self.stats_panel = cut_stats_panel(self.map)
        self.background, self.shop, self.floor_row = split_map(self.map, self.reward_badge)
        self.click_sound = None  # stays None when there is no audio device (e.g. Codespaces)
        if pygame.mixer.get_init():
            self.click_sound = pygame.mixer.Sound(os.path.join(config.SOUNDS_DIR, 'quack.wav'))
