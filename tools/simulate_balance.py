"""Balance simulator: a virtual player plays the real game rules at high speed.

It shows how long it takes to reach each level, so you can tweak the numbers in
duck_vs_toast/levels.py (or the duck prices in duck_vs_toast/shop.py) and see
the effect right away, without playing for an hour.

Run it from the project folder with:

    python -m tools.simulate_balance

The virtual player:
  - clicks the toast CLICKS_PER_SECOND times per second;
  - always saves up for the duck that adds the most damage per Duckcoin;
  - when a boss is too strong to beat in time, goes back one level and farms
    Duckcoins until it is strong enough.
"""
import copy

from duck_vs_toast import config, levels, shop
from duck_vs_toast.state import GameState

CLICKS_PER_SECOND = 5
STEP_MS = 50                  # simulated time per step
BOSS_SAFETY_MARGIN = 1.1      # only try a boss with 10% more damage than needed


def damage_per_second(state):
    """Total damage per second: clicks + DPS ducks + muscular duck's auto-click."""
    total = state.damage * CLICKS_PER_SECOND + state.dps
    if state.has_auto_click:
        total += state.damage * 1000 / state.auto_click_interval
    return total


def best_duck(state):
    """The duck that adds the most damage per second for each Duckcoin spent."""
    best, best_value = None, 0
    current = damage_per_second(state)
    for duck in shop.DUCKS:
        trial = copy.deepcopy(state)
        trial.duckcoins = state.costs[duck.name]
        shop.buy(trial, duck)
        value = (damage_per_second(trial) - current) / state.costs[duck.name]
        if value > best_value:
            best, best_value = duck, value
    return best


def can_beat_boss(state, level):
    boss_health = levels.health_for(level)
    seconds = config.BOSS_TIME_LIMIT / 1000
    return damage_per_second(state) * seconds >= boss_health * BOSS_SAFETY_MARGIN


def simulate(target_level=54, max_minutes=360):
    """Play until target_level. Returns {level: minutes when it was first reached}."""
    now = [0]
    state = GameState(clock=lambda: now[0])
    reached = {1: 0.0}
    next_click = 0
    farming = False
    duck = None

    while state.level < target_level and now[0] < max_minutes * 60000:
        now[0] += STEP_MS

        # Click the toast
        while next_click <= now[0]:
            state.deal_damage(state.damage)
            next_click += 1000 / CLICKS_PER_SECOND

        state.update(now[0])

        # Shopping (the best duck only changes after buying something)
        if duck is None:
            duck = best_duck(state)
        while duck and state.duckcoins >= state.costs[duck.name]:
            shop.buy(state, duck)
            duck = best_duck(state)

        # Bosses: farm the previous level until strong enough
        next_level = state.level + 1
        if not farming and levels.is_boss(next_level) and not can_beat_boss(state, next_level):
            farming = True
            state.level_advance = False
        if farming and can_beat_boss(state, next_level):
            farming = False
            state.level_advance = True
        boss_just_reset = (state.is_boss() and state.health == state.max_health
                           and now[0] - state.boss_start < STEP_MS)
        if boss_just_reset and not can_beat_boss(state, state.level):
            # The boss timer ran out (or the boss just appeared) and we are too weak: go back
            state.previous_level()
            farming = True
            state.level_advance = False

        if state.level not in reached:
            reached[state.level] = now[0] / 60000
    return reached


def main():
    reached = simulate()
    print('Level  Toast                        Health      Reward   Reached at   Time on these 5 levels')
    for level in sorted(reached):
        if level % 5 == 0 or level in (1, max(reached)):
            spent = reached[level] - reached.get(level - 5, 0) if level >= 5 else 0
            print(f'{level:>5}  {levels.toast_for(level):<26}  {levels.health_for(level):>8.3g}'
                  f'  {levels.reward_for(level):>10.3g}  {reached[level]:>7.1f} min  {spent:>8.1f} min')
    if 54 in reached:
        print(f'\nLevel 54 reached after {reached[54]:.0f} minutes.')
    else:
        print(f'\nGot stuck: only reached level {max(reached)}.')


if __name__ == '__main__':
    main()
