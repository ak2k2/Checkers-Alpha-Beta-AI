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


def bitboard_to_pdn_positions(bitboard):
    pdn_positions = [bitindex_to_coords(index) for index in find_set_bits(bitboard)]
    return pdn_positions


# Test the get_empty_board function
def test_get_empty_board():
    WP, BP, K = get_empty_board()
    assert WP == 0b0
    assert BP == 0b0
    assert K == 0b0


def test_get_fresh_board():
    WP, BP, K = get_fresh_board()
    assert WP == 0b11111111111100000000000000000000
    assert BP == 0b00000000000000000000111111111111
    assert K == 0b00000000000000000000000000000000


# Test inserting various pieces onto the board
@pytest.mark.parametrize("index", [1, 12, 31])
def test_insert_white_piece(index):
    WP, BP, K = get_empty_board()
    WP = insert_piece(WP, index)
    assert is_set(WP, index), f"Expected piece to be inserted at index {index}"


@pytest.mark.parametrize("index", [1, 12, 31])
def test_insert_black_piece(index):
    WP, BP, K = get_empty_board()
    BP = insert_piece(BP, index)
    assert is_set(BP, index), f"Expected piece to be inserted at index {index}"


def test_insert_with_pdn():
    WP, BP, K = get_empty_board()
    WP = insert_piece_by_pdntext(WP, "B8")
    BP = insert_piece_by_pdntext(BP, "A3")
    BP = insert_piece_by_pdntext(BP, "C3")
    WP = insert_piece_by_pdntext(WP, "D2")
    K = insert_piece_by_pdntext(K, "D2")
    for i in ["B8", "A3", "C3", "D2"]:
        assert is_set(BP | WP | K, coords_to_bitindex(i))


def test_get_movers_king_backwards():
    WP, BP, K = get_empty_board()
    WP = insert_piece_by_pdntext(WP, "B8")
    BP = insert_piece_by_pdntext(BP, "C1")
    BP = insert_piece_by_pdntext(BP, "E1")
    WP = insert_piece_by_pdntext(WP, "D2")
    K = insert_piece_by_pdntext(K, "D2")
    white_movers = get_movers_white(WP, BP, K)
    print_board(WP, BP, K)
    print(f"White movers: {bitboard_to_pdn_positions(white_movers)}")
    white_simple_moves = generate_simple_moves_white(WP, BP, K, white_movers)
    for move in white_simple_moves:
        print(f"{bitindex_to_coords(move[0])} -> {bitindex_to_coords(move[1])}")


def test_jump_moves():
    WP, BP, K = get_empty_board()
    WP = insert_piece_by_pdntext(WP, "B8")
    BP = insert_piece_by_pdntext(BP, "C7")
    WP = insert_piece_by_pdntext(WP, "F8")
    WP = insert_piece_by_pdntext(WP, "D8")
    white_jumpers = get_jumpers_white(WP, BP, K)
    print_board(WP, BP, K)
    print(f"White jumpers: {bitboard_to_pdn_positions(white_jumpers)}")
    white_jump_moves = generate_jump_moves(WP, BP, K, white_jumpers, "white")
    for move in white_jump_moves:
        print(f"{bitindex_to_coords(move[0])} -> {bitindex_to_coords(move[1])}")


def test_jump_king():
    WP, BP, K = get_empty_board()
    WP = insert_piece_by_pdntext(WP, "B6")
    WP = insert_piece_by_pdntext(WP, "D6")
    BP = insert_piece_by_pdntext(BP, "C7")
    BP = insert_piece_by_pdntext(BP, "C5")
    BP = insert_piece_by_pdntext(BP, "A5")
    K = insert_piece_by_pdntext(K, "B6")
    white_jumpers = get_jumpers_white(WP, BP, K)
    print_board(WP, BP, K)
    print(f"White jumpers: {bitboard_to_pdn_positions(white_jumpers)}")
    white_jump_moves = generate_jump_moves(WP, BP, K, white_jumpers, "white")
    for move in white_jump_moves:
        print(f"{bitindex_to_coords(move[0])} -> {bitindex_to_coords(move[1])}")


