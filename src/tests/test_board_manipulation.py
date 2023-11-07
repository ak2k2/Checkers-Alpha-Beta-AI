import pathlib
import sys

import pytest

parent = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(parent))

from checkers import (
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


def test_generate_legal_moves_from_start():
    WP, BP, K = get_fresh_board()
    white_legal_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_legal_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

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


def test_capture_on_weird_diagonal():
    WP, BP, K = get_empty_board()
    WP = insert_piece_by_pdntext(WP, "D6")
    BP = insert_piece_by_pdntext(BP, "C5")
    WP = insert_piece_by_pdntext(WP, "C7")
    BP = insert_piece_by_pdntext(BP, "B6")

    BP = insert_piece_by_pdntext(BP, "B2")
    WP = insert_piece_by_pdntext(WP, "C3")

    print_board(WP, BP, K)

    white_moves = convert_move_list_to_pdn(
        generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    )
    black_moves = convert_move_list_to_pdn(
        generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)
    )

    assert set(white_moves) == set(["C3->A1", "D6->B4", "C7->A5"])
    assert set(black_moves) == set(["B2->D4", "C5->E7", "B6->D8"])


def test_captures_becomes_king_can_no_longer_capture():
    WP, BP, K = get_empty_board()
    BP = insert_piece_by_pdntext(BP, "B6")
    WP = insert_piece_by_pdntext(WP, "C7")
    # WP on E7 can not be captured since black becomes a king
    WP = insert_piece_by_pdntext(WP, "E7")

    black_moves = convert_move_list_to_pdn(
        generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)
    )

    assert set(black_moves) == set(["B6->D8"])

    WP, BP, K = get_empty_board()
    BP = insert_piece_by_pdntext(BP, "B6")
    K = insert_piece_by_pdntext(K, "B6")
    WP = insert_piece_by_pdntext(WP, "C7")
    # WP on E7 can not be captured since black becomes a king
    WP = insert_piece_by_pdntext(WP, "E7")

    black_moves = convert_move_list_to_pdn(
        generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)
    )

    assert set(black_moves) == set(
        ["B6->D8->F6"]
    )  # WP on E7 now CAN be captured since BP is a king


def test_king_cyclical_capture_weird_diagonal():
    WP, BP, K = get_empty_board()
    BP = insert_piece_by_pdntext(BP, "B6")
    K = insert_piece_by_pdntext(K, "B6")
    WP = insert_piece_by_pdntext(WP, "C7")
    WP = insert_piece_by_pdntext(WP, "C5")
    # should not be captured as black becomes a king
    WP = insert_piece_by_pdntext(WP, "E7")

    black_moves = convert_move_list_to_pdn(
        generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)
    )

    assert set(black_moves) == set(["B6->D8->F6", "B6->D4"])


def test_dual_capture():
    WP, BP, K = get_empty_board()

    WP = insert_piece_by_pdntext(WP, "C5")
    BP = insert_piece_by_pdntext(BP, "B4")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

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

    assert set(convert_move_list_to_pdn(white_moves)) == set(["C5->E7", "C5->A7"])
    assert set(convert_move_list_to_pdn(black_moves)) == set(
        ["B6->C7", "B6->A7", "D6->E7", "D6->C7"]
    )


def test_path_to_BK():
    WP, BP, K = get_empty_board()

    WP = insert_piece_by_pdntext(WP, "C7")
    WP = insert_piece_by_pdntext(WP, "E5")
    WP = insert_piece_by_pdntext(WP, "G3")
    BP = insert_piece_by_pdntext(BP, "H2")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    assert set(convert_move_list_to_pdn(white_moves)) == set(
        ["G3->F2", "E5->D4", "E5->F4", "C7->B6", "C7->D6"]
    )
    assert set(convert_move_list_to_pdn(black_moves)) == set(["H2->F4->D6->B8"])


def test_WK_path():
    WP, BP, K = get_empty_board()

    WP = insert_piece_by_pdntext(WP, "E5")
    BP = insert_piece_by_pdntext(BP, "D4")
    BP = insert_piece_by_pdntext(BP, "D2")
    K = insert_piece_by_pdntext(K, "D4")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    assert set(convert_move_list_to_pdn(white_moves)) == set(["E5->C3->E1"])
    assert set(convert_move_list_to_pdn(black_moves)) == set(["D4->F6"])


