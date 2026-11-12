import unittest

from four_in_a_row.ai import WIN_SCORE, best_move, evaluate
from four_in_a_row.core import PLAYER1, PLAYER2, ROWS, Board

from .helpers import board_from_moves


class EvaluationTests(unittest.TestCase):
    def test_empty_board_is_neutral(self):
        self.assertEqual(evaluate(Board(), PLAYER2), 0)

    def test_own_threat_scores_higher_than_opponent_threat(self):
        mine = board_from_moves([(c, PLAYER2) for c in range(3)])
        theirs = board_from_moves([(c, PLAYER1) for c in range(3)])
        self.assertGreater(evaluate(mine, PLAYER2), 0)
        self.assertLess(evaluate(theirs, PLAYER2), 0)

    def test_centre_column_is_preferred(self):
        centre = board_from_moves([(3, PLAYER2)])
        edge = board_from_moves([(0, PLAYER2)])
        self.assertGreater(evaluate(centre, PLAYER2), evaluate(edge, PLAYER2))


class SearchTests(unittest.TestCase):
    def test_takes_an_immediate_win(self):
        board = board_from_moves(
            [(0, PLAYER2), (0, PLAYER1), (1, PLAYER2), (1, PLAYER1), (2, PLAYER2), (6, PLAYER1)]
        )
        col, stats = best_move(board, 4)
        self.assertEqual(col, 3)
        self.assertGreaterEqual(stats.score, WIN_SCORE)

    def test_blocks_a_horizontal_threat(self):
        board = board_from_moves(
            [(0, PLAYER1), (0, PLAYER2), (1, PLAYER1), (6, PLAYER2), (2, PLAYER1)]
        )
        col, _ = best_move(board, 4)
        self.assertEqual(col, 3)

    def test_blocks_a_vertical_threat(self):
        board = board_from_moves(
            [(5, PLAYER1), (0, PLAYER2), (5, PLAYER1), (1, PLAYER2), (5, PLAYER1)]
        )
        col, _ = best_move(board, 4)
        self.assertEqual(col, 5)

    def test_prefers_winning_over_blocking(self):
        board = board_from_moves(
            [(0, PLAYER1), (6, PLAYER2), (0, PLAYER1), (6, PLAYER2), (0, PLAYER1), (6, PLAYER2)]
        )
        col, _ = best_move(board, 4)
        self.assertEqual(col, 6)

    def test_search_leaves_the_board_unchanged(self):
        board = board_from_moves([(3, PLAYER1), (3, PLAYER2), (2, PLAYER1)])
        before = [row[:] for row in board.grid]
        best_move(board, 4)
        self.assertEqual(board.grid, before)
        self.assertEqual(board.moves_played, 3)

    def test_pruning_gives_the_same_answer_with_fewer_nodes(self):
        board = board_from_moves(
            [(3, PLAYER1), (3, PLAYER2), (2, PLAYER1), (4, PLAYER2), (4, PLAYER1), (2, PLAYER2)]
        )
        for depth in range(1, 6):
            plain_col, plain = best_move(board, depth, use_pruning=False)
            pruned_col, pruned = best_move(board, depth, use_pruning=True)
            self.assertEqual((plain_col, plain.score), (pruned_col, pruned.score))
            self.assertLessEqual(pruned.nodes, plain.nodes)
        self.assertLess(pruned.nodes, plain.nodes / 2)

    def test_never_plays_a_full_column(self):
        board = Board()
        for i in range(ROWS):
            board.drop(3, PLAYER1 if i % 2 else PLAYER2)
        col, _ = best_move(board, 4)
        self.assertNotEqual(col, 3)
        self.assertTrue(board.is_valid_move(col))


if __name__ == "__main__":
    unittest.main()
