"""Drawing everything that shows up on screen.

The colors come from the palette in config.py (PANEL, INK, GOLD, HEALTH_RED, GREEN...), and
where the buttons are comes from ui.py, so drawing and clicking always agree.
"""
import math

import pygame

from . import config, i18n, shop, ui
from .assets import Sprite, load_font, localized
from .effects import ease_in, outlined
from .i18n import t
from .numbers import format_number
from .shop import DUCKS


def write(screen, font, text, color, position):
    nudge = getattr(font, 'nudge', 0)  # see assets.load_font
    screen.blit(font.render(text, True, color), (position[0], position[1] + nudge))


def fit(text, max_width):
    """Make a rendered text smaller if it is wider than max_width."""
    if text.get_width() <= max_width:
        return text
    scale = max_width / text.get_width()
    return pygame.transform.smoothscale(text, (max_width, round(text.get_height() * scale)))


def scaled(image, scale):
    if scale == 1:
        return image
    return pygame.transform.smoothscale(
        image, (max(1, round(image.get_width() * scale)), max(1, round(image.get_height() * scale))))


def side_by_side(*images, gap=6):
    """Images in a row, centered on one line."""
    width = sum(image.get_width() for image in images) + gap * (len(images) - 1)
    height = max(image.get_height() for image in images)
    row = pygame.Surface((width, height), pygame.SRCALPHA)
    x = 0
    for image in images:
        row.blit(image, (x, (height - image.get_height()) // 2))
        x += image.get_width() + gap
    return row


def pulse(now, every=1200):
    """0 -> 1 -> 0, over and over (for things that glow)."""
    return (1 - math.cos(2 * math.pi * (now % every) / every)) / 2


def hop(now, every=config.SHOP_HOP_EVERY, height=config.SHOP_HOP_HEIGHT):
    """How high to hop now: a quick little jump, then a rest until the next one."""
    phase = (now % every) / every
    return -height * math.sin(math.pi * phase / 0.25) if phase < 0.25 else 0


def draw_panel(screen, rect, radius=16, shadow=True, **corners):
    """A cream box with a soft border, like the paper of the drawings."""
    rect = pygame.Rect(rect)
    if shadow:
        shade = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(shade, (40, 40, 60, 45), shade.get_rect(), border_radius=radius, **corners)
        screen.blit(shade, rect.move(0, 4))
    pygame.draw.rect(screen, config.PANEL, rect, border_radius=radius, **corners)
    pygame.draw.rect(screen, config.PANEL_EDGE, rect, width=3, border_radius=radius, **corners)


def draw_box(screen, small_font, lines, center_x, bottom):
    """A tooltip: lines of (text, color) in a box centered on center_x, ending at bottom."""
    texts = [small_font.render(text, True, color) for text, color in lines]
    padding = 12
    width = max(text.get_width() for text in texts) + 2 * padding
    height = sum(text.get_height() for text in texts) + 2 * padding
    # Without leaving the screen
    x = min(max(round(center_x - width / 2), 5), screen.get_width() - width - 5)
    y = max(round(bottom - height), 5)
    draw_panel(screen, (x, y, width, height), radius=12)
    y += padding
    for text in texts:
        screen.blit(text, (x + padding, y))
        y += text.get_height()


# --- The toast ---

def toast_drawing(assets, name, mood=None):
    """The toast's drawing for a mood ('hurt' or 'dead'), and whether it still needs a tint.

    A mood is the image "<toast>_<mood>.png" (for example nerd_toast_hurt.png) when it exists
    in assets/images/toasts; until it is drawn, the normal toast is used with a tint.
    """
    if mood is not None and localized(assets.toasts, name + '_' + mood) is not None:
        return localized(assets.toasts, name + '_' + mood), False
    return localized(assets.toasts, name), mood is not None


def draw_dead_toast(screen, assets, name, progress):
    """The beaten toast shrinks very fast until it disappears.

    Its face is "<toast>_dead.png" when it exists; until it is drawn, the toast turns gray.
    """
    toast, tint = toast_drawing(assets, name, 'dead')
    if toast is None:
        return
    image, body = toast.image, toast.rect
    size = 1 - ease_in(progress)
    width, height = round(body.width * size), round(body.height * size)
    if width <= 0 or height <= 0:
        return
    image = pygame.transform.smoothscale(image, (width, height))
    if tint:
        image.fill(config.DEATH_TINT + (255,), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(image, image.get_rect(center=body.center))


def draw_toast_title(screen, font, toast):
    """The toast's name above it (the upside-down toast's name is upside down too).

    Returns where it was drawn.
    """
    text = fit(outlined(font, t(toast), config.INK, outline=config.PANEL, width=3),
               config.TOAST_TITLE_MAX_WIDTH)
    if toast == 'upside_down_toast':
        text = pygame.transform.rotate(text, 180)
    rect = text.get_rect(center=config.TOAST_TITLE_CENTER)
    screen.blit(text, rect)
    return rect


def boss_tag(font):
    """The red "BOSS" label, tilted like a sticker."""
    text = font.render(t('boss'), True, config.PANEL)
    label = pygame.Surface((text.get_width() + 20, text.get_height() + 6), pygame.SRCALPHA)
    pygame.draw.rect(label, config.HEALTH_RED, label.get_rect(), border_radius=8)
    pygame.draw.rect(label, config.HEALTH_RED_DARK, label.get_rect(), width=3, border_radius=8)
    label.blit(text, text.get_rect(center=label.get_rect().center))
    return pygame.transform.rotozoom(label, config.BOSS_TAG_ANGLE, 1)


def draw_toast(screen, assets, state, effects, fonts=None):
    """The toast, flinching when hit: it shakes, squashes and looks hurt.

    A beaten toast shrinks away while the next one pops up (see effects.py).
    fonts: the Screen's fonts, to write the toast's name (and "BOSS") above it.
    """
    death = effects.death()
    if death is not None:
        draw_dead_toast(screen, assets, effects.dead_toast, death)

    if fonts is not None:
        title = draw_toast_title(screen, fonts['toast_title'], state.toast)
        if state.is_boss():
            tag = boss_tag(fonts['tag'])
            screen.blit(tag, tag.get_rect(center=(title.left + 4, title.top + 6)))

    toast, tint = toast_drawing(assets, state.toast, 'hurt' if effects.is_hurt() else None)
    if toast is None:
        return
    body_image, body = toast.image, toast.rect
    squish = effects.squish()
    spawn = effects.spawn()
    width = body.width * (1 + config.SQUISH_WIDTH * squish) * spawn
    height = body.height * (1 - config.SQUISH_HEIGHT * squish) * spawn
    if round(width) <= 0 or round(height) <= 0:  # the next toast hasn't popped up yet
        return
    if (round(width), round(height)) != body.size:
        body_image = pygame.transform.smoothscale(body_image, (round(width), round(height)))
    if tint:
        if body_image is toast.image:  # tint a copy: never the drawing itself, or the red adds up
            body_image = body_image.copy()
        body_image.fill(config.HURT_TINT + (255,), special_flags=pygame.BLEND_RGBA_MULT)

    dx, dy = effects.toast_offset()
    # Squashing and popping up keep the toast's feet on the ground (bottom center stays in place)
    screen.blit(body_image, body_image.get_rect(midbottom=(body.centerx + dx, body.bottom + dy)))


def draw_health(screen, font, heart, state):
    """The toast's health: "3.3 K / 4.4 K" with the heart, and a bar with round ends."""
    text = outlined(font, f'{format_number(round(state.health))} / {format_number(state.max_health)}',
                    config.HEALTH_RED, outline=config.PANEL, width=3)
    row = side_by_side(heart.image, text, gap=8) if heart is not None else text
    screen.blit(row, row.get_rect(center=config.HEALTH_TEXT_CENTER))

    bar = pygame.Rect(config.HEALTH_BAR)
    radius = bar.height // 2
    pygame.draw.rect(screen, config.HEALTH_TRACK, bar, border_radius=radius)
    filled = round(bar.width * max(0, min(1, state.health / state.max_health)))
    if filled > 0:
        part = pygame.Rect(bar.left, bar.top, max(filled, bar.height), bar.height)
        pygame.draw.rect(screen, config.HEALTH_RED, part, border_radius=radius)
        shine = pygame.Rect(part.left + radius // 2, part.top + 4, max(part.width - radius, 1), 5)
        pygame.draw.rect(screen, (255, 150, 160), shine, border_radius=3)
    pygame.draw.rect(screen, config.INK, bar, width=3, border_radius=radius)


def draw_boss_timer(screen, font, assets, state, now):
    """The seconds left to beat the boss, in a circle (the owner's ui/boss_timer.png when drawn).

    In the last seconds the number turns red and the circle pulses.
    """
    seconds = state.boss_time_left(now)
    hurry = seconds < config.BOSS_TIMER_HURRY
    size = 1 + (0.12 * pulse(now, 500) if hurry else 0)
    drawing = assets.ui.get('boss_timer')
    radius = config.BOSS_TIMER_RADIUS
    if drawing is not None:
        circle = scaled(drawing.image, size)
    else:
        circle = pygame.Surface((2 * radius + 2, 2 * radius + 2), pygame.SRCALPHA)
        middle = (radius + 1, radius + 1)
        pygame.draw.circle(circle, config.PANEL, middle, radius)
        pygame.draw.circle(circle, config.HEALTH_RED_DARK if hurry else config.INK, middle, radius, width=3)
        circle = scaled(circle, size)
    screen.blit(circle, circle.get_rect(center=config.BOSS_TIMER_CENTER))
    number = font.render(str(seconds), True, config.HEALTH_RED if hurry else config.INK)
    screen.blit(number, number.get_rect(center=config.BOSS_TIMER_CENTER))


def draw_reward(screen, font, assets, state):
    """"+ (coin) 1.2 K" under the toast: what beating it gives."""
    color = config.BOOST_COLOR if state.is_boosted() else config.GREEN
    plus = outlined(font, '+', color, outline=config.PANEL, width=3)
    amount = outlined(font, format_number(state.current_reward()), color, outline=config.PANEL, width=3)
    row = side_by_side(plus, assets.coin_icon(34), amount, gap=4)
    screen.blit(row, row.get_rect(center=config.REWARD_CENTER))


# --- The ducks ---

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


_tinted = {}  # tinted copies of drawings, made when first needed


def tinted(image, tint):
    """A copy of image multiplied by tint (r, g, b, a): darker, grayer or see-through."""
    key = (id(image), tint)
    if key not in _tinted:
        copy = image.copy()
        copy.fill(tint, special_flags=pygame.BLEND_RGBA_MULT)
        _tinted[key] = copy
    return _tinted[key]


def resting_duck(sprite):
    """The muscular duck while it rests: grayish and see-through."""
    return Sprite(tinted(sprite.image, config.RESTING_TINT + (config.RESTING_ALPHA,)), sprite.pos)


def draw_muscular_duck(screen, font, sprite, state, smacking, scale):
    """The muscular duck: at its spot, held (or hopping back), or resting with a timer above it."""
    if smacking.is_away():
        image = sprite.image
        lift = config.HELD_LIFT if smacking.held else 1
        if smacking.angle or lift != 1:
            image = pygame.transform.rotozoom(image, smacking.angle, lift)
        screen.blit(image, image.get_rect(center=smacking.center))
    elif state.is_muscular_resting():
        resting_duck(sprite).draw(screen)
        text = outlined(font, shop.format_time(state.muscular_rest_left()), config.INK,
                        outline=config.PANEL, width=3)
        screen.blit(text, text.get_rect(midbottom=(sprite.rect.centerx, sprite.rect.top + 8)))
    else:
        draw_duck(screen, sprite, scale)


# --- The background ---

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
    """The sky and the floor for this window size: the sky goes up and the floor goes down."""
    width, height = layout.size
    background = pygame.Surface(layout.size)
    top = layout.background_y
    parts = assets.map_parts()
    band = stretch(parts.background, width, *config.BACKGROUND_STRETCH)
    background.blit(band, (0, top))
    if top:
        top_row = band.subsurface((0, 0, width, 1))
        background.blit(pygame.transform.scale(top_row, (width, top)), (0, 0))
    floor_top = top + band.get_height()
    if height > floor_top:
        floor_row = stretch(parts.floor_row, width, *config.BACKGROUND_STRETCH)
        background.blit(pygame.transform.scale(floor_row, (width, height - floor_top)), (0, floor_top))
    return background


# --- The parts of the screen ---

def draw_center(screen, fonts, assets, state, effects, smacking, now):
    """The toast, its name and health, and the ducks around it."""
    draw_health(screen, fonts['health'], assets.map_parts().heart, state)

    # Bought ducks, toast and starter duck (the muscular duck is drawn last when held, on top)
    for name in state.ducks_on_screen:
        if name == 'muscular_duck' and smacking.is_away():
            continue
        if name == 'muscular_duck':
            draw_muscular_duck(screen, fonts['small_number'], localized(assets.ducks, name), state,
                               smacking, effects.duck_scale(name))
        else:
            draw_duck(screen, localized(assets.ducks, name), effects.duck_scale(name))
    draw_toast(screen, assets, state, effects, fonts)
    localized(assets.ducks, 'starter_duck').draw(screen)
    draw_reward(screen, fonts['reward'], assets, state)

    if state.has_auto_click and not state.is_muscular_resting():
        localized(assets.ui, 'auto_click_pointer').draw(screen)
    if state.is_boss():
        draw_boss_timer(screen, fonts['timer'], assets, state, now)
    if smacking.is_away():
        draw_muscular_duck(screen, fonts['small_number'], localized(assets.ducks, 'muscular_duck'),
                           state, smacking, (1, 1))


def draw_stats(screen, fonts, assets, state, effects):
    """Duckcoins, damage per second and click damage (top left)."""
    assets.map_parts().stats_panel.draw(screen)
    coin = assets.coin_icon(config.DUCKCOINS_ICON_SIZE)
    screen.blit(coin, coin.get_rect(center=config.DUCKCOINS_ICON_POS))
    pointer = assets.cursors.get('pointer')
    if pointer is not None:  # the click damage's icon is the owner's mouse drawing
        icon = scaled(pointer.data[1], config.DAMAGE_ICON_SIZE / max(pointer.data[1].get_size()))
        screen.blit(icon, icon.get_rect(center=config.DAMAGE_ICON_POS))

    shown = state.duckcoins if effects.shown_duckcoins is None else round(effects.shown_duckcoins)
    coins = outlined(fonts['coins'], format_number(shown), config.GOLD, outline=config.GOLD_DARK, width=2)
    screen.blit(coins, coins.get_rect(midleft=config.DUCKCOINS_TEXT_LEFT))
    # While the Bourgeois Duck's boost is on, the boosted numbers are shown in gold
    color = config.BOOST_COLOR if state.is_boosted() else config.INK
    for value, position in ((state.current_dps(), config.DPS_TEXT_LEFT),
                            (state.click_damage(), config.DAMAGE_TEXT_LEFT)):
        text = fonts['stat'].render(format_number(value), True, color)
        screen.blit(text, text.get_rect(midleft=position))


def draw_level_buttons(screen, font, assets, state):
    """The level, with the buttons to go back, forward and to stay on it (top center)."""
    level_image = 'level_advance_on' if state.level_advance else 'level_advance_off'
    localized(assets.ui, level_image).draw(screen)
    number = outlined(font, str(state.level), config.PANEL, outline=config.INK, width=2)
    screen.blit(number, number.get_rect(center=config.LEVEL_TEXT_CENTER))
    next_image = 'next_level_on' if state.can_go_to_next_level() else 'next_level_off'
    localized(assets.ui, next_image).draw(screen)


def make_gear(size):
    """A gear icon (a placeholder drawn by code until the owner draws one)."""
    gear = pygame.Surface((size, size), pygame.SRCALPHA)
    middle = size / 2
    for i in range(8):
        angle = i * math.pi / 4
        points = [(middle + radius * math.cos(angle + spread), middle + radius * math.sin(angle + spread))
                  for radius, spread in ((size * 0.30, -0.28), (size * 0.48, -0.17),
                                         (size * 0.48, 0.17), (size * 0.30, 0.28))]
        pygame.draw.polygon(gear, config.INK, points)
    pygame.draw.circle(gear, config.INK, (middle, middle), size * 0.34)
    pygame.draw.circle(gear, config.PANEL, (middle, middle), size * 0.14)
    return gear


def draw_settings(screen, assets, settings, muted, gear, mouse):
    """The gear button (top right) and, when open, its menu with the sound and language buttons."""
    hovered = ui.in_circle(mouse, config.GEAR_POS, config.GEAR_RADIUS)
    radius = config.GEAR_RADIUS + (2 if hovered else 0)
    pygame.draw.circle(screen, config.PANEL, config.GEAR_POS, radius)
    pygame.draw.circle(screen, config.PANEL_EDGE, config.GEAR_POS, radius, width=3)
    screen.blit(gear, gear.get_rect(center=config.GEAR_POS))
    if not settings.open:
        return
    draw_panel(screen, settings.menu_rect(), radius=14)
    items = settings.items()
    icons = {'sound': 'sound_off' if muted else 'sound_on',
             'language': 'language_' + i18n.language}
    for name, center in items.items():
        icon = localized(assets.ui, icons[name])
        if icon is not None:
            grow = 1.1 if ui.in_circle(mouse, center, config.MENU_BUTTON_RADIUS) else 1
            image = scaled(icon.image, grow)
            screen.blit(image, image.get_rect(center=center))


def shop_tooltip(state, name):
    """The lines of the tooltip of a duck in the shop: name, price, what it does."""
    can_buy = ui.can_afford(state, name)
    if name == 'bourgeois_duck':
        cost = config.BOURGEOIS_COST
        lines = [(t('bourgeois_duck'), config.INK)]
        details = shop.bourgeois_description(state)
    else:
        duck = next(duck for duck in DUCKS if duck.name == name)
        cost = state.costs[name]
        lines = [(duck.title, config.INK)]
        details = [duck.describe(state), t('bought', count=state.purchases[name])]
    lines.append((t('price', cost=format_number(cost)), config.GOLD_DARK if can_buy else config.HEALTH_RED))
    lines += [(line, config.INK_SOFT) for line in details]
    if not can_buy and state.duckcoins < cost:
        lines.append((t('not_enough'), config.HEALTH_RED))
    return lines


def draw_shop(screen, fonts, assets, state, drawer, now, mouse):
    """The shop's button and, when open, the panel with the ducks (bottom).

    Ducks the player can buy glow and hop; the others are darker. mouse is in the shop's
    coordinates. Returns the duck under the mouse (for its tooltip), or None.
    """
    hovered = None
    if drawer.openness() > 0:
        draw_panel(screen, drawer.panel_rect(), radius=22)
        hovered = drawer.portrait_at(mouse)
        portraits = assets.map_parts().portraits
        for name, (center, diameter) in drawer.portraits().items():
            portrait = portraits.get(name)
            if portrait is None:
                continue
            can_buy = ui.can_afford(state, name)
            x, y = center
            if can_buy:
                y += hop(now)
                glow = pygame.Surface((diameter + 40, diameter + 40), pygame.SRCALPHA)
                pygame.draw.circle(glow, config.GOLD + (round(70 + 90 * pulse(now)),),
                                   glow.get_rect().center, diameter / 2 + 12)
                screen.blit(glow, glow.get_rect(center=(x, y)))
            image = portrait.image if can_buy else tinted(portrait.image, config.SHADE + (255,))
            grow = 1.08 if name == hovered else 1
            image = scaled(image, grow)
            shadow = pygame.Surface(image.get_size(), pygame.SRCALPHA)
            pygame.draw.circle(shadow, (40, 40, 60, 50), shadow.get_rect().center, diameter * grow / 2)
            screen.blit(shadow, shadow.get_rect(center=(x + 4, y + 5)))
            screen.blit(image, image.get_rect(center=(x, y)))
            draw_shop_badges(screen, fonts, state, name, (x, y), diameter)

    draw_shop_tab(screen, fonts['tab'], state, drawer, now, mouse)
    return hovered


def draw_shop_badges(screen, fonts, state, name, center, diameter):
    """How many of a duck were bought (a bubble), and the Bourgeois Duck's timers."""
    x, y = center
    if name == 'bourgeois_duck':
        if state.is_boosted():
            timer, color = state.boost_time_left(), config.BOOST_COLOR
        else:
            timer, color = state.bourgeois_recharge_left(), config.INK
        if timer:
            text = outlined(fonts['small_number'], shop.format_time(timer), color,
                            outline=config.PANEL, width=3)
            screen.blit(text, text.get_rect(center=center))
        return
    count = state.purchases[name]
    if count:
        bubble = (round(x + diameter * 0.36), round(y - diameter * 0.36))
        pygame.draw.circle(screen, config.INK, bubble, config.COUNT_BADGE_RADIUS)
        pygame.draw.circle(screen, config.PANEL, bubble, config.COUNT_BADGE_RADIUS, width=2)
        text = fonts['badge'].render(str(count), True, config.PANEL)
        screen.blit(text, text.get_rect(center=bubble))


def draw_shop_tab(screen, font, state, drawer, now, mouse):
    """The shop's button. When the shop is closed and something can be bought, it glows and hops."""
    tab = drawer.tab_rect()
    attention = not drawer.open and ui.any_affordable(state)
    if attention:
        tab = tab.move(0, hop(now, height=6))
        glow = pygame.Surface(tab.inflate(16, 16).size, pygame.SRCALPHA)
        pygame.draw.rect(glow, config.GOLD + (round(90 + 120 * pulse(now)),), glow.get_rect(),
                         border_top_left_radius=22, border_top_right_radius=22)
        screen.blit(glow, tab.inflate(16, 16).move(0, 8))
    if tab.collidepoint(mouse):
        tab = tab.inflate(8, 4)
    draw_panel(screen, tab, radius=16, shadow=False,
               border_bottom_left_radius=0, border_bottom_right_radius=0)
    label = font.render(t('shop').upper(), True, config.INK)
    arrow = pygame.Surface((18, 12), pygame.SRCALPHA)
    pointing_down = drawer.open
    points = [(0, 0), (18, 0), (9, 12)] if pointing_down else [(0, 12), (18, 12), (9, 0)]
    pygame.draw.polygon(arrow, config.INK, points)
    row = side_by_side(label, arrow, gap=10)
    screen.blit(row, row.get_rect(center=tab.center))


def draw_overlay(screen, title_font, font, lines):
    """A start, pause or victory screen: the game darkened, with a box of text in the middle.

    The first line is the title; an empty line leaves a gap.
    """
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill(config.OVERLAY_COLOR)
    screen.blit(shade, (0, 0))

    texts = [title_font.render(lines[0], True, config.INK)]
    texts += [font.render(line, True, config.INK_SOFT) for line in lines[1:]]
    padding = 40
    width = max(text.get_width() for text in texts) + 2 * padding
    height = sum(text.get_height() + 10 for text in texts) + 2 * padding
    box = pygame.Rect(0, 0, width, height)
    box.center = screen.get_rect().center
    draw_panel(screen, box, radius=24)
    y = box.top + padding
    for text in texts:
        screen.blit(text, text.get_rect(midtop=(box.centerx, y)))
        y += text.get_height() + 10


def part_of(canvas, offset):
    """The part of the canvas a group of things is drawn on (see layout.py), cut at the edges."""
    x, y = offset
    width = min(config.SCREEN_WIDTH, canvas.get_width() - x)
    height = min(config.SCREEN_HEIGHT, canvas.get_height() - y)
    return canvas.subsurface(pygame.Rect(x, y, width, height))


class Screen:
    """Draws the game in a window of any size (see layout.py for where each part goes)."""

    def __init__(self, assets, font, small_font):
        self.assets = assets
        self.font = font
        self.small_font = small_font
        self.title_font = load_font(config.TITLE_FONT_SIZE)
        number = config.NUMBER_FONT
        self.fonts = {
            'toast_title': load_font(config.TOAST_TITLE_SIZE),
            'health': load_font(config.HEALTH_TEXT_SIZE, number),
            'timer': load_font(34, number),
            'tag': load_font(26, number),
            'reward': load_font(38, number),
            'coins': load_font(config.DUCKCOINS_TEXT_SIZE, number),
            'stat': load_font(config.STAT_TEXT_SIZE, number),
            'level': load_font(config.LEVEL_TEXT_SIZE, number),
            'tab': load_font(config.SHOP_TAB_TEXT_SIZE, number),
            'badge': load_font(22, number),
            'small_number': load_font(34, number),
            'damage': load_font(40, number),
        }
        self.gear = make_gear(36)
        self.background = None
        self.background_size = None
        self.canvas = None

    def draw(self, window, layout, state, effects, smacking, interface, now, mouse_pos, overlay=None):
        """interface: the ui.Ui (shop and settings); overlay: the lines of a start/pause/victory
        screen to show over the game, or None."""
        assets, fonts = self.assets, self.fonts
        if self.background_size != (layout.size, i18n.language):  # resized, or language changed
            self.background = build_background(assets, layout)
            self.background_size = (layout.size, i18n.language)
            self.canvas = pygame.Surface(layout.size)
        # At the original size the game is drawn straight to the window, without scaling
        canvas = window if window.get_size() == layout.size else self.canvas

        canvas.blit(self.background, (0, 0))
        part = {group: part_of(canvas, offset) for group, offset in layout.offsets.items()}
        mouse = {group: layout.to_group(group, mouse_pos) for group in layout.offsets}

        draw_center(part['center'], fonts, assets, state, effects, smacking, now)
        draw_stats(part['top_left'], fonts, assets, state, effects)
        draw_level_buttons(part['top_center'], fonts['level'], assets, state)
        hovered = draw_shop(part['bottom'], fonts, assets, state, interface.shop, now, mouse['bottom'])
        draw_settings(part['top_right'], assets, interface.settings, state.muted, self.gear,
                      mouse['top_right'])
        effects.draw(canvas, fonts['damage'], assets.coin, offset=layout.offsets['center'],
                     coin_target=config.DUCKCOINS_ICON_POS)
        shake = effects.screen_offset()
        if shake != (0, 0):  # the whole screen shakes (the edges repeat for those few pixels)
            canvas.scroll(*shake)
        if overlay:
            draw_overlay(canvas, self.title_font, self.font, overlay)
        elif hovered is not None:
            (x, y), diameter = interface.shop.portraits()[hovered]
            offset_x, offset_y = layout.offsets['bottom']
            draw_box(canvas, self.small_font, shop_tooltip(state, hovered),
                     offset_x + x, offset_y + y - diameter / 2 - 16)

        if canvas is not window:
            pygame.transform.smoothscale(canvas, window.get_size(), window)
