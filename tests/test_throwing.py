import pygame
import pytest

from duck_vs_toast import config, levels, save, shop
from duck_vs_toast.assets import Sprite
from duck_vs_toast.throwing import Throws
from tests.helpers import new_game

SIAMESE, DOUBLE, MUSCULAR, REALISTIC = shop.DUCKS

TOAST_CENTER = pygame.Rect(config.TOAST_RECT).center
DUCK_HOME = (900, 300)  # to the right of the toast, like the starter duck


def duck_sprite(pos=DUCK_HOME, size=(100, 80)):
    """A plain square "duck", see-through in its top-left corner."""
    image = pygame.Surface(size, pygame.SRCALPHA)
    image.fill((255, 220, 100, 255))
    image.fill((0, 0, 0, 0), (0, 0, 20, 20))
    return Sprite(image, pos)


def setup(duckcoins=0):
    state, clock = new_game(duckcoins)
    throws = Throws(clock=clock)
    sprites = {'starter_duck': duck_sprite()}
    return state, clock, throws, sprites


def fly(throws, state, sprites, clock, ms, step=33):
    """Let the game run for ms milliseconds; returns every duck that hit the toast."""
    hits = []
    end = clock.now + ms
    while clock.now < end:
        clock.now += step
        hits += throws.update(state, sprites)
    return hits


def fling(throws, clock, start, end, ms=60):
    """Grab the duck at start and drag it to end in ms milliseconds, then let go."""
    throws.grab('starter_duck', start, duck_sprite())
    clock.now += ms
    throws.release(end)


# --- The rules (GameState) ---

def test_every_duck_on_screen_can_be_thrown_including_the_starter_duck():
    state, _ = new_game(duckcoins=10**6)
    assert state.throwable_ducks() == ['starter_duck']
    shop.buy(state, SIAMESE)
    assert state.throwable_ducks() == ['starter_duck', 'siamese_duck']


def test_a_throw_takes_a_share_of_the_toast_health():
    state, _ = new_game()
    state.level = 12
    state.load_level()
    expected = round(state.max_health * config.THROW_DAMAGE)
    assert state.duck_hits_toast('starter_duck')
    assert state.health == state.max_health - expected


def test_bosses_take_a_smaller_share():
    state, _ = new_game()
    state.level = 10
    state.load_level()
    assert state.throw_damage() == round(state.max_health * config.THROW_BOSS_DAMAGE)


def test_the_bourgeois_duck_boosts_throws_too():
    state, _ = new_game(duckcoins=config.BOURGEOIS_COST)
    normal = state.throw_damage()
    shop.buy_bourgeois(state)
    assert state.throw_damage() == normal * config.BOURGEOIS_DAMAGE_MULTIPLIER


def test_after_five_hits_a_duck_is_battered_and_does_no_damage():
    state, _ = new_game()
    state.level = 30
    state.load_level()
    for _ in range(config.DUCK_MAX_BUMPS):
        assert state.duck_hits_toast('starter_duck')
    assert state.is_battered('starter_duck')
    health = state.health
    assert not state.duck_hits_toast('starter_duck')
    assert state.health == health


def test_a_battered_duck_keeps_its_shop_bonus():
    state, _ = new_game(duckcoins=10**6)
    shop.buy(state, SIAMESE)
    state.duck_bumps['siamese_duck'] = config.DUCK_MAX_BUMPS
    assert state.is_battered('siamese_duck')
    assert state.dps == config.STARTING_DPS_BASE


def test_healing_costs_about_one_toast_and_fixes_the_duck():
    state, _ = new_game(duckcoins=10**9)
    state.level = 20
    state.load_level()  # a boss level: the price comes from the level before
    state.duck_bumps['starter_duck'] = config.DUCK_MAX_BUMPS
    cost = levels.reward_for(19)
    assert state.heal_cost() == cost
    assert state.heal_duck('starter_duck')
    assert state.duckcoins == 10**9 - cost
    assert state.bumps('starter_duck') == 0


def test_healing_needs_enough_duckcoins_and_a_battered_duck():
    state, _ = new_game(duckcoins=0)
    state.duck_bumps['starter_duck'] = config.DUCK_MAX_BUMPS
    assert not state.heal_duck('starter_duck')
    assert state.is_battered('starter_duck')
    state.duckcoins = 10**9
    state.duck_bumps['starter_duck'] = 2
    assert not state.heal_duck('starter_duck')  # not battered: nothing to heal
    assert state.duckcoins == 10**9


