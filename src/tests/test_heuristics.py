import pathlib
import sys

import pytest

parent = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(parent))

from game import *
from heuristic import mobility_diff_score
from util.fen_pdn_helper import *
from util.helpers import *


def test_mobility_score_calculator():
    WP, BP, K = setup_board_from_position_lists(
        white_positions=["A7"], black_positions=["H8"]
    )
    assert mobility_diff_score(WP, BP, K) == 1

    WP, BP, K = setup_board_from_position_lists(
        white_positions=["KD4"], black_positions=["KE5"]
    )

    assert mobility_diff_score(WP, BP, K) == 0

    WP, BP, K = setup_board_from_position_lists(
        white_positions=["KA1"], black_positions=["H8"]
    )

    assert mobility_diff_score(WP, BP, K) == 1

    WP, BP, K = get_fresh_board()

    assert mobility_diff_score(WP, BP, K) == 0

    WP, BP, K = setup_board_from_position_lists(
        white_positions=["KA3", "KC1", "KE3", "KG1"],
        black_positions=["A7", "KC7", "E7", "KG7"],
    )

    assert mobility_diff_score(WP, BP, K) == -1


def test_symmetric_mobility():
    white_positions = ["KC3"]
    black_positions = ["KD4", "KF6", "KD6", "KE3"]

    assert mobility_diff_score(  # ensure that the mobility score is symmetric in this contrived example
        *setup_board_from_position_lists(white_positions, black_positions)
    ) == (
        -1
        * mobility_diff_score(
            *setup_board_from_position_lists(black_positions, white_positions)
        )
    )


if __name__ == "__main__":
    pytest.main()
