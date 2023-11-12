from checkers import *
from util.fen_pdn_helper import *
from util.helpers import *
from util.masks import *


def evolve_base_B(
    WP,
    BP,
    K,
    turn=None,
    man_weight=703.0013689332421,
    king_weight=742.0181308525031,
    chebychev_distance_weight=115.76682955495899,
    verge_king_weight=56.67775009304168,
    mobility_weight=50.1582997888212,
    jump_weight=9.378160411934207,
    capture_safety_weight=94.5652792759392,
    kinged_mult=6.362973149622056,
    land_edge_mult=0.38480787077298406,
    took_king_mult=1.0131168126451606,
    back_row_importance_factor=43.04383692865011,
    back_row_weight=17.874331360077267,
    backwards_backup_factor=45.622932127330245,
    backwards_backup_weight=38.10038709306349,
    center_control_factor=23.61850346296953,
    center_control_weight=23.62445621620175,
    kings_main_diagonal_weight=18.27923086275151,
    men_side_diagonals_weight=11.050875827750238,
    endgame_threshold=6,
    double_corner_weight=115.76682955495899,
    single_corner_weight=115.76682955495899,
    kgw=0,
    mgw=0,
    maj_loss_thresh=0.6666666666666666,
    attack_weight=0,
    agw=0,
    mix_row_not_box_weight=0,
    mrnbw=0,
    promotion_weight=0,
    pgw=0,
):
    num_total_pieces = count_bits(WP) + count_bits(BP)

    num_white_man = count_bits(WP & ~K & MASK_32)
    num_white_king = count_bits(WP & K & MASK_32)
    num_black_man = count_bits(BP & ~K & MASK_32)
    num_black_king = count_bits(BP & K & MASK_32)

    king_weight += (
        kgw * num_total_pieces
    )  # increase king weight as the game progresses?

    man_weight += mgw * num_total_pieces

    piece_count_score = (man_weight * num_white_man + king_weight * num_white_king) - (
        man_weight * num_black_man + king_weight * num_black_king
    )

    if num_total_pieces <= endgame_threshold:
        EVAL = piece_count_score
        sum_chebychev_distance = calculate_sum_distances(WP, BP)
        if piece_count_score > 0:
            EVAL -= chebychev_distance_weight * sum_chebychev_distance
            if count_bits(BP) < (maj_loss_thresh * count_bits(WP)):
                EVAL -= (
                    count_bits(BP & ~K & MASK_32 & DOUBLE_CORNER) * double_corner_weight
                )
                EVAL += (
                    count_bits(BP & ~K & MASK_32 & SINGLE_CORNER) * single_corner_weight
                )
        elif piece_count_score < 0:
            EVAL += chebychev_distance_weight * sum_chebychev_distance
            if count_bits(WP) < (maj_loss_thresh * count_bits(BP)):
                EVAL += (
                    count_bits(WP & ~K & MASK_32 & DOUBLE_CORNER) * double_corner_weight
                )
                EVAL -= (
                    count_bits(WP & ~K & MASK_32 & SINGLE_CORNER) * single_corner_weight
                )
        return int(EVAL)
    else:
        verge_of_kinging = verge_king_weight * pieces_on_verge_of_kinging(WP, BP, K)
        mobility_score = mobility_weight * mobility_diff_score(
            WP, BP, K, jw=jump_weight
        )
        capture_safety_score = 0
        if turn == PlayerTurn.WHITE:
            capture_safety_score = count_black_pieces_that_can_be_captured_by_white(
                WP,
                BP,
                K,
                kinged_mult=kinged_mult,
                land_edge_mult=land_edge_mult,
                took_king_mult=took_king_mult,
            )
            capture_safety_score = capture_safety_weight * capture_safety_score
        else:
            capture_safety_score = count_white_pieces_that_can_be_captured_by_black(
                WP,
                BP,
                K,
                kinged_mult=kinged_mult,
                land_edge_mult=land_edge_mult,
                took_king_mult=took_king_mult,
            )
            capture_safety_score = -capture_safety_weight * capture_safety_score

        back_row_importance = (
            num_total_pieces / back_row_importance_factor
            if back_row_importance_factor != 0
            else 1
        )
        back_row_score = (
            back_row_weight
            * back_row_importance
            * (
                count_bits(WP & ~K & MASK_32 & KING_ROW_BLACK)
                - count_bits(BP & ~K & MASK_32 & KING_ROW_WHITE)
            )
        )

        backwards_backup_weight_adjusted = (
            num_total_pieces / backwards_backup_factor
            if backwards_backup_factor != 0
            else 1
        )
        men_with_backwards_backup = (
            backwards_backup_weight_adjusted
            * backwards_backup_weight
            * (calculate_safe_white_pieces(WP, K) - calculate_safe_black_pieces(BP, K))
        )

        center_control_importance = (
            num_total_pieces / center_control_factor
            if center_control_factor != 0
            else 1
        )
        center_score = (
            center_control_weight
            * center_control_importance
            * (
                count_bits(WP & CENTER_8 & MASK_32)
                - count_bits(BP & CENTER_8 & MASK_32)
            )
        )
        kings_on_main_diagonal = kings_main_diagonal_weight * (
            count_bits(WP & K & MAIN_DIAGONAL) - count_bits(BP & K & MAIN_DIAGONAL)
        )
        men_on_side_diagonals = men_side_diagonals_weight * (
            count_bits(WP & ~K & DOUBLE_DIAGONAL)
            - count_bits(BP & ~K & DOUBLE_DIAGONAL)
        )

        attack_weight += agw * num_total_pieces
        attacking_pieces_score = attack_weight * (
            count_bits(WP & ATTACK_ROWS_BLACK) - count_bits(BP & ATTACK_ROWS_WHITE)
        )

        mix_row_not_box_weight += mrnbw * num_total_pieces
        mix_row_not_box_score = mix_row_not_box_weight * (
            count_bits(WP & MID_ROW_NOT_MID_BOX) - count_bits(BP & MID_ROW_NOT_MID_BOX)
        )

        promotion_weight += pgw * num_total_pieces
        promotion_boost = promotion_weight * (
            calculate_total_distance_to_promotion_black(BP, K)
            - calculate_total_distance_to_promotion_white(WP, K)
        )

        EVAL = (
            piece_count_score
            + back_row_score
            + capture_safety_score
            + center_score
            + men_with_backwards_backup
            + mobility_score
            + kings_on_main_diagonal
            + men_on_side_diagonals
            + verge_of_kinging
            + attacking_pieces_score
            + mix_row_not_box_score
            + promotion_boost
        )

        return int(EVAL)