def test_WK_path_already_king():
    WP, BP, K = get_empty_board()

    WP = insert_piece_by_pdntext(WP, "E5")
    K = insert_piece_by_pdntext(K, "E5")
    BP = insert_piece_by_pdntext(BP, "D4")
    BP = insert_piece_by_pdntext(BP, "D2")
    BP = insert_piece_by_pdntext(BP, "F2")
    K = insert_piece_by_pdntext(K, "D4")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    assert set(convert_move_list_to_pdn(white_moves)) == set(["E5->C3->E1->G3"])
    assert set(convert_move_list_to_pdn(black_moves)) == set(["D4->F6"])


def test_white_king_takes_many_rounds():  # TODO: validate this again
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

    assert set(convert_move_list_to_pdn(white_moves)) == set(
        [
            "A5->C3->E1->G3->E5->C3",
            "A5->C3->E1->G3->E5->G7",
            "A5->C3->E5->G3->E1->C3",
            "A5->C3->E5->G7",
            "C5->E3->G1",
            "C5->E3->C1",
            "C5->A3",
            "E7->G5->E3->G1",
            "E7->G5->E3->C1",
        ]
    )

    assert set(convert_move_list_to_pdn(black_moves)) == set(
        ["B4->D6->B8", "D4->B6->D8", "F6->D8"]
    )


def test_grid_capture_puzzle():
    WP, BP, K = get_empty_board()

    WP = insert_piece_by_pdntext(WP, "H8")
    K = insert_piece_by_pdntext(K, "H8")
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

    assert set(convert_move_list_to_pdn(white_moves)) == set(
        [
            "H8->F6->H4->F2->D4->B2",
            "H8->F6->H4->F2->D4->F6->D8->B6->D4->B2",
            "H8->F6->H4->F2->D4->B6->D8->F6->D4->B2",
            "H8->F6->D4->F2->H4->F6->D8->B6->D4->B2",
            "H8->F6->D4->B2",
            "H8->F6->D4->B6->D8->F6->H4->F2->D4->B2",
            "H8->F6->D8->B6->D4->F2->H4->F6->D4->B2",
            "H8->F6->D8->B6->D4->B2",
            "H8->F6->D8->B6->D4->F6->H4->F2->D4->B2",
        ]
    )

    assert set(convert_move_list_to_pdn(black_moves)) == set(
        [
            "C3->D4",
            "C3->B4",
            "E3->F4",
            "E3->D4",
            "G3->H4",
            "G3->F4",
            "C5->D6",
            "C5->B6",
            "E5->F6",
            "E5->D6",
            "G5->H6",
            "G5->F6",
            "C7->D8",
            "C7->B8",
            "E7->F8",
            "E7->D8",
            "G7->F8",
        ]
    )


def test_black_piece_thinks_it_can_move_into_corner():
    WP, BP, K = get_empty_board()
    WP = insert_piece_by_pdntext(WP, "B8")
    BP = insert_piece_by_pdntext(BP, "C7")
    BP = insert_piece_by_pdntext(BP, "E5")
    K = insert_piece_by_pdntext(K, "E5")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    assert set(convert_move_list_to_pdn(white_moves)) == set(["B8->D6->F4"])
    assert set(convert_move_list_to_pdn(black_moves)) == set(
        ["E5->F6", "E5->D6", "E5->D4", "E5->F4", "C7->D8"]
    )


def test_white_piece_bottom():
    WP, BP, K = get_empty_board()

    BP = insert_piece_by_pdntext(BP, "C1")
    BP = insert_piece_by_pdntext(BP, "E1")
    WP = insert_piece_by_pdntext(WP, "D2")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    assert set(convert_move_list_to_pdn(white_moves)) == set([])
    assert set(convert_move_list_to_pdn(black_moves)) == set(["C1->E3", "E1->C3"])


def test_white_piece_upper_half():
    WP, BP, K = get_empty_board()

    BP = insert_piece_by_pdntext(BP, "C7")
    WP = insert_piece_by_pdntext(WP, "D8")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    assert set(convert_move_list_to_pdn(white_moves)) == set(["D8->B6"])
    assert set(convert_move_list_to_pdn(black_moves)) == set(["C7->B8"])


