"""Main game loop and handling of clicks and keys."""
import sys

import pygame

from . import config, save, shop
from .assets import Assets
from .clock import GameClock
from .effects import Effects
from .i18n import t
from .layout import Layout
from .numbers import format_number
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
        state.deal_damage(state.click_damage())
    elif clicked_circle(in_top_right, config.LEVEL_ADVANCE_BUTTON_POS, config.LEVEL_ADVANCE_BUTTON_RADIUS):
        state.toggle_level_advance()
    elif clicked_circle(in_top_right, config.PREVIOUS_LEVEL_BUTTON_POS, config.PREVIOUS_LEVEL_BUTTON_RADIUS):
        state.previous_level()
    elif clicked_circle(in_top_right, config.NEXT_LEVEL_BUTTON_POS, config.NEXT_LEVEL_BUTTON_RADIUS):
        state.next_level()
    elif clicked_circle(in_top_right, config.SOUND_BUTTON_POS, config.SOUND_BUTTON_RADIUS):
        state.toggle_mute()
    elif clicked_circle(in_top_right, config.LANGUAGE_BUTTON_POS, config.LANGUAGE_BUTTON_RADIUS):
        state.toggle_language()
        pygame.display.set_caption(t('title'))
    else:
        hit_something = False
        for duck in shop.DUCKS:
            if clicked_circle(in_shop, duck.button_pos, config.SHOP_BUTTON_RADIUS):
                shop.buy(state, duck)
                hit_something = True
                break
        if clicked_circle(in_shop, config.BOURGEOIS_BUTTON_POS, config.SHOP_BUTTON_RADIUS):
            shop.buy_bourgeois(state)
            hit_something = True

    # Quack only when the click hit the toast or a button
    if hit_something and assets.click_sound and not state.muted:
        assets.click_sound.play()


def overlay_lines(screen_name, away=0, earned=0):
    """The text of the start ('start'), pause ('paused') or victory ('victory') screen."""
    if screen_name == 'paused':
        return [t('paused'), '', t('press_to_continue')]
    if screen_name == 'victory':
        return [t('victory'), '', t('toasts_are_back'), '', t('keep_playing')]
    lines = [t('title'), '', t('click_to_play')]
    if earned:
        hours, minutes = divmod(round(away / 60), 60)
        time_away = ' '.join(part for part in (hours and f'{hours} h', minutes and f'{minutes} min') if part)
        lines[1:1] = ['', t('welcome_back', time=time_away), t('ducks_earned', amount=format_number(earned))]
    return lines


def save_game(state):
    try:
        save.save(state)
    except OSError as error:  # e.g. no permission to write: keep playing anyway
        print(f'Could not save the game: {error}')


def main():
    pygame.init()
    # The window can be resized; the game spreads out to fill it (see layout.py)
    window = pygame.display.set_mode(config.SCREEN_SIZE, pygame.RESIZABLE)
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

    # The game clock stops while a start/pause/victory screen is up (see clock.py)
    game_clock = GameClock(paused=True)
    state = GameState(clock=game_clock)
    away = save.load(state)
    earned = 0
    if away is not None and away >= config.OFFLINE_MINIMUM_SECONDS:
        earned = save.offline_earnings(state, away)
        state.duckcoins += earned
    pygame.display.set_caption(t('title'))  # after loading: the save knows the language
    overlay = 'start'  # 'start', 'paused', 'victory' or None while playing

    effects = Effects(clock=game_clock)
    # Clicks pop their damage number where the mouse is; automatic hits pop over the toast
    state.on_hit = lambda amount, kind: effects.hit(
        amount, kind, layout.to_group('center', pygame.mouse.get_pos()) if kind == 'click' else None)
    state.on_defeat = lambda: effects.defeat(state.toast)  # still the beaten toast here
    state.on_buy = effects.duck_bought
    mouse_button_down = False
    last_save = pygame.time.get_ticks()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game(state)
                pygame.quit()
                sys.exit()

            clicked = event.type == pygame.MOUSEBUTTONDOWN and not mouse_button_down \
                and event.button == 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_button_down = True
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_button_down = False
            escape = event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE

            if overlay:  # start, pause or victory screen: a click (or Esc) goes back to the game
                if clicked or escape:
                    overlay = None
                    game_clock.resume()
            elif escape:
                overlay = 'paused'
                game_clock.pause()
            elif clicked:
                handle_click(event, state, assets, toast_rect, layout)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                state.toggle_mute()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                state.toggle_language()
                pygame.display.set_caption(t('title'))
            if config.DEV_MODE and event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                state.duckcoins += config.CHEAT_DUCKCOINS

        if not overlay and state.has_won() and not state.victory_seen:
            state.victory_seen = True
            overlay = 'victory'
            game_clock.pause()

        if pygame.time.get_ticks() - last_save >= config.AUTOSAVE_INTERVAL:
            save_game(state)
            last_save = pygame.time.get_ticks()

        window = pygame.display.get_surface()
        if window.get_size() != layout.window_size:
            layout = Layout(window.get_size())
        now = game_clock()
        state.update(now)
        effects.update()
        lines = overlay_lines(overlay, away or 0, earned) if overlay else None
        screen.draw(window, layout, state, effects, now, pygame.mouse.get_pos(), lines)
        pygame.display.update()
        clock.tick(config.FPS)