def evolve_base_A(
    WP,
    BP,
    K,
    turn=None,
    man_weight=703.0013689332421,
    king_weight=742.0181308525031,
    chebychev_distance_weight=115.76682955495899,
    verge_king_weight=56.67775009304168,
    mobility_weight=50.1582997888212,
    jump_weight=9.378160411934207,
    capture_safety_weight=94.5652792759392,
    kinged_mult=6.362973149622056,
    land_edge_mult=0.38480787077298406,
    took_king_mult=1.0131168126451606,
    back_row_importance_factor=43.04383692865011,
    back_row_weight=17.874331360077267,
    backwards_backup_factor=45.622932127330245,
    backwards_backup_weight=38.10038709306349,
    center_control_factor=23.61850346296953,
    center_control_weight=23.62445621620175,
    kings_main_diagonal_weight=18.27923086275151,
    men_side_diagonals_weight=11.050875827750238,
    endgame_threshold=6,
    double_corner_weight=115.76682955495899,
    single_corner_weight=115.76682955495899,
    kgw=0,
):
    num_total_pieces = count_bits(WP) + count_bits(BP)

    num_white_man = count_bits(WP & ~K & MASK_32)
    num_white_king = count_bits(WP & K & MASK_32)
    num_black_man = count_bits(BP & ~K & MASK_32)
    num_black_king = count_bits(BP & K & MASK_32)

    king_weight += (
        kgw * num_total_pieces
    )  # increase king weight as the game progresses?

    piece_count_score = (man_weight * num_white_man + king_weight * num_white_king) - (
        man_weight * num_black_man + king_weight * num_black_king
    )

    if num_total_pieces <= endgame_threshold:
        EVAL = piece_count_score
        sum_chebychev_distance = calculate_sum_distances(WP, BP)
        if piece_count_score > 0:
            EVAL -= chebychev_distance_weight * sum_chebychev_distance
            if count_bits(BP) < 2 / 3 * count_bits(WP):
                EVAL -= (
                    count_bits(BP & ~K & MASK_32 & DOUBLE_CORNER) * double_corner_weight
                )
                EVAL += (
                    count_bits(BP & ~K & MASK_32 & SINGLE_CORNER) * single_corner_weight
                )
        elif piece_count_score < 0:
            EVAL += chebychev_distance_weight * sum_chebychev_distance
            if count_bits(WP) < 2 / 3 * count_bits(BP):
                EVAL += (
                    count_bits(WP & ~K & MASK_32 & DOUBLE_CORNER) * double_corner_weight
                )
                EVAL -= (
                    count_bits(WP & ~K & MASK_32 & SINGLE_CORNER) * single_corner_weight
                )
        return int(EVAL)
    else:
        verge_of_kinging = verge_king_weight * pieces_on_verge_of_kinging(WP, BP, K)
        mobility_score = mobility_weight * mobility_diff_score(
            WP, BP, K, jw=jump_weight
        )
        capture_safety_score = 0
        if turn == PlayerTurn.WHITE:
            capture_safety_score = count_black_pieces_that_can_be_captured_by_white(
                WP,
                BP,
                K,
                kinged_mult=kinged_mult,
                land_edge_mult=land_edge_mult,
                took_king_mult=took_king_mult,
            )
            capture_safety_score = capture_safety_weight * capture_safety_score
        else:
            capture_safety_score = count_white_pieces_that_can_be_captured_by_black(
                WP,
                BP,
                K,
                kinged_mult=kinged_mult,
                land_edge_mult=land_edge_mult,
                took_king_mult=took_king_mult,
            )
            capture_safety_score = -capture_safety_weight * capture_safety_score

        back_row_importance = num_total_pieces / back_row_importance_factor
        back_row_score = (
            back_row_weight
            * back_row_importance
            * (
                count_bits(WP & ~K & MASK_32 & KING_ROW_BLACK)
                - count_bits(BP & ~K & MASK_32 & KING_ROW_WHITE)
            )
        )
        backwards_backup_weight_adjusted = num_total_pieces / backwards_backup_factor
        men_with_backwards_backup = (
            backwards_backup_weight_adjusted
            * backwards_backup_weight
            * (calculate_safe_white_pieces(WP, K) - calculate_safe_black_pieces(BP, K))
        )
        center_control_importance = num_total_pieces / center_control_factor
        center_score = (
            center_control_weight
            * center_control_importance
            * (
                count_bits(WP & CENTER_8 & MASK_32)
                - count_bits(BP & CENTER_8 & MASK_32)
            )
        )
        kings_on_main_diagonal = kings_main_diagonal_weight * (
            count_bits(WP & K & MAIN_DIAGONAL) - count_bits(BP & K & MAIN_DIAGONAL)
        )
        men_on_side_diagonals = men_side_diagonals_weight * (
            count_bits(WP & ~K & DOUBLE_DIAGONAL)
            - count_bits(BP & ~K & DOUBLE_DIAGONAL)
        )

        EVAL = (
            piece_count_score
            + back_row_score
            + capture_safety_score
            + center_score
            + men_with_backwards_backup
            + mobility_score
            + kings_on_main_diagonal
            + men_on_side_diagonals
            + verge_of_kinging
        )

        return int(EVAL)


