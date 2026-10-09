"""Loading images and sounds."""
import os

import pygame

from . import config


def load_image(category, name):
    path = os.path.join(config.IMAGES_DIR, category, name)
    return pygame.image.load(path).convert_alpha()


def load_folder(category):
    """Load every .png image in a folder.

    Returns a dict {file_name_without_extension: image}.
    To add a new image, just drop the file in the right folder.
    """
    folder = os.path.join(config.IMAGES_DIR, category)
    images = {}
    for file_name in sorted(os.listdir(folder)):
        name, extension = os.path.splitext(file_name)
        if extension.lower() == '.png':
            images[name] = load_image(category, file_name)
    return images


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

    The bread is painted on the map and each toast image only adds its face on top.
    Returns (map without the bread, bread on a transparent 1280x720 image).
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
    return background, bread_image


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
    return badge


class Assets:
    """Holds every image and sound in the game.

    Must be created after pygame.display.set_mode().
    """

    def __init__(self):
        game_map = load_image('maps', 'map1.png')
        game_map = pygame.transform.scale(game_map, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.map, self.bread = split_bread(game_map)
        self.reward_badge = cut_reward_badge(game_map)
        self.ducks = load_folder('ducks')
        self.toasts = load_folder('toasts')
        self.ui = load_folder('ui')
        self.coin = cut_coin(game_map)
        self.click_sound = None  # stays None when there is no audio device (e.g. Codespaces)
        if pygame.mixer.get_init():
            self.click_sound = pygame.mixer.Sound(os.path.join(config.SOUNDS_DIR, 'quack.wav'))
