"""Game state: everything that changes while playing (level, health, Duckcoins, ...)."""
import pygame

from . import config, levels
from .shop import DUCKS


class GameState:
    def __init__(self, clock=pygame.time.get_ticks):
        # clock() returns the current time in milliseconds. The game uses Pygame's
        # clock; the tests and the balance simulator pass a fake one.
        self.clock = clock
        now = clock()

        # Progress
        self.duckcoins = 0
        self.level = 1
        self.level_advance = True  # if False, the player keeps "farming" the same level
        self.highest_level = 1     # the furthest level unlocked (the next button can't go past it)

        # Current toast
        self.toast = ''
        self.health = 1
        self.max_health = 1
        self.reward = 50
        self.boss_start = 0

        # Duck power
        self.damage = config.STARTING_DAMAGE
        self.dps = 0
        self.dps_base = config.STARTING_DPS_BASE
        self.has_auto_click = False  # muscular duck: clicks on its own with the click damage
        self.auto_click_interval = config.AUTO_CLICK_INTERVAL_START
        self.last_auto_click = now
        self.last_dps = now

        # Shop
        self.costs = {duck.name: duck.starting_cost for duck in DUCKS}
        self.ducks_on_screen = []
        self.purchases = {duck.name: 0 for duck in DUCKS}

        # Bourgeois Duck: a boost for a while, then it has to recharge (times from clock())
        self.boost_end = None       # when the current boost ends
        self.bourgeois_ready = None  # when it can be bought again
        self.bourgeois_purchases = 0

        # Settings
        self.muted = False
        self.victory_seen = False  # the "you beat every toast" screen shows only once

        # Called when a toast is hit / beaten, so the screen can animate it (see effects.py)
        self.on_hit = lambda _amount, _kind: None
        self.on_defeat = lambda: None
        self.on_buy = lambda _name, _first_time: None

        self.load_level()

    # --- Levels ---

    def is_boss(self):
        return levels.is_boss(self.level)

    def load_level(self):
        """Put the current level's toast on screen (with full health)."""
        self.toast, self.max_health, self.reward = levels.get_level(self.level)
        self.health = self.max_health
        if self.is_boss():
            self.boss_start = self.clock()

    def previous_level(self):
        if self.level > 1:
            self.level -= 1
            self.load_level()

    def can_go_to_next_level(self):
        return self.level < self.highest_level

    def next_level(self):
        """Go forward again after farming an earlier level (only up to levels already unlocked)."""
        if self.can_go_to_next_level():
            self.level += 1
            self.load_level()

    def toggle_level_advance(self):
        self.level_advance = not self.level_advance

    def boss_time_left(self, now):
        """Seconds left before the boss gets its health back."""
        return max(0, (self.boss_start + config.BOSS_TIME_LIMIT - now) // 1000)

    def toggle_mute(self):
        self.muted = not self.muted

    def has_won(self):
        """True once every toast has been beaten (after that they come back, stronger)."""
        return self.highest_level >= len(levels.TOASTS) * config.BOSS_EVERY_N_LEVELS

    # --- Bourgeois Duck ---

    def is_boosted(self):
        return self.boost_end is not None and self.clock() < self.boost_end

    def boost_time_left(self):
        """Milliseconds left of the Bourgeois Duck's boost (0 when not boosted)."""
        return max(0, self.boost_end - self.clock()) if self.boost_end is not None else 0

    def bourgeois_recharge_left(self):
        """Milliseconds before the Bourgeois Duck can be bought again (0 when it can)."""
        return max(0, self.bourgeois_ready - self.clock()) if self.bourgeois_ready is not None else 0

    def damage_multiplier(self):
        return config.BOURGEOIS_DAMAGE_MULTIPLIER if self.is_boosted() else 1

    def reward_multiplier(self):
        return config.BOURGEOIS_REWARD_MULTIPLIER if self.is_boosted() else 1

    def click_damage(self):
        """Damage of a click (and of the muscular duck), with the Bourgeois boost."""
        return self.damage * self.damage_multiplier()

    def current_dps(self):
        """Damage per second, with the Bourgeois boost."""
        return self.dps * self.damage_multiplier()

    def current_reward(self):
        """Duckcoins for beating the current toast, with the Bourgeois boost."""
        return self.reward * self.reward_multiplier()

    # --- Combat ---

    def deal_damage(self, amount, kind='click'):
        """Hit the toast. kind is 'click', 'auto' (muscular duck) or 'dps'."""
        if self.health == 0:
            return
        self.health = max(self.health - amount, 0)
        self.on_hit(amount, kind)
        if self.health == 0:
            self.defeat_toast()

    def defeat_toast(self):
        """Give the reward and move on to the next toast (or repeat the level)."""
        self.on_defeat()
        self.duckcoins += self.current_reward()
        self.highest_level = max(self.highest_level, self.level + 1)
        if self.level_advance:
            self.level += 1
        self.load_level()

    @staticmethod
    def interval_passed(now, last, interval):
        """Tell whether the next automatic hit is due, and compute the new "last".

        The new "last" moves forward by exactly one interval, so the delay of each
        frame (up to 1/FPS seconds) doesn't add up and damage per second stays right.
        If it fell far behind (e.g. the duck was just bought), it restarts from now.
        """
        if now - last < interval:
            return False, last
        last += interval
        if now - last >= interval:
            last = now
        return True, last

    def update(self, now):
        """Called once per frame: automatic damage and boss timer."""
        # Muscular duck's automatic click
        if self.has_auto_click:
            hit, self.last_auto_click = self.interval_passed(
                now, self.last_auto_click, self.auto_click_interval)
            if hit:
                self.deal_damage(self.click_damage(), 'auto')

        # Damage per second
        if self.dps > 0:
            hit, self.last_dps = self.interval_passed(now, self.last_dps, config.DPS_INTERVAL)
            if hit:
                self.deal_damage(self.current_dps(), 'dps')

        # If the boss timer runs out, the boss gets all its health back
        if self.is_boss() and now - self.boss_start >= config.BOSS_TIME_LIMIT and self.health > 0:
            self.health = self.max_health
            self.boss_start = now
