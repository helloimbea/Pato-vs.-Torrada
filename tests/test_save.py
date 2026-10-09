import json
import math

import pytest

from duck_vs_toast import config, levels, save, shop
from duck_vs_toast.clock import GameClock
from tests.helpers import FakeClock, new_game

SIAMESE, DOUBLE, MUSCULAR, REALISTIC = shop.DUCKS


def played_game():
    state, clock = new_game(duckcoins=10**8)
    for duck in (SIAMESE, SIAMESE, DOUBLE, MUSCULAR, REALISTIC):
        shop.buy(state, duck)
    state.level = 12
    state.highest_level = 14
    state.level_advance = False
    state.muted = True
    state.load_level()
    return state, clock


def test_saving_and_loading_keeps_the_progress(tmp_path):
    state, _ = played_game()
    path = str(tmp_path / 'save.json')
    save.save(state, path)

    loaded, _ = new_game()
    away = save.load(loaded, path)
    assert away == pytest.approx(0, abs=5)
    for field in save.SAVED_FIELDS:
        assert getattr(loaded, field) == getattr(state, field), field
    assert loaded.toast == state.toast and loaded.health == loaded.max_health


def test_no_save_starts_a_new_game(tmp_path):
    state, _ = new_game()
    assert save.load(state, str(tmp_path / 'missing.json')) is None
    assert state.level == 1


def test_broken_save_starts_a_new_game_and_is_kept_aside(tmp_path):
    path = tmp_path / 'save.json'
    path.write_text('{ this is not json')
    state, _ = new_game()
    assert save.load(state, str(path)) is None
    assert state.level == 1
    assert (tmp_path / 'save.json.broken').exists()


def test_old_saves_keep_defaults_for_new_things():
    state, _ = new_game()
    data = save.to_dict(played_game()[0], wall_time=1000)
    del data['victory_seen']
    del data['costs']['realistic_duck']
    save.from_dict(state, json.loads(json.dumps(data)), wall_time=1000)
    assert state.victory_seen is False
    assert state.costs['realistic_duck'] == REALISTIC.starting_cost
    assert state.level == 12


def test_time_away_is_counted_and_the_bourgeois_duck_keeps_recharging():
    state, clock = new_game(duckcoins=config.BOURGEOIS_COST)
    shop.buy_bourgeois(state)
    data = save.to_dict(state, wall_time=1000)

    loaded, _ = new_game()
    away = save.from_dict(loaded, data, wall_time=1000 + 120)  # closed for 2 minutes
    assert away == 120
    assert not loaded.is_boosted()  # the 1-minute boost ran out while closed
    assert loaded.bourgeois_recharge_left() == config.BOURGEOIS_COOLDOWN - 120_000


def test_offline_earnings_come_from_dps_and_stop_at_the_limit():
    state, _ = new_game()
    assert save.offline_earnings(state, 3600) == 0  # no ducks, nothing earned
    state.level = 3
    state.dps = math.ceil(levels.health_for(3) / 10)  # beats a toast every 10 seconds
    assert save.offline_earnings(state, 100) == pytest.approx(10 * levels.reward_for(3), rel=1e-6)
    limit = config.OFFLINE_LIMIT_HOURS * 3600
    assert save.offline_earnings(state, limit * 3) == save.offline_earnings(state, limit)


def test_offline_earnings_cannot_beat_more_than_one_toast_per_hit():
    state, _ = new_game()
    state.level = 3
    state.dps = levels.health_for(3) * 1000  # huge overkill: still one toast per second
    assert save.offline_earnings(state, 60) == 60 * levels.reward_for(3)


def test_offline_earnings_waste_extra_damage_like_the_game():
    state, _ = new_game()
    state.level = 3
    state.dps = math.ceil(levels.health_for(3) * 0.6)  # needs 2 hits: one toast every 2 s
    assert save.offline_earnings(state, 60) == 30 * levels.reward_for(3)


def test_game_clock_stops_while_paused():
    real = FakeClock()
    clock = GameClock(real_clock=real, paused=True)
    real.now = 5000  # time on the start screen doesn't count
    assert clock() == 0
    clock.resume()
    real.now = 6000
    assert clock() == 1000
    clock.pause()
    real.now = 9000
    assert clock() == 1000 and clock.paused
    clock.resume()
    real.now = 9500
    assert clock() == 1500
