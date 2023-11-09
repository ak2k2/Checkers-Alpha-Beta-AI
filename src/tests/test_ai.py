import itertools
import pathlib
import random
import sys

import pytest

parent = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(parent))


from checkers import *
from heuristic import wed_heuristic, wed_heuristic
from minimax_alphabeta import AI
from util.fen_pdn_helper import *
from util.helpers import *
from util.masks import *


def test_white_ai_chases_sitting_duck_with_king_for_win():
    WP, BP, K = setup_board_from_position_lists(
        white_positions=["KC3", "KA1"],
        black_positions=["KH8"],
    )

    def get_stalling_move(WP, BP, K):
        lm = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)
        if (31, 27) in lm:
            return (31, 27)
        elif (27, 31) in lm:
            return (27, 31)

    turn = PlayerTurn.BLACK

    for _ in range(10):  # AI will be WHITE
        if turn == PlayerTurn.BLACK:
            stalling_move = get_stalling_move(WP, BP, K)
            print(f"stalling move: {stalling_move}")

            WP, BP, K = do_move(
                WP, BP, K, get_stalling_move(WP, BP, K), PlayerTurn.BLACK
            )

            turn = PlayerTurn.WHITE
        else:
            ai_move = AI(
                (WP, BP, K), current_player=PlayerTurn.WHITE, max_depth=10, time_limit=5
            )[0]
            print(f"ai move: {ai_move}")
            print(f"HEURISTIC: {wed_heuristic(WP, BP, K)}")
            WP, BP, K = do_move(WP, BP, K, ai_move, PlayerTurn.WHITE)
            turn = PlayerTurn.BLACK

        print_board(
            WP, BP, K
        )  # TODO: the AI does seem to be chasing the king. we need a better endgame heuristic to make this gaurenteed.

    assert count_bits(BP) == 0


def test_black_ai_chases_sitting_duck_with_king_for_win():
    WP, BP, K = setup_board_from_position_lists(
        white_positions=["KH8"],
        black_positions=["KC3", "KA1"],
    )

    def get_stalling_move(WP, BP, K):
        lm = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
        print(lm)
        if (31, 27) in lm:
            return (31, 27)
        elif (27, 31) in lm:
            return (27, 31)

    turn = PlayerTurn.WHITE

    for _ in range(10):  # AI will be WHITE
        if generate_legal_moves(WP, BP, K, PlayerTurn.WHITE) == []:
            break
        if turn == PlayerTurn.WHITE:
            stalling_move = get_stalling_move(WP, BP, K)
            print(f"stalling move: {stalling_move}")

            WP, BP, K = do_move(
                WP, BP, K, get_stalling_move(WP, BP, K), PlayerTurn.WHITE
            )

            turn = PlayerTurn.BLACK
        else:
            ai_move = AI(
                (WP, BP, K), current_player=PlayerTurn.BLACK, max_depth=10, time_limit=5
            )[0]
            print(f"ai move: {ai_move}")
            print(f"HEURISTIC: {wed_heuristic(WP, BP, K)}")
            print(ai_move)
            WP, BP, K = do_move(WP, BP, K, ai_move, PlayerTurn.BLACK)
            turn = PlayerTurn.WHITE

        print_board(
            WP, BP, K
        )  # TODO: the AI does seem to be chasing the king. we need a better endgame heuristic to make this gaurenteed.

    assert count_bits(WP) == 0


# def test_black_ai_chases_man_on_run_with_king_for_win():
#     WP, BP, K = setup_board_from_position_lists(
#         white_positions=["KH8"],
#         black_positions=["KC3", "KA1"],
#     )

#     def get_random_move(WP, BP, K):
#         lm = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
#         return random.choice(list(lm))

#     turn = PlayerTurn.WHITE

#     for _ in range(10):  # AI will be BLACK
#         if generate_legal_moves(WP, BP, K, PlayerTurn.BLACK) == []:
#             break
#         if turn == PlayerTurn.WHITE:
#             random_move = get_random_move(WP, BP, K)
#             print(f"random move: {random_move}")

#             WP, BP, K = do_move(WP, BP, K, random_move, PlayerTurn.WHITE)

#             turn = PlayerTurn.BLACK
#         else:
#             ai_move = AI(
#                 (WP, BP, K), current_player=PlayerTurn.BLACK, max_depth=10, time_limit=5
#             )[0]
#             print(f"ai move: {ai_move}")
#             print(f"HEURISTIC: {wed_heuristic(WP, BP, K)}")
#             print(ai_move)
#             WP, BP, K = do_move(WP, BP, K, ai_move, PlayerTurn.BLACK)
#             turn = PlayerTurn.WHITE

#         print_board(WP, BP, K)

#     assert count_bits(WP) == 0


if __name__ == "__main__":
    pytest.main()
