from typing import List

from util.helpers import find_set_bits, count_bits
from util.masks import (
    BLACK_NORTHEAST,
    BLACK_NORTHWEST,
    BLACK_JUMP_NORTHEAST,
    BLACK_JUMP_NORTHWEST,
    WHITE_SOUTHEAST,
    WHITE_SOUTHWEST,
    WHITE_JUMP_SOUTHEAST,
    WHITE_JUMP_SOUTHWEST,
    CENTER_8,
    DOUBLE_CORNER,
    SINGLE_CORNER,
    KING_ROW_BLACK,
    KING_ROW_WHITE,
    EDGES,
    ATTACK_ROWS_WHITE,
    ATTACK_ROWS_BLACK,
    MAIN_DIAGONAL,
    DOUBLE_DIAGONAL,
)

from main import (
    get_movers_white,
    get_movers_black,
    get_jumpers_white,
    get_jumpers_black,
    generate_simple_moves_white,
    generate_simple_moves_black,
    all_jump_sequences,
    PlayerTurn,
    print_board,
    convert_move_list_to_pdn,
)


def heuristic(WP, BP, K):
    return 0


def mobility_score(WP, BP, K):
    # Get movers and jumpers for both white and black
    white_movers = get_movers_white(WP, BP, K)
    black_movers = get_movers_black(WP, BP, K)
    white_jumpers = get_jumpers_white(WP, BP, K)
    black_jumpers = get_jumpers_black(WP, BP, K)

    # Generate simple and jump moves for both sides
    white_simple_moves = generate_simple_moves_white(WP, BP, K, white_movers)
    black_simple_moves = generate_simple_moves_black(BP, WP, K, black_movers)
    white_jump_sequences = all_jump_sequences(
        WP, BP, K, white_jumpers, None, player=PlayerTurn.WHITE
    )
    black_jump_sequences = all_jump_sequences(
        WP, BP, K, None, black_jumpers, player=PlayerTurn.BLACK
    )

    print("White simple moves: ", convert_move_list_to_pdn(white_simple_moves))
    print("Black simple moves: ", convert_move_list_to_pdn(black_simple_moves))
    print(
        "White jump sequences: ",
        convert_move_list_to_pdn(white_jump_sequences),
    )
    print(
        "Black jump sequences: ",
        convert_move_list_to_pdn(black_jump_sequences),
    )

    # Jumps could be considered (jw) times more valuable as they capture an opponent's piece
    jw = 2
    white_score = len(white_simple_moves) + jw * sum(
        len(seq) for seq in white_jump_sequences
    )
    black_score = len(black_simple_moves) + jw * sum(
        len(seq) for seq in black_jump_sequences
    )

    # The mobility score can be calculated as the difference between white and black mobility
    # A positive score favors white, a negative score favors black
    mobility_score = white_score - black_score

    return mobility_score


# def count_kings(bitboard: int, kings_bitboard: int) -> int:
#     """
#     Counts the number of kings in the bitboard.
#     """
#     return count_bits(bitboard & kings_bitboard)


# def count_safe_men(bitboard: int, edge_mask: int) -> int:
#     """
#     Counts the number of men that are on the edge of the board and are considered 'safe'.
#     """
#     return count_bits(bitboard & edge_mask)


# def count_moveable_men(
#     bitboard: int, empty_squares: int, own_kings: int, opponent_pieces: int
# ) -> int:
#     """
#     Counts the number of men that can move (not considering jumps).
#     """
#     # TODO: Implement the actual move generation logic based on the game rules.
#     pass


# def count_moveable_kings(
#     kings_bitboard: int, empty_squares: int, opponent_pieces: int
# ) -> int:
#     """
#     Counts the number of kings that can move (not considering jumps).
#     """
#     # TODO: Implement the actual move generation logic based on the game rules.
#     pass


# def aggregated_distance_to_promotion_line(bitboard: int, promotion_line: int) -> int:
#     """
#     Aggregates the distance of men to their promotion line.
#     """
#     # TODO: Define how distance is calculated and sum for all men.
#     pass


# def count_unoccupied_promotion_squares(empty_squares: int, promotion_line: int) -> int:
#     """
#     Counts the number of unoccupied fields on the promotion line.
#     """
#     return count_bits(empty_squares & promotion_line)


# def count_defending_pieces(bitboard: int, defending_rows: int) -> int:
#     """
#     Counts the number of pieces in the defending rows.
#     """
#     # TODO: Implement this function.
#     pass


# def count_attacking_men(bitboard: int, attacking_rows: int) -> int:
#     """
#     Counts the number of men in the attacking rows.
#     """
#     # TODO: Implement this function.
#     pass


# def count_central_men(bitboard: int, center_mask: int) -> int:
#     """
#     Counts the number of men in the center squares of the board.
#     """
#     # TODO: Implement this function.
#     pass


# def count_central_kings(kings_bitboard: int, center_mask: int) -> int:
#     """
#     Counts the number of kings in the center squares of the board.
#     """
#     # TODO: Implement this function.
#     pass


# def count_main_diagonal_pieces(bitboard: int, main_diagonal: int) -> int:
#     """
#     Counts the number of pieces on the main diagonal.
#     """
#     # TODO: Implement this function.
#     pass


# def count_double_diagonal_pieces(bitboard: int, double_diagonal: int) -> int:
#     """
#     Counts the number of pieces on the double diagonal.
#     """
#     # TODO: Implement this function.
#     pass


# def count_loner_men(bitboard: int, adjacency_mask: int) -> int:
#     """
#     Counts the number of men that are not adjacent to any other piece.
#     """
#     # TODO: Implement this function.
#     pass


# def count_loner_kings(kings_bitboard: int, adjacency_mask: int) -> int:
#     """
#     Counts the number of kings that are not adjacent to any other piece.
#     """
#     # TODO: Implement this function.
#     pass


# def count_holes(bitboard: int, own_pieces_mask: int) -> int:
#     """
#     Counts the number of empty squares adjacent to at least three pieces of the same color.
#     """
#     # TODO: Implement this function.
#     pass


# # Pattern detection functions with type hints


# def has_triangle_pattern(bitboard: int, triangle_pattern_mask: int) -> bool:
#     """
#     Returns True if a triangle pattern is detected.
#     """
#     # TODO: Implement this function.
#     pass


# def has_oreo_pattern(bitboard: int, oreo_pattern_mask: int) -> bool:
#     """
#     Returns True if an oreo pattern is detected.
#     """
#     # TODO: Implement this function.
#     pass


# def has_bridge_pattern(bitboard: int, bridge_pattern_mask: int) -> bool:
#     """
#     Returns True if a bridge pattern is detected.
#     """
#     # TODO: Implement this function.
#     pass


# def has_dog_pattern(bitboard: int, dog_pattern_mask: int) -> bool:
#     """
#     Returns True if a dog pattern is detected.
#     """
#     # TODO: Implement this function.
#     pass


# def has_pyramid_pattern(bitboard: int, pyramid_pattern_mask: int) -> bool:
#     """
#     Returns True if a pyramid pattern is detected.
#     """
#     # TODO: Implement this function.
#     pass
