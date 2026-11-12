"""AI opponent: Minimax search with Alpha-Beta pruning."""

from .evaluation import evaluate
from .minimax import DIFFICULTY_DEPTH, WIN_SCORE, SearchStats, best_move

__all__ = ["DIFFICULTY_DEPTH", "WIN_SCORE", "SearchStats", "best_move", "evaluate"]
