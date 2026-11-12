"""The menu screen."""

import math

import pygame

from ..ai import DIFFICULTY_DEPTH
from . import layout, theme
from .effects import FloatingDiscs
from .graphics import background, blit_centre, blit_shadow, disc_sprite, draw_text, panel, radial_glow
from .settings import GameSettings
from .widgets import Button, SegmentedControl

MODES = ["Player vs AI", "Two Players"]
DIFFICULTIES = list(DIFFICULTY_DEPTH)
FIRST_MOVE = ["You", "AI"]

CARD = pygame.Rect(62, 262, layout.WIDTH - 124, 344)


class MenuScene:
    def __init__(self, app):
        self.app = app
        self.fonts = app.fonts
        settings = app.settings
        self.time = 0.0
        self.background = background((layout.WIDTH // 2, 150), theme.ACCENT_BOTTOM)
        self.discs = FloatingDiscs()

        x, width = CARD.x + 28, CARD.width - 56
        self.mode = SegmentedControl(
            self.fonts, "Mode", MODES, x, CARD.y + 24, width, 0 if settings.vs_ai else 1
        )
        self.difficulty = SegmentedControl(
            self.fonts, "Difficulty", DIFFICULTIES, x, CARD.y + 126, width,
            DIFFICULTIES.index(settings.difficulty),
        )
        self.first = SegmentedControl(
            self.fonts, "First move", FIRST_MOVE, x, CARD.y + 228, width, 1 if settings.ai_first else 0
        )
        self.controls = (self.mode, self.difficulty, self.first)
        self.start = Button(self.fonts, "Start Game", (layout.WIDTH // 2 - 140, 638, 280, 62))

    def close(self):
        pass

    def chosen_settings(self):
        return GameSettings(
            vs_ai=self.mode.value == "Player vs AI",
            difficulty=self.difficulty.value,
            ai_first=self.first.value == "AI",
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for control in self.controls:
                control.click(event.pos)
            if self.start.hit(event.pos):
                self.app.start_game(self.chosen_settings())
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.app.start_game(self.chosen_settings())
            elif event.key == pygame.K_ESCAPE:
                self.app.quit()

    def update(self, dt):
        self.time += dt
        self.discs.update(dt)
        vs_ai = self.mode.value == "Player vs AI"
        self.difficulty.enabled = vs_ai
        self.first.enabled = vs_ai
        for control in self.controls:
            control.update(dt)
        self.start.update(dt, self.app.mouse)

    def draw(self, surface):
        surface.blit(self.background, (0, 0))
        self.discs.draw(surface)

        centre_x = layout.WIDTH // 2
        draw_text(surface, self.fonts.get(70), "Four in a Row", theme.TEXT, center=(centre_x, 112))

        # Four red discs in a row between two yellow ones, bobbing in a wave.
        colours = (theme.YELLOW, theme.RED, theme.RED, theme.RED, theme.RED, theme.YELLOW)
        for i, colour in enumerate(colours):
            x = centre_x + (i - 2.5) * 46
            y = 196 + math.sin(self.time * 2.4 - i * 0.55) * 5
            if colour == theme.RED:
                blit_centre(surface, radial_glow(36, theme.RED, 60), (x, y))
            blit_centre(surface, disc_sprite(17, colour), (x, y))

        blit_shadow(surface, CARD, 26, blur=18, alpha=110, offset=12)
        surface.blit(
            panel(CARD.size, 26, (255, 255, 255, 18), (255, 255, 255, 8), (255, 255, 255, 30)), CARD
        )
        for control in self.controls:
            control.draw(surface, self.app.mouse)

        self.start.draw(surface)
        draw_text(
            surface, self.fonts.get(15, bold=False), "Enter to start    Esc to quit",
            theme.FAINT, shadow=False, center=(centre_x, 730),
        )
