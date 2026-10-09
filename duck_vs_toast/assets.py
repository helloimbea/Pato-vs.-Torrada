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


class Assets:
    """Holds every image and sound in the game.

    Must be created after pygame.display.set_mode().
    """

    def __init__(self):
        game_map = load_image('maps', 'map1.png')
        self.map = pygame.transform.scale(game_map, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.ducks = load_folder('ducks')
        self.toasts = load_folder('toasts')
        self.ui = load_folder('ui')
        self.coin = cut_coin(game_map)
        self.click_sound = None  # stays None when there is no audio device (e.g. Codespaces)
        if pygame.mixer.get_init():
            self.click_sound = pygame.mixer.Sound(os.path.join(config.SOUNDS_DIR, 'quack.wav'))
