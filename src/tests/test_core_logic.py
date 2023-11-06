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
    convert_move_list_to_pdn,
    PlayerTurn,
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


def test_jump_king():
    WP, BP, K = get_empty_board()
    WP = insert_piece_by_pdntext(WP, "B6")
    WP = insert_piece_by_pdntext(WP, "D6")
    BP = insert_piece_by_pdntext(BP, "C7")
    BP = insert_piece_by_pdntext(BP, "C5")
    BP = insert_piece_by_pdntext(BP, "A5")
    K = insert_piece_by_pdntext(K, "B6")

    white_jumpers = get_jumpers_white(WP, BP, K)
    white_jump_moves = generate_jump_moves(WP, BP, K, white_jumpers, PlayerTurn.WHITE)

    assert set(bitboard_to_pdn_positions(white_jumpers)) == set(["B6", "D6"])
    assert set(white_jump_moves) == set([(20, 17, 13), (20, 25, 29), (21, 17, 12)])


def test_jump_corners():
    WP, BP, K = get_empty_board()
    WP = insert_piece_by_pdntext(WP, "B6")
    BP = insert_piece_by_pdntext(BP, "A5")
    K = insert_piece_by_pdntext(K, "B6")
    white_jumpers = get_jumpers_white(WP, BP, K)
    white_jump_moves = generate_jump_moves(WP, BP, K, white_jumpers, PlayerTurn.WHITE)
    assert white_jump_moves == []


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
    white_jump_moves = generate_jump_moves(WP, BP, K, white_jumpers, PlayerTurn.WHITE)
    white_simple_moves = generate_simple_moves_white(WP, BP, K, white_movers)

    assert set(bitboard_to_pdn_positions(white_jumpers)) == set(["B6", "D6"])
    assert set(white_jump_moves) == set([(20, 17, 13), (21, 17, 12)])
    assert set(bitboard_to_pdn_positions(white_movers)) == set(["B6", "D6", "F6", "H6"])
    assert set(white_simple_moves) == set(
        [(20, 16), (21, 18), (22, 18), (22, 19), (23, 19)]
    )


# test removing pieces from a fresh board
@pytest.mark.parametrize("index", [1, 12, 31])
def test_remove_white_piece(index):
    WP, BP, K = get_fresh_board()
    WP = remove_piece(WP, index)
    assert not is_set(WP, index), f"Expected piece to be removed at index {index}"


@pytest.mark.parametrize("index", [1, 12, 31])
def test_remove_black_piece(index):
    WP, BP, K = get_fresh_board()
    BP = remove_piece(BP, index)
    assert not is_set(BP, index), f"Expected piece to be removed at index {index}"


if __name__ == "__main__":
    pytest.main()
