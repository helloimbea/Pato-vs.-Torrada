"""Drawing everything that shows up on screen."""
import pygame

from . import config
from .shop import DUCKS

NUMBER_SUFFIXES = ['', 'K', 'M', 'B', 'T', 'Qa', 'Qi', 'Sx', 'Sp', 'Oc', 'No', 'Dc']


def format_number(num):
    """Make numbers short and readable: 1500 -> '1.5 K', 12.5 -> '12.5', 2e12 -> '2 T'."""
    tier = 0
    while abs(num) >= 1000 and tier < len(NUMBER_SUFFIXES) - 1:
        num /= 1000
        tier += 1
    num = round(num, 1)
    if abs(num) >= 1000 and tier < len(NUMBER_SUFFIXES) - 1:  # e.g. 999.96 K rounds to 1000 K -> 1 M
        num = round(num / 1000, 1)
        tier += 1
    text = str(int(num)) if num == int(num) else str(num)
    suffix = NUMBER_SUFFIXES[tier]
    return f'{text} {suffix}' if suffix else text


def write(screen, font, text, color, position):
    screen.blit(font.render(text, True, color), position)


def draw(screen, font, assets, state, now):
    # The duck, toast and UI images are screen-sized,
    # so they are all drawn at position (0, 0).
    screen.blit(assets.map, (0, 0))

    # Toast health bar
    bar_width = state.health * (config.HEALTH_BAR_WIDTH / state.max_health)
    bar = pygame.Rect(*config.HEALTH_BAR_POS, bar_width, config.HEALTH_BAR_HEIGHT)
    pygame.draw.rect(screen, config.RED, bar)

    # Bought ducks, toast and starter duck
    for name in state.ducks_on_screen:
        screen.blit(assets.ducks[name], (0, 0))
    if state.toast in assets.toasts:
        screen.blit(assets.toasts[state.toast], (0, 0))
    screen.blit(assets.ducks['starter_duck'], (0, 0))

    # Status texts
    write(screen, font, format_number(round(state.health)), config.RED, config.HEALTH_TEXT_POS)
    write(screen, font, format_number(state.duckcoins), config.LIGHT_BLUE, config.DUCKCOINS_TEXT_POS)
    for duck in DUCKS:
        write(screen, font, format_number(state.costs[duck.name]), config.BLUE, duck.cost_text_pos)
    write(screen, font, format_number(state.dps), config.LIGHT_BLUE, config.DPS_TEXT_POS)
    write(screen, font, format_number(state.damage), config.LIGHT_BLUE, config.DAMAGE_TEXT_POS)
    write(screen, font, format_number(state.reward), config.GREEN, config.REWARD_TEXT_POS)

    if state.has_auto_click:
        screen.blit(assets.ui['auto_click_pointer'], (0, 0))

    # Boss timer
    if state.is_boss():
        write(screen, font, f' {state.boss_time_left(now)}', config.TIMER_BLUE, config.BOSS_TIMER_TEXT_POS)
        screen.blit(assets.ui['boss_timer_box'], (0, 0))

    # Level advance button and current level
    level_image = 'level_advance_on' if state.level_advance else 'level_advance_off'
    screen.blit(assets.ui[level_image], (0, 0))
    write(screen, font, f'{state.level}', config.LIGHT_BLUE, config.LEVEL_TEXT_POS)

    # Ducks the player can't afford yet are shown as "locked"
    for duck in DUCKS:
        if state.duckcoins < state.costs[duck.name]:
            screen.blit(assets.ducks[duck.locked_image], (0, 0))
    screen.blit(assets.ducks['locked_bourgeois_duck'], (0, 0))  # bourgeois duck: coming soon
