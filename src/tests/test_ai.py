import pathlib
import sys
import random

import pytest

parent = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(parent))


from game import print_legal_moves
from checkers import *
from util.fen_pdn_helper import *
from util.helpers import *
from util.masks import *
from minimax_alphabeta import AI
from heuristic import basic_heuristic


def ai_vs_random_test_chases_with_king():
    WP, BP, K = setup_board_from_position_lists(
        white_positions=["KC3", "KA1"],
        black_positions=["KH8", "D8"],
    )

    def get_stalling_move(WP, BP, K):
        if (31, 27) in generate_legal_moves(WP, BP, K, PlayerTurn.BLACK):
            return (31, 27)
        elif (27, 31) in generate_legal_moves(WP, BP, K, PlayerTurn.BLACK):
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
            ai_move = AI((WP, BP, K), max_depth=7)
            print(f"ai move: {ai_move}")
            print(f"HEURISTIC: {basic_heuristic(WP, BP, K)}")
            WP, BP, K = do_move(WP, BP, K, ai_move, PlayerTurn.WHITE)
            turn = PlayerTurn.BLACK

        print_board(
            WP, BP, K
        )  # TODO: the AI does seem to be chasing the king. we need a endgame heuristic to make it win.


ai_vs_random_test_chases_with_king()
