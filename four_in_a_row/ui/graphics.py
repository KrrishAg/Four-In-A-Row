"""Drawing helpers and pre-rendered sprites.

Pygame's shape drawing is not anti-aliased, so every sprite here is drawn
at SS times its final size and scaled down smoothly. Sprites are built
once and cached.
"""

import math
from functools import lru_cache

import pygame

from ..core import COLS, ROWS
from . import layout, theme

SS = 3  # supersampling factor


# ----- small maths helpers ------------------------------------------


def mix(a, b, t):
    """Blend two colours; t = 0 gives a, t = 1 gives b."""
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def rgba(colour, alpha=255):
    return (colour[0], colour[1], colour[2], colour[3] if len(colour) == 4 else alpha)


def approach(value, target, dt, rate=14.0):
    """Move value towards target smoothly, independent of frame rate."""
    return target + (value - target) * math.exp(-rate * dt)


# ----- building blocks ----------------------------------------------


def opaque_surface(size):
    """A surface with no alpha channel.

    On some platforms (macOS) the window surface itself has an alpha
    channel, and translucent sprites blended onto it leave see-through
    pixels. Everything is therefore composed on an opaque surface first.
    """
    return pygame.Surface(size, 0, 32, (0xFF0000, 0x00FF00, 0x0000FF, 0))


def vertical_gradient(size, top, bottom):
    width, height = size
    top, bottom = rgba(top), rgba(bottom)
    strip = pygame.Surface((1, height), pygame.SRCALPHA)
    for y in range(height):
        strip.set_at((0, y), mix(top, bottom, y / max(1, height - 1)))
    return pygame.transform.scale(strip, (width, height))


def _rounded(size, radius, top, bottom):
    """A rounded rectangle with a vertical gradient, at the size given."""
    surface = vertical_gradient(size, top, bottom)
    mask = pygame.Surface(size, pygame.SRCALPHA)
    mask.fill((255, 255, 255, 0))
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
    surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return surface


def _ring(size, radius, top, bottom, width):
    """A rounded outline, made by cutting the middle out of a rounded rectangle."""
    ring = _rounded(size, radius, top, bottom)
    inner = pygame.Rect(width, width, size[0] - 2 * width, size[1] - 2 * width)
    pygame.draw.rect(ring, (*rgba(top)[:3], 0), inner, border_radius=max(0, radius - width))
    return ring


@lru_cache(maxsize=None)
def panel(size, radius, top, bottom=None, border=None, border_width=1):
    """An anti-aliased rounded rectangle, optionally with a border."""
    hi = (size[0] * SS, size[1] * SS)
    surface = _rounded(hi, radius * SS, top, bottom or top)
    if border:
        surface.blit(_ring(hi, radius * SS, border, border, border_width * SS), (0, 0))
    return pygame.transform.smoothscale(surface, size)


