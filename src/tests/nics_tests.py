import pathlib
import sys

import pytest

parent = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(parent))

from main import (
    PlayerTurn,
    bitindex_to_coords,
    convert_move_list_to_pdn,
    coords_to_bitindex,
    find_set_bits,
    generate_jump_moves,
    generate_legal_moves,
    generate_simple_moves_black,
    generate_simple_moves_white,
    get_empty_board,
    get_fresh_board,
    get_jumpers_black,
    get_jumpers_white,
    get_movers_black,
    get_movers_white,
    insert_piece,
    insert_piece_by_pdntext,
    is_set,
    print_board,
    remove_piece,
    remove_piece_by_pdntext,
)


def test_dual_capture():
    WP, BP, K = get_empty_board()

    WP = insert_piece_by_pdntext(WP, "C5")
    BP = insert_piece_by_pdntext(BP, "B4")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    print(f"White moves: {convert_move_list_to_pdn(white_moves)}")
    print(f"Black moves: {convert_move_list_to_pdn(black_moves)}")

    assert set(convert_move_list_to_pdn(white_moves)) == set(["C5->A3"])
    assert set(convert_move_list_to_pdn(black_moves)) == set(["B4->D6"])


def test_WK_capture_b():
    WP, BP, K = get_empty_board()

    WP = insert_piece_by_pdntext(WP, "C5")
    K = insert_piece_by_pdntext(K, "C5")
    BP = insert_piece_by_pdntext(BP, "D6")
    BP = insert_piece_by_pdntext(BP, "B6")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)
    print_board(WP, BP, K)
    print(f"White moves: {convert_move_list_to_pdn(white_moves)}")
    print(f"Black moves: {convert_move_list_to_pdn(black_moves)}")


# def test_path_to_BK():
#     WP, BP, K = get_empty_board()

#     WP = insert_piece_by_pdntext(WP, "C7")
#     WP = insert_piece_by_pdntext(WP, "E5")
#     WP = insert_piece_by_pdntext(WP, "G3")
#     BP = insert_piece_by_pdntext(BP, "H2")

#     white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
#     black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)
#     print_board(WP, BP, K)
#     print(f"White moves: {convert_move_list_to_pdn(white_moves)}")
#     print(f"Black moves: {convert_move_list_to_pdn(black_moves)}")


# def test_WK_path():
#     WP, BP, K = get_empty_board()

#     WP = insert_piece_by_pdntext(WP, "E5")
#     BP = insert_piece_by_pdntext(BP, "D4")
#     BP = insert_piece_by_pdntext(BP, "D2")
#     # K = insert_piece_by_pdntext(K, "D4")

#     white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
#     black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)
#     print_board(WP, BP, K)
#     print(f"White moves: {convert_move_list_to_pdn(white_moves)}")
#     print(f"Black moves: {convert_move_list_to_pdn(black_moves)}")


if __name__ == "__main__":
    test_dual_capture()
