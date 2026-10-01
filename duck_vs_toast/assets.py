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
        self.click_sound = pygame.mixer.Sound(os.path.join(config.SOUNDS_DIR, 'quack.wav'))
