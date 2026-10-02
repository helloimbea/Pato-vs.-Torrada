from duck_vs_toast import config, levels, shop
from duck_vs_toast.state import GameState
from tests.helpers import new_game

SIAMESE, DOUBLE, MUSCULAR, REALISTIC = shop.DUCKS


def test_game_starts_on_level_1_with_full_health():
    state, _ = new_game()
    assert state.level == 1
    assert state.toast == 'nerd_toast'
    assert state.health == state.max_health == levels.health_for(1)


def test_defeating_a_toast_pays_and_goes_to_the_next_level():
    state, _ = new_game()
    state.deal_damage(state.max_health)
    assert state.duckcoins == levels.reward_for(1)
    assert state.level == 2
    assert state.health == levels.health_for(2)


def test_farming_keeps_the_same_level():
    state, _ = new_game()
    state.toggle_level_advance()
    state.deal_damage(state.max_health)
    state.deal_damage(state.max_health)
    assert state.level == 1
    assert state.duckcoins == 2 * levels.reward_for(1)


def test_levels_never_run_out():
    state, _ = new_game()
    for _ in range(100):
        state.deal_damage(state.max_health)
    assert state.level == 101
    assert state.health > 0


def test_previous_level_stops_at_level_1():
    state, _ = new_game()
    state.previous_level()
    assert state.level == 1
    state.deal_damage(state.max_health)
    state.previous_level()
    assert state.level == 1
    assert state.health == state.max_health


def test_boss_gets_its_health_back_when_time_runs_out():
    state, clock = new_game()
    state.level = 5
    state.load_level()
    state.deal_damage(1)
    clock.now = config.BOSS_TIME_LIMIT - 1
    state.update(clock.now)
    assert state.health == state.max_health - 1
    clock.now = config.BOSS_TIME_LIMIT
    state.update(clock.now)
    assert state.health == state.max_health
    assert state.boss_time_left(clock.now) == config.BOSS_TIME_LIMIT // 1000


def test_dps_hits_once_per_second_even_at_30_fps():
    state, clock = new_game(duckcoins=10**9)
    shop.buy(state, SIAMESE)
    state.level_advance = False
    hits = []
    state.deal_damage = hits.append
    while clock.now < 60000:
        clock.now += 1000 / 30
        state.update(int(clock.now))
    assert len(hits) == 60
    assert sum(hits) == 60 * config.STARTING_DPS_BASE


def test_muscular_duck_uses_the_current_click_damage():
    state, clock = new_game(duckcoins=10**15)
    shop.buy(state, MUSCULAR)
    shop.buy(state, DOUBLE)
    shop.buy(state, DOUBLE)
    hits = []
    state.deal_damage = hits.append
    clock.now = 5000
    state.update(clock.now)
    assert hits == [4 * config.STARTING_DAMAGE]


def test_interval_passed_keeps_a_steady_rhythm():
    assert GameState.interval_passed(now=999, last=0, interval=1000) == (False, 0)
    assert GameState.interval_passed(now=1030, last=0, interval=1000) == (True, 1000)
    # Far behind (e.g. a duck was just bought): restart from now instead of hitting many times
    assert GameState.interval_passed(now=5000, last=0, interval=1000) == (True, 5000)
