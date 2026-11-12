"""Options chosen on the menu screen."""

from dataclasses import dataclass


@dataclass
class GameSettings:
    vs_ai: bool = True
    difficulty: str = "Medium"
    ai_first: bool = False
