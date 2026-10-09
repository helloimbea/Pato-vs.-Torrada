"""Saving and loading the game, and the Duckcoins earned while it was closed.

The save is a small JSON file (config.SAVE_FILE). The game saves every
config.AUTOSAVE_INTERVAL and when it is closed, and loads the save when it starts.
"""
import json
import os
import time

from . import config, levels

SAVE_VERSION = 1

# What is saved: everything about the player's progress. The current toast's health
# is not saved; the toast comes back with full health.
SAVED_FIELDS = [
    'duckcoins', 'level', 'level_advance', 'highest_level',
    'damage', 'dps', 'dps_base', 'has_auto_click', 'auto_click_interval',
    'costs', 'purchases', 'ducks_on_screen', 'bourgeois_purchases',
    'muted', 'victory_seen',
]


def to_dict(state, wall_time=None):
    data = {field: getattr(state, field) for field in SAVED_FIELDS}
    data['version'] = SAVE_VERSION
    data['saved_at'] = time.time() if wall_time is None else wall_time
    # Bourgeois Duck times are saved as "how long is left", because the game's clock
    # starts from zero every time the game opens
    data['boost_left'] = state.boost_time_left()
    data['bourgeois_recharge_left'] = state.bourgeois_recharge_left()
    return data


def from_dict(state, data, wall_time=None):
    """Put the saved progress into a new game. Returns how many seconds the game was closed."""
    for field in SAVED_FIELDS:
        if field not in data:  # saves from older versions keep the default for new things
            continue
        value = data[field]
        default = getattr(state, field)
        if isinstance(default, dict):  # keep new ducks that didn't exist when it was saved
            default.update(value)
        else:
            setattr(state, field, value)

    now = time.time() if wall_time is None else wall_time
    away = max(0.0, now - data.get('saved_at', now))
    # The Bourgeois Duck kept recharging (and its boost kept running out) while closed
    clock_now = state.clock()
    boost_left = data.get('boost_left', 0) - away * 1000
    if boost_left > 0:
        state.boost_end = clock_now + boost_left
    recharge_left = data.get('bourgeois_recharge_left', 0) - away * 1000
    if recharge_left > 0:
        state.bourgeois_ready = clock_now + recharge_left
    state.load_level()
    return away


def save(state, path=None):
    """Write the save file. It is written to a temporary file first, so a crash
    in the middle never leaves a broken save behind."""
    path = path or config.SAVE_FILE
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temporary = path + '.tmp'
    with open(temporary, 'w') as file:
        json.dump(to_dict(state), file, indent=1)
    os.replace(temporary, path)


def load(state, path=None):
    """Load the save file into a new game, if there is one.

    Returns how many seconds the game was closed, or None when there was no save
    (or it couldn't be read; a broken save is kept as save.json.broken).
    """
    path = path or config.SAVE_FILE
    try:
        with open(path) as file:
            data = json.load(file)
        return from_dict(state, data)
    except FileNotFoundError:
        return None
    except (ValueError, TypeError, AttributeError):
        print(f'Could not read the save file {path}; starting a new game.')
        os.replace(path, path + '.broken')
        return None


# --- Offline earnings ---

def offline_earnings(state, seconds):
    """Duckcoins the ducks earn while the game is closed, for at most OFFLINE_LIMIT_HOURS.

    The ducks keep beating the current level's toast (without moving on), at the speed
    they would in the game: DPS and the muscular duck, but not clicks. On a boss level
    they beat the toast before it instead (a boss has a timer nobody is watching).
    """
    seconds = min(seconds, config.OFFLINE_LIMIT_HOURS * 3600)
    level = state.level - 1 if levels.is_boss(state.level) else state.level
    time_per_toast = time_to_beat(levels.health_for(level), state)
    if time_per_toast is None:
        return 0
    return round(seconds / time_per_toast * levels.reward_for(level))


def time_to_beat(health, state):
    """Seconds the ducks take to beat a toast on their own (None if they can't).

    DPS hits once per second and the muscular duck once per interval, so damage beyond
    what the toast needs is wasted, like in the game.
    """
    hits = []  # (seconds between hits, damage of each hit)
    if state.dps:
        hits.append((config.DPS_INTERVAL / 1000, state.dps))
    if state.has_auto_click:
        hits.append((state.auto_click_interval / 1000, state.damage))
    if not hits:
        return None
    damage_per_second = sum(damage / interval for interval, damage in hits)
    if health / damage_per_second > 1000:  # very slow: an average is close enough
        return health / damage_per_second
    # Hit by hit, in order, until the toast is beaten
    next_hit = [interval for interval, _ in hits]
    while True:
        source = min(range(len(hits)), key=lambda i: next_hit[i])
        health -= hits[source][1]
        if health <= 0:
            return next_hit[source]
        next_hit[source] += hits[source][0]
