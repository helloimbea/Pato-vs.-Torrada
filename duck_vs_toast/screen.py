"""Drawing everything that shows up on screen."""
import pygame

from . import config, i18n, shop
from .assets import Sprite, load_font, localized
from .effects import ease_in, outlined
from .i18n import t
from .numbers import format_number
from .shop import DUCKS


def write(screen, font, text, color, position):
    nudge = getattr(font, 'nudge', 0)  # see assets.load_font
    screen.blit(font.render(text, True, color), (position[0], position[1] + nudge))


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

    # Above the shop, centered on the duck
    draw_box(screen, small_font, lines, offset[0] + center_x, offset[1] + 500)


def draw_box(screen, small_font, lines, center_x, bottom):
    """A tooltip: lines of (text, color) in a box centered on center_x, ending at bottom."""
    texts = [small_font.render(text, True, color) for text, color in lines]
    padding = 10
    width = max(text.get_width() for text in texts) + 2 * padding
    height = sum(text.get_height() for text in texts) + 2 * padding
    # Without leaving the screen
    x = min(max(round(center_x - width / 2), 5), screen.get_width() - width - 5)
    y = max(round(bottom - height), 5)
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


def fit(text, max_width):
    """Make a rendered text smaller if it is wider than max_width."""
    if text.get_width() <= max_width:
        return text
    scale = max_width / text.get_width()
    return pygame.transform.smoothscale(text, (max_width, round(text.get_height() * scale)))


def draw_toast_title(screen, font, toast):
    """The toast's name above it. The upside-down toast's name is upside down too."""
    text = fit(font.render(t(toast), True, config.INK), config.TOAST_TITLE_MAX_WIDTH)
    if toast == 'upside_down_toast':
        text = pygame.transform.rotate(text, 180)
    screen.blit(text, text.get_rect(center=config.TOAST_TITLE_CENTER))


def two_lines(text):
    """Split a name in two lines of about the same length ("PATO SIAMÊS" -> PATO / SIAMÊS)."""
    words = text.split()
    if len(words) < 2:
        return [text]
    best = min(range(1, len(words)),
               key=lambda i: abs(len(' '.join(words[:i])) - len(' '.join(words[i:]))))
    return [' '.join(words[:best]), ' '.join(words[best:])]


def draw_shop_titles(screen, font):
    """The ducks' names above their portraits in the shop."""
    names = [(duck.name, duck.button_pos[0]) for duck in DUCKS]
    names.append(('bourgeois_duck', config.BOURGEOIS_BUTTON_POS[0]))
    for name, center_x in names:
        # Fonts have letters of different heights: the lines are placed by their capital letters
        capital = font.render('H', True, config.INK).get_bounding_rect()
        y = config.SHOP_TITLE_TOP - capital.top
        for line in two_lines(t(name).upper()):
            text = fit(font.render(line, True, config.INK), config.SHOP_TITLE_MAX_WIDTH)
            screen.blit(text, text.get_rect(midtop=(center_x, y)))
            y += round(capital.height * config.SHOP_TITLE_LINE)


def draw_toast(screen, assets, state, effects, title_font=None):
    """The bread slice and the toast's face, flinching when hit: they shake, squash and look hurt.

    A beaten toast shrinks away while the next one pops up (see effects.py).
    """
    death = effects.death()
    if death is not None:
        draw_dead_toast(screen, assets, effects.dead_toast, death)

    toast, tint = toast_drawing(assets, state.toast, 'hurt' if effects.is_hurt() else None)
    # The toast's name is written with the font (the handwritten one, at the top of the
    # drawing above TOAST_TITLE_BOTTOM, isn't drawn anymore)
    if title_font is not None:
        draw_toast_title(screen, title_font, state.toast)

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


def duck_sprites(assets, state):
    """{duck name: Sprite} for every duck on screen, in drawing order (the starter duck on top)."""
    names = state.ducks_on_screen + ['starter_duck']
    return {name: localized(assets.ducks, name) for name in names}


_worn_ducks = {}  # tinted / bandaged duck drawings, made when first needed


