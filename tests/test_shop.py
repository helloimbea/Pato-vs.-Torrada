from duck_vs_toast import config, shop
from tests.helpers import new_game

SIAMESE, DOUBLE, MUSCULAR, REALISTIC = shop.DUCKS


def test_cannot_buy_without_enough_duckcoins():
    state, _ = new_game(duckcoins=199)
    shop.buy(state, SIAMESE)
    assert state.duckcoins == 199
    assert state.dps == 0
    assert state.ducks_on_screen == []


def test_buying_spends_duckcoins_and_raises_the_price():
    state, _ = new_game(duckcoins=1000)
    shop.buy(state, SIAMESE)
    assert state.duckcoins == 800
    assert state.costs['siamese_duck'] == 300
    assert state.ducks_on_screen == ['siamese_duck']


def test_duck_shows_up_only_once_on_screen():
    state, _ = new_game(duckcoins=10**9)
    shop.buy(state, SIAMESE)
    shop.buy(state, SIAMESE)
    assert state.ducks_on_screen == ['siamese_duck']


def test_siamese_duck_adds_dps():
    state, _ = new_game(duckcoins=10**9)
    shop.buy(state, SIAMESE)
    shop.buy(state, SIAMESE)
    assert state.dps == 2 * config.STARTING_DPS_BASE


def test_double_duck_doubles_click_damage():
    state, _ = new_game(duckcoins=10**9)
    shop.buy(state, DOUBLE)
    shop.buy(state, DOUBLE)
    assert state.damage == 4 * config.STARTING_DAMAGE


def test_muscular_duck_clicks_faster_with_each_purchase():
    state, _ = new_game(duckcoins=10**40)
    shop.buy(state, MUSCULAR)
    assert state.has_auto_click
    assert state.auto_click_interval == config.AUTO_CLICK_INTERVAL_START - config.AUTO_CLICK_INTERVAL_STEP
    for _ in range(100):
        shop.buy(state, MUSCULAR)
    assert state.auto_click_interval == config.AUTO_CLICK_INTERVAL_MIN


def test_realistic_duck_doubles_dps_and_future_siamese_ducks():
    state, _ = new_game(duckcoins=10**9)
    shop.buy(state, SIAMESE)
    shop.buy(state, REALISTIC)
    assert state.dps == 2 * config.STARTING_DPS_BASE
    shop.buy(state, SIAMESE)
    assert state.dps == 4 * config.STARTING_DPS_BASE
