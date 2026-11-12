"""Compare plain Minimax with Minimax + Alpha-Beta pruning.

Run from the project folder with:  python scripts/benchmark.py

Both searches return the same move and score. Pruning only changes how
many positions have to be examined to find it.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from four_in_a_row.ai import best_move  # noqa: E402
from four_in_a_row.core import PLAYER2, Board, other  # noqa: E402

# A short opening so the position is not symmetrical. Player 1 moves first.
OPENING = [3, 3, 2, 4, 4, 2]
MAX_DEPTH = 6


def main():
    board = Board()
    piece = other(PLAYER2)
    for col in OPENING:
        board.drop(col, piece)
        piece = other(piece)

    print("Position (X = player, O = AI, AI to move):\n")
    print(board)
    print()
    header = (
        f"{'Depth':>5} | {'Minimax nodes':>14} {'time':>8} | "
        f"{'Alpha-Beta nodes':>16} {'time':>8} | {'Saved':>6} | Move"
    )
    print(header)
    print("-" * len(header))

    for depth in range(1, MAX_DEPTH + 1):
        plain_col, plain = best_move(board, depth, PLAYER2, use_pruning=False)
        pruned_col, pruned = best_move(board, depth, PLAYER2, use_pruning=True)
        assert (plain_col, plain.score) == (pruned_col, pruned.score)
        saved = 100 * (1 - pruned.nodes / plain.nodes)
        print(
            f"{depth:>5} | {plain.nodes:>14,} {plain.seconds:>7.2f}s | "
            f"{pruned.nodes:>16,} {pruned.seconds:>7.2f}s | {saved:>5.1f}% | column {pruned_col + 1}"
        )


if __name__ == "__main__":
    main()