def test_jump_corners():
    WP, BP, K = get_empty_board()
    WP = insert_piece_by_pdntext(WP, "B6")
    BP = insert_piece_by_pdntext(BP, "A5")
    K = insert_piece_by_pdntext(K, "B6")
    white_jumpers = get_jumpers_white(WP, BP, K)
    print_board(WP, BP, K)
    print(f"White jumpers: {bitboard_to_pdn_positions(white_jumpers)}")
    white_jump_moves = generate_jump_moves(WP, BP, K, white_jumpers, "white")
    for move in white_jump_moves:
        print(f"{bitindex_to_coords(move[0])} -> {bitindex_to_coords(move[1])}")


def test_only_jump_opponents():  # confirms that it only moves into allotted free space, and does not jump itself
    WP, BP, K = get_empty_board()
    WP = insert_piece_by_pdntext(WP, "A7")
    WP = insert_piece_by_pdntext(WP, "B8")
    WP = insert_piece_by_pdntext(WP, "B6")
    WP = insert_piece_by_pdntext(WP, "C7")
    WP = insert_piece_by_pdntext(WP, "D8")
    WP = insert_piece_by_pdntext(WP, "D6")
    WP = insert_piece_by_pdntext(WP, "E7")
    WP = insert_piece_by_pdntext(WP, "F8")
    WP = insert_piece_by_pdntext(WP, "F6")
    WP = insert_piece_by_pdntext(WP, "G7")
    WP = insert_piece_by_pdntext(WP, "H8")
    WP = insert_piece_by_pdntext(WP, "H6")
    BP = insert_piece_by_pdntext(BP, "C5")
    K = insert_piece_by_pdntext(K, "C7")
    white_jumpers = get_jumpers_white(WP, BP, K)
    white_movers = get_movers_white(WP, BP, K)
    print_board(WP, BP, K)
    print(f"White jumpers: {bitboard_to_pdn_positions(white_jumpers)}")

    white_jump_moves = generate_jump_moves(WP, BP, K, white_jumpers, "white")
    for move in white_jump_moves:
        print(f"{bitindex_to_coords(move[0])} -> {bitindex_to_coords(move[1])}")

    print(f"White movers: {bitboard_to_pdn_positions(white_movers)}")
    white_simple_moves = generate_simple_moves_white(WP, BP, K, white_movers)
    for move in white_simple_moves:
        print(f"{bitindex_to_coords(move[0])} -> {bitindex_to_coords(move[1])}")


# test removing pieces from a fresh board
@pytest.mark.parametrize("index", [1, 12, 31])
def test_remove_white_piece(index):
    WP, BP, K = get_fresh_board()
    print_board(WP, BP, K)
    WP = remove_piece(WP, index)
    assert not is_set(WP, index), f"Expected piece to be removed at index {index}"


@pytest.mark.parametrize("index", [1, 12, 31])
def test_remove_black_piece(index):
    WP, BP, K = get_fresh_board()
    BP = remove_piece(BP, index)
    assert not is_set(BP, index), f"Expected piece to be removed at index {index}"


# Test generating simple moves for white pieces
def test_generate_simple_moves_white():
    WP, BP, K = get_empty_board()
    # Setting up a scenario for white pieces
    WP = insert_piece(WP, 9)  # A white piece at index 9
    WP = insert_piece(WP, 14)  # Another white piece at index 14
    BP = insert_piece(BP, 18)  # A black piece that blocks a simple move at index 18
    white_movers = get_movers_white(WP, BP, K)
    white_moves = generate_simple_moves_white(WP, BP, K, white_movers)
    white_pgn_moves = [
        bitindex_to_coords(m[0]) + "-" + bitindex_to_coords(m[1]) for m in white_moves
    ]
    assert set(white_pgn_moves) == set(
        [
            "C3-B2",
            "C3-D2",
            "F4-E3",
            "F4-G3",
        ]
    ), "Incorrect simple moves generated for white pieces"

    black_movers = get_movers_black(WP, BP, K)
    black_moves = generate_simple_moves_black(WP, BP, K, black_movers)
    black_pgn_moves = [
        bitindex_to_coords(m[0]) + "-" + bitindex_to_coords(m[1]) for m in black_moves
    ]
    assert set(black_pgn_moves) == set(
        [
            "E5-D6",
            "E5-F6",
        ]
    ), "Incorrect simple moves generated for black pieces"


if __name__ == "__main__":
    # pytest.main()
    test_only_jump_opponents()
