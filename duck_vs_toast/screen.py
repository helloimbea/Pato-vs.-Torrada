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


def draw_tooltip(screen, small_font, state, mouse_pos, offset=(0, 0)):
    """mouse_pos is in the shop's own coordinates; offset is where the shop is on the screen."""
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
    x = min(max(offset[0] + center_x - width // 2, 5), screen.get_width() - width - 5)
    y = offset[1] + 500 - height
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
    toast = assets.toasts.get(state.toast + '_hurt') if hurt else None
    tint = hurt and toast is None
    if toast is None:
        toast = assets.toasts.get(state.toast)

    # The toast's name (top of its image, above TOAST_TITLE_BOTTOM) stays still;
    # the bread and the face below it move together
    body = assets.bread.rect
    if toast is not None:
        x, y = toast.pos
        title_height = min(max(config.TOAST_TITLE_BOTTOM - y, 0), toast.image.get_height())
        screen.blit(toast.image, toast.pos, (0, 0, toast.image.get_width(), title_height))
        face = toast.rect.clip(
            pygame.Rect(0, config.TOAST_TITLE_BOTTOM, config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        body = body.union(face) if face.width and face.height else body
    body_image = pygame.Surface(body.size, pygame.SRCALPHA)
    body_image.blit(assets.bread.image, (assets.bread.pos[0] - body.x, assets.bread.pos[1] - body.y))
    if toast is not None and face.width and face.height:
        body_image.blit(toast.image, (face.x - body.x, face.y - body.y), face.move(-x, -y))

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
    assets.reward_badge.draw(screen)


def stretch(image, width, left, right):
    """Make an image wider without stretching the drawing.

    Its left end (before x=left) goes to the left edge, its right end (from x=right) to the
    right edge, and the middle stays centered. The gaps repeat the plain columns at the
    edges of the middle part.
    """
    extra = width - image.get_width()
    if extra <= 0:
        return image
    height = image.get_height()
    wide = pygame.Surface((width, height))
    middle_x = extra // 2 + left
    right_x = width - (image.get_width() - right)
    wide.blit(image, (0, 0), (0, 0, left, height))
    wide.blit(image, (middle_x, 0), (left, 0, right - left, height))
    wide.blit(image, (right_x, 0), (right, 0, image.get_width() - right, height))
    end_of_middle = middle_x + right - left
    wide.blit(pygame.transform.scale(image.subsurface((left, 0, 1, height)),
                                     (middle_x - left, height)), (left, 0))
    wide.blit(pygame.transform.scale(image.subsurface((right - 1, 0, 1, height)),
                                     (right_x - end_of_middle, height)), (end_of_middle, 0))
    return wide


def build_background(assets, layout):
    """The sky, floor and shop panel for this window size, each part at its edge."""
    width, height = layout.size
    background = pygame.Surface(layout.size)
    _, center_y = layout.offsets['center']
    _, bottom_y = layout.offsets['bottom']

    # Sky and floor around the toast, with the sky going up and the floor going down
    band = stretch(assets.background, width, *config.BACKGROUND_STRETCH)
    background.blit(band, (0, center_y))
    if center_y:
        top_row = band.subsurface((0, 0, width, 1))
        background.blit(pygame.transform.scale(top_row, (width, center_y)), (0, 0))
    floor_top = center_y + band.get_height()
    shop_top = bottom_y + config.SHOP_TOP
    if shop_top > floor_top:
        floor_row = stretch(assets.floor_row, width, *config.BACKGROUND_STRETCH)
        background.blit(pygame.transform.scale(floor_row, (width, shop_top - floor_top)), (0, floor_top))

    shop = stretch(assets.shop.image, width, *config.SHOP_STRETCH)
    background.blit(shop, (0, shop_top))
    return background


def draw_center(screen, font, assets, state, effects, now):
    """The toast, its health, and the ducks around it."""
    bar_width = state.health * (config.HEALTH_BAR_WIDTH / state.max_health)
    bar = pygame.Rect(*config.HEALTH_BAR_POS, bar_width, config.HEALTH_BAR_HEIGHT)
    pygame.draw.rect(screen, config.RED, bar)

    # Bought ducks, toast and starter duck
    for name in state.ducks_on_screen:
        assets.ducks[name].draw(screen)
    draw_toast(screen, assets, state, effects)
    assets.ducks['starter_duck'].draw(screen)

    write(screen, font, format_number(round(state.health)), config.RED, config.HEALTH_TEXT_POS)
    write(screen, font, format_number(state.reward), config.GREEN, config.REWARD_TEXT_POS)

    if state.has_auto_click:
        assets.ui['auto_click_pointer'].draw(screen)

    if state.is_boss():
        write(screen, font, f' {state.boss_time_left(now)}', config.TIMER_BLUE, config.BOSS_TIMER_TEXT_POS)
        assets.ui['boss_timer_box'].draw(screen)


def draw_stats(screen, font, state):
    """Duckcoins, damage per second and click damage (top left)."""
    write(screen, font, format_number(state.duckcoins), config.LIGHT_BLUE, config.DUCKCOINS_TEXT_POS)
    write(screen, font, format_number(state.dps), config.LIGHT_BLUE, config.DPS_TEXT_POS)
    write(screen, font, format_number(state.damage), config.LIGHT_BLUE, config.DAMAGE_TEXT_POS)


def draw_level_buttons(screen, font, assets, state):
    """Level, level buttons and sound button (top right)."""
    level_image = 'level_advance_on' if state.level_advance else 'level_advance_off'
    assets.ui[level_image].draw(screen)
    write(screen, font, f'{state.level}', config.LIGHT_BLUE, config.LEVEL_TEXT_POS)
    next_image = 'next_level_on' if state.can_go_to_next_level() else 'next_level_off'
    assets.ui[next_image].draw(screen)
    assets.ui['sound_off' if state.muted else 'sound_on'].draw(screen)


def draw_shop(screen, font, small_font, assets, state):
    """Prices, locked ducks and how many of each duck was bought (bottom)."""
    for duck in DUCKS:
        write(screen, font, format_number(state.costs[duck.name]), config.BLUE, duck.cost_text_pos)

    # Ducks the player can't afford yet are shown as "locked"
    for duck in DUCKS:
        if state.duckcoins < state.costs[duck.name]:
            assets.ducks[duck.locked_image].draw(screen)
    assets.ducks['locked_bourgeois_duck'].draw(screen)  # bourgeois duck: coming soon

    for duck in DUCKS:
        count = state.purchases[duck.name]
        if count:
            x, y = duck.button_pos
            dx, dy = config.PURCHASE_COUNT_OFFSET
            write(screen, small_font, f'x{count}', config.DARK_BLUE, (x + dx, y + dy))


class Screen:
    """Draws the game in a window of any size (see layout.py for where each part goes)."""

    def __init__(self, assets, font, small_font):
        self.assets = assets
        self.font = font
        self.small_font = small_font
        self.background = None
        self.background_size = None
        self.canvas = None

    def draw(self, window, layout, state, effects, now, mouse_pos):
        assets, font = self.assets, self.font
        if self.background_size != layout.size:  # the window was resized
            self.background = build_background(assets, layout)
            self.background_size = layout.size
            self.canvas = pygame.Surface(layout.size)
        # At the original size the game is drawn straight to the window, without scaling
        canvas = window if window.get_size() == layout.size else self.canvas

        canvas.blit(self.background, (0, 0))
        part = {group: canvas.subsurface(pygame.Rect(offset, config.SCREEN_SIZE))
                for group, offset in layout.offsets.items()}

        assets.stats_panel.draw(part['top_left'])
        draw_center(part['center'], font, assets, state, effects, now)
        draw_stats(part['top_left'], font, state)
        draw_level_buttons(part['top_right'], font, assets, state)
        draw_shop(part['bottom'], font, self.small_font, assets, state)
        effects.draw(canvas, font, assets.coin, offset=layout.offsets['center'],
                     coin_target=config.DUCKCOINS_ICON_POS)
        draw_tooltip(canvas, self.small_font, state, layout.to_group('bottom', mouse_pos),
                     layout.offsets['bottom'])

        if canvas is not window:
            pygame.transform.smoothscale(canvas, window.get_size(), window)
