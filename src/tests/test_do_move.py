import pathlib
import sys
import random

import pytest

parent = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(parent))


from checkers import *
from util.fen_pdn_helper import *
from util.helpers import *
from util.masks import *


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


def test_king_once_was_on_square_was_captured_man_returns_to_square_becomes_erroneously_kinged():
    WP, BP, K = setup_board_from_position_lists(["KC3", "C5"], ["D2"])
    print_board(WP, BP, K)
    WP, BP, K = do_move(WP, BP, K, (5, 12), PlayerTurn.BLACK)
    print_board(WP, BP, K)
    WP, BP, K = do_move(WP, BP, K, (17, 13), PlayerTurn.WHITE)
    print_board(WP, BP, K)
    WP, BP, K = do_move(WP, BP, K, (12, 16), PlayerTurn.BLACK)
    print_board(WP, BP, K)
    WP, BP, K = do_move(WP, BP, K, (13, 9), PlayerTurn.WHITE)
    print_board(WP, BP, K)

    assert (WP, BP, K) == setup_board_from_position_lists(["C3"], ["A5"])


def test_oscilate_to_test_bit_errors():
    WP, BP, K = setup_board_from_position_lists(
        white_positions=["D4"], black_positions=["A1", "G1", "F2"]
    )
    print_board(WP, BP, K)
    for i in range(100):
        WP, BP, K = do_move(WP, BP, K, (6, 10), PlayerTurn.BLACK)
        WP, BP, K = do_move(WP, BP, K, (10, 6), PlayerTurn.BLACK)

    assert (WP, BP, K) == setup_board_from_position_lists(["D4"], ["A1", "G1", "F2"])


# def false_king_edge_case_simulation():  # FOUND THE ERRONEOUS KING PROMOTION
#     WP, BP, K = get_fresh_board()
#     turn = PlayerTurn.BLACK
#     game_hash = (
#         5,
#         0,
#         0,
#         4,
#         0,
#         5,
#         5,
#         4,
#         0,
#         0,
#         4,
#         0,
#         0,
#         7,
#         1,
#         4,
#         0,
#         2,
#         3,
#         0,
#         2,
#         2,
#         0,
#         0,
#         4,
#         0,
#         0,
#     )

#     i = 0
#     while i < len(game_hash):
#         if turn == PlayerTurn.BLACK:
#             legal_move_list = generate_legal_moves(WP, BP, K, turn)
#             print(f"Before move: WP={WP:032b}, BP={BP:032b}, K={K:032b}")
#             WP, BP, K = do_move(
#                 WP, BP, K, legal_move_list[game_hash[i]], PlayerTurn.BLACK
#             )
#             print(f"After move: WP={WP:032b}, BP={BP:032b}, K={K:032b}")
#             i += 1
#             turn = PlayerTurn.WHITE
#         else:
#             ai_move = AI((WP, BP, K), max_depth=7)
#             WP, BP, K = do_move(WP, BP, K, ai_move, PlayerTurn.WHITE)
#             turn = PlayerTurn.BLACK

#         print_board(WP, BP, K)


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
    pytest.main()
