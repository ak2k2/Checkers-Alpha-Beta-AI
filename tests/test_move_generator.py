import os
import sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)

import unittest
from parameterized import parameterized


from game import (
    check_if_legal,
    setup_board,
    get_blank_board,
    generate_all_legal_moves,
)


class TestGenerateAllLegalMoves(unittest.TestCase):
    def setUp(self):
        self.board = get_blank_board()
        setup_board(self.board)

    def test_generate_legal_moves_for_X_from_starting_position(self):
        legal_moves = generate_all_legal_moves(self.board, "X")
        for move in legal_moves:
            self.assertTrue(check_if_legal(self.board, "X", move))
        # assert that there are 7 legal moves first moves for X
        self.assertEqual(len(legal_moves), 7)

    def test_generate_legal_moves_for_O_from_starting_position(self):
        legal_moves = generate_all_legal_moves(self.board, "O")
        for move in legal_moves:
            self.assertTrue(check_if_legal(self.board, "O", move))
        # assert that there are 7 legal first moves for O
        self.assertEqual(len(legal_moves), 7)

    def test_sparse_endgames(self):
        self.board = [
            ["X", ".", "X", ".", "X", ".", "X", "."],
            [".", "X", ".", "X", ".", "X", ".", "X"],
            ["X", ".", "X", ".", ".", ".", "X", "."],
            [".", "O", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", "O", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
        ]
        X_legal_moves = generate_all_legal_moves(self.board, "X")
        self.assertEqual(
            X_legal_moves, ["2,0->4,2", "2,2->4,0"]
        )  # X can only move to 4,2 or 4,0 since it must capture O

        O_legal_moves = generate_all_legal_moves(self.board, "O")
        self.assertEqual(
            O_legal_moves, ["5,5->4,4", "5,5->4,6"]
        )  # O can only move to 4,4 or 4,6 since the other moves are blocked by X


if __name__ == "__main__":
    unittest.main()
