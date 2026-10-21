"""Throwing ducks: grab a duck with the mouse, fling it, and it flies at the toast.

GameState keeps the rules (how much damage a throw does, how battered each duck is,
healing). This module only moves the ducks around: following the mouse while held,
flying (and falling) after being let go, and hopping back to their spot.

Positions are in the 'center' part's own 1280x720 coordinates (see layout.py), and a
duck's position is its top-left corner, like Sprite.pos.
"""
import math
from dataclasses import dataclass, field

import pygame

from . import config
from .effects import ease_out

SPEED_SAMPLE_TIME = 100  # the throw's speed is how far the mouse moved in its last 100 ms


@dataclass
class MovingDuck:
    """A duck away from its spot: 'held' (following the mouse), 'flying' or 'returning'."""
    name: str
    pos: pygame.Vector2
    size: tuple
    mode: str
    start: int                      # when the current mode started
    grab: pygame.Vector2 = field(default_factory=pygame.Vector2)  # mouse spot, from the top-left
    velocity: pygame.Vector2 = field(default_factory=pygame.Vector2)  # pixels per millisecond
    angle: float = 0                # degrees it is turned
    spin: float = 0                 # degrees per millisecond while flying
    last_update: int = 0
    samples: list = field(default_factory=list)  # (time, mouse position) while held
    return_from: pygame.Vector2 = field(default_factory=pygame.Vector2)
    return_angle: float = 0

    @property
    def center(self):
        return self.pos + pygame.Vector2(self.size) / 2


def touches(sprite, pos, point):
    """True if point is on the drawing of sprite (not a see-through pixel) when it is at pos."""
    x, y = round(point[0] - pos[0]), round(point[1] - pos[1])
    width, height = sprite.image.get_size()
    if not (0 <= x < width and 0 <= y < height):
        return False
    return sprite.image.get_at((x, y)).a >= config.GRAB_ALPHA


class Throws:
    def __init__(self, clock=pygame.time.get_ticks):
        self.clock = clock
        self.moving = {}   # duck name -> MovingDuck, for the ducks away from their spot
        self.held = None   # the name of the duck following the mouse
        self.impact = None  # where the last thrown duck hit the toast

    def is_away(self, name):
        return name in self.moving

    def duck_at(self, point, sprites):
        """The duck under the mouse that can be grabbed, or None.

        sprites: {duck name: Sprite} for every duck on screen, in drawing order (the last
        one is drawn on top, so it is checked first). Flying ducks can't be caught.
        """
        for name in reversed(list(sprites)):
            duck = self.moving.get(name)
            if duck is not None and duck.mode == 'flying':
                continue
            pos = duck.pos if duck is not None else sprites[name].pos
            if touches(sprites[name], pos, point):
                return name
        return None

    def grab(self, name, point, sprite):
        """Pick up a duck where the mouse is (point)."""
        now = self.clock()
        duck = self.moving.get(name)
        pos = pygame.Vector2(duck.pos if duck is not None else sprite.pos)
        self.moving[name] = MovingDuck(name, pos, sprite.image.get_size(), 'held', now,
                                       grab=pygame.Vector2(point) - pos, samples=[(now, tuple(point))])
        self.held = name

    def move(self, point):
        """The mouse moved: the held duck follows it."""
        duck = self.moving.get(self.held)
        if duck is None:
            return
        now = self.clock()
        duck.pos = pygame.Vector2(point) - duck.grab
        duck.samples.append((now, tuple(point)))
        duck.samples = [s for s in duck.samples if now - s[0] <= SPEED_SAMPLE_TIME] or duck.samples[-1:]

    def release(self, point):
        """Let go of the held duck: it flies with the speed the mouse had."""
        duck = self.moving.get(self.held)
        if duck is None:
            self.held = None
            return
        self.move(point)
        self.held = None
        now = self.clock()
        (first_time, first), (last_time, last) = duck.samples[0], duck.samples[-1]
        velocity = pygame.Vector2(last) - pygame.Vector2(first)
        if last_time > first_time:
            velocity /= last_time - first_time
        else:
            velocity = pygame.Vector2()
        if velocity.length() > config.THROW_MAX_SPEED:
            velocity.scale_to_length(config.THROW_MAX_SPEED)
        duck.mode, duck.start, duck.last_update = 'flying', now, now
        duck.velocity = velocity
        duck.spin = -velocity.x * config.THROW_SPIN

    def drop(self):
        """Let go of the held duck without throwing it (e.g. the game was paused)."""
        duck = self.moving.get(self.held)
        self.held = None
        if duck is not None:
            self.go_home(duck, self.clock())

    def go_home(self, duck, now):
        duck.mode, duck.start = 'returning', now
        duck.return_from = pygame.Vector2(duck.pos)
        duck.return_angle = duck.angle

    def update(self, state, sprites):
        """Move the flying and returning ducks. Returns the names of the ducks that hit the toast.

        sprites: {duck name: Sprite} (their spots, see duck_at).
        """
        now = self.clock()
        toast = pygame.Rect(config.TOAST_RECT).inflate(-2 * config.THROW_HIT_MARGIN,
                                                        -2 * config.THROW_HIT_MARGIN)
        hits = []
        for name, duck in list(self.moving.items()):
            if name not in sprites:  # not on screen anymore
                del self.moving[name]
                continue
            if duck.mode == 'flying':
                elapsed, duck.last_update = now - duck.last_update, now
                duck.pos += duck.velocity * elapsed
                duck.velocity.y += config.THROW_GRAVITY * elapsed
                duck.angle += duck.spin * elapsed
                if toast.collidepoint(duck.center):
                    self.impact = tuple(duck.center)
                    if state.duck_hits_toast(name):
                        hits.append(name)
                    self.go_home(duck, now)
                elif now - duck.start >= config.THROW_FLIGHT_TIME or not self.on_screen(duck):
                    self.go_home(duck, now)
            elif duck.mode == 'returning':
                progress = (now - duck.start) / config.THROW_RETURN_TIME
                if progress >= 1:
                    del self.moving[name]
                    continue
                t = ease_out(progress)
                home = pygame.Vector2(sprites[name].pos)
                duck.pos = duck.return_from.lerp(home, t)
                duck.pos.y -= math.sin(math.pi * progress) * config.THROW_RETURN_ARC
                duck.angle = duck.return_angle * (1 - t)
        return hits

    @staticmethod
    def on_screen(duck):
        margin = 300
        x, y = duck.center
        return -margin < x < config.SCREEN_WIDTH + margin and -margin < y < config.SCREEN_HEIGHT + margin
