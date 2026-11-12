"""Menu widgets: a segmented control and a button."""

import pygame

from . import theme
from .graphics import approach, blit_shadow, draw_text, panel


class SegmentedControl:
    """A labelled row of options where exactly one is selected.

    The highlight slides to the selected option.
    """

    LABEL_H = 28
    TRACK_H = 52
    INSET = 4

    def __init__(self, fonts, label, options, x, y, width, selected=0):
        self.fonts = fonts
        self.label = label
        self.options = options
        self.selected = selected
        self.enabled = True
        self.track = pygame.Rect(x, y + self.LABEL_H, width, self.TRACK_H)
        self.segment_w = (width - 2 * self.INSET) // len(options)
        self.pill_x = float(self.segment_rect(selected).x)

    @property
    def value(self):
        return self.options[self.selected]

    def segment_rect(self, index):
        return pygame.Rect(
            self.track.x + self.INSET + index * self.segment_w,
            self.track.y + self.INSET,
            self.segment_w,
            self.TRACK_H - 2 * self.INSET,
        )

    def click(self, pos):
        if not self.enabled:
            return
        for i in range(len(self.options)):
            if self.segment_rect(i).collidepoint(pos):
                self.selected = i

    def update(self, dt):
        self.pill_x = approach(self.pill_x, self.segment_rect(self.selected).x, dt, 18)

    def draw(self, surface, mouse):
        draw_text(
            surface,
            self.fonts.get(15),
            self.label.upper(),
            theme.MUTED if self.enabled else theme.FAINT,
            shadow=False,
            topleft=(self.track.x + 6, self.track.y - self.LABEL_H + 4),
        )
        surface.blit(
            panel(self.track.size, 16, (0, 0, 0, 80), (0, 0, 0, 56), (255, 255, 255, 20)), self.track
        )

        pill_rect = self.segment_rect(self.selected)
        if self.enabled:
            pill = panel(pill_rect.size, 13, theme.ACCENT_TOP, theme.ACCENT_BOTTOM, (255, 255, 255, 60))
        else:
            pill = panel(pill_rect.size, 13, (255, 255, 255, 22), (255, 255, 255, 14))
        surface.blit(pill, (round(self.pill_x), pill_rect.y))

        for i, option in enumerate(self.options):
            rect = self.segment_rect(i)
            if not self.enabled:
                colour = theme.FAINT
            elif i == self.selected or rect.collidepoint(mouse):
                colour = theme.TEXT
            else:
                colour = theme.MUTED
            draw_text(
                surface,
                self.fonts.get(19),
                option,
                colour,
                shadow=self.enabled and i == self.selected,
                center=rect.center,
            )


class Button:
    """The primary action button. It lifts and brightens on hover."""

    def __init__(self, fonts, text, rect):
        self.fonts = fonts
        self.text = text
        self.rect = pygame.Rect(rect)
        self.hover = 0.0

    def hit(self, pos):
        return self.rect.collidepoint(pos)

    def update(self, dt, mouse):
        self.hover = approach(self.hover, 1.0 if self.hit(mouse) else 0.0, dt, 16)

    def draw(self, surface):
        rect = self.rect.move(0, -round(3 * self.hover))
        blit_shadow(surface, rect, 22, blur=12, alpha=150, offset=8 + round(4 * self.hover))
        surface.blit(
            panel(rect.size, 22, theme.BUTTON_TOP, theme.BUTTON_BOTTOM, (255, 255, 255, 90)), rect
        )
        if self.hover > 0.01:
            shine = panel(rect.size, 22, (255, 255, 255, 70), (255, 255, 255, 20))
            shine.set_alpha(round(255 * self.hover))
            surface.blit(shine, rect)
        draw_text(
            surface, self.fonts.get(25), self.text, theme.BUTTON_TEXT, shadow=False, center=rect.center
        )
