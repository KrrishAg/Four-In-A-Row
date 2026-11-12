"""Heuristic evaluation of a board that is not yet won, lost, or drawn.

The search cannot reach the end of the game from most positions, so at
its depth limit it needs an estimate of how good the board is.
"""

from ..core import COLS, ROWS, WINDOWS, other

CENTRE_BONUS = 3
MY_THREE = 5
MY_TWO = 2
THEIR_THREE = -4
THEIR_TWO = -1


def evaluate(board, piece):
    """Score the board from `piece`'s point of view. Higher is better."""
    grid = board.grid
    opponent = other(piece)
    score = 0

    # Reward control of the centre column, which is part of the most lines.
    centre = COLS // 2
    for row in range(ROWS):
        if grid[row][centre] == piece:
            score += CENTRE_BONUS

    # Look at every group of 4 cells. A group is only useful to a player
    # if the opponent has no disc in it.
    for (r0, c0), (r1, c1), (r2, c2), (r3, c3) in WINDOWS:
        cells = (grid[r0][c0], grid[r1][c1], grid[r2][c2], grid[r3][c3])
        mine = cells.count(piece)
        theirs = cells.count(opponent)
        if mine and theirs:
            continue
        if mine == 3:
            score += MY_THREE
        elif mine == 2:
            score += MY_TWO
        elif theirs == 3:
            score += THEIR_THREE
        elif theirs == 2:
            score += THEIR_TWO
    return score
