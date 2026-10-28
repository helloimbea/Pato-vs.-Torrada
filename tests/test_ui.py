import pygame

from duck_vs_toast import config, shop
from duck_vs_toast.layout import Layout
from duck_vs_toast.ui import Ui, any_affordable
from tests.helpers import new_game

LAYOUT = Layout(config.SCREEN_SIZE)  # the original size: every part is where config.py says


def setup(duckcoins=0):
    state, clock = new_game(duckcoins)
    return state, clock, Ui(clock=clock)


def click(interface, state, point, group='bottom'):
    """A click at a point given in a part's own coordinates."""
    offset_x, offset_y = LAYOUT.offsets[group]
    return interface.click(state, LAYOUT, (point[0] + offset_x, point[1] + offset_y))


def open_shop(interface, clock):
    interface.shop.toggle()
    clock.now += config.SHOP_SLIDE_TIME


def test_the_shop_starts_closed_with_its_button_at_the_bottom():
    _, _, interface = setup()
    assert interface.shop.openness() == 0
    assert interface.shop.panel_rect().top == config.SCREEN_HEIGHT
    assert interface.shop.tab_rect().bottom == config.SCREEN_HEIGHT


def test_clicking_the_shop_button_slides_the_shop_up_and_down():
    state, clock, interface = setup()
    assert click(interface, state, interface.shop.tab_rect().center) == (True, True)
    clock.now += config.SHOP_SLIDE_TIME // 2
    assert 0 < interface.shop.openness() < 1
    clock.now += config.SHOP_SLIDE_TIME
    assert interface.shop.openness() == 1
    assert interface.shop.panel_rect().top == config.SHOP_PANEL[1]
    click(interface, state, interface.shop.tab_rect().center)
    clock.now += config.SHOP_SLIDE_TIME
    assert interface.shop.openness() == 0


def test_closing_halfway_turns_around_without_jumping():
    state, clock, interface = setup()
    interface.shop.toggle()
    clock.now += config.SHOP_SLIDE_TIME // 3
    before = interface.shop.openness()
    interface.shop.toggle()
    assert abs(interface.shop.openness() - before) < 0.01


def test_clicking_a_duck_in_the_open_shop_buys_it():
    state, clock, interface = setup(duckcoins=1000)
    open_shop(interface, clock)
    center, _ = interface.shop.portraits()['siamese_duck']
    assert click(interface, state, center) == (True, True)
    assert state.purchases['siamese_duck'] == 1


def test_a_duck_that_cant_be_bought_takes_the_click_but_doesnt_quack():
    state, clock, interface = setup(duckcoins=0)
    open_shop(interface, clock)
    center, _ = interface.shop.portraits()['realistic_duck']
    assert click(interface, state, center) == (True, False)
    assert state.purchases['realistic_duck'] == 0


def test_the_closed_shop_cant_be_clicked():
    state, _, interface = setup(duckcoins=1000)
    x, _, _ = config.SHOP_PORTRAITS['siamese_duck']
    click(interface, state, (x, config.SHOP_PANEL[1] + config.SHOP_PORTRAIT_Y))
    assert state.purchases['siamese_duck'] == 0


def test_the_bourgeois_duck_is_in_the_shop_too():
    state, clock, interface = setup(duckcoins=config.BOURGEOIS_COST)
    open_shop(interface, clock)
    center, _ = interface.shop.portraits()['bourgeois_duck']
    assert click(interface, state, center) == (True, True)
    assert state.is_boosted()


def test_the_shop_button_calls_attention_when_something_can_be_bought():
    state, _, _ = setup(duckcoins=0)
    assert not any_affordable(state)
    state.duckcoins = shop.DUCKS[0].starting_cost
    assert any_affordable(state)


def test_the_gear_opens_the_settings_with_sound_and_language():
    state, _, interface = setup()
    assert click(interface, state, config.GEAR_POS, 'top_right') == (True, True)
    assert interface.settings.open
    items = interface.settings.items()
    click(interface, state, items['sound'], 'top_right')
    assert state.muted
    click(interface, state, items['language'], 'top_right')
    assert state.language == 'pt'
    state.set_language('en')
    # A click anywhere else closes the menu
    click(interface, state, (10, 10), 'top_right')
    assert not interface.settings.open


def test_the_level_buttons_are_above_the_toast():
    state, _, interface = setup()
    state.highest_level = 3
    click(interface, state, config.NEXT_LEVEL_BUTTON_POS, 'top_center')
    assert state.level == 2
    click(interface, state, config.PREVIOUS_LEVEL_BUTTON_POS, 'top_center')
    assert state.level == 1
    click(interface, state, config.LEVEL_ADVANCE_BUTTON_POS, 'top_center')
    assert not state.level_advance


def test_a_click_on_nothing_goes_on_to_the_toast():
    state, _, interface = setup()
    assert click(interface, state, pygame.Rect(config.TOAST_RECT).center, 'center') == (False, False)