def test_how_battered_each_duck_is_is_saved():
    state, _ = new_game()
    state.duck_bumps['starter_duck'] = 3
    loaded, _ = new_game()
    save.from_dict(loaded, save.to_dict(state, wall_time=0), wall_time=0)
    assert loaded.bumps('starter_duck') == 3


# --- Moving the ducks (Throws) ---

def test_a_duck_is_grabbed_by_its_drawing_not_its_see_through_corner():
    _, _, throws, sprites = setup()
    assert throws.duck_at((DUCK_HOME[0] + 50, DUCK_HOME[1] + 40), sprites) == 'starter_duck'
    assert throws.duck_at((DUCK_HOME[0] + 5, DUCK_HOME[1] + 5), sprites) is None
    assert throws.duck_at((10, 10), sprites) is None


def test_a_held_duck_follows_the_mouse():
    _, clock, throws, _ = setup()
    grab = (DUCK_HOME[0] + 50, DUCK_HOME[1] + 40)
    throws.grab('starter_duck', grab, duck_sprite())
    clock.now += 16
    throws.move((700, 100))
    assert throws.moving['starter_duck'].pos == pygame.Vector2(650, 60)
    assert throws.held == 'starter_duck'


def test_flinging_a_duck_at_the_toast_hits_it_and_the_duck_goes_home():
    state, clock, throws, sprites = setup()
    health = state.health
    start = (DUCK_HOME[0] + 50, DUCK_HOME[1] + 40)
    fling(throws, clock, start, (start[0] - 60, start[1] - 10))  # a quick flick to the left
    assert fly(throws, state, sprites, clock, 600) == ['starter_duck']
    assert state.health < health
    assert state.bumps('starter_duck') == 1
    fly(throws, state, sprites, clock, config.THROW_RETURN_TIME + 100)
    assert not throws.is_away('starter_duck')


def test_dropping_a_duck_on_the_toast_hits_it():
    state, clock, throws, sprites = setup()
    start = (DUCK_HOME[0] + 50, DUCK_HOME[1] + 40)
    throws.grab('starter_duck', start, duck_sprite())
    clock.now += 500
    throws.move(TOAST_CENTER)
    clock.now += 500  # held still for a while: no speed
    throws.release(TOAST_CENTER)
    assert fly(throws, state, sprites, clock, 100) == ['starter_duck']


def test_a_duck_that_misses_does_no_damage_and_comes_back():
    state, clock, throws, sprites = setup()
    health = state.health
    start = (DUCK_HOME[0] + 50, DUCK_HOME[1] + 40)
    fling(throws, clock, start, (start[0] + 80, start[1] - 40))  # away from the toast
    hits = fly(throws, state, sprites, clock, config.THROW_FLIGHT_TIME + config.THROW_RETURN_TIME + 200)
    assert hits == []
    assert state.health == health and state.bumps('starter_duck') == 0
    assert not throws.is_away('starter_duck')


def test_a_very_fast_flick_is_slowed_down():
    _, clock, throws, _ = setup()
    start = (DUCK_HOME[0] + 50, DUCK_HOME[1] + 40)
    fling(throws, clock, start, (start[0] - 5000, start[1]), ms=10)
    assert throws.moving['starter_duck'].velocity.length() == pytest.approx(config.THROW_MAX_SPEED)


def test_dropping_without_throwing_sends_the_duck_home():
    state, clock, throws, sprites = setup()
    throws.grab('starter_duck', (DUCK_HOME[0] + 50, DUCK_HOME[1] + 40), duck_sprite())
    throws.move(TOAST_CENTER)
    throws.drop()
    assert throws.held is None
    assert fly(throws, state, sprites, clock, config.THROW_RETURN_TIME + 100) == []
    assert not throws.is_away('starter_duck')


def test_flying_ducks_cant_be_caught():
    state, clock, throws, sprites = setup()
    start = (DUCK_HOME[0] + 50, DUCK_HOME[1] + 40)
    fling(throws, clock, start, (start[0] + 80, start[1] - 40))
    duck = throws.moving['starter_duck']
    assert throws.duck_at(tuple(duck.center), sprites) is None
