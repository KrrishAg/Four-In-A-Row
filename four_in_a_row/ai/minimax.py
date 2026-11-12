"""Minimax search with Alpha-Beta pruning.

The AI is the maximizing player and assumes the opponent (the minimizing
player) always replies with the move that is worst for the AI. The full
game tree is far too large to search, so the search stops at a fixed
depth and scores the board there with the heuristic evaluation.
"""

import math
import time
from dataclasses import dataclass

from ..core import COLS, PLAYER2, ROWS, other
from .evaluation import evaluate

WIN_SCORE = 1_000_000

# Centre columns are part of more possible lines, so they are searched
# first. Good moves found early make Alpha-Beta prune more branches.
MOVE_ORDER = sorted(range(COLS), key=lambda col: abs(col - COLS // 2))

DIFFICULTY_DEPTH = {"Easy": 2, "Medium": 4, "Hard": 6}


@dataclass
class SearchStats:
    nodes: int = 0  # positions examined
    seconds: float = 0.0
    score: float = 0.0  # minimax value of the chosen move
    depth: int = 0


class Searcher:
    def __init__(self, board, ai_piece, use_pruning=True):
        self.board = board
        self.ai_piece = ai_piece
        self.human_piece = other(ai_piece)
        self.use_pruning = use_pruning
        self.nodes = 0

    def minimax(self, depth, alpha, beta, maximizing):
        """Return (best column, score) for the player to move."""
        self.nodes += 1
        board = self.board

        if board.is_full():
            return None, 0
        if depth == 0:
            return None, evaluate(board, self.ai_piece)

        piece = self.ai_piece if maximizing else self.human_piece
        best_col = None
        best_score = -math.inf if maximizing else math.inf

        for col in MOVE_ORDER:
            if board.heights[col] >= ROWS:
                continue
            row = board.drop(col, piece)
            if board.is_winning_cell(row, col):
                # Terminal state. Adding the remaining depth makes the AI
                # prefer quicker wins and put off losses as long as it can.
                self.nodes += 1
                score = WIN_SCORE + depth if maximizing else -(WIN_SCORE + depth)
            else:
                _, score = self.minimax(depth - 1, alpha, beta, not maximizing)
            board.undo(col)

            if maximizing:
                if score > best_score:
                    best_col, best_score = col, score
                alpha = max(alpha, best_score)
            else:
                if score < best_score:
                    best_col, best_score = col, score
                beta = min(beta, best_score)

            # Alpha-Beta cut-off: the other player already has a better
            # option elsewhere, so the rest of this branch cannot matter.
            if self.use_pruning and alpha >= beta:
                break

        return best_col, best_score


def best_move(board, depth, ai_piece=PLAYER2, use_pruning=True):
    """Choose a column for `ai_piece`. Returns (column, SearchStats).

    The board is searched in place (moves are made and undone), so it is
    left unchanged when the function returns.
    """
    searcher = Searcher(board, ai_piece, use_pruning)
    start = time.perf_counter()
    col, score = searcher.minimax(depth, -math.inf, math.inf, True)
    stats = SearchStats(
        nodes=searcher.nodes,
        seconds=time.perf_counter() - start,
        score=score,
        depth=depth,
    )
    return col, stats
