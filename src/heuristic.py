from checkers import (
    PlayerTurn,
    all_jump_sequences,
    convert_move_list_to_pdn,
    generate_simple_moves_black,
    generate_simple_moves_white,
    get_jumpers_black,
    get_jumpers_white,
    get_movers_black,
    get_movers_white,
    print_board,
)
from util.fen_pdn_helper import setup_board_from_position_lists
from util.helpers import (
    count_bits,
    find_set_bits,
    get_empty_board,
    get_fresh_board,
    insert_piece,
    remove_piece,
)
from util.masks import (
    ATTACK_ROWS_BLACK,
    ATTACK_ROWS_WHITE,
    BLACK_JUMP_NORTHEAST,
    BLACK_JUMP_NORTHWEST,
    BLACK_NORTHEAST,
    BLACK_NORTHWEST,
    CENTER_8,
    DOUBLE_CORNER,
    DOUBLE_DIAGONAL,
    EDGES,
    KING_ROW_BLACK,
    KING_ROW_WHITE,
    MAIN_DIAGONAL,
    MASK_32,
    SINGLE_CORNER,
    WHITE_JUMP_SOUTHEAST,
    WHITE_JUMP_SOUTHWEST,
    WHITE_SOUTHEAST,
    WHITE_SOUTHWEST,
)


def basic_heuristic(WP, BP, K):
    return mobility_diff_score(WP, BP, K, jw=2) + piece_count_diff_score(
        WP, BP, K, kw=1.5
    )


def basic_heuristic_2(WP, BP, K):
    return (
        (100 * mobility_diff_score(WP, BP, K, jw=2))
        + (200 * piece_count_diff_score(WP, BP, K, kw=1.5))
        + (
            50
            * (
                calculate_total_distance_to_promotion_white(WP & ~K)
                - calculate_total_distance_to_promotion_black(BP & ~K)
            )
        )
    )


def new_heuristic(
    WP,
    BP,
    K,
    back_row_weight=500,
    center_weight=300,
    middle_four_rows_weight=150,
    edges_weight=-200,
    double_diagonals_weight=200,
    main_diagonal_weight=250,
    mobility_weight=3000,
    promotion_weight_a=1000,
    promotion_weight_b=100,
    promotion_weight_threshold=5,
    piece_count_diff_weight=7000,
    tpw=-100,
):
    back_row_score = count_bits(WP & KING_ROW_BLACK) - count_bits(BP & KING_ROW_WHITE)
    center_score = count_bits(WP & CENTER_8) - count_bits(BP & CENTER_8)
    middle_four_rows_score = count_bits(
        WP & (ATTACK_ROWS_WHITE | ATTACK_ROWS_BLACK)
    ) - count_bits(BP & (ATTACK_ROWS_WHITE | ATTACK_ROWS_BLACK))
    edges_score = count_bits(WP & EDGES) - count_bits(BP & EDGES)
    double_diagonals_score = count_bits(WP & DOUBLE_DIAGONAL) - count_bits(
        BP & DOUBLE_DIAGONAL
    )
    main_diagonal_score = count_bits(WP & MAIN_DIAGONAL) - count_bits(
        BP & MAIN_DIAGONAL
    )
    mds = mobility_diff_score(WP, BP, K)
    dpl = calculate_total_distance_to_promotion_white(
        WP & ~K
    ) - calculate_total_distance_to_promotion_black(BP & ~K)

    # calculate how many pieces are being threatened by the opponent (i.e. how many pieces are on the opponent's attack rows)
    threatened_pieces = count_bits(WP & ATTACK_ROWS_BLACK) + count_bits(
        BP & ATTACK_ROWS_WHITE
    )

    # Apply the weights to the respective scores
    total_score = (
        (back_row_weight * back_row_score)
        + (center_weight * center_score)
        + (middle_four_rows_weight * middle_four_rows_score)
        + (edges_weight * edges_score)
        + (double_diagonals_weight * double_diagonals_score)
        + (main_diagonal_weight * main_diagonal_score)
        + (mobility_weight * mds)
        + (
            promotion_weight_a * dpl
            if abs(mds)
            < promotion_weight_threshold  # the pieces have very simmilair mobility
            else promotion_weight_b * dpl
        )
        + (piece_count_diff_weight * piece_count_diff_score(WP, BP, K))
        + (tpw * threatened_pieces)
    )

    return int(total_score)


def mobility_diff_score(WP, BP, K, jw=2):
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

    # Jumps could be considered (jw) times more valuable as they capture an opponent's piece
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


def piece_count_diff_score(WP, BP, K, kw=1.5):
    # Count the number of men each player has
    white_piece_count = count_bits(WP)
    black_piece_count = count_bits(BP)

    # Count the number of kings each player has
    white_king_count = count_bits(WP & K & MASK_32)
    black_king_count = count_bits(BP & K & MASK_32)

    # Give kings a higher weight
    white_score = white_piece_count + kw * white_king_count
    black_score = black_piece_count + kw * black_king_count

    # Calculate the difference
    piece_count_score = white_score - black_score

    # Positive score favors white, Negative score favors black
    return piece_count_score


def calculate_total_distance_to_promotion_white(bitboard):
    """
    Calculates the sum of the distances of all pieces on the bitboard to the promotion line.
    """
    distance_sum = 0
    for index in find_set_bits(bitboard):
        if bitboard & (1 << index):
            # Calculate the row by dividing by 4 (since 4 cells per row)
            row = index // 4
            # Distance to promotion is 7 minus the row number
            distance = 7 - row
            distance_sum += max(
                0, distance
            )  # Ensure distance is not negative for already promoted pieces

    return distance_sum


def calculate_total_distance_to_promotion_black(bitboard):
    """
    Calculates the sum of the distances of all pieces on the bitboard to the promotion line.
    """
    distance_sum = 0
    for index in find_set_bits(bitboard):
        if bitboard & (1 << index):
            # Calculate the row by dividing by 4 (since 4 cells per row)
            row = index // 4
            # Distance to promotion for black is the row number
            distance = row
            distance_sum += distance  # Distance for black is just the row number, since they move down the board

    return distance_sum


# WP, BP, K = setup_board_from_position_lists(
#     white_positions=["D4", "F4", "B6", "KA7", "KG7"], black_positions=["KE5", "KC7"]
# )

# print_board(WP, BP, K)

# print(
#     f"Total distance to promotion for white: {calculate_total_distance_to_promotion_white(WP)}"
# )
# print(
#     f"Total distance to promotion for black: {calculate_total_distance_to_promotion_black(BP)}"
# )

# print(f"Mobility Score: {mobility_diff_score(WP, BP, K)}")

# print(f"Basic Heuristic: {basic_heuristic(WP, BP, K)}")
# print(f"New Heuristic: {new_heuristic(WP, BP, K)}")
