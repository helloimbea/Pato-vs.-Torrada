"""Drawing everything that shows up on screen."""
import pygame

from . import config
from .numbers import format_number
from .shop import DUCKS


def write(screen, font, text, color, position):
    screen.blit(font.render(text, True, color), position)


def hovered_duck(mouse_pos):
    """The duck whose buy button is under the mouse ('bourgeois' for the coming-soon one), or None."""
    mouse = pygame.math.Vector2(mouse_pos)
    for duck in DUCKS:
        if mouse.distance_to(duck.button_pos) < config.SHOP_BUTTON_RADIUS:
            return duck
    if mouse.distance_to(config.BOURGEOIS_BUTTON_POS) < config.SHOP_BUTTON_RADIUS:
        return 'bourgeois'
    return None


def draw_tooltip(screen, small_font, state, mouse_pos):
    duck = hovered_duck(mouse_pos)
    if duck is None:
        return
    if duck == 'bourgeois':
        center_x = config.BOURGEOIS_BUTTON_POS[0]
        lines = [('Bourgeois Duck', config.DARK_BLUE), ('Coming soon!', config.BLUE)]
    else:
        center_x = duck.button_pos[0]
        lines = [
            (duck.title, config.DARK_BLUE),
            (duck.describe(state), config.BLUE),
            (f'Bought: {state.purchases[duck.name]}', config.BLUE),
        ]

    texts = [small_font.render(text, True, color) for text, color in lines]
    padding = 10
    width = max(text.get_width() for text in texts) + 2 * padding
    height = sum(text.get_height() for text in texts) + 2 * padding
    # Above the shop, centered on the duck, without leaving the screen
    x = min(max(center_x - width // 2, 5), config.SCREEN_WIDTH - width - 5)
    y = 500 - height
    box = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, config.TOOLTIP_BACKGROUND, box, border_radius=10)
    pygame.draw.rect(screen, config.BLUE, box, width=2, border_radius=10)
    for text in texts:
        screen.blit(text, (x + padding, y + padding))
        y += text.get_height()


def draw_toast(screen, assets, state, effects):
    """The bread slice and the toast's face, flinching when hit: they shake, squash and look hurt.

    The pained face is the image "<toast>_hurt.png" (for example nerd_toast_hurt.png) when it
    exists in assets/images/toasts; until it is drawn, the toast turns reddish instead.
    """
    hurt = effects.is_hurt()
    image = assets.toasts.get(state.toast + '_hurt') if hurt else None
    tint = hurt and image is None
    if image is None:
        image = assets.toasts.get(state.toast)

    # The toast's name (top of its image) stays still; the bread and the face move together
    body = assets.bread.get_bounding_rect()
    if image is not None:
        title = pygame.Rect(0, 0, config.SCREEN_WIDTH, config.TOAST_TITLE_BOTTOM)
        screen.blit(image, title, title)
        face = image.get_bounding_rect().clip(
            pygame.Rect(0, config.TOAST_TITLE_BOTTOM, config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        body = body.union(face) if face.width else body
    body_image = pygame.Surface(body.size, pygame.SRCALPHA)
    body_image.blit(assets.bread, (0, 0), body)
    if image is not None:
        body_image.blit(image, (0, 0), body)

    squish = effects.squish()
    if squish:
        size = (round(body.width * (1 + config.SQUISH_WIDTH * squish)),
                round(body.height * (1 - config.SQUISH_HEIGHT * squish)))
        body_image = pygame.transform.smoothscale(body_image, size)
    if tint:
        body_image.fill(config.HURT_TINT + (255,), special_flags=pygame.BLEND_RGBA_MULT)

    dx, dy = effects.toast_offset()
    # Squashing keeps the toast's feet on the ground (bottom center stays in place)
    screen.blit(body_image, body_image.get_rect(midbottom=(body.centerx + dx, body.bottom + dy)))
    screen.blit(assets.reward_badge, (0, 0))


def draw(screen, font, small_font, assets, state, effects, now, mouse_pos):
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
    draw_toast(screen, assets, state, effects)
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
    next_image = 'next_level_on' if state.can_go_to_next_level() else 'next_level_off'
    screen.blit(assets.ui[next_image], (0, 0))

    # Sound button
    screen.blit(assets.ui['sound_off' if state.muted else 'sound_on'], (0, 0))

    # Ducks the player can't afford yet are shown as "locked"
    for duck in DUCKS:
        if state.duckcoins < state.costs[duck.name]:
            screen.blit(assets.ducks[duck.locked_image], (0, 0))
    screen.blit(assets.ducks['locked_bourgeois_duck'], (0, 0))  # bourgeois duck: coming soon

    # How many times each duck was bought
    for duck in DUCKS:
        count = state.purchases[duck.name]
        if count:
            x, y = duck.button_pos
            dx, dy = config.PURCHASE_COUNT_OFFSET
            write(screen, small_font, f'x{count}', config.DARK_BLUE, (x + dx, y + dy))

    effects.draw(screen, font, assets.coin)
    draw_tooltip(screen, small_font, state, mouse_pos)
