import pathlib
import sys

import pytest

parent = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(parent))

from game import *
from util.helpers import *
from util.fen_pdn_helper import *

from heuristic import (
    mobility_score,
)


def test_mobility_score_basic():
    WP, BP, K = setup_board_from_position_lists(
        white_positions=["A7"], black_positions=["H8"]
    )
    print_board(WP, BP, K)
    score = mobility_score(WP, BP, K)
    print(score)


# def test_mobility_score():
#     WP, BP, K = get_empty_board()
#     WP = insert_piece_by_pdntext(WP, "D6")
#     WP = insert_piece_by_pdntext(WP, "F6")
#     K = insert_piece_by_pdntext(K, "F6")
#     BP = insert_piece_by_pdntext(BP, "E5")
#     BP = insert_piece_by_pdntext(BP, "G5")
#     K = insert_piece_by_pdntext(K, "G5")
#     print_board(WP, BP, K)
#     score = mobility_score(WP, BP, K)
#     print(score)


if __name__ == "__main__":
    test_mobility_score_basic()
