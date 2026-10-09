"""Little animations that make hitting toasts feel good.

- damage numbers that float up and fade out after each hit;
- the toast shaking when it gets hit;
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

    def defeat(self):
        """A toast was beaten: send coins flying to the Duckcoins counter."""
        now = self.clock()
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

    def coin_position(self, coin, now):
        """Where a coin is: first a quick burst out of the toast, then a flight to the counter."""
        elapsed = now - coin.start
        burst_time = config.COIN_BURST_TIME
        if elapsed < burst_time:
            t = ease_out(max(elapsed, 0) / burst_time)
            start, end = coin.start_pos, coin.burst_pos
        else:
            t = ease_in((elapsed - burst_time) / config.COIN_FLIGHT_TIME)
            start, end = coin.burst_pos, config.DUCKCOINS_ICON_POS
        return start[0] + (end[0] - start[0]) * t, start[1] + (end[1] - start[1]) * t

    def update(self):
        """Forget the animations that are over."""
        now = self.clock()
        self.damage_numbers = [n for n in self.damage_numbers
                               if now - n.start < config.DAMAGE_NUMBER_DURATION]
        coin_time = config.COIN_BURST_TIME + config.COIN_FLIGHT_TIME
        self.coins = [c for c in self.coins if now - c.start < coin_time]

    def draw(self, screen, font, coin_image):
        now = self.clock()
        for coin in self.coins:
            x, y = self.coin_position(coin, now)
            screen.blit(coin_image, coin_image.get_rect(center=(x, y)))

        for number in self.damage_numbers:
            progress = (now - number.start) / config.DAMAGE_NUMBER_DURATION
            text = outlined(font, number.text, number.color)
            text.set_alpha(round(255 * (1 - progress ** 2)))  # fades out faster at the end
            y = number.y - config.DAMAGE_NUMBER_RISE * ease_out(progress)
            screen.blit(text, text.get_rect(center=(number.x, y)))


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
