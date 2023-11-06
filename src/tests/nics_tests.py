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
    # should not be captured as black becomes a king
    WP = insert_piece_by_pdntext(WP, "E7")
    # print_board(WP, BP, K)

    black_moves = convert_move_list_to_pdn(
        generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)
    )

    assert set(black_moves) == set(["B6->D8"])


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


# def test_black_piece_thinks_it_can_move_into_corner():
#     WP, BP, K = get_empty_board()
#     WP = insert_piece_by_pdntext(  # NOTE: making this a BP results in empty move list and throws TypeError: 'NoneType' object is not iterable
#         WP, "B8"
#     )  # TODO: black thinks he can captire by moving into a piece that is weird
#     BP = insert_piece_by_pdntext(BP, "C7")
#     BP = insert_piece_by_pdntext(BP, "E5")
#     K = insert_piece_by_pdntext(K, "E5")

#     white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
#     black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

#     print(f"White moves: {convert_move_list_to_pdn(white_moves)}")
#     print(f"Black moves: {convert_move_list_to_pdn(black_moves)}")

#     print_board(WP, BP, K)


# def test_white_piece_thinks_it_can_move_into_corner():
#     WP, BP, K = get_empty_board()
#     WP = insert_piece_by_pdntext(
#         WP, "B8"
#     )  # TODO: black thinks he can captire by moving into a piece that is weird
#     BP = insert_piece_by_pdntext(BP, "C7")
#     BP = insert_piece_by_pdntext(BP, "E5")
#     K = insert_piece_by_pdntext(K, "E5")

#     white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
#     black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

#     print(f"White moves: {convert_move_list_to_pdn(white_moves)}")
#     print(f"Black moves: {convert_move_list_to_pdn(black_moves)}")

#     print_board(WP, BP, K)


# def test_insert_bp_corner():  # TODO: THIS IS THE PROBLEM TOP PRIORITIZE
#     WP, BP, K = get_empty_board()
#     BP = insert_piece_by_pdntext(BP, "B8")
#     BP = insert_piece_by_pdntext(BP, "C7")
#     BP = insert_piece_by_pdntext(BP, "D6")

#     print_board(WP, BP, K)

#     white_moves = generate_legal_moves(WP, BP, K, PlayerTurn.WHITE)
#     black_moves = generate_legal_moves(WP, BP, K, PlayerTurn.BLACK)

#     print(f"White moves: {convert_move_list_to_pdn(white_moves)}")
#     print(f"Black moves: {convert_move_list_to_pdn(black_moves)}")


if __name__ == "__main__":
    pytest.main()
