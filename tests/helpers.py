from four_in_a_row.core import Board


def board_from_moves(moves):
    """Play a list of (column, piece) moves onto a new board."""
    board = Board()
    for col, piece in moves:
        board.drop(col, piece)
    return board
