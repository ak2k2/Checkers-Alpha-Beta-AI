import os
import sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

import unittest

from game import (
    setup_board,
    get_blank_board,
    setup_game,
    update_player_positions,
)


class TestBoardFunctions(unittest.TestCase):
    def test_get_blank_board(self):
        board = get_blank_board()
        self.assertEqual(len(board), 8)
        self.assertEqual(len(board[0]), 8)
        for row in board:
            for cell in row:
                self.assertEqual(cell, ".")

    def test_setup_board(self):
        board = get_blank_board()
        board = setup_board(board)

        # Check that the first three rows are filled with "X" in the right positions
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 != 0:
                    self.assertEqual(board[row][col], "X")
                else:
                    self.assertEqual(board[row][col], ".")

        # Check that the last three rows are filled with "O" in the right positions
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 != 0:
                    self.assertEqual(board[row][col], "O")
                else:
                    self.assertEqual(board[row][col], ".")

        # Check that remaining rows are empty
        for row in range(3, 5):
            for col in range(8):
                self.assertEqual(board[row][col], ".")

    def test_setup_game(self):
        board, player_positions = setup_game()
        self.assertEqual(len(board), 8)
        self.assertEqual(len(player_positions["X"]), 12)
        self.assertEqual(len(player_positions["O"]), 12)
        self.assertEqual(
            player_positions["X"],
            {
                (0, 1),  # row, col indices of X
                (0, 7),
                (1, 2),
                (2, 1),
                (2, 7),
                (0, 3),
                (1, 4),
                (2, 3),
                (0, 5),
                (1, 0),
                (1, 6),
                (2, 5),
            },
        )
        self.assertEqual(
            player_positions["O"],
            {
                (5, 0),  # row, col indices of O
                (5, 2),
                (5, 4),
                (5, 6),
                (6, 1),
                (6, 3),
                (6, 5),
                (6, 7),
                (7, 0),
                (7, 2),
                (7, 4),
                (7, 6),
            },
        )

    def test_update_player_positions(self):
        player_positions = {
            "X": {(0, 1), (0, 3), (0, 5)},
            "O": {(7, 0), (7, 2), (7, 4)},
        }
        updated_positions = update_player_positions("0,1->1,0", "X", player_positions)
        self.assertEqual(updated_positions["X"], {(0, 3), (0, 5), (1, 0)})
        updated_positions = update_player_positions("7,0->6,1", "O", updated_positions)
        self.assertEqual(updated_positions["O"], {(6, 1), (7, 2), (7, 4)})
        updated_positions = update_player_positions("6,1->7,2", "O", updated_positions)
        self.assertEqual(
            updated_positions["O"], {(7, 2), (7, 4)}
        )  # overwrote (6,1) only 2 pieces left


if __name__ == "__main__":
    unittest.main()
