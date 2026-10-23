import pygame

from duck_vs_toast import config, save, shop
from duck_vs_toast.assets import Sprite
from duck_vs_toast.smacking import Smacking
from duck_vs_toast.state import GameState
from tests.helpers import FakeClock

SIAMESE, DOUBLE, MUSCULAR, REALISTIC = shop.DUCKS

TOAST_CENTER = pygame.Rect(config.TOAST_RECT).center
DUCK_HOME = (900, 300)
GRAB = (DUCK_HOME[0] + 50, DUCK_HOME[1] + 40)  # on the duck's drawing
OUTSIDE = (1100, 300)                            # the duck's middle is far from the toast here


class FixedRandom:
    """Always "rolls" the same number: 0 is always a critical hit, 1 never."""

    def __init__(self, value):
        self.value = value

    def random(self):
        return self.value


def game_with_muscular_duck(crit=False):
    clock = FakeClock()
    state = GameState(clock=clock, rng=FixedRandom(0 if crit else 1))
    state.duckcoins = 10**9
    shop.buy(state, MUSCULAR)
    state.level = 31  # lots of health (and not a boss, whose health comes back)
    state.load_level()
    return state, clock


def duck_sprite():
    """A plain square "duck", see-through in its top-left corner."""
    image = pygame.Surface((100, 80), pygame.SRCALPHA)
    image.fill((255, 220, 100, 255))
    image.fill((0, 0, 0, 0), (0, 0, 20, 20))
    return Sprite(image, DUCK_HOME)


def drag_to(smacking, state, point):
    """Move the mouse so the duck's middle ends up at point."""
    offset = pygame.Vector2(smacking.size) / 2 - smacking.grab_offset
    return smacking.move(pygame.Vector2(point) - offset, state)


# --- The rules (GameState) ---

def test_a_smack_does_five_clicks_of_damage():
    state, _ = game_with_muscular_duck()
    shop.buy(state, DOUBLE)
    health = state.health
    assert state.smack_toast() == 'hit'
    assert health - state.health == 5 * state.click_damage()


def test_a_critical_smack_does_much_more():
    state, _ = game_with_muscular_duck(crit=True)
    health = state.health
    assert state.smack_toast() == 'crit'
    assert health - state.health == config.SMACK_DAMAGE * config.SMACK_CRIT_MULTIPLIER * state.click_damage()


def test_the_bourgeois_boost_makes_smacks_stronger_too():
    state, _ = game_with_muscular_duck()
    shop.buy_bourgeois(state)
    health = state.health
    state.smack_toast()
    assert health - state.health == config.SMACK_DAMAGE * config.BOURGEOIS_DAMAGE_MULTIPLIER


def test_only_the_muscular_duck_smacks_and_only_after_buying_it():
    clock = FakeClock()
    state = GameState(clock=clock)
    assert state.smack_toast() is None


def test_after_five_smacks_the_duck_rests_for_two_minutes():
    state, clock = game_with_muscular_duck()
    for _ in range(config.SMACKS_BEFORE_REST):
        assert state.smack_toast() == 'hit'
    assert state.is_muscular_resting()
    assert state.muscular_rest_left() == config.MUSCULAR_REST
    health = state.health
    assert state.smack_toast() is None
    assert state.health == health

    clock.now = config.MUSCULAR_REST
    assert not state.is_muscular_resting()
    assert state.smack_toast() == 'hit'


def test_a_resting_duck_stops_clicking_on_its_own():
    state, clock = game_with_muscular_duck()
    for _ in range(config.SMACKS_BEFORE_REST):
        state.smack_toast()
    health = state.health
    while clock.now < config.MUSCULAR_REST - 100:
        clock.now += 33
        state.update(clock.now)
    assert state.health == health
    clock.now = config.MUSCULAR_REST + 3000
    state.update(clock.now)
    assert state.health < health  # back to work


def test_smacks_and_the_rest_are_saved():
    state, clock = game_with_muscular_duck()
    for _ in range(config.SMACKS_BEFORE_REST + 2):
        state.smack_toast()  # the last two do nothing: it is resting
    clock.now = 20_000
    data = save.to_dict(state, wall_time=0)

    loaded = GameState(clock=FakeClock())
    save.from_dict(loaded, data, wall_time=0)
    assert loaded.muscular_rest_left() == config.MUSCULAR_REST - 20_000
    loaded2 = GameState(clock=FakeClock())
    save.from_dict(loaded2, data, wall_time=200)  # closed for longer than the rest
    assert not loaded2.is_muscular_resting()


# --- Holding the duck (Smacking) ---

def test_the_duck_is_grabbed_by_its_drawing_only():
    state, clock = game_with_muscular_duck()
    smacking = Smacking(clock=clock)
    assert smacking.can_grab(state, GRAB, duck_sprite())
    assert not smacking.can_grab(state, (DUCK_HOME[0] + 5, DUCK_HOME[1] + 5), duck_sprite())


def test_the_duck_cant_be_grabbed_before_buying_it_or_while_resting():
    clock = FakeClock()
    state = GameState(clock=clock)
    smacking = Smacking(clock=clock)
    assert not smacking.can_grab(state, GRAB, duck_sprite())
    state, clock = game_with_muscular_duck()
    for _ in range(config.SMACKS_BEFORE_REST):
        state.smack_toast()
    assert not smacking.can_grab(state, GRAB, duck_sprite())


def test_dragging_the_duck_into_the_toast_smacks_it_once():
    state, clock = game_with_muscular_duck()
    smacking = Smacking(clock=clock)
    smacking.grab(GRAB, duck_sprite())
    health = state.health
    assert drag_to(smacking, state, TOAST_CENTER) == 'hit'
    assert drag_to(smacking, state, (TOAST_CENTER[0] + 10, TOAST_CENTER[1])) is None  # still inside
    assert health - state.health == config.SMACK_DAMAGE * state.click_damage()
    assert smacking.impact is not None


def test_the_duck_has_to_come_out_before_smacking_again():
    state, clock = game_with_muscular_duck()
    smacking = Smacking(clock=clock)
    smacking.grab(GRAB, duck_sprite())
    hits = []
    for _ in range(3):
        hits.append(drag_to(smacking, state, TOAST_CENTER))
        drag_to(smacking, state, OUTSIDE)
    assert hits == ['hit'] * 3
    assert state.smacks == 3


def test_after_the_last_smack_the_duck_is_let_go_and_hops_home():
    state, clock = game_with_muscular_duck()
    smacking = Smacking(clock=clock)
    sprite = duck_sprite()
    smacking.grab(GRAB, sprite)
    for _ in range(config.SMACKS_BEFORE_REST):
        drag_to(smacking, state, TOAST_CENTER)
        drag_to(smacking, state, OUTSIDE)
    assert not smacking.held
    assert state.is_muscular_resting()
    clock.now += config.RETURN_TIME
    smacking.update(sprite)
    assert not smacking.is_away()


def test_letting_go_sends_the_duck_home():
    state, clock = game_with_muscular_duck()
    smacking = Smacking(clock=clock)
    sprite = duck_sprite()
    smacking.grab(GRAB, sprite)
    drag_to(smacking, state, (700, 100))
    smacking.release()
    clock.now += config.RETURN_TIME // 2
    smacking.update(sprite)
    assert smacking.is_away()
    clock.now += config.RETURN_TIME
    smacking.update(sprite)
    assert not smacking.is_away()
