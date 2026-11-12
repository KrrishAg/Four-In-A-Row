"""The game screen: board, discs, animation, and the turn flow."""

import math
import threading

import pygame

from ..ai import DIFFICULTY_DEPTH, best_move
from ..core import COLS, PLAYER1, PLAYER2, ROWS, Board, other
from . import layout, theme
from .effects import Confetti
from .graphics import (
    approach,
    background,
    blit_centre,
    blit_shadow,
    board_back,
    board_front,
    circle_sprite,
    disc_sprite,
    draw_text,
    halo,
    panel,
)

GRAVITY = 5200  # pixels per second squared
BOUNCE = 0.25  # fraction of speed kept after hitting the bottom
MIN_BOUNCE_SPEED = 300
MIN_THINK_TIME = 0.45  # so the AI's move never appears instantly
DISC_RADIUS = layout.RADIUS + 1  # slightly larger than the hole, so no gap shows
CARD_W = 204


class GameScene:
    def __init__(self, app, settings):
        self.app = app
        self.fonts = app.fonts
        self.vs_ai = settings.vs_ai
        self.ai_first = settings.ai_first
        self.difficulty = settings.difficulty
        self.depth = DIFFICULTY_DEPTH[settings.difficulty]

        if self.vs_ai:
            self.names = {PLAYER1: "You", PLAYER2: "AI"}
            self.subtitles = {PLAYER1: "Red", PLAYER2: self.difficulty}
        else:
            self.names = {PLAYER1: "Player 1", PLAYER2: "Player 2"}
            self.subtitles = dict(theme.PIECE_NAME)
        self.scores = {PLAYER1: 0, PLAYER2: 0}

        board_centre = (layout.WIDTH // 2, layout.BOARD_Y + layout.BOARD_H // 2)
        self.background = background(board_centre)
        self.board_back = board_back()
        self.board_front = board_front()
        self.board_rect = pygame.Rect(layout.BOARD_X, layout.BOARD_Y, layout.BOARD_W, layout.BOARD_H)

        self.time = 0.0
        self.hover_x = float(layout.WIDTH // 2)
        self.card_glow = {PLAYER1: 0.0, PLAYER2: 0.0}
        self.confetti = Confetti()
        self.search_id = 0  # identifies the current AI search; stale results are ignored
        self.new_round()

    # ----- round setup -----------------------------------------------

    def new_round(self):
        self.board = Board()
        self.turn = PLAYER2 if (self.vs_ai and self.ai_first) else PLAYER1
        self.game_over = False
        self.winner = None
        self.win_cells = set()
        self.over_time = 0.0
        self.falling = None  # the disc currently being animated
        self.last_move = None
        self.last_stats = None
        self.thinking = False
        self.ai_col = None  # the AI's chosen column, once the search has finished
        self.ai_result = None
        self.search_id += 1
        self.confetti.clear()
        if self.is_ai_turn():
            self.start_ai_search()

    def close(self):
        self.search_id += 1  # any search still running is now stale

    # ----- game flow -------------------------------------------------

    def is_ai_turn(self):
        return self.vs_ai and self.turn == PLAYER2

    def can_human_move(self):
        return not (self.game_over or self.falling or self.is_ai_turn())

    def play_move(self, col):
        """Place a disc for the current player and start its drop animation."""
        row = self.board.drop(col, self.turn)
        self.hover_x = float(layout.column_x(col))
        self.falling = {
            "row": row,
            "col": col,
            "piece": self.turn,
            "y": float(layout.DROP_Y),
            "speed": 0.0,
            "bounces": 0,
        }

    def finish_move(self, row, col):
        """Called when the falling disc comes to rest: check the result, switch turns."""
        self.last_move = (row, col)
        if self.board.is_winning_cell(row, col):
            self.game_over = True
            self.winner = self.turn
            self.win_cells = self.board.winning_cells()
            self.scores[self.winner] += 1
            if not (self.vs_ai and self.winner == PLAYER2):
                colour = theme.PIECE_COLOUR[self.winner]
                self.confetti.burst([colour, colour, theme.WHITE])
        elif self.board.is_full():
            self.game_over = True
        else:
            self.turn = other(self.turn)
            if self.is_ai_turn():
                self.start_ai_search()

    def start_ai_search(self):
        """Run the Minimax search in a background thread so the window stays responsive."""
        self.thinking = True
        self.think_started = self.time
        self.ai_col = None
        self.ai_result = None
        search_id = self.search_id
        snapshot = self.board.copy()
        depth = self.depth

        def work():
            col, stats = best_move(snapshot, depth, PLAYER2)
            self.ai_result = (search_id, col, stats)

        threading.Thread(target=work, daemon=True).start()

    # ----- events ----------------------------------------------------

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.new_round()
            elif event.key in (pygame.K_m, pygame.K_ESCAPE):
                self.app.show_menu()
            elif pygame.K_1 <= event.key <= pygame.K_7:
                self.try_human_move(event.key - pygame.K_1)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.game_over:
                self.new_round()
            else:
                self.try_human_move(layout.column_at(event.pos[0]))

    def try_human_move(self, col):
        if col is not None and self.can_human_move() and self.board.is_valid_move(col):
            self.play_move(col)

    def hovered_column(self):
        """The column the human is pointing at, if a disc can be dropped there."""
        if not self.can_human_move():
            return None
        col = layout.column_at(self.app.mouse[0])
        if col is not None and self.board.is_valid_move(col):
            return col
        return None

    # ----- update ----------------------------------------------------

    def update(self, dt):
        self.time += dt
        self.confetti.update(dt)
        if self.game_over:
            self.over_time += dt
        for piece in (PLAYER1, PLAYER2):
            active = not self.game_over and self.turn == piece
            won = self.game_over and self.winner == piece
            self.card_glow[piece] = approach(self.card_glow[piece], 1.0 if active or won else 0.0, dt, 10)

        if self.falling:
            self._update_falling(dt)
            return

        if self.thinking:
            self._update_ai(dt)
        else:
            col = self.hovered_column()
            if col is not None:
                self.hover_x = approach(self.hover_x, layout.column_x(col), dt, 22)

    def _update_falling(self, dt):
        disc = self.falling
        disc["speed"] += GRAVITY * dt
        disc["y"] += disc["speed"] * dt
        target_y = layout.cell_centre(disc["row"], disc["col"])[1]
        if disc["y"] >= target_y:
            disc["y"] = target_y
            if disc["bounces"] < 2 and disc["speed"] > MIN_BOUNCE_SPEED:
                disc["speed"] *= -BOUNCE
                disc["bounces"] += 1
            else:
                self.falling = None
                self.finish_move(disc["row"], disc["col"])

    def _update_ai(self, dt):
        if self.ai_result is not None:
            search_id, col, stats = self.ai_result
            self.ai_result = None
            if search_id == self.search_id:
                self.ai_col = col
                self.last_stats = stats

        # The waiting disc slides over to the chosen column before it drops.
        target_x = layout.column_x(self.ai_col) if self.ai_col is not None else layout.WIDTH // 2
        self.hover_x = approach(self.hover_x, target_x, dt, 12)
        ready = (
            self.ai_col is not None
            and self.time - self.think_started >= MIN_THINK_TIME
            and abs(self.hover_x - target_x) < 3
        )
        if ready:
            col, self.ai_col = self.ai_col, None
            self.thinking = False
            self.play_move(col)

    # ----- drawing ---------------------------------------------------

    def draw(self, surface):
        surface.blit(self.background, (0, 0))
        self._draw_hud(surface)
        self._draw_waiting_disc(surface)
        self._draw_board(surface)
        if self.game_over:
            self._draw_result(surface)
        self._draw_footer(surface)
        self.confetti.draw(surface)

    def _draw_board(self, surface):
        blit_shadow(surface, self.board_rect, layout.BOARD_RADIUS, blur=20, alpha=150, offset=16)
        surface.blit(self.board_back, self.board_rect)

        hovered = self.hovered_column()
        if hovered is not None:
            ghost = disc_sprite(DISC_RADIUS, theme.PIECE_COLOUR[self.turn], 56)
            blit_centre(surface, ghost, layout.cell_centre(self.board.heights[hovered], hovered))

        # Discs at rest. The falling one is drawn separately, also behind the board front.
        falling_cell = (self.falling["row"], self.falling["col"]) if self.falling else None
        dim = circle_sprite(DISC_RADIUS, (*theme.BOARD_BACK_BOTTOM, 165))
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board.grid[row][col]
                if not piece or (row, col) == falling_cell:
                    continue
                centre = layout.cell_centre(row, col)
                blit_centre(surface, disc_sprite(DISC_RADIUS, theme.PIECE_COLOUR[piece]), centre)
                if self.win_cells and (row, col) not in self.win_cells:
                    blit_centre(surface, dim, centre)

        if self.falling:
            sprite = disc_sprite(DISC_RADIUS, theme.PIECE_COLOUR[self.falling["piece"]])
            blit_centre(surface, sprite, (layout.column_x(self.falling["col"]), self.falling["y"]))

        surface.blit(self.board_front, self.board_rect)

        if hovered is not None:
            strip = panel(
                (layout.CELL - 8, ROWS * layout.CELL - 8), 22, (255, 255, 255, 26), (255, 255, 255, 4)
            )
            surface.blit(strip, (layout.column_x(hovered) - strip.get_width() // 2,
                                 layout.BOARD_Y + layout.BOARD_PAD + 4))

        if self.win_cells:
            pulse = 0.6 + 0.4 * math.sin(self.time * 5)
            glow = halo(layout.RADIUS + 2, 6, theme.WHITE, 235)
            glow.set_alpha(round(255 * pulse))
            for row, col in self.win_cells:
                blit_centre(surface, glow, layout.cell_centre(row, col))
        elif self.last_move and not self.falling:
            blit_centre(surface, circle_sprite(5, (255, 255, 255, 215)), layout.cell_centre(*self.last_move))

    def _draw_waiting_disc(self, surface):
        """The next disc, hovering above the board."""
        if self.game_over or self.falling:
            return
        if not self.is_ai_turn() and self.hovered_column() is None:
            return
        y = layout.DROP_Y + math.sin(self.time * 4) * 3
        blit_centre(surface, disc_sprite(DISC_RADIUS, theme.PIECE_COLOUR[self.turn]), (self.hover_x, y))

    def _draw_hud(self, surface):
        self._draw_card(surface, PLAYER1, layout.BOARD_X)
        self._draw_card(surface, PLAYER2, layout.WIDTH - layout.BOARD_X - CARD_W)

        if self.game_over:
            text, colour = "Round over", theme.MUTED
        elif self.is_ai_turn():
            text, colour = "Thinking" + "." * (int(self.time * 3) % 4), theme.YELLOW
        elif self.vs_ai:
            text, colour = "Your turn", theme.RED
        else:
            text, colour = f"{theme.PIECE_NAME[self.turn]}'s turn", theme.PIECE_COLOUR[self.turn]
        draw_text(surface, self.fonts.get(19), text, colour,
                  center=(layout.WIDTH // 2, layout.HUD_Y + layout.HUD_H // 2))

    def _draw_card(self, surface, piece, x):
        rect = pygame.Rect(x, layout.HUD_Y, CARD_W, layout.HUD_H)
        colour = theme.PIECE_COLOUR[piece]
        surface.blit(
            panel(rect.size, 18, (255, 255, 255, 18), (255, 255, 255, 8), (255, 255, 255, 28)), rect
        )
        glow = self.card_glow[piece]
        if glow > 0.01:
            active = panel(rect.size, 18, (*colour, 46), (*colour, 14), (*colour, 235), 2)
            active.set_alpha(round(255 * glow))
            surface.blit(active, rect)

        blit_centre(surface, disc_sprite(17, colour), (rect.x + 32, rect.centery))
        draw_text(surface, self.fonts.get(20), self.names[piece], theme.TEXT,
                  midleft=(rect.x + 60, rect.centery - 10))
        draw_text(surface, self.fonts.get(13, bold=False), self.subtitles[piece], theme.MUTED,
                  shadow=False, midleft=(rect.x + 60, rect.centery + 13))
        draw_text(surface, self.fonts.get(32), str(self.scores[piece]), theme.TEXT,
                  midright=(rect.right - 20, rect.centery))

    def _draw_result(self, surface):
        if self.winner is None:
            text, colour = "It's a draw", theme.TEXT
        elif self.vs_ai:
            text = "You win!" if self.winner == PLAYER1 else "AI wins"
            colour = theme.PIECE_COLOUR[self.winner]
        else:
            text, colour = f"{self.names[self.winner]} wins!", theme.PIECE_COLOUR[self.winner]

        appear = min(1.0, self.over_time / 0.35)
        alpha = round(255 * appear)
        rise = round(10 * (1 - appear) ** 2)
        centre_x = layout.WIDTH // 2
        draw_text(surface, self.fonts.get(40), text, colour, alpha=alpha,
                  center=(centre_x, layout.DROP_Y - 12 + rise))
        draw_text(surface, self.fonts.get(15, bold=False), "Click or press R to play again",
                  theme.MUTED, shadow=False, alpha=alpha, center=(centre_x, layout.DROP_Y + 24 + rise))

    def _draw_footer(self, surface):
        font = self.fonts.get(14, bold=False)
        if self.vs_ai and self.last_stats:
            s = self.last_stats
            stats = f"AI searched {s.nodes:,} positions in {s.seconds:.2f}s at depth {s.depth}"
            draw_text(surface, font, stats, theme.MUTED, shadow=False,
                      midleft=(layout.BOARD_X + 6, layout.FOOTER_Y))
        draw_text(surface, font, "R restart    M menu", theme.FAINT, shadow=False,
                  midright=(layout.WIDTH - layout.BOARD_X - 6, layout.FOOTER_Y))
