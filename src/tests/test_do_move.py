import pathlib
import sys
import random

import pytest

parent = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(parent))


from game import do_move, find_jumped_pos, print_board, print_legal_moves
from main import *
from util.fen_pdn_helper import *
from util.helpers import *
from util.masks import *
from minimax_alphabeta import AI


def test_find_jump_position():
    jloc = find_jumped_pos(16, 9)
    assert jloc == 12
    jloc = find_jumped_pos(8, 1)
    assert jloc == 4
    jloc = find_jumped_pos(2, 11)
    assert jloc == 6
    jloc = find_jumped_pos(2, 9)
    assert jloc == 5
    jloc = find_jumped_pos(9, 2)
    assert jloc == 5
    jloc = find_jumped_pos(3, 10)
    assert jloc == 6
    jloc = find_jumped_pos(10, 3)
    assert jloc == 6
    jloc = find_jumped_pos(6, 15)
    assert jloc == 11
    jloc = find_jumped_pos(1, 10)
    assert jloc == 5
    jloc = find_jumped_pos(5, 14)
    assert jloc == 10
    jloc = find_jumped_pos(10, 19)
    assert jloc == 14
    jloc = find_jumped_pos(0, 9)
    assert jloc == 4
    jloc = find_jumped_pos(4, 13)
    assert jloc == 9
    jloc = find_jumped_pos(9, 18)
    assert jloc == 13
    jloc = find_jumped_pos(13, 22)
    assert jloc == 18
    jloc = find_jumped_pos(18, 27)
    assert jloc == 22
    jloc = find_jumped_pos(22, 31)
    assert jloc == 27
    jloc = find_jumped_pos(8, 17)
    assert jloc == 12
    jloc = find_jumped_pos(12, 21)
    assert jloc == 17
    jloc = find_jumped_pos(17, 26)
    assert jloc == 21
    jloc = find_jumped_pos(21, 30)
    assert jloc == 26
    jloc = find_jumped_pos(16, 25)
    assert jloc == 20
    jloc = find_jumped_pos(20, 29)
    assert jloc == 25


# def test_do_move():
#     WP, BP, K = setup_board_from_position_lists(
#         white_positions=["KA1", "E5"], black_positions=["B2", "KF2"]
#     )
#     print_board(WP, BP, K)
#     legal_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
#     print_legal_moves(legal_moves)
#     selected_move = legal_moves[
#         0
#     ]  # which move to choose from legal moves list by index.
#     move = choose_move(selected_move)
#     print(f"Move Chosen: {move}")

#     for m in move:
#         WP, BP, K = do_move(WP, BP, K, m, PlayerTurn.WHITE)
#         print_board(WP, BP, K)


def test_position_jumping_manually():
    WP, BP, K = setup_board_from_position_lists(
        white_positions=["F6", "F4", "D2"], black_positions=["C1"]
    )
    WP, BP, K = do_move(WP, BP, K, (1, 10), PlayerTurn.BLACK)
    assert (WP, BP, K) == setup_board_from_position_lists(["F6", "F4"], ["E3"])
    WP, BP, K = do_move(WP, BP, K, (10, 19), PlayerTurn.BLACK)
    assert (WP, BP, K) == setup_board_from_position_lists(["F6"], ["G5"])
    WP, BP, K = do_move(WP, BP, K, (19, 26), PlayerTurn.BLACK)
    assert (WP, BP, K) == setup_board_from_position_lists([], ["E7"])


def test_position_jumping_in_sequence():
    WP, BP, K = setup_board_from_position_lists(
        white_positions=["F6", "F4", "D2"], black_positions=["C1"]
    )
    WP, BP, K = do_move(WP, BP, K, (1, 10, 19, 26), PlayerTurn.BLACK)
    assert (WP, BP, K) == setup_board_from_position_lists([], ["E7"])


def test_black_becoming_king():
    WP, BP, K = setup_board_from_position_lists(
        white_positions=["E3", "E5", "E7"], black_positions=["C1", "D2"]
    )
    only_legal_move = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)[
        0
    ]  # [5, 14, 21, 30]
    WP, BP, K = do_move(WP, BP, K, only_legal_move, PlayerTurn.BLACK)

    assert (WP, BP, K) == setup_board_from_position_lists([], ["C1", "KF8"])


def test_white_becoming_king():
    WP, BP, K = setup_board_from_position_lists(
        white_positions=["E5"], black_positions=["F4", "F2"]
    )
    only_legal_move = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)[
        0
    ]  # [5, 14, 21, 30]

    WP, BP, K = do_move(WP, BP, K, only_legal_move, PlayerTurn.WHITE)

    assert (WP, BP, K) == setup_board_from_position_lists(["KE1"], [])


# def oscilate_to_test_bit_errors():
#     WP, BP, K = setup_board_from_position_lists(
#         white_positions=["D4"], black_positions=["A1", "G1", "F2"]
#     )
#     print_board(WP, BP, K)
#     for i in range(10):
#         WP, BP, K = do_move(WP, BP, K, (6, 10), PlayerTurn.BLACK)
#         WP, BP, K = do_move(WP, BP, K, (10, 6), PlayerTurn.BLACK)
#     print_board(WP, BP, K)


# def test_white_becoming_king():
#     WP, BP, K = test_setup_board_from_position_lists(white_positions=["E5"],black_positions=["F4","F2"])
#     print_board(WP, BP, K)
#     white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
#     black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

#     white_move = do_move(WP,BP,K,white_move,"white")
#     black_move = do_move(WP,BP,K,black_move,"black")

#     print_board(WP, BP, K)
#     # Expected positions: white king at e1 black: d6


# def test_white_king_jumping():
#     WP, BP, K = test_setup_board_from_position_lists(white_positions=["KE5"],black_positions=["D6"])
#     print_board(WP, BP, K)
#     white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
#     black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

#     white_move = do_move(WP,BP,K,white_move,"white")
#     black_move = do_move(WP,BP,K,black_move,"black")

#     print_board(WP, BP, K)
#     # Expected positions: white king at c7 or b at f4


# def test_black_king_jumping():
#     WP, BP, K = test_setup_board_from_position_lists(white_positions=["C5","E3"],black_positions=["KB6"])
#     print_board(WP, BP, K)
#     white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
#     black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

#     white_move = do_move(WP,BP,K,white_move,"white")
#     black_move = do_move(WP,BP,K,black_move,"black")

#     print_board(WP, BP, K)
#     # Expected positions: black king at f2, if white goes first then: C5->D4 or B4, E3-> D2 or F2


if __name__ == "__main__":
    # pytest.main()
    # nics_edge_case()
    # test_do_move()
    pytest.main()
