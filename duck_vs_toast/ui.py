"""Where the buttons are and what they do: the shop that slides up, the settings menu and the
level buttons. Drawing (screen.py) and clicking (game.py) both ask this module, so they always
agree on where everything is.

Positions are in the coordinates of each part of the screen (see layout.py): the shop in
'bottom', the settings in 'top_right' and the level buttons in 'top_center'.
"""
import math

import pygame

from . import config, shop

SHOP_ITEMS = [duck.name for duck in shop.DUCKS] + ['bourgeois_duck']


def in_circle(point, center, radius):
    return math.dist(point, center) < radius


class ShopDrawer:
    """The shop: a panel that slides up from the bottom when its button is clicked."""

    def __init__(self, clock=pygame.time.get_ticks):
        self.clock = clock
        self.open = False
        self.changed_at = -config.SHOP_SLIDE_TIME  # when it last started opening or closing

    def toggle(self):
        # Turning around halfway keeps the panel where it is (no jump)
        now = self.clock()
        self.changed_at = now - round((1 - self.raw_progress()) * config.SHOP_SLIDE_TIME)
        self.open = not self.open

    def raw_progress(self):
        """How far the last opening/closing went: 0 -> 1."""
        return min(1, (self.clock() - self.changed_at) / config.SHOP_SLIDE_TIME)

    def openness(self):
        """0 = closed (hidden below the screen), 1 = open."""
        # Smooth at both ends, and the same going up and down (so turning around doesn't jump)
        progress = self.raw_progress()
        progress = progress * progress * (3 - 2 * progress)
        return progress if self.open else 1 - progress

    def panel_rect(self):
        x, y, width, height = config.SHOP_PANEL
        hidden_by = config.SCREEN_HEIGHT - y  # how far it goes down when closed
        return pygame.Rect(x, round(y + hidden_by * (1 - self.openness())), width, height)

    def tab_rect(self):
        """The shop's button, stuck to the top of the panel (at the bottom of the screen when closed)."""
        width, height = config.SHOP_TAB_SIZE
        panel = self.panel_rect()
        return pygame.Rect(panel.centerx - width // 2, panel.top - height, width, height)

    def portraits(self):
        """{duck name: (center, diameter)} of the ducks in the panel, where they are now."""
        panel = self.panel_rect()
        spots = {}
        for name in SHOP_ITEMS:
            x, _, diameter = config.SHOP_PORTRAITS[name]
            spots[name] = ((x, panel.top + config.SHOP_PORTRAIT_Y), diameter)
        return spots

    def portrait_at(self, point):
        """The duck under the mouse in the open shop, or None."""
        if self.openness() < 0.95:
            return None
        for name, (center, diameter) in self.portraits().items():
            if in_circle(point, center, diameter / 2 + 4):
                return name
        return None


class SettingsMenu:
    """The gear button (top right) and its little menu with the sound and language buttons."""

    def __init__(self):
        self.open = False

    @staticmethod
    def items():
        """{'sound' or 'language': center} of the buttons in the menu."""
        x, y = config.GEAR_POS
        return {name: (x, y + config.MENU_STEP * (i + 1)) for i, name in enumerate(('sound', 'language'))}

    def menu_rect(self):
        x, y = config.GEAR_POS
        radius = config.MENU_BUTTON_RADIUS
        bottom = y + config.MENU_STEP * 2 + radius + 8
        return pygame.Rect(x - radius - 8, y + config.GEAR_RADIUS - 4, 2 * radius + 16,
                           bottom - (y + config.GEAR_RADIUS - 4))


def any_affordable(state):
    """True when the player can buy something in the shop (to call attention to its button)."""
    return any(state.duckcoins >= state.costs[duck.name] for duck in shop.DUCKS) \
        or shop.can_buy_bourgeois(state)


def can_afford(state, name):
    if name == 'bourgeois_duck':
        return shop.can_buy_bourgeois(state)
    return state.duckcoins >= state.costs[name]


class Ui:
    def __init__(self, clock=pygame.time.get_ticks):
        self.shop = ShopDrawer(clock)
        self.settings = SettingsMenu()

    def click(self, state, layout, window_pos):
        """A left click. Returns (handled, quack): whether a button took it, and whether to quack.

        A click the buttons don't take goes on to the toast (see game.handle_click).
        """
        in_top_right = layout.to_group('top_right', window_pos)
        in_top_center = layout.to_group('top_center', window_pos)
        in_shop = layout.to_group('bottom', window_pos)

        # Settings: the gear opens the menu; a click anywhere else closes it
        if in_circle(in_top_right, config.GEAR_POS, config.GEAR_RADIUS):
            self.settings.open = not self.settings.open
            return True, True
        if self.settings.open:
            items = self.settings.items()
            if in_circle(in_top_right, items['sound'], config.MENU_BUTTON_RADIUS):
                state.toggle_mute()
                return True, True
            if in_circle(in_top_right, items['language'], config.MENU_BUTTON_RADIUS):
                state.toggle_language()
                return True, True
            self.settings.open = False

        # The shop's button, and the ducks in the open shop
        if self.shop.tab_rect().collidepoint(in_shop):
            self.shop.toggle()
            return True, True
        name = self.shop.portrait_at(in_shop)
        if name == 'bourgeois_duck':
            return True, shop.buy_bourgeois(state)
        if name is not None:
            duck = next(duck for duck in shop.DUCKS if duck.name == name)
            bought = state.duckcoins >= state.costs[name]
            shop.buy(state, duck)
            return True, bought
        if self.shop.openness() > 0 and self.shop.panel_rect().collidepoint(in_shop):
            return True, False  # a click on the panel, between the ducks

        # Level buttons (top center)
        for position, radius, action in (
                (config.LEVEL_ADVANCE_BUTTON_POS, config.LEVEL_ADVANCE_BUTTON_RADIUS,
                 state.toggle_level_advance),
                (config.PREVIOUS_LEVEL_BUTTON_POS, config.LEVEL_ARROW_RADIUS, state.previous_level),
                (config.NEXT_LEVEL_BUTTON_POS, config.LEVEL_ARROW_RADIUS, state.next_level)):
            if in_circle(in_top_center, position, radius):
                action()
                return True, True
        return False, False
