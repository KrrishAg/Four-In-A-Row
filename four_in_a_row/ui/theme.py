"""Colours and fonts."""

from ..core import PLAYER1, PLAYER2

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

BG_TOP = (9, 13, 28)
BG_BOTTOM = (14, 21, 46)

BOARD_TOP = (52, 108, 238)
BOARD_BOTTOM = (29, 66, 178)
BOARD_RIM_DARK = (20, 46, 134)
BOARD_RIM_LIGHT = (116, 158, 250)
BOARD_BACK_TOP = (6, 9, 21)
BOARD_BACK_BOTTOM = (11, 16, 36)

RED = (240, 68, 72)
YELLOW = (250, 200, 40)
PIECE_COLOUR = {PLAYER1: RED, PLAYER2: YELLOW}
PIECE_NAME = {PLAYER1: "Red", PLAYER2: "Yellow"}

TEXT = (240, 243, 255)
MUTED = (148, 160, 190)
FAINT = (84, 96, 128)
BACKDROP_DISC = (70, 110, 210)  # faint discs drifting behind the menu

ACCENT_TOP = (64, 120, 245)
ACCENT_BOTTOM = (40, 86, 208)
BUTTON_TOP = (255, 255, 255)
BUTTON_BOTTOM = (212, 222, 244)
BUTTON_TEXT = (14, 21, 46)

# Tried in order; the first one installed is used.
FONT_FAMILIES = ("avenirnext", "helveticaneue", "segoeui", "dejavusans", "arial")
