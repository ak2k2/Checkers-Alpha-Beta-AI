from checkers import *
from util.fen_pdn_helper import *
from util.helpers import *
from util.masks import *

import random


def new_heuristic(WP, BP, K, turn=None):
    # White aims to maximize this score while black aims to minimize it.

    num_total_pieces = count_bits(WP) + count_bits(
        BP
    )  # Total number of pieces on the board.

    # Count the number of each type of piece for white and black.
    num_white_man = count_bits(WP & ~K & MASK_32)
    num_white_king = count_bits(WP & K & MASK_32)
    num_black_man = count_bits(BP & ~K & MASK_32)
    num_black_king = count_bits(BP & K & MASK_32)

    # Piece value weights should reflect the importance of kings over men.
    piece_count_score = (500 * num_white_man + 750 * num_white_king) - (
        500 * num_black_man + 750 * num_black_king
    )

    # Sum of the chebychev distances"
    if num_total_pieces < 6:
        EVAL = 0
        sum_chebychev_distance = calculate_sum_distances(WP, BP)
        if piece_count_score > 0:  # White has more weighted material.
            EVAL = (
                50 * sum_chebychev_distance
            )  # White wants to minimize chevychev distance and get closer to black.

        elif piece_count_score < 0:  # Black has more weighted material.
            EVAL = (
                50 * sum_chebychev_distance
            )  # White wants to maximize chevychev distance and get further from black.
        else:
            # If the piece count is equal the player with more mobility should have the advantage. This will prevent giving up and forcing draws if/when applicable.
            EVAL = 50 * mobility_diff_score(WP, BP, K)
        return int(EVAL)
    else:
        # Mobility is defined as a weighted sum of the number of simple and jump moves white has vs. black. More mobility generally means more options.
        mobility_score = 250 * mobility_diff_score(
            WP, BP, K, jw=5
        )  # jw is the weight of jumps vs. simple moves.

        # As the game progresses, the back row's importance diminishes since it prevents kinging.
        # Early game, it is important to control the back row to prevent the opponent from kinging.
        back_row_importance = (
            num_total_pieces / 24
        )  # Tapers off as the number of pieces decreases.
        back_row_score = (
            50
            * back_row_importance
            * (
                count_bits(
                    WP & ~K & MASK_32 & KING_ROW_BLACK
                )  # Number of white pieces on the 8th rank.
                - count_bits(
                    BP & ~K & MASK_32 & KING_ROW_WHITE
                )  # Number of black pieces on the 1st rank.
            )
        )

        # To be a "man with backwards backup" a piece must have only friendly pieces or walls directly behind them.
        men_with_backwards_backup = 50 * (
            calculate_safe_white_pieces(WP, K) - calculate_safe_black_pieces(BP, K)
        )

        # Refects the tradeoff between capturing and being captured wrt. the current turn.
        capture_safety_score = 0
        if turn == PlayerTurn.WHITE:
            capture_safety_score += count_black_pieces_that_can_be_captured_by_white(
                WP, BP, K
            )  # White wants to capture as MANY black pieces as he can by MAXIMIZING this score.
        else:  # turn == PlayerTurn.BLACK
            capture_safety_score -= count_white_pieces_that_can_be_captured_by_black(
                WP, BP, K
            )  # Black is wants to capture as MANY white pieces as he can by MINIMIZING this score.

        capture_safety_score *= 20

        # Center control is crucial in the opening and mid-game for mobility and kinging paths.
        center_control_importance = (
            num_total_pieces / 24
        )  # Tapers off as the number of pieces decreases.
        center_score = (
            50
            * center_control_importance
            * (
                count_bits(WP & CENTER_8 & MASK_32)
                - count_bits(BP & CENTER_8 & MASK_32)
            )
        )

        # Kings positioned on the main diagonal can control more squares.
        kings_on_main_diagonal = 20 * (
            count_bits(WP & K & MAIN_DIAGONAL) - count_bits(BP & K & MAIN_DIAGONAL)
        )

        # Men on side diagonals are less likely to be captured but also have reduced mobility.
        men_on_side_diagonals = 10 * (
            count_bits(WP & ~K & DOUBLE_DIAGONAL)
            - count_bits(BP & ~K & DOUBLE_DIAGONAL)
        )

        # Combine all evaluations into a final score.
        EVAL = (
            piece_count_score
            + back_row_score
            + capture_safety_score
            + center_score
            + men_with_backwards_backup
            + mobility_score
            + kings_on_main_diagonal
            + men_on_side_diagonals
        )

        return int(EVAL)


# ----------------- OLD HEURISTIC -----------------
# ----------------- OLD HEURISTIC -----------------
# ----------------- OLD HEURISTIC -----------------