def test_white_piece_upper_half_switch():  ## BROKE
    WP, BP, K = get_empty_board()

    BP = insert_piece_by_pdntext(BP, "E7")
    WP = insert_piece_by_pdntext(WP, "D8")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    assert set(convert_move_list_to_pdn(white_moves)) == set(["D8->F6"])
    assert set(convert_move_list_to_pdn(black_moves)) == set(["E7->F8"])


def test_black_piece_upper_half():
    WP, BP, K = get_empty_board()

    BP = insert_piece_by_pdntext(BP, "D8")
    WP = insert_piece_by_pdntext(WP, "C7")
    K = insert_piece_by_pdntext(K, "D8")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    assert set(convert_move_list_to_pdn(white_moves)) == set(["C7->B6", "C7->D6"])
    assert set(convert_move_list_to_pdn(black_moves)) == set(["D8->B6"])


def test_white_piece_left():
    WP, BP, K = get_empty_board()

    BP = insert_piece_by_pdntext(BP, "B4")
    WP = insert_piece_by_pdntext(WP, "A5")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    assert set(convert_move_list_to_pdn(white_moves)) == set(["A5->C3"])
    assert set(convert_move_list_to_pdn(black_moves)) == set(["B4->C5"])


def test_white_piece_right():
    WP, BP, K = get_empty_board()

    BP = insert_piece_by_pdntext(BP, "G5")
    WP = insert_piece_by_pdntext(WP, "H6")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    assert set(convert_move_list_to_pdn(white_moves)) == set(["H6->F4"])
    assert set(convert_move_list_to_pdn(black_moves)) == set(["G5->F6"])


def test_black_piece_right():
    WP, BP, K = get_empty_board()

    BP = insert_piece_by_pdntext(BP, "H6")
    WP = insert_piece_by_pdntext(WP, "G5")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    assert set(convert_move_list_to_pdn(white_moves)) == set(["G5->F4", "G5->H4"])
    assert set(convert_move_list_to_pdn(black_moves)) == set(["H6->G7"])


def test_triangle():
    WP, BP, K = get_empty_board()

    BP = insert_piece_by_pdntext(BP, "C1")
    WP = insert_piece_by_pdntext(WP, "D2")
    WP = insert_piece_by_pdntext(WP, "E3")
    WP = insert_piece_by_pdntext(WP, "F4")
    WP = insert_piece_by_pdntext(WP, "G3")
    WP = insert_piece_by_pdntext(WP, "F2")
    WP = insert_piece_by_pdntext(WP, "G1")
    BP = insert_piece_by_pdntext(BP, "H2")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    assert set(convert_move_list_to_pdn(white_moves)) == set(["D2->E1", "F2->E1"])
    assert set(convert_move_list_to_pdn(black_moves)) == set(["C1->B2"])


def test_setup_teams():
    WP, BP, K = get_empty_board()

    BP = insert_piece_by_pdntext(BP, "B8")
    WP = insert_piece_by_pdntext(WP, "D8")
    BP = insert_piece_by_pdntext(BP, "H8")
    BP = insert_piece_by_pdntext(BP, "C7")
    BP = insert_piece_by_pdntext(BP, "D6")
    BP = insert_piece_by_pdntext(BP, "D4")
    WP = insert_piece_by_pdntext(WP, "D2")
    WP = insert_piece_by_pdntext(WP, "A3")
    WP = insert_piece_by_pdntext(WP, "C5")
    WP = insert_piece_by_pdntext(WP, "H6")
    WP = insert_piece_by_pdntext(WP, "E7")
    K = insert_piece_by_pdntext(K, "E7")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    assert set(convert_move_list_to_pdn(white_moves)) == set(["C5->E3", "D8->B6"])
    assert set(convert_move_list_to_pdn(black_moves)) == set(["D6->F8", "D4->B6"])


def test_complex_situation():
    WP, BP, K = get_empty_board()

    WP = insert_piece_by_pdntext(WP, "D8")
    BP = insert_piece_by_pdntext(BP, "F8")
    BP = insert_piece_by_pdntext(BP, "E7")
    BP = insert_piece_by_pdntext(BP, "D6")
    WP = insert_piece_by_pdntext(WP, "H6")
    WP = insert_piece_by_pdntext(WP, "E5")

    BP = insert_piece_by_pdntext(BP, "F4")
    BP = insert_piece_by_pdntext(BP, "H4")
    BP = insert_piece_by_pdntext(BP, "A3")
    WP = insert_piece_by_pdntext(WP, "B2")
    K = insert_piece_by_pdntext(K, "A3")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    assert set(convert_move_list_to_pdn(white_moves)) == set(["E5->G3", "D8->F6"])
    assert set(convert_move_list_to_pdn(black_moves)) == set(["A3->C1"])


