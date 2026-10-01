"""Main game loop and handling of clicks and keys."""
import sys

import pygame

from . import config, shop
from .assets import Assets
from .screen import draw
from .state import GameState


def clicked_circle(mouse_pos, center, radius):
    return pygame.math.Vector2(center).distance_to(mouse_pos) < radius


def handle_click(event, state, assets, toast_rect):
    position = pygame.mouse.get_pos()
    if config.PRINT_CLICK_POSITION:
        print(f'Mouse clicked at: {position}')

    if clicked_circle(position, config.LEVEL_ADVANCE_BUTTON_POS, config.LEVEL_ADVANCE_BUTTON_RADIUS):
        state.toggle_level_advance()

    if assets.click_sound:
        assets.click_sound.play()

    if clicked_circle(position, config.PREVIOUS_LEVEL_BUTTON_POS, config.PREVIOUS_LEVEL_BUTTON_RADIUS):
        state.previous_level()

    if event.button != 1:  # only the left button attacks and buys
        return

    if toast_rect.collidepoint(position):
        state.deal_damage(state.damage)

    for duck in shop.DUCKS:
        if clicked_circle(position, duck.button_pos, config.SHOP_BUTTON_RADIUS):
            shop.buy(state, duck)
            break


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
    toast_rect = pygame.Rect(config.TOAST_RECT)
    state = GameState()
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

            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                state.duckcoins += config.CHEAT_DUCKCOINS

        now = pygame.time.get_ticks()
        state.update(now)
        draw(screen, font, assets, state, now)
        pygame.display.update()
        clock.tick(config.FPS)
