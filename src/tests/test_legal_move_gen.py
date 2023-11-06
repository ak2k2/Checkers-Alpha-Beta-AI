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
)


def test_generate_legal_moves_from_start():
    WP, BP, K = get_fresh_board()
    white_legal_moves = generate_legal_moves(WP, BP, K, "white")
    print(white_legal_moves)
    black_legal_moves = generate_legal_moves(WP, BP, K, "black")
    print(black_legal_moves)
    assert len(white_legal_moves) == 7
    assert len(black_legal_moves) == 7


if __name__ == "__main__":
    test_generate_legal_moves_from_start()
