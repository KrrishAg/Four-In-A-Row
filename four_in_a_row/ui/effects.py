"""Decorative animations: confetti and the drifting discs behind the menu."""

import math
import random

import pygame

from . import layout, theme
from .graphics import disc_sprite


class Confetti:
    def __init__(self):
        self.pieces = []

    def clear(self):
        self.pieces = []

    def burst(self, colours, count=160):
        for _ in range(count):
            self.pieces.append(
                {
                    "x": random.uniform(0, layout.WIDTH),
                    "y": random.uniform(-layout.HEIGHT * 0.7, -10),
                    "vx": random.uniform(-40, 40),
                    "vy": random.uniform(140, 280),
                    "size": random.uniform(6, 11),
                    "angle": random.uniform(0, math.tau),
                    "spin": random.uniform(-7, 7),
                    "phase": random.uniform(0, math.tau),
                    "colour": random.choice(colours),
                }
            )

    def update(self, dt):
        for p in self.pieces:
            p["phase"] += dt * 3
            p["x"] += (p["vx"] + math.sin(p["phase"]) * 45) * dt
            p["vy"] = min(p["vy"] + 120 * dt, 420)
            p["y"] += p["vy"] * dt
            p["angle"] += p["spin"] * dt
        self.pieces = [p for p in self.pieces if p["y"] < layout.HEIGHT + 20]

    def draw(self, surface):
        for p in self.pieces:
            # The height shrinks and grows so each piece looks like it tumbles.
            half_w = p["size"] / 2
            half_h = p["size"] * (0.15 + 0.35 * abs(math.cos(p["phase"])))
            cos_a, sin_a = math.cos(p["angle"]), math.sin(p["angle"])
            points = [
                (p["x"] + dx * cos_a - dy * sin_a, p["y"] + dx * sin_a + dy * cos_a)
                for dx, dy in ((-half_w, -half_h), (half_w, -half_h), (half_w, half_h), (-half_w, half_h))
            ]
            pygame.draw.polygon(surface, p["colour"], points)


class FloatingDiscs:
    """Faint discs that fall slowly behind the menu."""

    SIZES = (18, 26, 38, 52)

    def __init__(self, count=12):
        self.discs = [self._spawn(anywhere=True) for _ in range(count)]

    def _spawn(self, anywhere=False):
        radius = random.choice(self.SIZES)
        return {
            "x": random.uniform(0, layout.WIDTH),
            "y": random.uniform(-60, layout.HEIGHT) if anywhere else -radius - 10,
            "speed": random.uniform(14, 34) * (radius / 26),
            "radius": radius,
            "colour": theme.BACKDROP_DISC,
            "alpha": random.choice((22, 30, 40)),
        }

    def update(self, dt):
        for i, disc in enumerate(self.discs):
            disc["y"] += disc["speed"] * dt
            if disc["y"] - disc["radius"] > layout.HEIGHT:
                self.discs[i] = self._spawn()

    def draw(self, surface):
        for disc in self.discs:
            sprite = disc_sprite(disc["radius"], disc["colour"], disc["alpha"])
            surface.blit(sprite, sprite.get_rect(center=(disc["x"], disc["y"])))
