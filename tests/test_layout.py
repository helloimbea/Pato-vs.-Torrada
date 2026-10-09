import pygame
import pytest

from duck_vs_toast import config
from duck_vs_toast.layout import Layout
from duck_vs_toast.screen import stretch


def test_original_size_keeps_everything_in_place():
    layout = Layout(config.SCREEN_SIZE)
    assert layout.scale == 1
    assert layout.size == config.SCREEN_SIZE
    assert set(layout.offsets.values()) == {(0, 0)}
    assert layout.to_group('bottom', (157, 605)) == (157, 605)


def test_bigger_window_with_same_shape_only_scales():
    layout = Layout((1920, 1080))
    assert layout.scale == 1.5
    assert layout.size == config.SCREEN_SIZE
    assert layout.to_group('center', (960, 540)) == (640, 360)


def test_wider_window_pins_parts_to_the_edges():
    layout = Layout((1800, 720))
    assert layout.size == (1800, 720)
    assert layout.offsets == {'top_left': (0, 0), 'top_right': (520, 0),
                              'center': (260, 0), 'bottom': (260, 0)}
    # The sound button (top right corner) is still at the window's right edge
    assert layout.to_group('top_right', (1252 + 520, 26)) == config.SOUND_BUTTON_POS


def test_taller_window_puts_the_shop_at_the_bottom():
    layout = Layout((1280, 1000))
    assert layout.offsets['center'] == (0, 140)
    assert layout.offsets['bottom'] == (0, 280)
    assert layout.to_group('bottom', (157, 605 + 280)) == (157, 605)


def test_smaller_window_scales_down():
    layout = Layout((640, 400))
    assert layout.scale == 0.5
    assert layout.size == (1280, 800)
    assert layout.to_group('center', (320, 200)) == (640, 360)


@pytest.mark.parametrize('size', [(0, 0), (1, 1000)])
def test_tiny_window_does_not_crash(size):
    layout = Layout(size)
    assert layout.size[0] >= config.SCREEN_WIDTH and layout.size[1] >= config.SCREEN_HEIGHT


def test_stretch_keeps_the_ends_at_the_edges_and_the_middle_centered():
    image = pygame.Surface((10, 1))
    for x in range(10):
        image.set_at((x, 0), (x * 20, 0, 0))
    wide = stretch(image, 20, 2, 8)
    reds = [wide.get_at((x, 0)).r for x in range(20)]
    assert reds[:2] == [0, 20]               # left end, at the left edge
    assert reds[-2:] == [160, 180]           # right end, at the right edge
    assert reds[7:13] == [40, 60, 80, 100, 120, 140]  # the middle, centered
    assert set(reds[2:7]) == {40}            # gaps repeat the middle's edge columns
    assert set(reds[13:18]) == {140}


def test_stretch_does_nothing_when_not_wider():
    image = pygame.Surface((10, 1))
    assert stretch(image, 10, 2, 8) is image
