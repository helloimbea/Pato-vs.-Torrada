"""Where each part of the screen goes when the window is resized.

Everything is drawn as if the screen were 1280x720 (the size the art is drawn at), and each
part of the screen is pinned to its own spot of the window:

- 'top_left':  the Duckcoins, DPS and damage boxes, stuck to the top-left corner;
- 'top_right': the level buttons and the sound button, stuck to the top-right corner;
- 'center':    the toast and the ducks, always in the middle;
- 'bottom':    the shop, stuck to the bottom (and centered left to right).

When the window has a different shape than 16:9, the game gets extra room on the sides
or at the top and bottom, and the parts spread out to the edges. When the window is bigger
or smaller, everything is scaled up or down to fit.
"""
from . import config

GROUPS = ('top_left', 'top_right', 'center', 'bottom')


class Layout:
    def __init__(self, window_size):
        width, height = max(window_size[0], 1), max(window_size[1], 1)
        self.window_size = (width, height)
        self.scale = min(width / config.SCREEN_WIDTH, height / config.SCREEN_HEIGHT)
        # The game is drawn on a canvas of this size, then scaled to the window
        self.size = (max(config.SCREEN_WIDTH, round(width / self.scale)),
                     max(config.SCREEN_HEIGHT, round(height / self.scale)))
        self.extra_width = self.size[0] - config.SCREEN_WIDTH
        self.extra_height = self.size[1] - config.SCREEN_HEIGHT
        self.offsets = {
            'top_left': (0, 0),
            'top_right': (self.extra_width, 0),
            'center': (self.extra_width // 2, self.extra_height // 2),
            'bottom': (self.extra_width // 2, self.extra_height),
        }

    def to_canvas(self, window_pos):
        """A position in the window (like the mouse) -> the same spot on the canvas."""
        return (window_pos[0] * self.size[0] / self.window_size[0],
                window_pos[1] * self.size[1] / self.window_size[1])

    def to_group(self, group, window_pos):
        """A position in the window -> the same spot in a part's own 1280x720 coordinates."""
        x, y = self.to_canvas(window_pos)
        offset_x, offset_y = self.offsets[group]
        return round(x - offset_x), round(y - offset_y)
