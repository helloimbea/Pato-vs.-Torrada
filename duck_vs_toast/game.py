"""Main game loop and handling of clicks and keys."""
import sys

import pygame

from . import config, shop
from .assets import Assets
from .effects import Effects
from .layout import Layout
from .screen import Screen
from .state import GameState


def clicked_circle(mouse_pos, center, radius):
    return pygame.math.Vector2(center).distance_to(mouse_pos) < radius


def handle_click(event, state, assets, toast_rect, layout):
    if event.button != 1:  # only the left mouse button does anything
        return

    # Each part of the screen has its own place in the window (see layout.py)
    in_center = layout.to_group('center', event.pos)
    in_top_right = layout.to_group('top_right', event.pos)
    in_shop = layout.to_group('bottom', event.pos)
    if config.DEV_MODE:
        print(f'Mouse clicked at: {in_center} (center), {in_top_right} (top right), {in_shop} (shop)')

    hit_something = True
    if toast_rect.collidepoint(in_center):
        state.deal_damage(state.damage)
    elif clicked_circle(in_top_right, config.LEVEL_ADVANCE_BUTTON_POS, config.LEVEL_ADVANCE_BUTTON_RADIUS):
        state.toggle_level_advance()
    elif clicked_circle(in_top_right, config.PREVIOUS_LEVEL_BUTTON_POS, config.PREVIOUS_LEVEL_BUTTON_RADIUS):
        state.previous_level()
    elif clicked_circle(in_top_right, config.NEXT_LEVEL_BUTTON_POS, config.NEXT_LEVEL_BUTTON_RADIUS):
        state.next_level()
    elif clicked_circle(in_top_right, config.SOUND_BUTTON_POS, config.SOUND_BUTTON_RADIUS):
        state.toggle_mute()
    else:
        hit_something = False
        for duck in shop.DUCKS:
            if clicked_circle(in_shop, duck.button_pos, config.SHOP_BUTTON_RADIUS):
                shop.buy(state, duck)
                hit_something = True
                break

    # Quack only when the click hit the toast or a button
    if hit_something and assets.click_sound and not state.muted:
        assets.click_sound.play()


def main():
    pygame.init()
    # The window can be resized; the game spreads out to fill it (see layout.py)
    window = pygame.display.set_mode(config.SCREEN_SIZE, pygame.RESIZABLE)
    pygame.display.set_caption(config.TITLE)
    try:
        pygame.mixer.init()
    except pygame.error:
        print('No audio device found, playing without sound.')

    assets = Assets()
    font = pygame.font.SysFont(None, config.FONT_SIZE)
    small_font = pygame.font.SysFont(None, config.SMALL_FONT_SIZE)
    screen = Screen(assets, font, small_font)
    layout = Layout(window.get_size())
    toast_rect = pygame.Rect(config.TOAST_RECT)
    state = GameState()
    effects = Effects()
    # Clicks pop their damage number where the mouse is; automatic hits pop over the toast
    state.on_hit = lambda amount, kind: effects.hit(
        amount, kind, layout.to_group('center', pygame.mouse.get_pos()) if kind == 'click' else None)
    state.on_defeat = lambda: effects.defeat(state.toast)  # still the beaten toast here
    state.on_buy = effects.duck_bought
    mouse_button_down = False
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and not mouse_button_down:
                mouse_button_down = True
                handle_click(event, state, assets, toast_rect, layout)
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_button_down = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                state.toggle_mute()
            if config.DEV_MODE and event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                state.duckcoins += config.CHEAT_DUCKCOINS

        window = pygame.display.get_surface()
        if window.get_size() != layout.window_size:
            layout = Layout(window.get_size())
        now = pygame.time.get_ticks()
        state.update(now)
        effects.update()
        screen.draw(window, layout, state, effects, now, pygame.mouse.get_pos())
        pygame.display.update()
        clock.tick(config.FPS)
