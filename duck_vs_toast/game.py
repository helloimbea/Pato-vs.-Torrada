"""Main game loop and handling of clicks and keys."""
import contextlib
import sys

import pygame

from . import config, save
from .assets import Assets, load_font, localized
from .clock import GameClock
from .effects import Effects
from .i18n import t
from .layout import Layout
from .numbers import format_number
from .screen import Screen
from .smacking import Smacking
from .state import GameState
from .ui import Ui


def handle_click(event, state, assets, toast_rect, layout, interface):
    """A left click: on a button (see ui.py), or else on the toast."""
    if event.button != 1:  # only the left mouse button does anything
        return
    if config.DEV_MODE:
        print(f"Mouse clicked at: {layout.to_group('center', event.pos)} (center), "
              f"{layout.to_group('bottom', event.pos)} (shop)")

    handled, quack = interface.click(state, layout, event.pos)
    if not handled and toast_rect.collidepoint(layout.to_group('center', event.pos)):
        state.deal_damage(state.click_damage())
        quack = True
    if quack:  # quack only when the click hit the toast or a button
        play_quack(assets, state)


def play_quack(assets, state):
    if assets.click_sound and not state.muted:
        assets.click_sound.play()


def set_cursor(assets, grabbing):
    """The pointing hand all the time, and the grabbing hand while holding the muscular duck.

    Without the drawings (assets/images/cursors), the computer's own cursors are used.
    """
    cursor = assets.cursors.get('grab' if grabbing else 'pointer')
    with contextlib.suppress(pygame.error):  # some systems can't change the cursor
        pygame.mouse.set_cursor(cursor or (pygame.SYSTEM_CURSOR_SIZEALL if grabbing
                                           else pygame.SYSTEM_CURSOR_ARROW))


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
    font = load_font(config.FONT_SIZE)
    small_font = load_font(config.SMALL_FONT_SIZE)
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
    smacking = Smacking(clock=game_clock)
    interface = Ui(clock=pygame.time.get_ticks)  # the shop slides even while paused
    language = state.language

    def hit_position(kind):
        """Clicks pop their damage number where the mouse is, smacks where the duck hit;
        automatic hits pop on the toast."""
        if kind == 'click':
            return layout.to_group('center', pygame.mouse.get_pos())
        if kind.startswith('smack'):
            return smacking.impact
        return None

    state.on_hit = lambda amount, kind: effects.hit(amount, kind, hit_position(kind))
    state.on_defeat = lambda: effects.defeat(state.toast)  # still the beaten toast here
    state.on_buy = effects.duck_bought
    mouse_button_down = False
    grabbing = False  # the cursor is a grabbing hand
    set_cursor(assets, grabbing)
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
                smacking.release()
                game_clock.pause()
            elif clicked:
                # A press on the muscular duck picks it up (a secret, see smacking.py)
                in_center = layout.to_group('center', event.pos)
                muscular = localized(assets.ducks, 'muscular_duck')
                if smacking.can_grab(state, in_center, muscular):
                    smacking.grab(in_center, muscular)
                else:
                    handle_click(event, state, assets, toast_rect, layout, interface)
            elif event.type == pygame.MOUSEMOTION and smacking.held:
                if smacking.move(layout.to_group('center', event.pos), state):
                    play_quack(assets, state)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and smacking.held:
                smacking.release()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                state.toggle_mute()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                state.toggle_language()
            if config.DEV_MODE and event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                state.duckcoins += config.CHEAT_DUCKCOINS

        if state.language != language:  # the window's title follows the language
            language = state.language
            pygame.display.set_caption(t('title'))

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
        smacking.update(localized(assets.ducks, 'muscular_duck'))
        if smacking.held != grabbing:
            grabbing = smacking.held
            set_cursor(assets, grabbing)
        effects.update(state.duckcoins)
        lines = overlay_lines(overlay, away or 0, earned) if overlay else None
        screen.draw(window, layout, state, effects, smacking, interface, now, pygame.mouse.get_pos(), lines)
        pygame.display.update()
        clock.tick(config.FPS)