# ----------------- ************* -----------------
# ----------------- NEW HEURISTIC -----------------
# ----------------- ************* -----------------


def new_heuristic(
    WP,
    BP,
    K,
    turn=None,
    man_weight=173.95273726570554,
    king_weight=762.497701649474,
    chebychev_distance_weight=194.66090956218156,
    verge_king_weight=190.7868333971115,
    mobility_weight=33.34099452399477,
    jump_weight=4.819434591168335,
    capture_safety_weight=57.17763656005479,
    kinged_mult=2.5849043979463793,
    land_edge_mult=1.5501970585431368,
    took_king_mult=7.979397420421903,
    back_row_importance_factor=21.920411151937007,
    back_row_weight=146.50887921072842,
    backwards_backup_factor=32.7335765781782,
    backwards_backup_weight=35.40914520220719,
    center_control_factor=24.277549931366753,
    center_control_weight=28.720168604104302,
    kings_main_diagonal_weight=16.00377924839683,
    men_side_diagonals_weight=11.441589438324682,
    endgame_threshold=4,
    double_corner_weight=87.27548004039183,
    single_corner_weight=118.54442252447106,
    kgw=1.450198154068636,
):
    num_total_pieces = count_bits(WP) + count_bits(BP)

    num_white_man = count_bits(WP & ~K & MASK_32)
    num_white_king = count_bits(WP & K & MASK_32)
    num_black_man = count_bits(BP & ~K & MASK_32)
    num_black_king = count_bits(BP & K & MASK_32)

    king_weight += (
        kgw * num_total_pieces
    )  # increase king weight as the game progresses?

    piece_count_score = (man_weight * num_white_man + king_weight * num_white_king) - (
        man_weight * num_black_man + king_weight * num_black_king
    )

    if num_total_pieces <= endgame_threshold:
        EVAL = piece_count_score
        sum_chebychev_distance = calculate_sum_distances(WP, BP)
        if piece_count_score > 0:
            EVAL -= chebychev_distance_weight * sum_chebychev_distance
            if count_bits(BP) < 2 / 3 * count_bits(WP):
                EVAL -= (
                    count_bits(BP & ~K & MASK_32 & DOUBLE_CORNER) * double_corner_weight
                )
                EVAL += (
                    count_bits(BP & ~K & MASK_32 & SINGLE_CORNER) * single_corner_weight
                )
        elif piece_count_score < 0:
            EVAL += chebychev_distance_weight * sum_chebychev_distance
            if count_bits(WP) < 2 / 3 * count_bits(BP):
                EVAL += (
                    count_bits(WP & ~K & MASK_32 & DOUBLE_CORNER) * double_corner_weight
                )
                EVAL -= (
                    count_bits(WP & ~K & MASK_32 & SINGLE_CORNER) * single_corner_weight
                )
        return int(EVAL)
    else:
        verge_of_kinging = verge_king_weight * pieces_on_verge_of_kinging(WP, BP, K)
        mobility_score = mobility_weight * mobility_diff_score(
            WP, BP, K, jw=jump_weight
        )
        capture_safety_score = 0
        if turn == PlayerTurn.WHITE:
            capture_safety_score = count_black_pieces_that_can_be_captured_by_white(
                WP,
                BP,
                K,
                kinged_mult=kinged_mult,
                land_edge_mult=land_edge_mult,
                took_king_mult=took_king_mult,
            )
            capture_safety_score = capture_safety_weight * capture_safety_score
        else:
            capture_safety_score = count_white_pieces_that_can_be_captured_by_black(
                WP,
                BP,
                K,
                kinged_mult=kinged_mult,
                land_edge_mult=land_edge_mult,
                took_king_mult=took_king_mult,
            )
            capture_safety_score = -capture_safety_weight * capture_safety_score

        back_row_importance = num_total_pieces / back_row_importance_factor
        back_row_score = (
            back_row_weight
            * back_row_importance
            * (
                count_bits(WP & ~K & MASK_32 & KING_ROW_BLACK)
                - count_bits(BP & ~K & MASK_32 & KING_ROW_WHITE)
            )
        )
        backwards_backup_weight_adjusted = num_total_pieces / backwards_backup_factor
        men_with_backwards_backup = (
            backwards_backup_weight_adjusted
            * backwards_backup_weight
            * (calculate_safe_white_pieces(WP, K) - calculate_safe_black_pieces(BP, K))
        )
        center_control_importance = num_total_pieces / center_control_factor
        center_score = (
            center_control_weight
            * center_control_importance
            * (
                count_bits(WP & CENTER_8 & MASK_32)
                - count_bits(BP & CENTER_8 & MASK_32)
            )
        )
        kings_on_main_diagonal = kings_main_diagonal_weight * (
            count_bits(WP & K & MAIN_DIAGONAL) - count_bits(BP & K & MAIN_DIAGONAL)
        )
        men_on_side_diagonals = men_side_diagonals_weight * (
            count_bits(WP & ~K & DOUBLE_DIAGONAL)
            - count_bits(BP & ~K & DOUBLE_DIAGONAL)
        )

        EVAL = (
            piece_count_score
            + back_row_score
            + capture_safety_score
            + center_score
            + men_with_backwards_backup
            + mobility_score
            + kings_on_main_diagonal
            + men_on_side_diagonals
            + verge_of_kinging
        )

        return int(EVAL)


