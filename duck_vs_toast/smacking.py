"""A secret (an easter egg, nothing in the game tells about it): the muscular duck can be
grabbed with the mouse and used to smack the toast.

Hold the left button on the muscular duck and drag it into the toast: every time it goes
into the toast is a smack. Let go and it hops back to its spot. GameState keeps the rules
(damage, critical hits, the rest after SMACKS_BEFORE_REST smacks); this module only moves
the duck and notices when it goes into the toast.

Positions are in the 'center' part's own 1280x720 coordinates (see layout.py), and the
duck's position is its top-left corner, like Sprite.pos.
"""
import math

import pygame

from . import config
from .effects import ease_out

DUCK = 'muscular_duck'


def touches(sprite, pos, point):
    """True if point is on the drawing of sprite (not a see-through pixel) when it is at pos."""
    x, y = round(point[0] - pos[0]), round(point[1] - pos[1])
    width, height = sprite.image.get_size()
    if not (0 <= x < width and 0 <= y < height):
        return False
    return sprite.image.get_at((x, y)).a >= config.GRAB_ALPHA


class Smacking:
    def __init__(self, clock=pygame.time.get_ticks):
        self.clock = clock
        self.held = False
        self.pos = None          # where the duck is while away from its spot (None: at its spot)
        self.size = (0, 0)
        self.grab_offset = pygame.Vector2()  # where the mouse holds it, from its top-left corner
        self.angle = 0           # it leans the way it is swung
        self.in_toast = False    # it has to come out of the toast before smacking again
        self.impact = None       # where the last smack hit
        self.return_start = None
        self.return_from = None

    def is_away(self):
        return self.pos is not None

    @property
    def center(self):
        return self.pos + pygame.Vector2(self.size) / 2

    def can_grab(self, state, point, sprite):
        """True if the mouse (point) is on the muscular duck and it can be picked up."""
        if DUCK not in state.ducks_on_screen or state.is_muscular_resting() or sprite is None:
            return False
        pos = self.pos if self.is_away() else sprite.pos
        return touches(sprite, pos, point)

    def grab(self, point, sprite):
        self.held = True
        if not self.is_away():
            self.pos = pygame.Vector2(sprite.pos)
        self.size = sprite.image.get_size()
        self.grab_offset = pygame.Vector2(point) - self.pos
        self.return_start = None
        self.in_toast = self.toast_area().collidepoint(self.center)

    @staticmethod
    def toast_area():
        margin = config.SMACK_MARGIN
        return pygame.Rect(config.TOAST_RECT).inflate(-2 * margin, -2 * margin)

    def move(self, point, state):
        """The mouse moved while holding the duck. Returns 'hit', 'crit' or None."""
        if not self.held:
            return None
        new_pos = pygame.Vector2(point) - self.grab_offset
        # Lean the way it is swung, and slowly straighten up
        self.angle = max(-30, min(30, self.angle * 0.7 - (new_pos.x - self.pos.x) * 0.8))
        self.pos = new_pos
        inside = self.toast_area().collidepoint(self.center)
        result = None
        if inside and not self.in_toast:
            self.impact = tuple(self.center)
            result = state.smack_toast()
            if state.is_muscular_resting():  # that was the last smack: it needs a rest
                self.release()
        self.in_toast = inside
        return result

    def release(self):
        """Let go: the duck hops back to its spot."""
        self.held = False
        if self.is_away():
            self.return_start = self.clock()
            self.return_from = pygame.Vector2(self.pos)

    def update(self, sprite):
        """Move the duck back to its spot after it was let go."""
        if self.return_start is None or sprite is None:
            if sprite is None:
                self.held, self.pos, self.return_start = False, None, None
            return
        progress = (self.clock() - self.return_start) / config.RETURN_TIME
        if progress >= 1:
            self.pos, self.return_start, self.angle = None, None, 0
            return
        t = ease_out(progress)
        self.pos = self.return_from.lerp(pygame.Vector2(sprite.pos), t)
        self.pos.y -= math.sin(math.pi * progress) * config.RETURN_ARC
        self.angle *= 0.8
