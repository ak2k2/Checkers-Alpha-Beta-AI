import pathlib
import sys

import pytest

parent = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(parent))

from main import (
    bitindex_to_coords,
    coords_to_bitindex,
    find_set_bits,
    generate_jump_moves,
    generate_simple_moves_black,
    generate_simple_moves_white,
    get_empty_board,
    get_fresh_board,
    generate_legal_moves,
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
    convert_move_list_to_pdn,
    PlayerTurn,
)


def test_generate_legal_moves_from_start():
    WP, BP, K = get_fresh_board()
    print_board(WP, BP, K)
    white_legal_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    print(convert_move_list_to_pdn(white_legal_moves))
    black_legal_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)
    print(convert_move_list_to_pdn(black_legal_moves))
    assert convert_move_list_to_pdn(white_legal_moves) == [
        "B6->A5",
        "B6->C5",
        "D6->C5",
        "D6->E5",
        "F6->E5",
        "F6->G5",
        "H6->G5",
    ]
    assert convert_move_list_to_pdn(black_legal_moves) == [
        "A3->B4",
        "C3->D4",
        "C3->B4",
        "E3->F4",
        "E3->D4",
        "G3->H4",
        "G3->F4",
    ]


def test_tricky_capture_sequence():
    WP, BP, K = get_empty_board()

    WP = insert_piece_by_pdntext(WP, "C5")
    WP = insert_piece_by_pdntext(WP, "E7")
    WP = insert_piece_by_pdntext(WP, "A5")
    K = insert_piece_by_pdntext(K, "A5")
    BP = insert_piece_by_pdntext(BP, "D2")
    K = insert_piece_by_pdntext(K, "D2")
    WP = insert_piece_by_pdntext(WP, "F8")
    WP = insert_piece_by_pdntext(WP, "C7")

    BP = insert_piece_by_pdntext(BP, "B4")
    BP = insert_piece_by_pdntext(BP, "F6")
    BP = insert_piece_by_pdntext(BP, "F2")
    BP = insert_piece_by_pdntext(BP, "H2")
    BP = insert_piece_by_pdntext(BP, "F4")
    BP = insert_piece_by_pdntext(BP, "D4")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    print_board(WP, BP, K)
    print(f"White moves: {convert_move_list_to_pdn(white_moves)}")
    print(f"Black moves: {convert_move_list_to_pdn(black_moves)}")


def test_capture_on_weird_diagonal():
    WP, BP, K = get_empty_board()
    WP = insert_piece_by_pdntext(WP, "D6")
    BP = insert_piece_by_pdntext(BP, "C5")
    WP = insert_piece_by_pdntext(WP, "C7")
    BP = insert_piece_by_pdntext(BP, "B6")

    BP = insert_piece_by_pdntext(BP, "B2")
    WP = insert_piece_by_pdntext(WP, "C3")

    white_moves = convert_move_list_to_pdn(
        generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    )
    black_moves = convert_move_list_to_pdn(
        generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)
    )

    assert set(white_moves) == set(["C3->A1", "D6->B4", "C7->A5"])
    assert set(black_moves) == set(["B2->D4", "C5->E7", "B6->D8"])


def test_tricky_capture_sequence_two():
    WP, BP, K = get_empty_board()

    WP = insert_piece_by_pdntext(WP, "H8")
    K = insert_piece_by_pdntext(K, "H8")
    WP = insert_piece_by_pdntext(WP, "B8")

    BP = insert_piece_by_pdntext(BP, "C7")
    BP = insert_piece_by_pdntext(BP, "E7")
    BP = insert_piece_by_pdntext(BP, "G7")
    BP = insert_piece_by_pdntext(BP, "C5")
    BP = insert_piece_by_pdntext(BP, "E5")
    BP = insert_piece_by_pdntext(BP, "G5")
    BP = insert_piece_by_pdntext(BP, "C3")
    BP = insert_piece_by_pdntext(BP, "E3")
    BP = insert_piece_by_pdntext(BP, "G3")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    print_board(WP, BP, K)
    print(f"White moves: {convert_move_list_to_pdn(white_moves)}")
    print(f"Black moves: {convert_move_list_to_pdn(black_moves)}")


if __name__ == "__main__":
    # test_generate_legal_moves_from_start()
    test_capture_on_weird_diagonal()
    # test_tricky_capture_sequence()
