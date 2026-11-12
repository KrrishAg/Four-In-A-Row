"""Window geometry and conversions between board cells and pixels."""

from ..core import COLS, ROWS

CELL = 84
RADIUS = 34  # radius of a hole in the board
BOARD_PAD = 14  # frame around the grid of holes
BOARD_RADIUS = 28  # corner radius of the board

BOARD_W = COLS * CELL + 2 * BOARD_PAD
BOARD_H = ROWS * CELL + 2 * BOARD_PAD

WIDTH = BOARD_W + 84
BOARD_X = (WIDTH - BOARD_W) // 2

HUD_Y = 18  # player cards
HUD_H = 64
DROP_Y = 132  # centre line of the disc waiting above the board
BOARD_Y = 178
FOOTER_Y = BOARD_Y + BOARD_H + 25
HEIGHT = BOARD_Y + BOARD_H + 50

FPS = 60


def column_x(col):
    """Pixel x of the centre of a column."""
    return BOARD_X + BOARD_PAD + col * CELL + CELL // 2


def cell_centre(row, col):
    """Pixel centre of a board cell. Row 0 is the bottom row."""
    return column_x(col), BOARD_Y + BOARD_PAD + (ROWS - 1 - row) * CELL + CELL // 2


def column_at(x):
    """The column under pixel x, or None if x is outside the grid."""
    offset = x - BOARD_X - BOARD_PAD
    if 0 <= offset < COLS * CELL:
        return int(offset // CELL)
    return None