def old_heuristic(WP, BP, K, turn=None):
    # White aims to maximize this score while black aims to minimize it.

    num_total_pieces = count_bits(WP) + count_bits(
        BP
    )  # Total number of pieces on the board.

    # Count the number of each type of piece for white and black.
    num_white_man = count_bits(WP & ~K & MASK_32)
    num_white_king = count_bits(WP & K & MASK_32)
    num_black_man = count_bits(BP & ~K & MASK_32)
    num_black_king = count_bits(BP & K & MASK_32)

    # Piece value weights should reflect the importance of kings over men.
    piece_count_score = (500 * num_white_man + 750 * num_white_king) - (
        500 * num_black_man + 750 * num_black_king
    )

    # Sum of the chebychev distances"
    if num_total_pieces < 6:
        EVAL = 0
        sum_chebychev_distance = calculate_sum_distances(WP, BP)
        if piece_count_score > 0:  # White has more weighted material.
            EVAL = (
                50 * sum_chebychev_distance
            )  # White wants to minimize chevychev distance and get closer to black.

        elif piece_count_score < 0:  # Black has more weighted material.
            EVAL = (
                50 * sum_chebychev_distance
            )  # White wants to maximize chevychev distance and get further from black.
        else:
            # If the piece count is equal the player with more mobility should have the advantage. This will prevent giving up and forcing draws if/when applicable.
            EVAL = 50 * mobility_diff_score(WP, BP, K)
        return int(EVAL)
    else:
        # Mobility is defined as a weighted sum of the number of simple and jump moves white has vs. black. More mobility generally means more options.
        mobility_score = 250 * mobility_diff_score(
            WP, BP, K, jw=4
        )  # jw is the weight of jumps vs. simple moves.

        # As the game progresses, the back row's importance diminishes since it prevents kinging.
        # Early game, it is important to control the back row to prevent the opponent from kinging.
        back_row_importance = (
            num_total_pieces / 24
        )  # Tapers off as the number of pieces decreases.
        back_row_score = (
            50
            * back_row_importance
            * (
                count_bits(
                    WP & ~K & MASK_32 & KING_ROW_BLACK
                )  # Number of white pieces on the 8th rank.
                - count_bits(
                    BP & ~K & MASK_32 & KING_ROW_WHITE
                )  # Number of black pieces on the 1st rank.
            )
        )

        # Refects the tradeoff between capturing and being captured wrt. the current turn.
        capture_safety_score = 0
        if turn == PlayerTurn.WHITE:
            capture_safety_score += count_black_pieces_that_can_be_captured_by_white(
                WP, BP, K
            )  # White wants to capture as MANY black pieces as he can by MAXIMIZING this score.
        else:  # turn == PlayerTurn.BLACK
            capture_safety_score -= count_white_pieces_that_can_be_captured_by_black(
                WP, BP, K
            )  # Black is wants to capture as MANY white pieces as he can by MINIMIZING this score.

        # Center control is crucial in the opening and mid-game for mobility and kinging paths.
        center_control_importance = (
            num_total_pieces / 24
        )  # Tapers off as the number of pieces decreases.
        center_score = (
            50
            * center_control_importance
            * (
                count_bits(WP & CENTER_8 & MASK_32)
                - count_bits(BP & CENTER_8 & MASK_32)
            )
        )

        # Kings positioned on the main diagonal can control more squares.
        kings_on_main_diagonal = 20 * (
            count_bits(WP & K & MAIN_DIAGONAL) - count_bits(BP & K & MAIN_DIAGONAL)
        )

        # Men on side diagonals are less likely to be captured but also have reduced mobility.
        men_on_side_diagonals = 10 * (
            count_bits(WP & ~K & DOUBLE_DIAGONAL)
            - count_bits(BP & ~K & DOUBLE_DIAGONAL)
        )

        # Combine all evaluations into a final score.
        EVAL = (
            piece_count_score
            + back_row_score
            + capture_safety_score
            + center_score
            # + men_with_backwards_backup
            + mobility_score
            + kings_on_main_diagonal
            + men_on_side_diagonals
        )

        return int(EVAL)


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


def mobility_diff_score(WP, BP, K, jw=4):
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
        ["B4", "B6", "C5", "D6", "F2", "F4"], ["KC3", "KE7"]
    )
    # WP, BP, K = get_fresh_board()
    print_board(WP, BP, K)
    print(
        num_pieces_that_can_be_captured_by_black_if_he_gets_two_consecutive_jumps(
            WP, BP, K
        )
    )
    print(count_white_pieces_that_can_be_captured_by_black(WP, BP, K))
    # print(cheat_two_move_score(WP, BP, K))
