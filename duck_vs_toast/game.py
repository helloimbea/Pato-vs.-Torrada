"""Main game loop and handling of clicks and keys."""
import sys

import pygame

from . import config, shop
from .assets import Assets
from .effects import Effects
from .screen import draw
from .state import GameState


def clicked_circle(mouse_pos, center, radius):
    return pygame.math.Vector2(center).distance_to(mouse_pos) < radius


def handle_click(event, state, assets, toast_rect):
    if event.button != 1:  # only the left mouse button does anything
        return

    position = pygame.mouse.get_pos()
    if config.DEV_MODE:
        print(f'Mouse clicked at: {position}')

    hit_something = True
    if toast_rect.collidepoint(position):
        state.deal_damage(state.damage)
    elif clicked_circle(position, config.LEVEL_ADVANCE_BUTTON_POS, config.LEVEL_ADVANCE_BUTTON_RADIUS):
        state.toggle_level_advance()
    elif clicked_circle(position, config.PREVIOUS_LEVEL_BUTTON_POS, config.PREVIOUS_LEVEL_BUTTON_RADIUS):
        state.previous_level()
    elif clicked_circle(position, config.NEXT_LEVEL_BUTTON_POS, config.NEXT_LEVEL_BUTTON_RADIUS):
        state.next_level()
    elif clicked_circle(position, config.SOUND_BUTTON_POS, config.SOUND_BUTTON_RADIUS):
        state.toggle_mute()
    else:
        hit_something = False
        for duck in shop.DUCKS:
            if clicked_circle(position, duck.button_pos, config.SHOP_BUTTON_RADIUS):
                shop.buy(state, duck)
                hit_something = True
                break

    # Quack only when the click hit the toast or a button
    if hit_something and assets.click_sound and not state.muted:
        assets.click_sound.play()


def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption(config.TITLE)
    try:
        pygame.mixer.init()
    except pygame.error:
        print('No audio device found, playing without sound.')

    assets = Assets()
    font = pygame.font.SysFont(None, config.FONT_SIZE)
    small_font = pygame.font.SysFont(None, config.SMALL_FONT_SIZE)
    toast_rect = pygame.Rect(config.TOAST_RECT)
    state = GameState()
    effects = Effects()
    # Clicks pop their damage number where the mouse is; automatic hits pop over the toast
    state.on_hit = lambda amount, kind: effects.hit(
        amount, kind, pygame.mouse.get_pos() if kind == 'click' else None)
    state.on_defeat = effects.defeat
    mouse_button_down = False
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and not mouse_button_down:
                mouse_button_down = True
                handle_click(event, state, assets, toast_rect)
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_button_down = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                state.toggle_mute()
            if config.DEV_MODE and event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                state.duckcoins += config.CHEAT_DUCKCOINS

        now = pygame.time.get_ticks()
        state.update(now)
        effects.update()
        draw(screen, font, small_font, assets, state, effects, now, pygame.mouse.get_pos())
        pygame.display.update()
        clock.tick(config.FPS)