def worn_duck(assets, name, bumps):
    """A duck's drawing after bumps hits: grayer with each hit, with a bandage once battered.

    A battered duck uses "<duck>_battered.png" when it exists in assets/images/ducks;
    until it is drawn, the duck turns gray and gets a bandage drawn by code.
    """
    sprite = localized(assets.ducks, name)
    if bumps <= 0:
        return sprite
    battered = bumps >= config.DUCK_MAX_BUMPS
    if battered and localized(assets.ducks, name + '_battered') is not None:
        return localized(assets.ducks, name + '_battered')
    key = (id(sprite.image), bumps)
    if key not in _worn_ducks:
        share = bumps / config.DUCK_MAX_BUMPS
        tint = tuple(round(255 + (gray - 255) * share) for gray in config.BATTERED_TINT)
        image = sprite.image.copy()
        image.fill(tint + (255,), special_flags=pygame.BLEND_RGBA_MULT)
        if battered:
            draw_bandage(image)
        _worn_ducks[key] = Sprite(image, sprite.pos)
    return _worn_ducks[key]


def draw_bandage(image):
    """A crossed bandage on the top of a duck's drawing (a placeholder until it is drawn)."""
    area = image.get_bounding_rect()
    length = max(area.width // 3, 12)
    thickness = max(length // 3, 5)
    strip = pygame.Surface((length, thickness), pygame.SRCALPHA)
    pygame.draw.rect(strip, config.BANDAGE_COLOR, strip.get_rect(), border_radius=thickness // 2)
    pygame.draw.rect(strip, config.DARK_BLUE, strip.get_rect(), width=1, border_radius=thickness // 2)
    center = (area.centerx, area.top + area.height // 4)
    for angle in (35, -35):
        turned = pygame.transform.rotate(strip, angle)
        image.blit(turned, turned.get_rect(center=center))


def draw_moving_duck(screen, sprite, duck, held):
    """A duck that is held, flying or going back home (see throwing.py)."""
    image = sprite.image
    lift = config.HELD_LIFT if held else 1
    if duck.angle or lift != 1:
        image = pygame.transform.rotozoom(image, duck.angle, lift)
    screen.blit(image, image.get_rect(center=duck.center))


def scene_duck_lines(state, name):
    """The tooltip of a duck on screen: its name and what can be done with it."""
    lines = [(t(name), config.DARK_BLUE)]
    if state.is_battered(name):
        cost = state.heal_cost()
        lines.append((t('battered'), config.RED))
        lines.append((t('heal_for', cost=format_number(cost)),
                      config.BLUE if state.duckcoins >= cost else config.RED))
    else:
        lines.append((t('throw_hint'), config.BLUE))
        left = config.DUCK_MAX_BUMPS - state.bumps(name)
        lines.append((t('throws_left', count=left, total=config.DUCK_MAX_BUMPS), config.BLUE))
    return lines


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


def draw_center(screen, font, assets, state, effects, throws, now, title_font=None):
    """The toast, its health, and the ducks around it (and the ones being thrown)."""
    bar_width = state.health * (config.HEALTH_BAR_WIDTH / state.max_health)
    bar = pygame.Rect(*config.HEALTH_BAR_POS, bar_width, config.HEALTH_BAR_HEIGHT)
    pygame.draw.rect(screen, config.RED, bar)

    # Bought ducks, toast and starter duck (the ones being thrown are drawn last, on top)
    for name in state.ducks_on_screen:
        if not throws.is_away(name):
            draw_duck(screen, worn_duck(assets, name, state.bumps(name)), effects.duck_scale(name))
    draw_toast(screen, assets, state, effects, title_font)
    if not throws.is_away('starter_duck'):
        draw_duck(screen, worn_duck(assets, 'starter_duck', state.bumps('starter_duck')),
                  effects.duck_scale('starter_duck'))

    write(screen, font, format_number(round(state.health)), config.RED, config.HEALTH_TEXT_POS)
    reward_color = config.BOOST_COLOR if state.is_boosted() else config.GREEN
    write(screen, font, format_number(state.current_reward()), reward_color, config.REWARD_TEXT_POS)

    if state.has_auto_click:
        localized(assets.ui, 'auto_click_pointer').draw(screen)

    if state.is_boss():
        write(screen, font, f' {state.boss_time_left(now)}', config.TIMER_BLUE, config.BOSS_TIMER_TEXT_POS)
        localized(assets.ui, 'boss_timer_box').draw(screen)

    for name, duck in throws.moving.items():
        sprite = worn_duck(assets, name, state.bumps(name))
        draw_moving_duck(screen, sprite, duck, held=name == throws.held)


def draw_stats(screen, font, state, effects):
    """Duckcoins, damage per second and click damage (top left)."""
    shown = state.duckcoins if effects.shown_duckcoins is None else round(effects.shown_duckcoins)
    write(screen, font, format_number(shown), config.LIGHT_BLUE, config.DUCKCOINS_TEXT_POS)
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


_locked_sizes = {}  # the locked sign resized for each portrait size, made when first needed


def draw_locked(screen, assets, name, button_pos):
    """Draw the "locked" sign over a duck's portrait in the shop.

    ui/locked.png is drawn over the Siamese duck's portrait; for the other ducks it is
    resized and moved so it fits their circle (config.SHOP_PORTRAITS).
    """
    locked = assets.ui['locked']
    ref_x, ref_y, ref_size = config.SHOP_PORTRAITS['siamese_duck']
    x, y, size = config.SHOP_PORTRAITS.get(name, (*button_pos, ref_size))
    scale = size / ref_size
    key = (id(locked.image), size)
    if key not in _locked_sizes:
        width, height = locked.image.get_size()
        _locked_sizes[key] = pygame.transform.smoothscale(
            locked.image, (round(width * scale), round(height * scale)))
    screen.blit(_locked_sizes[key], (round(x + (locked.pos[0] - ref_x) * scale),
                                     round(y + (locked.pos[1] - ref_y) * scale)))


def draw_shop(screen, font, small_font, assets, state, title_font=None):
    """Names, prices, locked ducks and how many of each duck was bought (bottom)."""
    if title_font is not None:
        draw_shop_titles(screen, title_font)
    for duck in DUCKS:
        write(screen, font, format_number(state.costs[duck.name]), config.BLUE, duck.cost_text_pos)

    # Ducks the player can't afford yet are shown as "locked"
    for duck in DUCKS:
        if state.duckcoins < state.costs[duck.name]:
            draw_locked(screen, assets, duck.name, duck.button_pos)

    # Bourgeois Duck: fixed price; after buying it, a boost and then a recharge time
    write(screen, font, format_number(config.BOURGEOIS_COST), config.BLUE, config.BOURGEOIS_COST_TEXT_POS)
    if not shop.can_buy_bourgeois(state):
        draw_locked(screen, assets, 'bourgeois_duck', config.BOURGEOIS_BUTTON_POS)
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
        self.title_font = load_font(config.TITLE_FONT_SIZE)
        self.toast_title_font = load_font(config.TOAST_TITLE_SIZE)
        self.shop_title_font = load_font(config.SHOP_TITLE_SIZE)
        self.background = None
        self.background_size = None
        self.canvas = None

    def draw(self, window, layout, state, effects, throws, now, mouse_pos, overlay=None):
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
        draw_center(part['center'], font, assets, state, effects, throws, now, self.toast_title_font)
        draw_stats(part['top_left'], font, state, effects)
        draw_level_buttons(part['top_right'], font, assets, state)
        draw_shop(part['bottom'], font, self.small_font, assets, state, self.shop_title_font)
        effects.draw(canvas, font, assets.coin, offset=layout.offsets['center'],
                     coin_target=config.DUCKCOINS_ICON_POS)
        if overlay:
            draw_overlay(canvas, self.title_font, font, overlay)
        else:
            draw_tooltip(canvas, self.small_font, state, layout.to_group('bottom', mouse_pos),
                         layout.offsets['bottom'])
            # Hovering a duck on screen (not while holding one) tells what it can do
            in_center = layout.to_group('center', mouse_pos)
            name = None if throws.held else throws.duck_at(in_center, duck_sprites(assets, state))
            if name is not None:
                offset_x, offset_y = layout.offsets['center']
                draw_box(canvas, self.small_font, scene_duck_lines(state, name),
                         offset_x + in_center[0], offset_y + in_center[1] - 25)

        if canvas is not window:
            pygame.transform.smoothscale(canvas, window.get_size(), window)
