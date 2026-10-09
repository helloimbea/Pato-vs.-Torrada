"""The game's clock, which stops while the game is paused.

Everything that depends on time (DPS, the muscular duck, boss timers, the Bourgeois Duck,
animations) reads this clock, so pausing freezes all of it at once.
"""
import pygame


class GameClock:
    def __init__(self, real_clock=pygame.time.get_ticks, paused=False):
        self.real_clock = real_clock
        self.paused_time = 0                          # total time spent paused
        self.paused_at = real_clock() if paused else None

    def __call__(self):
        """Milliseconds of play so far (not counting pauses)."""
        now = self.paused_at if self.paused_at is not None else self.real_clock()
        return now - self.paused_time

    @property
    def paused(self):
        return self.paused_at is not None

    def pause(self):
        if self.paused_at is None:
            self.paused_at = self.real_clock()

    def resume(self):
        if self.paused_at is not None:
            self.paused_time += self.real_clock() - self.paused_at
            self.paused_at = None
