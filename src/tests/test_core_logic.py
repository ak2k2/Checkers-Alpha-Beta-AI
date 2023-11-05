import pathlib
import sys

import pytest

parent = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(parent))

from main import (
    bitindex_to_coords,
    coords_to_bitindex,
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
    remove_piece,
    is_set,
    print_board,
)


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

    white_moves = generate_simple_moves_white(WP, BP, K)
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

    black_moves = generate_simple_moves_black(WP, BP, K)
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
    pytest.main()
