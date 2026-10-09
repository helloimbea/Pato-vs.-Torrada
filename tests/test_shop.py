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


def test_purchases_are_counted():
    state, _ = new_game(duckcoins=10**9)
    shop.buy(state, SIAMESE)
    shop.buy(state, SIAMESE)
    shop.buy(state, DOUBLE)
    assert state.purchases[SIAMESE.name] == 2
    assert state.purchases[DOUBLE.name] == 1
    assert state.purchases[MUSCULAR.name] == 0


def test_failed_purchase_is_not_counted():
    state, _ = new_game(duckcoins=0)
    shop.buy(state, SIAMESE)
    assert state.purchases[SIAMESE.name] == 0


def test_tooltips_describe_what_the_next_purchase_does():
    state, _ = new_game(duckcoins=10**9)
    assert SIAMESE.describe(state) == 'Adds 12.5 damage per second.'
    assert DOUBLE.describe(state) == 'Doubles your click damage (1 -> 2).'
    assert MUSCULAR.describe(state) == 'Clicks the toast for you every 1.95 s, with your click damage.'
    shop.buy(state, MUSCULAR)
    assert state.auto_click_interval == 1950  # the tooltip was right
    assert MUSCULAR.describe(state) == 'Clicks the toast for you every 1.9 s, with your click damage.'
    for duck in shop.DUCKS:
        assert duck.title and duck.describe(state)


def test_buying_tells_the_screen_so_the_duck_can_stretch():
    state, _ = new_game(duckcoins=10**6)
    bought = []
    state.on_buy = lambda name, first_time: bought.append((name, first_time))
    shop.buy(state, SIAMESE)
    shop.buy(state, SIAMESE)
    assert bought == [('siamese_duck', True), ('siamese_duck', False)]


def test_bourgeois_duck_boosts_damage_and_duckcoins_for_a_minute():
    state, clock = new_game(duckcoins=config.BOURGEOIS_COST)
    state.dps = 10
    assert shop.buy_bourgeois(state)
    assert state.duckcoins == 0
    assert state.click_damage() == state.damage * config.BOURGEOIS_DAMAGE_MULTIPLIER
    assert state.current_dps() == 10 * config.BOURGEOIS_DAMAGE_MULTIPLIER
    assert state.current_reward() == state.reward * config.BOURGEOIS_REWARD_MULTIPLIER
    clock.now += config.BOURGEOIS_DURATION
    assert not state.is_boosted()
    assert state.click_damage() == state.damage and state.current_reward() == state.reward


def test_beating_a_toast_while_boosted_pays_double():
    state, _ = new_game(duckcoins=config.BOURGEOIS_COST)
    shop.buy_bourgeois(state)
    reward = state.reward
    state.deal_damage(state.health)
    assert state.duckcoins == reward * config.BOURGEOIS_REWARD_MULTIPLIER


def test_bourgeois_duck_has_a_fixed_price_and_recharges():
    state, clock = new_game(duckcoins=3 * config.BOURGEOIS_COST)
    assert shop.buy_bourgeois(state)
    assert not shop.buy_bourgeois(state)  # recharging
    clock.now += config.BOURGEOIS_COOLDOWN - 1
    assert not shop.can_buy_bourgeois(state)
    clock.now += 1
    assert shop.buy_bourgeois(state)
    assert state.duckcoins == config.BOURGEOIS_COST  # same price both times


def test_bourgeois_duck_needs_enough_duckcoins():
    state, _ = new_game(duckcoins=config.BOURGEOIS_COST - 1)
    assert not shop.buy_bourgeois(state)
    assert not state.is_boosted()


def test_bourgeois_tooltip_says_what_it_does_and_when_it_is_ready():
    state, clock = new_game(duckcoins=config.BOURGEOIS_COST)
    shop.buy_bourgeois(state)
    clock.now += 15_000
    lines = shop.bourgeois_description(state)
    assert 'x2 damage' in lines[0]
    assert lines[1] == 'Active! 0:45 left.'
    assert lines[2] == 'Recharging: ready in 9:45.'
