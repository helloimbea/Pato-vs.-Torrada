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
    # In a wider window the counter is further left of the toast, and the coins still reach it
    assert fx.coin_position(coin, arrival, target=(-178, 61)) == pytest.approx((-178, 61))
    clock.now = fx.coins[-1].start + config.COIN_BURST_TIME + config.COIN_FLIGHT_TIME
    fx.update()
    assert fx.coins == []


def test_toast_flinches_and_looks_hurt_after_any_hit(effects):
    fx, clock = effects
    clock.now = 1000
    assert fx.squish() == 0 and not fx.is_hurt()
    fx.hit(12.5, 'dps')
    clock.now += config.SQUISH_DURATION // 2
    assert fx.squish() == pytest.approx(1)  # most squashed halfway through
    assert fx.is_hurt()
    clock.now = 1000 + config.SQUISH_DURATION
    assert fx.squish() == 0
    clock.now = 1000 + config.HURT_DURATION
    assert not fx.is_hurt()


def test_beaten_toast_falls_over_while_the_next_one_pops_up(effects):
    fx, clock = effects
    assert fx.death() is None and fx.spawn() == 1
    fx.defeat('nerd_toast')
    assert fx.dead_toast == 'nerd_toast'
    assert fx.death() == 0
    assert fx.spawn() == 0  # the next toast waits a moment
    clock.now += config.SPAWN_DELAY + config.SPAWN_DURATION // 2
    assert fx.spawn() > 0
    clock.now += config.SPAWN_DURATION
    assert fx.spawn() == 1
    clock.now += config.DEATH_DURATION
    fx.update()
    assert fx.death() is None and fx.dead_toast is None


def test_bought_duck_stretches_then_settles(effects):
    fx, clock = effects
    assert fx.duck_scale('siamese_duck') == (1, 1)
    fx.duck_bought('siamese_duck', first_time=False)
    clock.now += config.DUCK_POP_DURATION // 6  # first it gets taller and thinner
    width, height = fx.duck_scale('siamese_duck')
    assert height > 1 > width
    clock.now += config.DUCK_POP_DURATION // 3  # then shorter and wider
    width, height = fx.duck_scale('siamese_duck')
    assert width > 1 > height
    clock.now += config.DUCK_POP_DURATION
    assert fx.duck_scale('siamese_duck') == (1, 1)


def test_new_duck_grows_in_from_nothing(effects):
    fx, clock = effects
    fx.duck_bought('realistic_duck', first_time=True)
    assert fx.duck_scale('realistic_duck') == (0, 0)
    clock.now += config.DUCK_GROW_TIME
    assert fx.duck_scale('realistic_duck')[1] > 0.9
