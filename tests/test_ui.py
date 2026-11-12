"""Drives the real interface without opening a window."""

import os
import time
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

try:
    import pygame
except ImportError:  # the rules and AI tests still run without pygame
    pygame = None

if pygame:
    from four_in_a_row.core import PLAYER1, PLAYER2
    from four_in_a_row.ui import App, layout
    from four_in_a_row.ui.game import GameScene
    from four_in_a_row.ui.menu import MenuScene


@unittest.skipIf(pygame is None, "pygame is not installed")
class UITests(unittest.TestCase):
    def setUp(self):
        self.app = App()

    def tearDown(self):
        self.app.scene.close()
        pygame.quit()

    def click(self, pos):
        self.app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))

    def key(self, key):
        self.app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))

    def settle(self):
        """Advance frames until no disc is falling and the AI is not thinking."""
        deadline = time.time() + 20
        while time.time() < deadline:
            self.app.update(1 / 60)
            self.app.draw()
            scene = self.app.scene
            if not scene.falling and not scene.thinking:
                return
            time.sleep(0.001)
        self.fail("the game did not settle")

    def test_menu_starts_a_game_against_the_ai(self):
        self.assertIsInstance(self.app.scene, MenuScene)
        self.app.update(1 / 60)
        self.app.draw()
        menu = self.app.scene
        self.click(menu.difficulty.segment_rect(2).center)
        self.click(menu.start.rect.center)
        game = self.app.scene
        self.assertIsInstance(game, GameScene)
        self.assertTrue(game.vs_ai)
        self.assertEqual(game.depth, 6)

    def test_full_game_against_the_ai(self):
        self.key(pygame.K_RETURN)
        game = self.app.scene
        human_moves = 0
        while not game.game_over:
            self.assertEqual(game.turn, PLAYER1)
            col = game.board.valid_moves()[0]
            self.click((layout.column_x(col), 400))
            self.assertIsNotNone(game.falling)
            self.click((layout.column_x(col), 400))  # ignored while the disc is falling
            human_moves += 1
            self.settle()
        # The human only ever plays the leftmost open column, so the AI wins.
        self.assertEqual(game.winner, PLAYER2)
        self.assertEqual(game.scores[PLAYER2], 1)
        self.assertEqual(len(game.win_cells), 4)
        self.assertIn(game.board.moves_played, (2 * human_moves, 2 * human_moves - 1))

    def test_ai_can_move_first(self):
        menu = self.app.scene
        self.click(menu.first.segment_rect(1).center)
        self.key(pygame.K_RETURN)
        self.settle()
        game = self.app.scene
        self.assertEqual(game.board.moves_played, 1)
        self.assertEqual(game.turn, PLAYER1)

    def test_two_player_round_and_restart(self):
        menu = self.app.scene
        self.click(menu.mode.segment_rect(1).center)
        self.key(pygame.K_RETURN)
        game = self.app.scene
        self.assertFalse(game.vs_ai)
        for key in [pygame.K_1, pygame.K_2] * 3 + [pygame.K_1]:
            self.key(key)
            self.settle()
        self.assertTrue(game.game_over)
        self.assertEqual(game.winner, PLAYER1)

        self.key(pygame.K_r)
        self.assertFalse(game.game_over)
        self.assertEqual(game.board.moves_played, 0)
        self.assertEqual(game.scores[PLAYER1], 1)  # the score carries over

    def test_click_outside_the_columns_is_ignored(self):
        self.key(pygame.K_RETURN)
        game = self.app.scene
        self.click((4, 400))
        self.assertIsNone(game.falling)
        self.assertEqual(game.board.moves_played, 0)

    def test_escape_returns_to_the_menu_and_keeps_settings(self):
        menu = self.app.scene
        self.click(menu.difficulty.segment_rect(0).center)
        self.key(pygame.K_RETURN)
        self.key(pygame.K_ESCAPE)
        self.assertIsInstance(self.app.scene, MenuScene)
        self.assertEqual(self.app.scene.difficulty.value, "Easy")


if __name__ == "__main__":
    unittest.main()
