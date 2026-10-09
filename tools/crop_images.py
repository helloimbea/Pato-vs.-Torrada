"""Crop full-screen drawings down to the drawing itself and remember where they go.

Draw new images on a 1280x720 canvas, in the spot where they go on screen (the game
already understands those). Then run:

    python -m tools.crop_images

Every 1280x720 image in assets/images/{ducks,toasts,ui,extras} is cut down to the drawing
and its position is saved in assets/images/positions.json. Images that are already
cropped are left alone. Maps (backgrounds) are never cropped.
"""
import json
import os

import pygame

from duck_vs_toast import config

FOLDERS = ['ducks', 'toasts', 'ui', 'extras']


def crop_folder(category, positions):
    folder = os.path.join(config.IMAGES_DIR, category)
    for file_name in sorted(os.listdir(folder)):
        name, extension = os.path.splitext(file_name)
        if extension.lower() != '.png':
            continue
        path = os.path.join(folder, file_name)
        image = pygame.image.load(path)
        if image.get_size() != (config.SCREEN_WIDTH, config.SCREEN_HEIGHT):
            continue  # already cropped
        area = image.get_bounding_rect()
        pygame.image.save(image.subsurface(area), path)
        positions[f'{category}/{name}'] = [area.x, area.y]
        print(f'{category}/{file_name}: {image.get_width()}x{image.get_height()} -> '
              f'{area.width}x{area.height} at ({area.x}, {area.y})')


def main():
    positions = {}
    if os.path.exists(config.POSITIONS_FILE):
        with open(config.POSITIONS_FILE) as file:
            positions = json.load(file)
    for category in FOLDERS:
        crop_folder(category, positions)
    lines = [f'  "{key}": [{x}, {y}]' for key, (x, y) in sorted(positions.items())]
    with open(config.POSITIONS_FILE, 'w') as file:
        file.write('{\n' + ',\n'.join(lines) + '\n}\n')


if __name__ == '__main__':
    main()
