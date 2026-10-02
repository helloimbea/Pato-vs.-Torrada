"""Draw the placeholder icons for the sound and next level buttons.

They are temporary: replace the PNG files in assets/images/ui with your own
drawings whenever you like (same file names, 1280x720 like the other UI images,
with the icon drawn at the position set in duck_vs_toast/config.py).

    python -m tools.make_placeholder_icons
"""
import os

import pygame

from duck_vs_toast import config

BUTTON_BLUE = (136, 167, 200)
WHITE = (255, 255, 255)
X_RED = (234, 95, 112)
UI_DIR = os.path.join(config.IMAGES_DIR, 'ui')


def blank():
    return pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)


def next_level_icon(alpha):
    surface = blank()
    x, y = config.NEXT_LEVEL_BUTTON_POS
    pygame.draw.circle(surface, BUTTON_BLUE + (alpha,), (x, y), 26)
    pygame.draw.lines(surface, WHITE + (alpha,), False, [(x - 5, y - 11), (x + 6, y), (x - 5, y + 11)], 5)
    return surface


def sound_icon(muted):
    surface = blank()
    x, y = config.SOUND_BUTTON_POS
    pygame.draw.circle(surface, BUTTON_BLUE, (x, y), 20)
    speaker = [(x - 11, y - 4), (x - 6, y - 4), (x + 1, y - 10),
               (x + 1, y + 10), (x - 6, y + 4), (x - 11, y + 4)]
    pygame.draw.polygon(surface, WHITE, speaker)
    if muted:
        pygame.draw.line(surface, X_RED, (x + 4, y - 5), (x + 12, y + 5), 3)
        pygame.draw.line(surface, X_RED, (x + 4, y + 5), (x + 12, y - 5), 3)
    else:
        pygame.draw.arc(surface, WHITE, (x - 4, y - 7, 12, 14), -1.1, 1.1, 2)
        pygame.draw.arc(surface, WHITE, (x - 6, y - 12, 20, 24), -1.1, 1.1, 2)
    return surface


def main():
    pygame.init()
    icons = {
        'next_level_on': next_level_icon(255),
        'next_level_off': next_level_icon(90),
        'sound_on': sound_icon(muted=False),
        'sound_off': sound_icon(muted=True),
    }
    for name, surface in icons.items():
        path = os.path.join(UI_DIR, name + '.png')
        pygame.image.save(surface, path)
        print('Saved', path)


if __name__ == '__main__':
    main()
