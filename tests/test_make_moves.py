import os
import sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

import unittest
from parameterized import parameterized


from game import (
    make_move,
    do_move,
)


class TestMakeMoveAndDoMove(unittest.TestCase):
    def setUp(self):
        self.board = [["." * 8 for _ in range(8)] for _ in range(8)] # blank board
        self.board[2][2] = "X"
        self.board[4][4] = "O"

    def test_make_move_for_X(self):
        make_move(2, 2, 3, 3, self.board, "X")
        self.assertEqual(self.board[2][2], ".")
        self.assertEqual(self.board[3][3], "X")

    def test_make_move_for_O(self):
        make_move(4, 4, 3, 3, self.board, "O")
        self.assertEqual(self.board[4][4], ".")
        self.assertEqual(self.board[3][3], "O")

    def test_ignore_collision_and_overwrite(self):
        make_move(2, 2, 3, 3, self.board, "X")
        make_move(4, 4, 3, 3, self.board, "O")
        self.assertEqual(self.board[3][3], "O") # O overwrites X
        self.assertEqual(self.board[2][2], ".") # X was removed from its original position
        self.assertEqual(self.board[4][4], ".") # O was removed from its original position as well

    def test_do_move_for_X(self):
        do_move(self.board, "2,2->3,3", "X")
        self.assertEqual(self.board[2][2], ".")
        self.assertEqual(self.board[3][3], "X")

    def test_do_move_for_O(self):
        do_move(self.board, "4,4->3,3", "O")
        self.assertEqual(self.board[4][4], ".")
        self.assertEqual(self.board[3][3], "O")


if __name__ == "__main__":
    unittest.main()
