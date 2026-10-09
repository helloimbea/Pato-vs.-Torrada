import os

import pygame
import pytest

from duck_vs_toast import config
from duck_vs_toast.assets import load_positions, make_sprite


def test_full_screen_drawings_are_cropped_to_the_drawing():
    image = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
    image.fill((255, 0, 0, 255), (100, 50, 30, 20))
    sprite = make_sprite(image, 'ui/test', {})
    assert sprite.pos == (100, 50)
    assert sprite.image.get_size() == (30, 20)


def test_cropped_drawings_use_their_saved_position():
    sprite = make_sprite(pygame.Surface((30, 20)), 'ui/test', {'ui/test': [7, 9]})
    assert sprite.rect == pygame.Rect(7, 9, 30, 20)


def test_cropped_drawing_without_a_position_explains_what_to_do():
    with pytest.raises(ValueError, match='positions.json'):
        make_sprite(pygame.Surface((30, 20)), 'ui/test', {})


def test_every_cropped_image_in_the_game_has_a_position():
    positions = load_positions()
    for category in ['ducks', 'toasts', 'ui']:
        folder = os.path.join(config.IMAGES_DIR, category)
        for file_name in os.listdir(folder):
            name, extension = os.path.splitext(file_name)
            if extension.lower() != '.png':
                continue
            size = pygame.image.load(os.path.join(folder, file_name)).get_size()
            if size != (config.SCREEN_WIDTH, config.SCREEN_HEIGHT):
                assert f'{category}/{name}' in positions, f'{category}/{file_name} has no position'
