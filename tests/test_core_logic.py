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
    player_has_capture,
    piece_has_capture,
)


class TestCoreLogic(unittest.TestCase):
    def setUp(self):
        self.board = get_blank_board()
        self.board = setup_board(self.board)

    def test_move_X(self):
        self.assertEqual(
            check_if_legal(self.board, "X", "2,1->3,0"), ((2, 1), (3, 0), False)
        )

    def test_move_O(self):
        self.assertEqual(
            check_if_legal(self.board, "O", "5,0->4,1"), ((5, 0), (4, 1), False)
        )

    def test_O_captures_X(self):
        self.board[2][1] = "."  # the X at 2,1 has moved -> 3,2 -> 4,1
        self.board[4][1] = "X"

        self.assertEqual(
            check_if_legal(self.board, "O", "5,0->3,2"), ((5, 0), (3, 2), True)
        )

    def test_X_captures_O(self):
        self.board[5][2] = "."  # the O at 5,2 has moved -> 4,3 -> 3,2
        self.board[3][2] = "O"

        self.assertEqual(
            check_if_legal(self.board, "X", "2,1->4,3"), ((2, 1), (4, 3), True)
        )

    def test_out_of_bounds_move(self):
        with self.assertRaises(Exception) as context:
            check_if_legal(self.board, "X", ((2, 1), (8, 3)))
        self.assertTrue("Out of bounds move." in str(context.exception))

    def test_invalid_move_not_diagonal_X(self):
        with self.assertRaises(Exception) as context:
            check_if_legal(self.board, "X", "2,1->4,1")
        self.assertTrue("Invalid move." in str(context.exception))

    def test_invalid_move_not_diagonal_O(self):
        with self.assertRaises(Exception) as context:
            check_if_legal(self.board, "O", "5,0->4,0")
        self.assertTrue("Invalid move." in str(context.exception))

    def test_invalid_move_not_1_or_2_X(self):
        opponent = "O"
        with self.assertRaises(Exception) as context:
            check_if_legal(self.board, "X", "2,1->4,3")
        self.assertTrue(
            f"There is no '{opponent}' piece to capture." in str(context.exception)
        )

    def test_invalid_move_not_1_or_2_O(self):
        opponent = "X"
        with self.assertRaises(Exception) as context:
            check_if_legal(self.board, "O", "5,0->3,2")
        self.assertTrue(
            f"There is no '{opponent}' piece to capture." in str(context.exception)
        )

    def test_invalid_move_backwards_X(self):
        self.board = get_blank_board()
        self.board[3][4] = "X"
        with self.assertRaises(Exception) as context:
            check_if_legal(self.board, "X", "3,4->2,3")
        self.assertTrue("You cannot move backwards." in str(context.exception))

    def test_invalid_move_backwards_O(self):
        self.board = get_blank_board()
        self.board[4][3] = "O"
        with self.assertRaises(Exception) as context:
            check_if_legal(self.board, "O", ((4, 3), (5, 2)))
        self.assertTrue("You cannot move backwards." in str(context.exception))

    def test_opponent_in_destination(self):
        self.board[4][1] = "O"  # Putting an O here
        with self.assertRaises(Exception) as context:
            check_if_legal(self.board, "X", "2,1->4,1")
        self.assertTrue("That space is already occupied." in str(context.exception))

    def test_move_opponent_piece(self):
        with self.assertRaises(Exception) as context:
            check_if_legal(self.board, "X", "5,0->4,1")  # 5,0 is an 'O'
        self.assertTrue("That is not your piece." in str(context.exception))

    def test_move_into_own_piece(self):
        self.board = get_blank_board()
        self.board[2][3] = "X"  # Putting an X here
        self.board[3][4] = "X"  # Putting an X here
        with self.assertRaises(Exception) as context:
            check_if_legal(self.board, "X", "2,3->3,4")

        print("\n\n\n\n\n" + str(context.exception) + "\n\n\n\n\n")
        self.assertTrue("That space is already occupied." in str(context.exception))

    # @parameterized.expand(
    #     [
    #         ((5, 4), True),  # Has a capture
    #         ((5, 6), True),  # Captures from the other side
    #     ]
    # )
    # def test_O_and_piece_have_capture(self, piece, expected):
    #     self.board[2][5] = "."
    #     self.board[4][5] = "X"
    #     self.assertTrue(player_has_capture(self.board, "O"))
    #     self.assertEqual(piece_has_capture(self.board, piece), expected)

    # @parameterized.expand(
    #     [
    #         ((2, 3), True),  # Has a capture
    #         ((2, 1), False),  # Blocked by the X on 4,3
    #     ]
    # )
    # def test_X_has_capture(self, piece, expected):
    #     self.board[5][2] = "."
    #     self.board[3][2] = "O"
    #     self.board[4][3] = "X"
    #     self.assertTrue(player_has_capture(self.board, "X"))
    #     self.assertEqual(piece_has_capture(self.board, piece), expected)

    # def test_X_has_no_capture(self):
    #     self.board[5][6] = "."
    #     self.board[3][6] = "X"
    #     player_positions = {
    #         "X": {
    #             (row, col)
    #             for row in range(8)
    #             for col in range(8)
    #             if self.board[row][col] == "X"
    #         },
    #         "O": {
    #             (row, col)
    #             for row in range(8)
    #             for col in range(8)
    #             if self.board[row][col] == "O"
    #         },
    #     }
    #     piece = (7, 7)  # this is not a piece so it should return False
    #     self.assertFalse(player_has_capture("O", player_positions))
    #     self.assertFalse(piece_has_capture(self.board, piece))

    # def test_O_has_no_capture(self):
    #     # Simulate a board state where 'O' has no capture available
    #     self.board[5][2] = "."
    #     self.board[3][2] = "O"
    #     player_positions = {
    #         "X": {
    #             (row, col)
    #             for row in range(8)
    #             for col in range(8)
    #             if self.board[row][col] == "X"
    #         },
    #         "O": {
    #             (row, col)
    #             for row in range(8)
    #             for col in range(8)
    #             if self.board[row][col] == "O"
    #         },
    #     }

    #     piece = (3, 2)  # this is a piece but it has no capture available
    #     self.assertFalse(player_has_capture("O", player_positions))

    # def test_capture_move_mandatory_for_O(self):
    #     # Simulating a board state where 'X' has a capture available
    #     self.board[2][5] = "."  # the O at 2,5 has moved -> 3,4 -> 4,5
    #     self.board[4][5] = "X"
    #     with self.assertRaises(Exception) as context:
    #         check_if_legal(self.board, "O", "5,6->4,7")  # Not capturing
    #     self.assertTrue(
    #         "Captures are mandatory when availible." in str(context.exception)
    #     )
    #     # now the capture move is made
    #     self.assertEqual(
    #         check_if_legal(self.board, "O", "5,6->3,4"), ((5, 6), (3, 4), True)
    #     )

    # def test_capture_move_mandatory_for_X(self):
    #     # Simulating a board state where 'O' has a capture available
    #     self.board[5][2] = "."
    #     self.board[3][2] = "O"
    #     with self.assertRaises(Exception) as context:
    #         check_if_legal(self.board, "X", "2,1->3,0")  # Not capturing
    #     self.assertTrue(
    #         "Captures are mandatory when availible." in str(context.exception)
    #     )
    #     # now the capture move is made
    #     self.assertEqual(
    #         check_if_legal(self.board, "X", "2,1->4,3"), ((2, 1), (4, 3), True)
    #     )


if __name__ == "__main__":
    unittest.main()
