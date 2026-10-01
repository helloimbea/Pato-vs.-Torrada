"""Duck shop: what each duck costs and what it does when bought.

To create a new duck:
  1. put its image (and its "locked_" version) in assets/images/ducks;
  2. write an effect function (like the ones below);
  3. add a Duck to the DUCKS list.
"""
import math
from dataclasses import dataclass
from typing import Callable

from . import config


@dataclass
class Duck:
    name: str                # image name in assets/images/ducks
    starting_cost: int
    cost_multiplier: float   # the cost is multiplied by this after each purchase
    button_pos: tuple        # center of the buy button
    cost_text_pos: tuple     # where the cost is written
    effect: Callable         # function that receives the game state

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
    """Clicks on its own, faster and faster."""
    state.auto_click_damage = state.damage
    if state.auto_click_interval > config.AUTO_CLICK_INTERVAL_MIN:
        state.auto_click_interval -= config.AUTO_CLICK_INTERVAL_STEP
    state.show_pointer = True


def realistic_duck_effect(state):
    """Doubles total DPS."""
    state.dps *= 2
    state.dps_base *= 2


DUCKS = [
    Duck('siamese_duck', 200, 1.5, (157, 605), (119, 675), siamese_duck_effect),
    Duck('double_duck', 5000, 3, (399, 603), (381, 675), double_duck_effect),
    Duck('muscular_duck', 50000, 2, (641, 603), (616, 675), muscular_duck_effect),
    Duck('realistic_duck', 200000, 4, (883, 603), (863, 675), realistic_duck_effect),
    # Bourgeois duck (coming soon) would use the button at (1125, 603)
]


def buy(state, duck):
    cost = state.costs[duck.name]
    if state.duckcoins < cost:
        return
    if duck.name not in state.ducks_on_screen:
        state.ducks_on_screen.append(duck.name)
    state.duckcoins -= cost
    duck.effect(state)
    state.costs[duck.name] = math.floor(cost * duck.cost_multiplier)