# ----------------- ************* -----------------
# ----------------- OLD HEURISTIC -----------------
# ----------------- ************* -----------------


# def old_heuristic(WP, BP, K, turn=None):
#     # White aims to maximize this score while black aims to minimize it.

#     num_total_pieces = count_bits(WP) + count_bits(
#         BP
#     )  # Total number of pieces on the board.

#     # Count the number of each type of piece for white and black.
#     num_white_man = count_bits(WP & ~K & MASK_32)
#     num_white_king = count_bits(WP & K & MASK_32)
#     num_black_man = count_bits(BP & ~K & MASK_32)
#     num_black_king = count_bits(BP & K & MASK_32)

#     # Piece value weights should reflect the importance of kings over men.
#     piece_count_score = (500 * num_white_man + 750 * num_white_king) - (
#         500 * num_black_man + 750 * num_black_king
#     )

#     # Sum of the chebychev distances"
#     if num_total_pieces < 6:
#         EVAL = 0
#         sum_chebychev_distance = calculate_sum_distances(WP, BP)
#         if piece_count_score > 0:  # White has more weighted material.
#             EVAL = (
#                 50 * sum_chebychev_distance
#             )  # White wants to minimize chevychev distance and get closer to black.

#         elif piece_count_score < 0:  # Black has more weighted material.
#             EVAL = (
#                 50 * sum_chebychev_distance
#             )  # White wants to maximize chevychev distance and get further from black.
#         else:
#             # If the piece count is equal the player with more mobility should have the advantage. This will prevent giving up and forcing draws if/when applicable.
#             EVAL = 50 * mobility_diff_score(WP, BP, K)
#         return int(EVAL)
#     else:
#         # Mobility is defined as a weighted sum of the number of simple and jump moves white has vs. black. More mobility generally means more options.
#         mobility_score = 250 * mobility_diff_score(
#             WP, BP, K, jw=4
#         )  # jw is the weight of jumps vs. simple moves.

