import pathlib
import sys

import pytest

parent = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(parent))


from game import do_move, find_jumped_pos, print_board, print_legal_moves
from main import *
from util.fen_pdn_helper import *
from util.helpers import *
from util.masks import *


def test_find_jump_position():
    jloc = find_jumped_pos(2, 11)
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


if __name__ == "__main__":
    pytest.main()
    # test_do_move()
