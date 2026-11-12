# Four in a Row

A Python implementation of the classic Four in a Row game. Two players take
turns dropping coloured discs into a 7x6 grid, and the first to line up four
discs horizontally, vertically, or diagonally wins. The AI opponent uses the
Minimax algorithm with Alpha-Beta pruning to choose its moves.

## Running

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Controls

| Input | Action |
| --- | --- |
| Mouse click or keys `1` to `7` | Drop a disc in that column |
| `R` | Start a new round (scores are kept) |
| `M` or `Esc` | Back to the menu |

The menu lets you choose Player vs AI or Two Players, the difficulty, and who
moves first. Red always belongs to the human (or Player 1), yellow to the AI
(or Player 2).

## Project structure

```
Four_In_A_Row/
├── main.py                  entry point
├── requirements.txt
├── four_in_a_row/
│   ├── core/
│   │   └── board.py         grid, disc dropping, win and draw detection
│   ├── ai/
│   │   ├── evaluation.py    heuristic score of an unfinished board
│   │   └── minimax.py       Minimax search with Alpha-Beta pruning
│   └── ui/
│       ├── app.py           window, main loop, scene switching
│       ├── menu.py          menu screen
│       ├── game.py          game screen, animation, turn flow
│       ├── widgets.py       segmented control and button
│       ├── effects.py       confetti and menu background discs
│       ├── graphics.py      anti-aliased sprites and drawing helpers
│       ├── layout.py        window geometry
│       ├── theme.py         colours and fonts
│       └── settings.py      options chosen on the menu
├── scripts/
│   └── benchmark.py         Minimax with and without pruning
└── tests/
    ├── test_board.py        rules
    ├── test_ai.py           evaluation and search
    └── test_ui.py           drives the interface without a window
```

`core` and `ai` do not depend on Pygame, so the rules and the search can be
used and tested on their own.

## How the AI works

- **Minimax**: the AI is the maximizing player and assumes the human, the
  minimizing player, always replies with the move that is worst for the AI.
  It picks the move with the best guaranteed outcome.
- **Alpha-Beta pruning**: `alpha` is the best score the maximizer can already
  guarantee and `beta` the best the minimizer can. When `alpha >= beta`, the
  rest of the branch cannot change the result and is skipped. The chosen move
  is identical to plain Minimax.
- **Depth limit**: the search stops after a fixed number of moves. The
  difficulty levels are depths 2 (Easy), 4 (Medium), and 6 (Hard).
- **Evaluation function**: at the depth limit the board is scored by looking
  at all 69 groups of four cells. The AI's open twos and threes add to the
  score, the opponent's subtract from it, and discs in the centre column earn
  a bonus.
- **Terminal states**: a win is worth 1,000,000 plus the remaining depth, so
  the AI prefers faster wins and delays losses.
- **Move ordering**: centre columns are searched first, which makes pruning
  more effective.

## Pruning comparison

Output of `python scripts/benchmark.py` on one mid-opening position:

| Depth | Minimax nodes | Alpha-Beta nodes | Saved |
| --- | --- | --- | --- |
| 2 | 57 | 22 | 61.4% |
| 4 | 2,801 | 295 | 89.5% |
| 6 | 132,817 | 3,319 | 97.5% |

## Tests

```bash
python -m unittest
```
