"""Little animations that make hitting toasts feel good.

- damage numbers that float up and fade out after each hit;
- the toast shaking, squishing and making a pained face when it gets hit;
- a beaten toast falling over and fading away, while the next one pops up;
- a duck stretching and squashing when it is bought;
- coins flying to the Duckcoins counter when a toast is beaten.

The game state tells this module what happened (GameState.on_hit and
GameState.on_defeat); this module only decides how it looks.
"""
import math
import random
from dataclasses import dataclass

import pygame

from . import config
from .numbers import format_number


@dataclass
class DamageNumber:
    text: str
    color: tuple
    x: float
    y: float
    start: int


@dataclass
class FlyingCoin:
    start_pos: tuple     # where it pops out of the toast
    burst_pos: tuple     # where it lands after the little burst
    start: int           # when it starts moving (coins leave one after another)


class Effects:
    def __init__(self, clock=pygame.time.get_ticks, rng=None):
        self.clock = clock
        self.random = rng or random.Random()
        self.damage_numbers = []
        self.coins = []
        self.shake_start = -config.SHAKE_DURATION
        self.squish_start = -config.HURT_DURATION
        self.dead_toast = None  # the toast that was just beaten, while it falls over
        self.death_start = -config.DEATH_DURATION
        self.duck_pops = {}  # duck name -> (when it was bought, whether it just appeared)

    # --- Things that happened in the game ---

    def hit(self, amount, kind, position=None):
        """A toast was hit. kind is 'click', 'auto' (muscular duck) or 'dps'."""
        now = self.clock()
        if position is None:  # automatic hits pop up somewhere over the toast
            x, y, width, _ = config.TOAST_RECT
            position = (x + self.random.uniform(0.15, 0.85) * width, y + 40)
        else:  # a little sideways jitter, so fast clicks don't pile up in one spot
            position = (position[0] + self.random.uniform(-15, 15), position[1])
        color = config.TIMER_BLUE if kind == 'dps' else config.RED
        self.damage_numbers.append(
            DamageNumber(format_number(amount), color, position[0], position[1], now))
        # Many hits per second would fill the screen, so only the newest ones stay
        del self.damage_numbers[:-config.MAX_DAMAGE_NUMBERS]
        if kind != 'dps':  # the toast shakes on clicks; DPS ticks would keep it shaking forever
            self.shake_start = now
        self.squish_start = now  # every hit makes it flinch (DPS only once per second)

    def defeat(self, toast=None):
        """A toast was beaten: it falls over, and coins fly to the Duckcoins counter.

        toast is the name of the beaten toast (state.toast before the next one comes).
        """
        now = self.clock()
        self.dead_toast = toast
        self.death_start = now
        self.squish_start = -config.HURT_DURATION  # the next toast arrives looking fine
        center = pygame.Rect(config.TOAST_RECT).center
        for i in range(config.COINS_PER_DEFEAT):
            angle = self.random.uniform(0, 2 * math.pi)
            distance = self.random.uniform(40, 110)
            burst = (center[0] + math.cos(angle) * distance, center[1] + math.sin(angle) * distance)
            self.coins.append(FlyingCoin(center, burst, now + i * config.COIN_DELAY))

    # --- Animation ---

    def toast_offset(self):
        """How far to move the toast this frame, (0, 0) when it isn't shaking."""
        elapsed = self.clock() - self.shake_start
        if elapsed >= config.SHAKE_DURATION:
            return 0, 0
        strength = config.SHAKE_STRENGTH * (1 - elapsed / config.SHAKE_DURATION)
        return round(math.sin(elapsed / 15) * strength), round(math.cos(elapsed / 20) * strength / 2)

    def squish(self):
        """How squashed the toast is: 0 = normal, 1 = fully squashed. It squashes fast and springs back."""
        elapsed = self.clock() - self.squish_start
        if elapsed >= config.SQUISH_DURATION:
            return 0
        return math.sin(math.pi * elapsed / config.SQUISH_DURATION)

    def is_hurt(self):
        """True right after a hit, while the toast shows its pained face."""
        return self.clock() - self.squish_start < config.HURT_DURATION

    def duck_bought(self, name, first_time):
        """A duck was bought: it stretches and squashes (and grows in, if it is new)."""
        self.duck_pops[name] = (self.clock(), first_time)

    def duck_scale(self, name):
        """How much to stretch a duck this frame: (width, height), (1, 1) when it's still."""
        start, first_time = self.duck_pops.get(name, (None, False))
        if start is None:
            return 1, 1
        elapsed = self.clock() - start
        if elapsed >= config.DUCK_POP_DURATION:
            return 1, 1
        t = elapsed / config.DUCK_POP_DURATION
        # A wobble that fades out: taller, then shorter and wider, then a little taller again
        wobble = math.sin(3 * math.pi * t) * (1 - t) * config.DUCK_POP_STRETCH
        width, height = 1 - wobble * 0.6, 1 + wobble
        if first_time:
            grow = ease_out_back(elapsed / config.DUCK_GROW_TIME)
            width, height = width * grow, height * grow
        return width, height

    def death(self):
        """How far along the beaten toast's fall is: 0 -> 1, or None when nothing is dying."""
        elapsed = self.clock() - self.death_start
        if self.dead_toast is None or elapsed >= config.DEATH_DURATION:
            return None
        return elapsed / config.DEATH_DURATION

    def spawn(self):
        """How much the new toast has popped up: 0 = not yet, 1 = full size.

        It grows a little too big and settles back, like a spring.
        """
        elapsed = self.clock() - self.death_start - config.SPAWN_DELAY
        if elapsed >= config.SPAWN_DURATION:
            return 1
        return ease_out_back(max(elapsed, 0) / config.SPAWN_DURATION)

    def coin_position(self, coin, now, target=config.DUCKCOINS_ICON_POS):
        """Where a coin is: first a quick burst out of the toast, then a flight to the counter.

        target is where the Duckcoins counter is, measured from the toast's part of the screen.
        """
        elapsed = now - coin.start
        burst_time = config.COIN_BURST_TIME
        if elapsed < burst_time:
            t = ease_out(max(elapsed, 0) / burst_time)
            start, end = coin.start_pos, coin.burst_pos
        else:
            t = ease_in((elapsed - burst_time) / config.COIN_FLIGHT_TIME)
            start, end = coin.burst_pos, target
        return start[0] + (end[0] - start[0]) * t, start[1] + (end[1] - start[1]) * t

    def update(self):
        """Forget the animations that are over."""
        now = self.clock()
        self.damage_numbers = [n for n in self.damage_numbers
                               if now - n.start < config.DAMAGE_NUMBER_DURATION]
        coin_time = config.COIN_BURST_TIME + config.COIN_FLIGHT_TIME
        self.coins = [c for c in self.coins if now - c.start < coin_time]
        if self.death() is None:
            self.dead_toast = None

    def draw(self, screen, font, coin_image, offset=(0, 0), coin_target=config.DUCKCOINS_ICON_POS):
        """offset: where the toast's part of the screen is (see layout.py);
        coin_target: where the coins fly to, on the screen."""
        now = self.clock()
        offset_x, offset_y = offset
        target = (coin_target[0] - offset_x, coin_target[1] - offset_y)
        for coin in self.coins:
            x, y = self.coin_position(coin, now, target)
            screen.blit(coin_image, coin_image.get_rect(center=(x + offset_x, y + offset_y)))

        for number in self.damage_numbers:
            progress = (now - number.start) / config.DAMAGE_NUMBER_DURATION
            text = outlined(font, number.text, number.color)
            text.set_alpha(round(255 * (1 - progress ** 2)))  # fades out faster at the end
            y = number.y - config.DAMAGE_NUMBER_RISE * ease_out(progress)
            screen.blit(text, text.get_rect(center=(number.x + offset_x, y + offset_y)))


def outlined(font, text, color, outline=(255, 255, 255), width=2):
    """Text with a white border, so it can be read over the toast and the sky."""
    inside = font.render(text, True, color)
    border = font.render(text, True, outline)
    surface = pygame.Surface((inside.get_width() + 2 * width, inside.get_height() + 2 * width),
                             pygame.SRCALPHA)
    for dx in (-width, 0, width):
        for dy in (-width, 0, width):
            surface.blit(border, (width + dx, width + dy))
    surface.blit(inside, (width, width))
    return surface


def ease_out(t):
    """Fast at the start, slow at the end (0 -> 1)."""
    t = min(max(t, 0), 1)
    return 1 - (1 - t) ** 2


def ease_in(t):
    """Slow at the start, fast at the end (0 -> 1)."""
    t = min(max(t, 0), 1)
    return t * t


def ease_out_back(t):
    """Fast at the start, goes a little past the end and comes back (0 -> 1)."""
    if t <= 0:
        return 0
    t = min(t, 1)
    overshoot = 1.7
    return 1 + (overshoot + 1) * (t - 1) ** 3 + overshoot * (t - 1) ** 2
