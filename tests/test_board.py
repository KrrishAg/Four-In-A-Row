import unittest

from four_in_a_row.core import COLS, EMPTY, PLAYER1, PLAYER2, ROWS, WINDOWS, Board

from .helpers import board_from_moves


class BoardTests(unittest.TestCase):
    def test_window_count(self):
        # 24 horizontal + 21 vertical + 12 + 12 diagonal
        self.assertEqual(len(WINDOWS), 69)

    def test_discs_stack_from_the_bottom(self):
        board = Board()
        self.assertEqual(board.drop(3, PLAYER1), 0)
        self.assertEqual(board.drop(3, PLAYER2), 1)
        self.assertEqual(board.grid[0][3], PLAYER1)
        self.assertEqual(board.grid[1][3], PLAYER2)

    def test_full_column_is_rejected(self):
        board = Board()
        for i in range(ROWS):
            board.drop(0, PLAYER1 if i % 2 else PLAYER2)
        self.assertFalse(board.is_valid_move(0))
        self.assertNotIn(0, board.valid_moves())
        with self.assertRaises(ValueError):
            board.drop(0, PLAYER1)

    def test_undo_restores_the_board(self):
        board = Board()
        board.drop(2, PLAYER1)
        board.undo(2)
        self.assertEqual(board.grid[0][2], EMPTY)
        self.assertEqual(board.moves_played, 0)

    def test_copy_is_independent(self):
        board = board_from_moves([(3, PLAYER1)])
        clone = board.copy()
        clone.drop(3, PLAYER2)
        self.assertEqual(board.moves_played, 1)
        self.assertEqual(board.grid[1][3], EMPTY)

    def test_horizontal_win(self):
        board = board_from_moves([(c, PLAYER1) for c in range(4)])
        self.assertEqual(board.winner(), PLAYER1)
        self.assertTrue(board.is_winning_cell(0, 3))
        self.assertEqual(board.winning_cells(), {(0, 0), (0, 1), (0, 2), (0, 3)})

    def test_vertical_win(self):
        board = board_from_moves([(5, PLAYER2)] * 4)
        self.assertEqual(board.winner(), PLAYER2)
        self.assertTrue(board.is_winning_cell(3, 5))

    def test_rising_diagonal_win(self):
        board = Board()
        for col in range(4):
            for _ in range(col):
                board.drop(col, PLAYER2)
            board.drop(col, PLAYER1)
        self.assertEqual(board.winner(), PLAYER1)
        self.assertTrue(board.is_winning_cell(3, 3))

    def test_falling_diagonal_win(self):
        board = Board()
        for col in range(4):
            for _ in range(3 - col):
                board.drop(col, PLAYER2)
            board.drop(col, PLAYER1)
        self.assertEqual(board.winner(), PLAYER1)
        self.assertTrue(board.is_winning_cell(3, 0))

    def test_three_in_a_row_is_not_a_win(self):
        board = board_from_moves([(c, PLAYER1) for c in range(3)])
        self.assertEqual(board.winner(), EMPTY)
        self.assertFalse(board.is_winning_cell(0, 2))

    def test_full_board_with_no_winner_is_a_draw(self):
        # Columns filled in a pattern that never lines up four.
        board = Board()
        pattern = [PLAYER1, PLAYER1, PLAYER2, PLAYER2]
        for col in range(COLS):
            for row in range(ROWS):
                board.drop(col, pattern[(row + 2 * (col % 2)) % 4])
        self.assertTrue(board.is_full())
        self.assertEqual(board.winner(), EMPTY)
        self.assertEqual(board.valid_moves(), [])


if __name__ == "__main__":
    unittest.main()