def test_second_complex_situation():
    WP, BP, K = get_empty_board()

    BP = insert_piece_by_pdntext(BP, "B8")
    BP = insert_piece_by_pdntext(BP, "D8")
    WP = insert_piece_by_pdntext(WP, "D8")
    BP = insert_piece_by_pdntext(BP, "H8")
    BP = insert_piece_by_pdntext(BP, "C7")
    WP = insert_piece_by_pdntext(WP, "E7")
    K = insert_piece_by_pdntext(K, "E7")
    WP = insert_piece_by_pdntext(WP, "H6")
    BP = insert_piece_by_pdntext(BP, "D6")
    WP = insert_piece_by_pdntext(WP, "C5")
    BP = insert_piece_by_pdntext(BP, "D4")
    WP = insert_piece_by_pdntext(WP, "A3")
    WP = insert_piece_by_pdntext(WP, "D2")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    assert set(convert_move_list_to_pdn(white_moves)) == set(["C5->E3", "D8->B6"])
    assert set(convert_move_list_to_pdn(black_moves)) == set(["D6->F8", "D4->B6"])


def test_pesky_7rank_32bit_errors():
    WP, BP, K = get_empty_board()
    WP = insert_piece_by_pdntext(WP, "B8")
    BP = insert_piece_by_pdntext(BP, "C7")
    BP = insert_piece_by_pdntext(BP, "E5")
    K = insert_piece_by_pdntext(K, "E5")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    assert set(convert_move_list_to_pdn(white_moves)) == set(["B8->D6->F4"])
    assert set(convert_move_list_to_pdn(black_moves)) == set(
        ["E5->F6", "E5->D6", "E5->D4", "E5->F4", "C7->D8"]
    )


def test_only_black_and_7rank():
    WP, BP, K = get_empty_board()
    BP = insert_piece_by_pdntext(BP, "B8")
    BP = insert_piece_by_pdntext(BP, "C7")
    BP = insert_piece_by_pdntext(BP, "D6")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    assert set(convert_move_list_to_pdn(white_moves)) == set([])
    assert set(convert_move_list_to_pdn(black_moves)) == set(["D6->E7", "C7->D8"])


def test_tricky_corners():
    WP, BP, K = get_empty_board()
    WP = insert_piece_by_pdntext(WP, "A7")
    WP = insert_piece_by_pdntext(WP, "B8")
    BP = insert_piece_by_pdntext(BP, "H8")
    WP = insert_piece_by_pdntext(WP, "A1")
    BP = insert_piece_by_pdntext(BP, "H2")
    BP = insert_piece_by_pdntext(BP, "G1")
    K = insert_piece_by_pdntext(K, "G1")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    assert set(convert_move_list_to_pdn(white_moves)) == set(["A7->B6", "B8->C7"])
    assert set(convert_move_list_to_pdn(black_moves)) == set(["G1->F2", "H2->G3"])


def test_soo_many_kings():
    WP, BP, K = get_empty_board()
    BP = insert_piece_by_pdntext(BP, "C1")
    K = insert_piece_by_pdntext(K, "C1")
    WP = insert_piece_by_pdntext(WP, "D2")
    WP = insert_piece_by_pdntext(WP, "D4")
    WP = insert_piece_by_pdntext(WP, "D6")
    WP = insert_piece_by_pdntext(WP, "F6")
    WP = insert_piece_by_pdntext(WP, "F4")
    WP = insert_piece_by_pdntext(WP, "F2")

    white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
    black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

    assert set(convert_move_list_to_pdn(white_moves)) == set(
        [
            "D2->E1",
            "F2->E1",
            "F2->G1",
            "D4->C3",
            "D4->E3",
            "F4->E3",
            "F4->G3",
            "D6->C5",
            "D6->E5",
            "F6->E5",
            "F6->G5",
        ]
    )

    assert set(convert_move_list_to_pdn(black_moves)) == set(
        ["C1->E3->G5->E7->C5->E3->G1", "C1->E3->C5->E7->G5->E3->G1", "C1->E3->G1"]
    )


if __name__ == "__main__":
    pytest.main()