#         # As the game progresses, the back row's importance diminishes since it prevents kinging.
#         # Early game, it is important to control the back row to prevent the opponent from kinging.
#         back_row_importance = (
#             num_total_pieces / 24
#         )  # Tapers off as the number of pieces decreases.
#         back_row_score = (
#             50
#             * back_row_importance
#             * (
#                 count_bits(
#                     WP & ~K & MASK_32 & KING_ROW_BLACK
#                 )  # Number of white pieces on the 8th rank.
#                 - count_bits(
#                     BP & ~K & MASK_32 & KING_ROW_WHITE
#                 )  # Number of black pieces on the 1st rank.
#             )
#         )

#         # Refects the tradeoff between capturing and being captured wrt. the current turn.
#         capture_safety_score = 0
#         if turn == PlayerTurn.WHITE:
#             capture_safety_score += count_black_pieces_that_can_be_captured_by_white(
#                 WP, BP, K
#             )  # White wants to capture as MANY black pieces as he can by MAXIMIZING this score.
#         else:  # turn == PlayerTurn.BLACK
#             capture_safety_score -= count_white_pieces_that_can_be_captured_by_black(
#                 WP, BP, K
#             )  # Black is wants to capture as MANY white pieces as he can by MINIMIZING this score.

#         # Center control is crucial in the opening and mid-game for mobility and kinging paths.
#         center_control_importance = (
#             num_total_pieces / 24
#         )  # Tapers off as the number of pieces decreases.
#         center_score = (
#             50
#             * center_control_importance
#             * (
#                 count_bits(WP & CENTER_8 & MASK_32)
#                 - count_bits(BP & CENTER_8 & MASK_32)
#             )
#         )

#         # Kings positioned on the main diagonal can control more squares.
#         kings_on_main_diagonal = 20 * (
#             count_bits(WP & K & MAIN_DIAGONAL) - count_bits(BP & K & MAIN_DIAGONAL)
#         )

