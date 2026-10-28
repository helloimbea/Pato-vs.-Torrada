"""Draw the game with each font in config.FONTS, to choose one.

Run it from the project folder with:

    python -m tools.preview_fonts

It saves one picture per font (in Portuguese and in English) in the font_previews folder.
To use a font in the game, set TEXT_FONT in duck_vs_toast/config.py to its name.
"""
import os

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')  # no window needed
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import pygame  # noqa: E402

from duck_vs_toast import config, i18n, shop  # noqa: E402
from duck_vs_toast.assets import Assets, load_font  # noqa: E402
from duck_vs_toast.effects import Effects  # noqa: E402
from duck_vs_toast.layout import Layout  # noqa: E402
from duck_vs_toast.screen import Screen  # noqa: E402
from duck_vs_toast.smacking import Smacking  # noqa: E402
from duck_vs_toast.state import GameState  # noqa: E402
from duck_vs_toast.ui import Ui  # noqa: E402

OUTPUT_DIR = os.path.join(config.GAME_DIR, 'font_previews')


def example_game():
    """A game in the middle: some ducks bought, a toast with a long name."""
    now = 0
    state = GameState(clock=lambda: now)
    state.duckcoins = 2_500_000
    for duck in shop.DUCKS[:3]:
        shop.buy(state, duck)
    state.level = 37  # the UwU toast
    state.load_level()
    return state


def main():
    pygame.init()
    window = pygame.display.set_mode(config.SCREEN_SIZE)
    assets = Assets()
    layout = Layout(window.get_size())
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    chosen = config.TEXT_FONT
    for name in config.FONTS:
        config.TEXT_FONT = name
        font = load_font(config.FONT_SIZE)
        small_font = load_font(config.SMALL_FONT_SIZE)
        screen = Screen(assets, font, small_font)
        for language, level in (('pt', 37), ('en', 50)):
            i18n.set_language(language)
            state = example_game()
            state.level = level
            state.load_level()
            effects = Effects(clock=lambda: 0)
            screen.draw(window, layout, state, effects, Smacking(clock=lambda: 0), Ui(clock=lambda: 0),
                        0, (0, 0))
            path = os.path.join(OUTPUT_DIR, f'{name}_{language}.png')
            pygame.image.save(window, path)
            print(f'{name:<14} {language}: {path}')
    config.TEXT_FONT = chosen
    i18n.set_language('en')


if __name__ == '__main__':
    main()
