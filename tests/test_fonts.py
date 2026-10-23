import os

import pygame
import pytest

from duck_vs_toast import config
from duck_vs_toast.assets import load_font

ACCENTS = 'ÁÂÃÉÊÍÓÔÕÚÇÑáâãéêíóôõúçñ¿¡'


@pytest.mark.parametrize('name', config.FONTS)
def test_every_font_is_there_and_has_its_license(name):
    file_name = config.FONTS[name]
    assert os.path.exists(os.path.join(config.FONTS_DIR, file_name))
    assert os.path.exists(os.path.join(config.FONTS_DIR, file_name.replace('.ttf', '-OFL.txt')))


@pytest.mark.parametrize('name', config.FONTS)
def test_every_font_draws_portuguese_and_spanish_letters(name):
    pygame.font.init()
    font = load_font(30, name)
    missing = [c for c in ACCENTS if font.render(c, True, (0, 0, 0)).get_bounding_rect().width == 0]
    assert missing == []


def test_the_chosen_font_exists():
    assert config.TEXT_FONT in config.FONTS