#         # Men on side diagonals are less likely to be captured but also have reduced mobility.
#         men_on_side_diagonals = 10 * (
#             count_bits(WP & ~K & DOUBLE_DIAGONAL)
#             - count_bits(BP & ~K & DOUBLE_DIAGONAL)
#         )

#         # Combine all evaluations into a final score.

#         EVAL = (
#             piece_count_score
#             + back_row_score
#             + capture_safety_score
#             + center_score
#             + mobility_score
#             + kings_on_main_diagonal
#             + men_on_side_diagonals
#         )

#         return int(EVAL)


def old_heuristic(WP, BP, K, turn=None):
    num_white_man = count_bits(WP & ~K & MASK_32)
    num_white_king = count_bits(WP & K & MASK_32)
    num_black_man = count_bits(BP & ~K & MASK_32)
    num_black_king = count_bits(BP & K & MASK_32)

    piece_count_score = (500 * num_white_man + 775 * num_white_king) - (
        500 * num_black_man + 775 * num_black_king
    )

    back_row = 200 * (count_bits(WP & MASK_32) - count_bits(BP & MASK_32))

    capture_score = 100 * (
        count_black_pieces_that_can_be_captured_by_white(WP, BP, K)
        - count_white_pieces_that_can_be_captured_by_black(  # white wants to maximize this
            WP, BP, K
        )
    )

    return piece_count_score + back_row + capture_score


# ----------------- ************* -----------------
# ---------------  HELPER FUNCTIONS -----------------
# ----------------- ************* -----------------


