import pathlib
import sys

import pytest

parent = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(parent))

from checkers import *
from heuristic import new_heuristic
from minimax_alphabeta import *
from util.fen_pdn_helper import *
from util.helpers import *
from util.masks import *


def test_sort_moves_by_heuristic():
    WP, BP, K = setup_board_from_position_lists()
    pass
