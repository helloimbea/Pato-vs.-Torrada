"""Drawing everything that shows up on screen."""
import pygame

from . import config, i18n, shop
from .assets import localized
from .effects import ease_in, outlined
from .i18n import t
from .numbers import format_number
from .shop import DUCKS


def write(screen, font, text, color, position):
    screen.blit(font.render(text, True, color), position)


def hovered_duck(mouse_pos):
    """The duck whose buy button is under the mouse ('bourgeois' for the Bourgeois Duck), or None."""
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
        lines = [(t('bourgeois_duck'), config.DARK_BLUE)]
        lines += [(line, config.BLUE) for line in shop.bourgeois_description(state)]
    else:
        center_x = duck.button_pos[0]
        lines = [
            (duck.title, config.DARK_BLUE),
            (duck.describe(state), config.BLUE),
            (t('bought', count=state.purchases[duck.name]), config.BLUE),
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


def toast_drawing(assets, name, mood=None):
    """The toast's drawing for a mood ('hurt' or 'dead'), and whether it still needs a tint.

    A mood is the image "<toast>_<mood>.png" (for example nerd_toast_hurt.png) when it exists
    in assets/images/toasts; until it is drawn, the normal toast is used with a tint.
    """
    if mood is not None and localized(assets.toasts, name + '_' + mood) is not None:
        return localized(assets.toasts, name + '_' + mood), False
    return localized(assets.toasts, name), mood is not None


def toast_body(assets, toast):
    """The bread slice with the toast's face on it (everything below the title): (image, rect)."""
    body = assets.bread.rect
    face = None
    if toast is not None:
        face = toast.rect.clip(
            pygame.Rect(0, config.TOAST_TITLE_BOTTOM, config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        if face.width and face.height:
            body = body.union(face)
        else:
            face = None
    image = pygame.Surface(body.size, pygame.SRCALPHA)
    image.blit(assets.bread.image, (assets.bread.pos[0] - body.x, assets.bread.pos[1] - body.y))
    if face is not None:
        image.blit(toast.image, (face.x - body.x, face.y - body.y), face.move(-toast.pos[0], -toast.pos[1]))
    return image, body


def draw_dead_toast(screen, assets, name, progress):
    """The beaten toast shrinks very fast until it disappears.

    Its face is "<toast>_dead.png" when it exists; until it is drawn, the toast turns gray.
    """
    toast, tint = toast_drawing(assets, name, 'dead')
    image, body = toast_body(assets, toast)
    size = 1 - ease_in(progress)
    width, height = round(body.width * size), round(body.height * size)
    if width <= 0 or height <= 0:
        return
    image = pygame.transform.smoothscale(image, (width, height))
    if tint:
        image.fill(config.DEATH_TINT + (255,), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(image, image.get_rect(center=body.center))


def draw_toast(screen, assets, state, effects):
    """The bread slice and the toast's face, flinching when hit: they shake, squash and look hurt.

    A beaten toast shrinks away while the next one pops up (see effects.py).
    """
    death = effects.death()
    if death is not None:
        draw_dead_toast(screen, assets, effects.dead_toast, death)

    toast, tint = toast_drawing(assets, state.toast, 'hurt' if effects.is_hurt() else None)
    if toast is not None:
        # The toast's name (top of its image, above TOAST_TITLE_BOTTOM) stays still
        title_height = min(max(config.TOAST_TITLE_BOTTOM - toast.pos[1], 0), toast.image.get_height())
        screen.blit(toast.image, toast.pos, (0, 0, toast.image.get_width(), title_height))

    # The bread and the face move together
    body_image, body = toast_body(assets, toast)
    squish = effects.squish()
    spawn = effects.spawn()
    width = body.width * (1 + config.SQUISH_WIDTH * squish) * spawn
    height = body.height * (1 - config.SQUISH_HEIGHT * squish) * spawn
    if round(width) <= 0 or round(height) <= 0:  # the next toast hasn't popped up yet
        assets.reward_badge.draw(screen)
        return
    if (round(width), round(height)) != body.size:
        body_image = pygame.transform.smoothscale(body_image, (round(width), round(height)))
    if tint:
        body_image.fill(config.HURT_TINT + (255,), special_flags=pygame.BLEND_RGBA_MULT)

    dx, dy = effects.toast_offset()
    # Squashing and popping up keep the toast's feet on the ground (bottom center stays in place)
    screen.blit(body_image, body_image.get_rect(midbottom=(body.centerx + dx, body.bottom + dy)))
    assets.reward_badge.draw(screen)


def draw_duck(screen, sprite, scale):
    """A bought duck, stretched by scale = (width, height) with its feet in place."""
    if scale == (1, 1):
        sprite.draw(screen)
        return
    size = (round(sprite.image.get_width() * scale[0]), round(sprite.image.get_height() * scale[1]))
    if size[0] <= 0 or size[1] <= 0:
        return
    image = pygame.transform.smoothscale(sprite.image, size)
    screen.blit(image, image.get_rect(midbottom=sprite.rect.midbottom))


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
    parts = assets.map_parts()
    band = stretch(parts.background, width, *config.BACKGROUND_STRETCH)
    background.blit(band, (0, center_y))
    if center_y:
        top_row = band.subsurface((0, 0, width, 1))
        background.blit(pygame.transform.scale(top_row, (width, center_y)), (0, 0))
    floor_top = center_y + band.get_height()
    shop_top = bottom_y + config.SHOP_TOP
    if shop_top > floor_top:
        floor_row = stretch(parts.floor_row, width, *config.BACKGROUND_STRETCH)
        background.blit(pygame.transform.scale(floor_row, (width, shop_top - floor_top)), (0, floor_top))

    shop = stretch(parts.shop.image, width, *config.SHOP_STRETCH)
    background.blit(shop, (0, shop_top))
    return background


def draw_center(screen, font, assets, state, effects, now):
    """The toast, its health, and the ducks around it."""
    bar_width = state.health * (config.HEALTH_BAR_WIDTH / state.max_health)
    bar = pygame.Rect(*config.HEALTH_BAR_POS, bar_width, config.HEALTH_BAR_HEIGHT)
    pygame.draw.rect(screen, config.RED, bar)

    # Bought ducks, toast and starter duck
    for name in state.ducks_on_screen:
        draw_duck(screen, localized(assets.ducks, name), effects.duck_scale(name))
    draw_toast(screen, assets, state, effects)
    localized(assets.ducks, 'starter_duck').draw(screen)

    write(screen, font, format_number(round(state.health)), config.RED, config.HEALTH_TEXT_POS)
    reward_color = config.BOOST_COLOR if state.is_boosted() else config.GREEN
    write(screen, font, format_number(state.current_reward()), reward_color, config.REWARD_TEXT_POS)

    if state.has_auto_click:
        localized(assets.ui, 'auto_click_pointer').draw(screen)

    if state.is_boss():
        write(screen, font, f' {state.boss_time_left(now)}', config.TIMER_BLUE, config.BOSS_TIMER_TEXT_POS)
        localized(assets.ui, 'boss_timer_box').draw(screen)


def draw_stats(screen, font, state):
    """Duckcoins, damage per second and click damage (top left)."""
    write(screen, font, format_number(state.duckcoins), config.LIGHT_BLUE, config.DUCKCOINS_TEXT_POS)
    # While the Bourgeois Duck's boost is on, the boosted numbers are shown in gold
    color = config.BOOST_COLOR if state.is_boosted() else config.LIGHT_BLUE
    write(screen, font, format_number(state.current_dps()), color, config.DPS_TEXT_POS)
    write(screen, font, format_number(state.click_damage()), color, config.DAMAGE_TEXT_POS)


def draw_level_buttons(screen, font, assets, state):
    """Level, level buttons, sound and language buttons (top right)."""
    level_image = 'level_advance_on' if state.level_advance else 'level_advance_off'
    localized(assets.ui, level_image).draw(screen)
    write(screen, font, f'{state.level}', config.LIGHT_BLUE, config.LEVEL_TEXT_POS)
    next_image = 'next_level_on' if state.can_go_to_next_level() else 'next_level_off'
    localized(assets.ui, next_image).draw(screen)
    localized(assets.ui, 'sound_off' if state.muted else 'sound_on').draw(screen)
    localized(assets.ui, 'language_' + i18n.language).draw(screen)


def draw_shop(screen, font, small_font, assets, state):
    """Prices, locked ducks and how many of each duck was bought (bottom)."""
    for duck in DUCKS:
        write(screen, font, format_number(state.costs[duck.name]), config.BLUE, duck.cost_text_pos)

    # Ducks the player can't afford yet are shown as "locked"
    for duck in DUCKS:
        if state.duckcoins < state.costs[duck.name]:
            localized(assets.ducks, duck.locked_image).draw(screen)

    # Bourgeois Duck: fixed price; after buying it, a boost and then a recharge time
    write(screen, font, format_number(config.BOURGEOIS_COST), config.BLUE, config.BOURGEOIS_COST_TEXT_POS)
    if not shop.can_buy_bourgeois(state):
        localized(assets.ducks, 'locked_bourgeois_duck').draw(screen)
    if state.is_boosted():
        timer, color = state.boost_time_left(), config.BOOST_COLOR
    else:
        timer, color = state.bourgeois_recharge_left(), config.DARK_BLUE
    if timer:
        text = outlined(font, shop.format_time(timer), color)
        screen.blit(text, text.get_rect(center=config.BOURGEOIS_BUTTON_POS))

    for duck in DUCKS:
        count = state.purchases[duck.name]
        if count:
            x, y = duck.button_pos
            dx, dy = config.PURCHASE_COUNT_OFFSET
            write(screen, small_font, f'x{count}', config.DARK_BLUE, (x + dx, y + dy))


def draw_overlay(screen, title_font, font, lines):
    """A start, pause or victory screen: the game darkened, with a box of text in the middle.

    The first line is the title; an empty line leaves a gap.
    """
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill(config.OVERLAY_COLOR)
    screen.blit(shade, (0, 0))

    texts = [title_font.render(lines[0], True, config.DARK_BLUE)]
    texts += [font.render(line, True, config.BLUE) for line in lines[1:]]
    padding = 40
    width = max(text.get_width() for text in texts) + 2 * padding
    height = sum(text.get_height() + 10 for text in texts) + 2 * padding
    box = pygame.Rect(0, 0, width, height)
    box.center = screen.get_rect().center
    pygame.draw.rect(screen, config.TOOLTIP_BACKGROUND, box, border_radius=20)
    pygame.draw.rect(screen, config.BLUE, box, width=3, border_radius=20)
    y = box.top + padding
    for text in texts:
        screen.blit(text, text.get_rect(midtop=(box.centerx, y)))
        y += text.get_height() + 10


class Screen:
    """Draws the game in a window of any size (see layout.py for where each part goes)."""

    def __init__(self, assets, font, small_font):
        self.assets = assets
        self.font = font
        self.small_font = small_font
        self.title_font = pygame.font.SysFont(None, config.TITLE_FONT_SIZE)
        self.background = None
        self.background_size = None
        self.canvas = None

    def draw(self, window, layout, state, effects, now, mouse_pos, overlay=None):
        """overlay: the lines of a start/pause/victory screen to show over the game, or None."""
        assets, font = self.assets, self.font
        if self.background_size != (layout.size, i18n.language):  # resized, or language changed
            self.background = build_background(assets, layout)
            self.background_size = (layout.size, i18n.language)
            self.canvas = pygame.Surface(layout.size)
        # At the original size the game is drawn straight to the window, without scaling
        canvas = window if window.get_size() == layout.size else self.canvas

        canvas.blit(self.background, (0, 0))
        part = {group: canvas.subsurface(pygame.Rect(offset, config.SCREEN_SIZE))
                for group, offset in layout.offsets.items()}

        assets.map_parts().stats_panel.draw(part['top_left'])
        draw_center(part['center'], font, assets, state, effects, now)
        draw_stats(part['top_left'], font, state)
        draw_level_buttons(part['top_right'], font, assets, state)
        draw_shop(part['bottom'], font, self.small_font, assets, state)
        effects.draw(canvas, font, assets.coin, offset=layout.offsets['center'],
                     coin_target=config.DUCKCOINS_ICON_POS)
        if overlay:
            draw_overlay(canvas, self.title_font, font, overlay)
        else:
            draw_tooltip(canvas, self.small_font, state, layout.to_group('bottom', mouse_pos),
                         layout.offsets['bottom'])

        if canvas is not window:
            pygame.transform.smoothscale(canvas, window.get_size(), window)
