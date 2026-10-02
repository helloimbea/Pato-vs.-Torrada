"""Duck shop: what each duck costs and what it does when bought.

To create a new duck:
  1. put its image (and its "locked_" version) in assets/images/ducks;
  2. write an effect function (like the ones below);
  3. write a description function for the tooltip;
  4. add a Duck to the DUCKS list.
"""
import math
from dataclasses import dataclass
from typing import Callable

from . import config
from .numbers import format_number


@dataclass
class Duck:
    name: str                # image name in assets/images/ducks
    starting_cost: int
    cost_multiplier: float   # the cost is multiplied by this after each purchase
    button_pos: tuple        # center of the buy button
    cost_text_pos: tuple     # where the cost is written
    title: str               # name shown in the tooltip
    effect: Callable         # function that receives the game state
    describe: Callable       # returns the tooltip text (what the next purchase does)

    @property
    def locked_image(self):
        return 'locked_' + self.name


# --- Duck effects ---

def siamese_duck_effect(state):
    """Adds DPS."""
    state.dps += state.dps_base


def double_duck_effect(state):
    """Doubles click damage."""
    state.damage *= 2


def muscular_duck_effect(state):
    """Clicks on its own (with the current click damage), faster and faster."""
    state.has_auto_click = True
    if state.auto_click_interval > config.AUTO_CLICK_INTERVAL_MIN:
        state.auto_click_interval -= config.AUTO_CLICK_INTERVAL_STEP


def realistic_duck_effect(state):
    """Doubles total DPS."""
    state.dps *= 2
    state.dps_base *= 2


# --- Tooltip texts ---

def siamese_duck_description(state):
    return f'Adds {format_number(state.dps_base)} damage per second.'


def double_duck_description(state):
    return f'Doubles your click damage ({format_number(state.damage)} -> {format_number(state.damage * 2)}).'


def muscular_duck_description(state):
    interval = state.auto_click_interval
    if interval > config.AUTO_CLICK_INTERVAL_MIN:  # same rule as muscular_duck_effect
        interval -= config.AUTO_CLICK_INTERVAL_STEP
    return f'Clicks the toast for you every {interval / 1000:g} s, with your click damage.'


def realistic_duck_description(state):
    return f'Doubles all damage per second ({format_number(state.dps)} -> {format_number(state.dps * 2)}).'


DUCKS = [
    Duck('siamese_duck', 200, 1.5, (157, 605), (119, 675), 'Siamese Duck',
         siamese_duck_effect, siamese_duck_description),
    Duck('double_duck', 5000, 3, (399, 603), (381, 675), 'Double Duck',
         double_duck_effect, double_duck_description),
    Duck('muscular_duck', 50000, 2, (641, 603), (616, 675), 'Muscular Duck',
         muscular_duck_effect, muscular_duck_description),
    Duck('realistic_duck', 200000, 4, (883, 603), (863, 675), 'Realistic Duck',
         realistic_duck_effect, realistic_duck_description),
    # Bourgeois duck (coming soon) will use the button at config.BOURGEOIS_BUTTON_POS
]


def buy(state, duck):
    cost = state.costs[duck.name]
    if state.duckcoins < cost:
        return
    if duck.name not in state.ducks_on_screen:
        state.ducks_on_screen.append(duck.name)
    state.duckcoins -= cost
    state.purchases[duck.name] += 1
    duck.effect(state)
    state.costs[duck.name] = math.floor(cost * duck.cost_multiplier)
