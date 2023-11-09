from checkers import *
from util.fen_pdn_helper import *
from util.helpers import *
from util.masks import *


def new_heuristic(WP, BP, K):
    num_total_pieces = count_bits(WP) + count_bits(BP)

    num_white_man = count_bits(WP & ~K & MASK_32)
    num_white_king = count_bits(WP & K & MASK_32)
    num_black_man = count_bits(BP & ~K & MASK_32)
    num_black_king = count_bits(BP & K & MASK_32)

    piece_count_score = (500 * num_white_man + 775 * num_white_king) - (
        500 * num_black_man + 775 * num_black_king
    )  # white wants to maximize this

    back_row = 400 * (
        count_bits(WP & MASK_32 & KING_ROW_BLACK)
        - count_bits(BP & MASK_32 & KING_ROW_WHITE)
    )

    capture_score = 300 * (
        count_black_pieces_that_can_be_captured_by_white(WP, BP, K)
        - count_white_pieces_that_can_be_captured_by_black(WP, BP, K)
    )  # white wants to maximize number of black pieces that can be captured and minimize number of white pieces that can be captured

    center_score = 25 * (
        count_bits(WP & CENTER_8) - count_bits(BP & CENTER_8)
    )  # white wants to maximize center control

    mobility_score = 150 * mobility_diff_score(
        WP, BP, K
    )  # white wants to maximize its mobility and minimize black's mobility

    kings_on_main_diagonal = 25 * (
        count_bits(WP & K & MAIN_DIAGONAL) - count_bits(BP & K & MAIN_DIAGONAL)
    )

    men_on_side_diagonals = 25 * (
        count_bits(WP & ~K & DOUBLE_DIAGONAL) - count_bits(BP & ~K & DOUBLE_DIAGONAL)
    )

    safety_score = 200 * (
        calculate_safe_white_pieces(WP, K) - calculate_safe_black_pieces(BP, K)
    )

    final_eval = (
        piece_count_score
        + back_row
        + capture_score
        + center_score
        + mobility_score
        + kings_on_main_diagonal
        + men_on_side_diagonals
        + safety_score
    )

    if num_total_pieces < 6:  # less than 6 pieces on the board. endgame stage.
        chebychev_distance = calculate_sum_distances(WP, BP)
        if piece_count_score > 0:  # white has more weighted material
            final_eval += (
                -100 * chebychev_distance
            )  # white wants to minimize chevychev distance and get closer to black
        else:  # white has less weighted material
            final_eval += (
                100 * chebychev_distance
            )  # # white wants to maximize chevychev distance and get further from black

    # elif num_total_pieces > 20:  # if were still in opening stage.
    #     final_eval += (
    #         100
    #         * (  # white wants to maximize blacks distance to promote and minimize its own
    #             calculate_total_distance_to_promotion_black(BP & ~K)
    #             - calculate_total_distance_to_promotion_white(WP & ~K)
    #         )
    #     )

    return final_eval


def wed_heuristic(WP, BP, K):
    num_white_man = count_bits(WP & ~K & MASK_32)
    num_white_king = count_bits(WP & K & MASK_32)
    num_black_man = count_bits(BP & ~K & MASK_32)
    num_black_king = count_bits(BP & K & MASK_32)

    piece_count_score = (500 * num_white_man + 775 * num_white_king) - (
        500 * num_black_man + 775 * num_black_king
    )  # white wants to maximize this

    back_row = 400 * (
        count_bits(WP & MASK_32 & KING_ROW_BLACK)
        - count_bits(BP & MASK_32 & KING_ROW_WHITE)
    )

    capture_score = 300 * (
        count_black_pieces_that_can_be_captured_by_white(WP, BP, K)
        - count_white_pieces_that_can_be_captured_by_black(WP, BP, K)
    )  # white wants to maximize number of black pieces that can be captured minus number of white pieces that can be captured

    center_score = 25 * (
        count_bits(WP & CENTER_8) - count_bits(BP & CENTER_8)
    )  # white wants to maximize center control

    mobility_score = 100 * mobility_diff_score(
        WP, BP, K
    )  # white wants to maximize its mobility and minimize black's mobility

    # white wants to maximize blacks distance to promote and minimize its own
    # promotion_score = 100 * (
    #     calculate_total_distance_to_promotion_black(BP & ~K)
    #     - calculate_total_distance_to_promotion_white(WP & ~K)
    # )

    final_eval = (
        piece_count_score
        + back_row
        + capture_score
        + center_score
        + mobility_score
        # + promotion_score
    )

    return final_eval


def piece_count_heuristic(WP, BP, K):
    num_white_man = count_bits(WP & ~K & MASK_32)
    num_white_king = count_bits(WP & K & MASK_32)
    num_black_man = count_bits(BP & ~K & MASK_32)
    num_black_king = count_bits(BP & K & MASK_32)

    piece_count_score = (500 * num_white_man + 775 * num_white_king) - (
        500 * num_black_man + 775 * num_black_king
    )

    return piece_count_score


