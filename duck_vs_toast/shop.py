"""Duck shop: what each duck costs and what it does when bought.

To create a new duck:
  1. put its image (and its "locked_" version) in assets/images/ducks;
  2. write an effect function (like the ones below);
  3. write a description function for the tooltip, and its name and text in i18n.py
     (in English and Portuguese, under the duck's name);
  4. add a Duck to the DUCKS list.
"""
import math
from dataclasses import dataclass
from typing import Callable

from . import config
from .i18n import t
from .numbers import format_number


@dataclass
class Duck:
    name: str                # image name in assets/images/ducks
    starting_cost: int
    cost_multiplier: float   # the cost is multiplied by this after each purchase
    button_pos: tuple        # center of the buy button
    cost_text_pos: tuple     # where the cost is written
    effect: Callable         # function that receives the game state
    describe: Callable       # returns the tooltip text (what the next purchase does)

    @property
    def title(self):
        """Name shown in the tooltip, in the current language (see i18n.py)."""
        return t(self.name)

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
    return t('siamese_duck_effect', dps=format_number(state.dps_base))


def double_duck_description(state):
    return t('double_duck_effect', now=format_number(state.damage), next=format_number(state.damage * 2))


def muscular_duck_description(state):
    interval = state.auto_click_interval
    if interval > config.AUTO_CLICK_INTERVAL_MIN:  # same rule as muscular_duck_effect
        interval -= config.AUTO_CLICK_INTERVAL_STEP
    return t('muscular_duck_effect', seconds=f'{interval / 1000:g}')


def realistic_duck_description(state):
    return t('realistic_duck_effect', now=format_number(state.dps), next=format_number(state.dps * 2))


DUCKS = [
    Duck('siamese_duck', 200, 1.5, (157, 605), (119, 675),
         siamese_duck_effect, siamese_duck_description),
    Duck('double_duck', 5000, 3, (399, 603), (381, 675),
         double_duck_effect, double_duck_description),
    Duck('muscular_duck', 50000, 2, (641, 603), (616, 675),
         muscular_duck_effect, muscular_duck_description),
    Duck('realistic_duck', 200000, 4, (883, 603), (863, 675),
         realistic_duck_effect, realistic_duck_description),
]


def buy(state, duck):
    cost = state.costs[duck.name]
    if state.duckcoins < cost:
        return
    first_time = duck.name not in state.ducks_on_screen
    if first_time:
        state.ducks_on_screen.append(duck.name)
    state.duckcoins -= cost
    state.purchases[duck.name] += 1
    duck.effect(state)
    state.costs[duck.name] = math.floor(cost * duck.cost_multiplier)
    state.on_buy(duck.name, first_time)  # lets the duck stretch on screen (see effects.py)


# --- Bourgeois Duck ---
# Not in DUCKS: it has a fixed price and, instead of a lasting upgrade, gives a boost
# for a while (see GameState.is_boosted) and then has to recharge.

def can_buy_bourgeois(state):
    return state.duckcoins >= config.BOURGEOIS_COST and state.bourgeois_recharge_left() == 0


def buy_bourgeois(state):
    """Boost all damage and Duckcoins for a while. Returns True if it was bought."""
    if not can_buy_bourgeois(state):
        return False
    now = state.clock()
    state.duckcoins -= config.BOURGEOIS_COST
    state.boost_end = now + config.BOURGEOIS_DURATION
    state.bourgeois_ready = now + config.BOURGEOIS_COOLDOWN
    state.bourgeois_purchases += 1
    return True


def format_time(milliseconds):
    """60000 -> "1:00"."""
    seconds = math.ceil(milliseconds / 1000)
    return f'{seconds // 60}:{seconds % 60:02d}'


def bourgeois_description(state):
    """Tooltip lines for the Bourgeois Duck."""
    lines = [t('bourgeois_duck_effect', minutes=f'{config.BOURGEOIS_DURATION / 60000:g}',
               damage=config.BOURGEOIS_DAMAGE_MULTIPLIER, coins=config.BOURGEOIS_REWARD_MULTIPLIER)]
    if state.is_boosted():
        lines.append(t('bourgeois_active', time=format_time(state.boost_time_left())))
    if state.bourgeois_recharge_left():
        lines.append(t('bourgeois_recharging', time=format_time(state.bourgeois_recharge_left())))
    else:
        lines.append(t('bourgeois_recharge_info', minutes=f'{config.BOURGEOIS_COOLDOWN / 60000:g}'))
    return lines
