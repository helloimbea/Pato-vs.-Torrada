import random

import pygame
import pytest

from duck_vs_toast import config
from duck_vs_toast.effects import Effects
from tests.helpers import FakeClock, new_game


@pytest.fixture
def effects():
    clock = FakeClock()
    return Effects(clock=clock, rng=random.Random(1)), clock


def test_state_reports_hits_and_defeats():
    state, _ = new_game()
    hits, defeats = [], []
    state.on_hit = lambda amount, kind: hits.append((amount, kind))
    state.on_defeat = lambda: defeats.append(state.level)

    state.deal_damage(1)
    state.deal_damage(state.max_health)
    assert [kind for _, kind in hits] == ['click', 'click']
    assert hits[0][0] == 1
    assert defeats == [1]  # reported before moving on to level 2


def test_automatic_hits_say_where_they_came_from():
    state, clock = new_game()
    kinds = []
    state.on_hit = lambda _amount, kind: kinds.append(kind)
    state.dps = 1
    state.has_auto_click = True
    clock.now = 2000
    state.update(clock.now)
    assert sorted(kinds) == ['auto', 'dps']


def test_damage_numbers_fade_away(effects):
    fx, clock = effects
    fx.hit(5, 'click', (600, 300))
    fx.hit(12.5, 'dps')
    assert [n.text for n in fx.damage_numbers] == ['5', '12.5']
    clock.now = config.DAMAGE_NUMBER_DURATION
    fx.update()
    assert fx.damage_numbers == []


def test_damage_numbers_are_limited(effects):
    fx, _ = effects
    for _ in range(config.MAX_DAMAGE_NUMBERS + 10):
        fx.hit(1, 'dps')
    assert len(fx.damage_numbers) == config.MAX_DAMAGE_NUMBERS


def test_toast_shakes_on_clicks_but_not_on_dps(effects):
    fx, clock = effects
    clock.now = 1000
    fx.hit(1, 'dps')
    assert fx.toast_offset() == (0, 0)
    fx.hit(1, 'click', (600, 300))
    clock.now += 20
    assert fx.toast_offset() != (0, 0)
    clock.now += config.SHAKE_DURATION
    assert fx.toast_offset() == (0, 0)


def test_coins_fly_to_the_duckcoins_counter(effects):
    fx, clock = effects
    fx.defeat()
    assert len(fx.coins) == config.COINS_PER_DEFEAT
    coin = fx.coins[0]
    assert fx.coin_position(coin, coin.start) == pytest.approx(pygame.Rect(config.TOAST_RECT).center)
    arrival = coin.start + config.COIN_BURST_TIME + config.COIN_FLIGHT_TIME
    assert fx.coin_position(coin, arrival) == pytest.approx(config.DUCKCOINS_ICON_POS)
    clock.now = fx.coins[-1].start + config.COIN_BURST_TIME + config.COIN_FLIGHT_TIME
    fx.update()
    assert fx.coins == []
