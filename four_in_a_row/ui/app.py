"""The application window: owns the main loop and switches between scenes."""

import pygame

from . import layout, theme
from .game import GameScene
from .graphics import Fonts, disc_sprite, opaque_surface
from .menu import MenuScene
from .settings import GameSettings

FADE_TIME = 0.28


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Four in a Row")
        self.screen = pygame.display.set_mode((layout.WIDTH, layout.HEIGHT))
        pygame.display.set_icon(disc_sprite(32, theme.RED))
        self.clock = pygame.time.Clock()
        self.fonts = Fonts()
        self.settings = GameSettings()
        self.mouse = pygame.mouse.get_pos()
        self.running = True
        self.fade = 1.0  # 1 = fully covered, 0 = fully visible
        # Scenes draw onto this opaque canvas, which is then copied to the window.
        self.canvas = opaque_surface((layout.WIDTH, layout.HEIGHT))
        self.fade_surface = opaque_surface((layout.WIDTH, layout.HEIGHT))
        self.fade_surface.fill(theme.BG_TOP)
        self.scene = MenuScene(self)

    # ----- scene switching -------------------------------------------

    def _switch(self, scene):
        self.scene.close()
        self.scene = scene
        self.fade = 1.0

    def show_menu(self):
        self._switch(MenuScene(self))

    def start_game(self, settings):
        self.settings = settings
        self._switch(GameScene(self, settings))

    def quit(self):
        self.running = False

    # ----- main loop -------------------------------------------------

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.quit()
            return
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            self.mouse = event.pos
        self.scene.handle_event(event)

    def update(self, dt):
        self.fade = max(0.0, self.fade - dt / FADE_TIME)
        self.scene.update(dt)

    def draw(self):
        self.scene.draw(self.canvas)
        if self.fade > 0:
            self.fade_surface.set_alpha(round(255 * self.fade))
            self.canvas.blit(self.fade_surface, (0, 0))
        self.screen.blit(self.canvas, (0, 0))
        pygame.display.flip()

    def run(self):
        while self.running:
            # Cap dt so a stall (such as dragging the window) cannot skip an animation.
            dt = min(self.clock.tick(layout.FPS) / 1000, 0.05)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()
        self.scene.close()
        pygame.quit()


def run():
    App().run()
