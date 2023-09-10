import os
import sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

import unittest

from game import (
    setup_board,
    get_blank_board,
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


if __name__ == "__main__":
    unittest.main()