@lru_cache(maxsize=None)
def soft_shadow(size, radius, blur=14, alpha=130):
    """A blurred drop shadow. The sprite is larger than `size` by 2 * blur on each side."""
    pad = blur * 2
    k = 4
    small = pygame.Surface(((size[0] + 2 * pad) // k, (size[1] + 2 * pad) // k), pygame.SRCALPHA)
    rect = pygame.Rect(pad // k, pad // k, size[0] // k, size[1] // k)
    pygame.draw.rect(small, (0, 0, 0, alpha), rect, border_radius=max(1, radius // k))
    tiny = pygame.transform.smoothscale(
        small, (max(1, small.get_width() // 3), max(1, small.get_height() // 3))
    )
    return pygame.transform.smoothscale(tiny, (size[0] + 2 * pad, size[1] + 2 * pad))


def blit_shadow(surface, rect, radius, blur=14, alpha=130, offset=8):
    pad = blur * 2
    shadow = soft_shadow((rect.width, rect.height), radius, blur, alpha)
    surface.blit(shadow, (rect.x - pad, rect.y - pad + offset))


@lru_cache(maxsize=None)
def radial_glow(radius, colour, max_alpha, power=2.0):
    """A soft circular glow that is brightest in the middle."""
    r = 48
    small = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
    small.fill((*colour, 0))
    for i in range(r, 0, -1):
        alpha = int(max_alpha * (1 - i / r) ** power)
        pygame.draw.circle(small, (*colour, alpha), (r, r), i)
    return pygame.transform.smoothscale(small, (2 * radius, 2 * radius))


@lru_cache(maxsize=None)
def halo(ring_radius, spread, colour, max_alpha):
    """A glowing ring: brightest at ring_radius, fading inwards and outwards."""
    r = ring_radius + spread * 2
    surface = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
    surface.fill((*colour, 0))
    for i in range(r, 0, -1):
        alpha = int(max_alpha * math.exp(-(((i - ring_radius) / spread) ** 2)))
        pygame.draw.circle(surface, (*colour, alpha), (r, r), i)
    return surface


@lru_cache(maxsize=None)
def circle_sprite(radius, colour):
    """An anti-aliased filled circle. `colour` may include alpha."""
    r = radius * SS
    surface = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
    surface.fill((*colour[:3], 0))
    pygame.draw.circle(surface, rgba(colour), (r, r), r)
    return pygame.transform.smoothscale(surface, (2 * radius, 2 * radius))


@lru_cache(maxsize=None)
def disc_sprite(radius, colour, alpha=255):
    """A playing disc with a darker rim, soft shading, and an embossed ring."""
    r = radius * SS
    dark = mix(colour, theme.BLACK, 0.34)
    surface = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
    surface.fill((*dark, 0))
    pygame.draw.circle(surface, dark, (r, r), r)

    # Body: circles that shrink and drift up-left, from shaded to lit.
    body = int(r * 0.93)
    shaded = mix(colour, theme.BLACK, 0.10)
    lit = mix(colour, theme.WHITE, 0.20)
    steps = 28
    for i in range(steps):
        t = i / (steps - 1)
        offset = int(-r * 0.20 * t)
        pygame.draw.circle(
            surface, mix(shaded, lit, t), (r + offset, r + offset), int(body * (1 - 0.72 * t))
        )

    # Embossed ring and a soft highlight, drawn on an overlay so they blend.
    overlay = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
    ring = int(r * 0.63)
    pygame.draw.circle(overlay, (*theme.WHITE, 70), (r, r + int(1.5 * SS)), ring, SS)
    pygame.draw.circle(overlay, (*dark, 120), (r, r), ring, int(1.6 * SS))
    surface.blit(overlay, (0, 0))
    gloss = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
    pygame.draw.ellipse(
        gloss, (*theme.WHITE, 46), (int(r * 0.42), int(r * 0.22), int(r * 0.80), int(r * 0.44))
    )
    surface.blit(gloss, (0, 0))

    sprite = pygame.transform.smoothscale(surface, (2 * radius, 2 * radius))
    if alpha < 255:
        sprite.set_alpha(alpha)
    return sprite


def blit_centre(surface, sprite, centre):
    surface.blit(sprite, sprite.get_rect(center=(round(centre[0]), round(centre[1]))))


# ----- the board ----------------------------------------------------


def board_back():
    """The dark wall seen through the holes."""
    return panel(
        (layout.BOARD_W, layout.BOARD_H),
        layout.BOARD_RADIUS,
        theme.BOARD_BACK_TOP,
        theme.BOARD_BACK_BOTTOM,
    )


def board_front():
    """The blue board with see-through holes. It is drawn over the discs."""
    size = (layout.BOARD_W * SS, layout.BOARD_H * SS)
    radius = layout.BOARD_RADIUS * SS
    front = _rounded(size, radius, theme.BOARD_TOP, theme.BOARD_BOTTOM)
    # A light edge that fades out down the board, like a lit bevel.
    front.blit(_ring(size, radius, (255, 255, 255, 120), (255, 255, 255, 0), 2 * SS), (0, 0))

    hole = layout.RADIUS * SS
    # Shadow cast by the board's thickness onto whatever is in the hole.
    shadow = pygame.Surface((2 * hole, 2 * hole), pygame.SRCALPHA)
    pygame.draw.circle(shadow, (0, 0, 0, 96), (hole, hole), hole)
    pygame.draw.circle(shadow, (0, 0, 0, 0), (hole, hole + 7 * SS), hole)

    for row in range(ROWS):
        for col in range(COLS):
            cx = (layout.BOARD_PAD + col * layout.CELL + layout.CELL // 2) * SS
            cy = (layout.BOARD_PAD + row * layout.CELL + layout.CELL // 2) * SS
            pygame.draw.circle(front, theme.BOARD_RIM_LIGHT, (cx, cy + 2 * SS), hole + 3 * SS)
            pygame.draw.circle(front, theme.BOARD_RIM_DARK, (cx, cy), hole + 3 * SS)
            pygame.draw.circle(front, (*theme.BOARD_RIM_DARK, 0), (cx, cy), hole)
            front.blit(shadow, (cx - hole, cy - hole))

    return pygame.transform.smoothscale(front, (layout.BOARD_W, layout.BOARD_H))


def background(glow_centre=None, glow_colour=theme.BOARD_TOP):
    """The window background: a gradient with an optional soft glow."""
    surface = opaque_surface((layout.WIDTH, layout.HEIGHT))
    surface.blit(vertical_gradient(surface.get_size(), theme.BG_TOP, theme.BG_BOTTOM), (0, 0))
    if glow_centre:
        blit_centre(surface, radial_glow(460, glow_colour, 46, 1.6), glow_centre)
    return surface


# ----- text ---------------------------------------------------------


class Fonts:
    def __init__(self):
        self._cache = {}
        self._family = next(
            (name for name in theme.FONT_FAMILIES if pygame.font.match_font(name)), None
        )

    def get(self, size, bold=True):
        key = (size, bold)
        if key not in self._cache:
            self._cache[key] = pygame.font.SysFont(self._family, size, bold=bold)
        return self._cache[key]


def draw_text(surface, font, text, colour, *, shadow=True, alpha=255, **anchor):
    """Draw text positioned by a rect keyword such as center= or midleft=."""
    image = font.render(text, True, colour)
    rect = image.get_rect(**anchor)
    if shadow:
        shade = font.render(text, True, theme.BLACK)
        shade.set_alpha(90 * alpha // 255)
        surface.blit(shade, rect.move(0, 2))
    if alpha < 255:
        image.set_alpha(alpha)
    surface.blit(image, rect)
    return rect