def calculate_sum_distances(WP, BP):
    total_distance = 0
    for w_index in find_set_bits(WP):
        w_coords = bit_to_coordinates(w_index)
        for b_index in find_set_bits(BP):
            # print(f"pair: {w_index}, {b_index}")
            b_coords = bit_to_coordinates(b_index)
            # print(f"coords: {w_coords}, {b_coords}")
            distance = max(
                abs(b_coords[0] - w_coords[0]), abs(b_coords[1] - w_coords[1])
            )
            total_distance += distance

    return total_distance


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


def piece_count_diff_score(WP, BP, K):
    # Count the number of men each player has
    white_man_count = count_bits(WP & ~K & MASK_32)
    black_man_count = count_bits(BP & ~K & MASK_32)

    # Count the number of kings each player has
    white_king_count = count_bits(WP & K & MASK_32)
    black_king_count = count_bits(BP & K & MASK_32)

    # Give kings a higher weight
    white_score = white_man_count + 1.5 * white_king_count
    black_score = black_man_count + 1.5 * black_king_count

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


def bit_to_coordinates(bit_index):
    # Convert the single-dimensional bit index to 2D coordinates,
    # taking into account that the board is only half filled
    # and playable squares are zigzagged.
    x = (bit_index % 4) * 2 + ((bit_index // 4) % 2)
    y = bit_index // 4
    return (x, y)


def count_black_pieces_that_can_be_captured_by_white(WP, BP, K):
    # Get white's jump sequences (potential captures)
    white_jump_sequences = all_jump_sequences(
        WP, BP, K, get_jumpers_white(WP, BP, K), None, player=PlayerTurn.WHITE
    )

    capturable_pieces = set()

    for sequence in white_jump_sequences:
        if len(sequence) == 2:
            capturable_pieces.add(find_jumped_pos(sequence[0], sequence[1]))
        else:
            pairs = [[sequence[i], sequence[i + 1]] for i in range(len(sequence) - 1)]
            for sequence in pairs:
                capturable_pieces.add(find_jumped_pos(sequence[0], sequence[1]))

    return len(
        capturable_pieces
    )  # number of unique black pieces that can be captured by white in the next turn


def count_white_pieces_that_can_be_captured_by_black(WP, BP, K):
    # Get white's jump sequences (potential captures)
    black_jump_sequences = all_jump_sequences(
        WP, BP, K, None, get_jumpers_black(WP, BP, K), player=PlayerTurn.BLACK
    )

    # Count the unique pieces that can be captured by white in the next turn
    # A set is used to ensure each piece is only counted once, even if it can be captured in multiple ways.
    capturable_pieces = set()

    for sequence in black_jump_sequences:
        if len(sequence) == 2:
            capturable_pieces.add(find_jumped_pos(sequence[0], sequence[1]))
        else:
            pairs = [[sequence[i], sequence[i + 1]] for i in range(len(sequence) - 1)]
            for sequence in pairs:
                capturable_pieces.add(find_jumped_pos(sequence[0], sequence[1]))

    return len(
        capturable_pieces
    )  # number of unique white pieces that can be captured by black on next turn


def calculate_safe_white_pieces(WP, K):
    # Counter for safe white pieces
    safe_white_pieces = 0

    # Get all white piece positions
    white_positions = find_set_bits(WP)

    # Iterate through each white piece
    for pos in white_positions:
        # Check the top-left (northwest) and top-right (northeast) positions for white pieces
        # Using the black movement direction dictionaries in reverse
        safe_northeast = BLACK_NORTHEAST.get(pos)
        safe_northwest = BLACK_NORTHWEST.get(pos)

        # Conditions to check if a piece is safe:
        # 1. There's a white piece or a wall (None) to the northeast
        # 2. There's a white piece or a wall (None) to the northwest
        is_safe_northeast = safe_northeast is None or is_set(WP, safe_northeast)
        is_safe_northwest = safe_northwest is None or is_set(WP, safe_northwest)

        # If both are safe, increment the counter
        if is_safe_northeast and is_safe_northwest:
            safe_white_pieces += 1

    return safe_white_pieces


def calculate_safe_black_pieces(BP, K):
    # Counter for safe black pieces
    safe_black_pieces = 0

    # Get all black piece positions
    black_positions = find_set_bits(BP)

    # Iterate through each black piece
    for pos in black_positions:
        # Check the southeast and southwest positions for black pieces
        # For black pieces moving upwards, southeast and southwest would be behind them
        safe_southeast = WHITE_SOUTHEAST.get(pos)
        safe_southwest = WHITE_SOUTHWEST.get(pos)

        # A piece is considered safe if it has support from behind in both southeast and southwest directions,
        # or if it's against the wall (None in the dictionaries) indicating it's on the back row.
        is_safe = (
            safe_southeast is None
            or (safe_southeast is not None and is_set(BP, safe_southeast))
        ) and (
            safe_southwest is None
            or (safe_southwest is not None and is_set(BP, safe_southwest))
        )

        # Increment the counter if the piece is safe
        safe_black_pieces += int(is_safe)

    return safe_black_pieces


if __name__ == "__main__":
    WP, BP, K = setup_board_from_position_lists(
        ["D4", "KD6", "B4", "B6", "A7", "C7", "C5", "E5"], ["KC3", "E7"]
    )
    # WP, BP, K = get_fresh_board()
    print_board(WP, BP, K)
    print(calculate_safe_white_pieces(WP, K))