def pieces_on_verge_of_kinging(WP, BP, K):
    # Create a bitboard for empty squares
    empty_squares = ~(WP | BP) & MASK_32

    # Get all white and black piece positions on the verge of kinging
    black_verge_positions = find_set_bits(BP & ~K & MASK_32 & RANK7)
    white_verge_positions = find_set_bits(WP & ~K & MASK_32 & RANK2)

    # Check for unblocked paths for each black and white piece
    unblocked_black_verge = [
        pos
        for pos in black_verge_positions
        if (
            (
                BLACK_NORTHEAST.get(pos) is not None
                and is_set(empty_squares, BLACK_NORTHEAST.get(pos))
            )
            or (
                BLACK_NORTHWEST.get(pos) is not None
                and is_set(empty_squares, BLACK_NORTHWEST.get(pos))
            )
        )
    ]
    unblocked_white_verge = [
        pos
        for pos in white_verge_positions
        if (
            (
                WHITE_SOUTHEAST.get(pos) is not None
                and is_set(empty_squares, WHITE_SOUTHEAST.get(pos))
            )
            or (
                WHITE_SOUTHWEST.get(pos) is not None
                and is_set(empty_squares, WHITE_SOUTHWEST.get(pos))
            )
        )
    ]

    # Count the unblocked pieces
    black_verge_count = len(unblocked_black_verge)
    white_verge_count = len(unblocked_white_verge)

    # Return the difference in count
    val = white_verge_count - black_verge_count
    return val


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
    white_simple_moves = (
        generate_simple_moves_white(WP, BP, K, white_movers) if white_movers else []
    )
    black_simple_moves = (
        generate_simple_moves_black(BP, WP, K, black_movers) if black_movers else []
    )
    white_jump_sequences = (
        all_jump_sequences(WP, BP, K, white_jumpers, None, player=PlayerTurn.WHITE)
        if white_jumpers
        else []
    )
    black_jump_sequences = (
        all_jump_sequences(WP, BP, K, None, black_jumpers, player=PlayerTurn.BLACK)
        if black_jumpers
        else []
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


def calculate_total_distance_to_promotion_white(bitboard, K):
    """
    Calculates the sum of the distances of all pieces on the bitboard to the promotion line.
    """
    distance_sum = 0
    for index in find_set_bits(bitboard & ~K):
        if bitboard & (1 << index) & MASK_32:
            # Calculate the row by dividing by 4 (since 4 cells per row)
            row = index // 4
            # Distance to promotion is 7 minus the row number
            distance = 7 - row
            distance_sum += max(
                0, distance
            )  # Ensure distance is not negative for already promoted pieces

    return distance_sum


def calculate_total_distance_to_promotion_black(bitboard, K):
    """
    Calculates the sum of the distances of all pieces on the bitboard to the promotion line.
    """
    distance_sum = 0
    for index in find_set_bits(bitboard & ~K):
        if bitboard & (1 << index) & MASK_32:
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


def count_black_pieces_that_can_be_captured_by_white(
    WP, BP, K, kinged_mult=1, land_edge_mult=1, took_king_mult=1
):
    # Get white's jump sequences (potential captures)
    if get_jumpers_white(WP, BP, K) == 0:
        return 0
    white_jump_sequences = all_jump_sequences(
        WP, BP, K, get_jumpers_white(WP, BP, K), None, player=PlayerTurn.WHITE
    )

    capturable_pieces = set()
    mult = 1
    for sequence in white_jump_sequences:
        if sequence[-1] in [
            0,
            1,
            2,
            3,
        ] and is_set(
            WP & ~K & MASK_32, sequence[0]
        ):  # white man started the jump seq and ended on the back row and became a king
            mult += kinged_mult
        if len(sequence) == 2:  # single jump
            capturable_pieces.add(find_jumped_pos(sequence[0], sequence[1]))
            if sequence[-1] in [
                0,
                1,
                2,
                3,
                7,
                15,
                23,
                31,
                30,
                29,
                28,
                24,
                16,
                8,
            ]:  # land on edge
                mult += land_edge_mult
            if is_set(BP & K, sequence[-1]):
                mult += took_king_mult
        else:  # more than one jump
            pairs = [[sequence[i], sequence[i + 1]] for i in range(len(sequence) - 1)]
            for sequence in pairs:
                capturable_pieces.add(find_jumped_pos(sequence[0], sequence[1]))
            if sequence[-1] in [
                0,
                1,
                2,
                3,
                7,
                15,
                23,
                31,
                30,
                29,
                28,
                24,
                16,
                8,
            ]:  # land on edge
                mult += land_edge_mult
            for s in sequence[1 : len(sequence) - 1]:
                if is_set(BP & K, s):
                    mult += took_king_mult

    return mult * len(
        capturable_pieces
    )  # number of unique black pieces that can be captured by white in the next turn


def count_white_pieces_that_can_be_captured_by_black(
    WP, BP, K, kinged_mult=1, land_edge_mult=1, took_king_mult=1
):
    # Get white's jump sequences (potential captures)
    if get_jumpers_black(WP, BP, K) == 0:
        return 0

    black_jump_sequences = all_jump_sequences(
        WP, BP, K, None, get_jumpers_black(WP, BP, K), player=PlayerTurn.BLACK
    )

    # Count the unique pieces that can be captured by white in the next turn
    # A set is used to ensure each piece is only counted once, even if it can be captured in multiple ways.
    capturable_pieces = set()
    mult = 1
    for sequence in black_jump_sequences:
        if sequence[-1] in [
            28,
            29,
            30,
            31,
        ] and is_set(
            BP & ~K & MASK_32, sequence[0]
        ):  # a black man started the jump seq and ended on the back row and became a king
            mult = kinged_mult
        if len(sequence) == 2:
            capturable_pieces.add(find_jumped_pos(sequence[0], sequence[1]))
            if sequence[-1] in [0, 1, 2, 3, 7, 15, 23, 31, 30, 29, 28, 24, 16, 8]:
                mult += land_edge_mult
            if is_set(WP & K, sequence[-1]):
                mult += took_king_mult
        else:
            pairs = [[sequence[i], sequence[i + 1]] for i in range(len(sequence) - 1)]
            for sequence in pairs:
                capturable_pieces.add(find_jumped_pos(sequence[0], sequence[1]))
            if sequence[-1] in [0, 1, 2, 3, 7, 15, 23, 31, 30, 29, 28, 24, 16, 8]:
                mult += land_edge_mult
            for s in sequence[1 : len(sequence) - 1]:
                if is_set(WP & K, s):
                    mult += took_king_mult
    return mult * len(
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
    WP, BP, K = get_fresh_board()

    # WP, BP, K = get_fresh_board()
    print_board(WP, BP, K)

    print(evolve_base_B(WP, BP, K, turn=PlayerTurn.BLACK))
