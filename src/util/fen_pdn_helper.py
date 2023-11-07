import sys
import pathlib

parent = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(parent))

from util.helpers import get_empty_board, insert_piece_by_pdntext


def setup_board_from_position_lists(white_positions, black_positions):
    """
    Sets up the board with the given white and black positions.
    A "K" prefix in the position indicates a king.

    :param white_positions: List of strings for white pieces' positions, with "K" indicating kings.
    :param black_positions: List of strings for black pieces' positions, with "K" indicating kings.
    :return: Tuple of (WP, BP, K) representing white pieces, black pieces, and kings respectively.
    """
    WP, BP, K = get_empty_board()  # Assuming this function initializes all boards to 0.

    white_positions = [pos.upper() for pos in white_positions]
    black_positions = [pos.upper() for pos in black_positions]

    for pos in white_positions:
        if pos.startswith("K"):
            # If the position starts with 'K', it's a king piece.
            pos = pos[1:]  # Remove the 'K' to get the board position.
            WP = insert_piece_by_pdntext(WP, pos)
            K = insert_piece_by_pdntext(K, pos)
        else:
            WP = insert_piece_by_pdntext(WP, pos)

    for pos in black_positions:
        if pos.startswith("K"):
            pos = pos[1:]  # Remove the 'K' to get the board position.
            BP = insert_piece_by_pdntext(BP, pos)
            K = insert_piece_by_pdntext(K, pos)
        else:
            BP = insert_piece_by_pdntext(BP, pos)

    return WP, BP, K
