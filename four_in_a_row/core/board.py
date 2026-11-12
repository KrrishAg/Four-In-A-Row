"""Board representation and game rules for Four in a Row.

The grid has 7 columns and 6 rows. Row 0 is the bottom row, so a disc
dropped into a column lands on the lowest empty row of that column.
"""

ROWS = 6
COLS = 7
CONNECT = 4

EMPTY = 0
PLAYER1 = 1  # red, the human in Player vs AI mode
PLAYER2 = 2  # yellow, the AI in Player vs AI mode

# The four directions a line can run in: (row step, column step).
DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))


def _build_windows():
    """Every group of 4 cells in a line on the board (69 in total)."""
    windows = []
    for row in range(ROWS):
        for col in range(COLS):
            for d_row, d_col in DIRECTIONS:
                end_row = row + (CONNECT - 1) * d_row
                end_col = col + (CONNECT - 1) * d_col
                if 0 <= end_row < ROWS and 0 <= end_col < COLS:
                    windows.append(
                        tuple((row + i * d_row, col + i * d_col) for i in range(CONNECT))
                    )
    return tuple(windows)


WINDOWS = _build_windows()


def other(piece):
    """The opponent of the given piece."""
    return PLAYER1 if piece == PLAYER2 else PLAYER2


class Board:
    def __init__(self):
        self.grid = [[EMPTY] * COLS for _ in range(ROWS)]
        self.heights = [0] * COLS  # number of discs in each column
        self.moves_played = 0

    def copy(self):
        clone = Board()
        clone.grid = [row[:] for row in self.grid]
        clone.heights = self.heights[:]
        clone.moves_played = self.moves_played
        return clone

    def is_valid_move(self, col):
        return 0 <= col < COLS and self.heights[col] < ROWS

    def valid_moves(self):
        return [col for col in range(COLS) if self.heights[col] < ROWS]

    def drop(self, col, piece):
        """Drop a disc into a column and return the row it lands on."""
        if not self.is_valid_move(col):
            raise ValueError(f"Column {col} is not a valid move")
        row = self.heights[col]
        self.grid[row][col] = piece
        self.heights[col] += 1
        self.moves_played += 1
        return row

    def undo(self, col):
        """Remove the top disc of a column (used by the AI search)."""
        self.heights[col] -= 1
        self.grid[self.heights[col]][col] = EMPTY
        self.moves_played -= 1

    def is_full(self):
        return self.moves_played == ROWS * COLS

    def is_winning_cell(self, row, col):
        """True if the disc at (row, col) is part of a line of four or more.

        Checking only around the last move is much cheaper than scanning
        the whole board, which matters inside the AI search.
        """
        piece = self.grid[row][col]
        if piece == EMPTY:
            return False
        for d_row, d_col in DIRECTIONS:
            count = 1
            for sign in (1, -1):
                r, c = row + sign * d_row, col + sign * d_col
                while 0 <= r < ROWS and 0 <= c < COLS and self.grid[r][c] == piece:
                    count += 1
                    r += sign * d_row
                    c += sign * d_col
            if count >= CONNECT:
                return True
        return False

    def winner(self):
        """The piece that has four in a row, or EMPTY if nobody has won."""
        for window in WINDOWS:
            first = self.grid[window[0][0]][window[0][1]]
            if first != EMPTY and all(self.grid[r][c] == first for r, c in window):
                return first
        return EMPTY

    def winning_cells(self):
        """All cells that belong to a completed line of four."""
        cells = set()
        for window in WINDOWS:
            first = self.grid[window[0][0]][window[0][1]]
            if first != EMPTY and all(self.grid[r][c] == first for r, c in window):
                cells.update(window)
        return cells

    def __str__(self):
        symbols = {EMPTY: ".", PLAYER1: "X", PLAYER2: "O"}
        lines = [
            " ".join(symbols[cell] for cell in self.grid[row])
            for row in range(ROWS - 1, -1, -1)
        ]
        lines.append(" ".join(str(col + 1) for col in range(COLS)))
        return "\n".join(lines)
