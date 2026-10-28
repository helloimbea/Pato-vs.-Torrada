"""Make the picture at the top of the README: the starter duck with the game's name under it.

Run it from the project folder (again after changing the font or the duck's drawing) with:

    python -m tools.make_readme_logo

It saves docs/logo.png.
"""
import os

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')  # no window needed

import pygame  # noqa: E402

from duck_vs_toast import config  # noqa: E402
from duck_vs_toast.assets import load_font, load_image  # noqa: E402

OUTPUT = os.path.join(config.GAME_DIR, 'docs', 'logo.png')
SIZE = (800, 440)
DUCK_HEIGHT = 250
TITLE = 'Duck vs. Toast'
TITLE_SIZE = 110


def main():
    pygame.init()
    pygame.display.set_mode((1, 1))
    logo = pygame.Surface(SIZE, pygame.SRCALPHA)

    # A rounded box with the game's sky color, so it looks the same on light and dark pages
    game_map = load_image('maps', 'map1.png')
    sky = game_map.get_at((game_map.get_width() // 2, 5))
    pygame.draw.rect(logo, sky, logo.get_rect(), border_radius=40)

    duck = load_image('ducks', 'starter_duck.png')
    duck = duck.subsurface(duck.get_bounding_rect())
    scale = DUCK_HEIGHT / duck.get_height()
    duck = pygame.transform.smoothscale(duck, (round(duck.get_width() * scale), DUCK_HEIGHT))
    logo.blit(duck, duck.get_rect(midtop=(SIZE[0] // 2, 30)))

    title = load_font(TITLE_SIZE).render(TITLE, True, config.INK)
    title = title.subsurface(title.get_bounding_rect())
    logo.blit(title, title.get_rect(midbottom=(SIZE[0] // 2, SIZE[1] - 35)))

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    pygame.image.save(logo, OUTPUT)
    print(f'Saved {OUTPUT}')


if __name__ == '__main__':
    main()
