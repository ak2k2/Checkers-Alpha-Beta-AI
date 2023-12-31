import random

from checkers import *
from util.fen_pdn_helper import *
from util.helpers import *
from util.masks import *


def experiment(
    WP,
    BP,
    K,
    turn,
    legal_moves,
    depth,
    global_board_state,
    man_weight=100,
    king_weight=155,
    trading_boost=30,
    king_boost=20,
    home_boost=50,
    center_box=50,
    mid_row=20,
    defend_home_boost=40,
    distance_weight=10,
    safety_weight=5,
    capture_weight=5,
    verge_king_weight=10,
    double_corner_king_reward=20,
):
    EVAL = 0  # evaluation score

    # Board MiniMax is currently looking at.
    num_white_man = count_bits(WP & ~K & MASK_32)
    num_white_king = count_bits(WP & K & MASK_32)
    num_black_man = count_bits(BP & ~K & MASK_32)
    num_black_king = count_bits(BP & K & MASK_32)
    num_wps = num_white_man + num_white_king
    num_bps = num_black_king + num_black_man
    num_local_total_pcs = num_wps + num_bps

    # Board that Players are looking at.
    gwp, gbp, gk = global_board_state
    num_global_white_men = count_bits(gwp & ~gk & MASK_32)
    num_global_black_men = count_bits(gbp & ~gk & MASK_32)
    num_global_white_king = count_bits(gwp & gk & MASK_32)
    num_global_black_king = count_bits(gbp & gk & MASK_32)
    num_global_white_pcs = num_global_white_men + num_global_white_king
    num_global_black_pcs = num_global_black_men + num_global_black_king
    num_global_total_pcs = num_global_white_pcs + num_global_black_pcs

    if not legal_moves:  # Lost game. Terminal State
        if turn == PlayerTurn.WHITE:
            EVAL -= 1000 + (700 - (depth * 20))  # delay loosing, expedite winning
        if turn == PlayerTurn.BLACK:
            EVAL += 1000 + (700 - (depth * 20))
    else:
        if turn == PlayerTurn.WHITE:
            EVAL += (
                count_black_pieces_that_can_be_captured_by_white(  # white wants to capture black
                    WP, BP, K, kinged_mult=6, land_edge_mult=1, took_king_mult=3
                )
                * 10
            )
        if turn == PlayerTurn.BLACK:
            EVAL -= (
                count_white_pieces_that_can_be_captured_by_black(  # black wants to capture white
                    WP, BP, K, kinged_mult=6, land_edge_mult=1, took_king_mult=2
                )
                * 10
            )

    # MATERIAL
    EVAL += (king_weight * (num_white_king - num_black_king)) + (
        man_weight * (num_white_man - num_black_man)
    )

    # ENDGAME
    if (
        (num_global_total_pcs <= 10)
        or (
            num_global_white_pcs * (2 / 3) >= num_global_black_pcs
        )  # black is loosing badly
        or (
            num_global_black_pcs * (2 / 3) >= num_global_white_pcs
        )  # white is loosing badly
        or (
            (num_global_total_pcs <= 14)
            and (abs(num_global_white_king - num_global_black_king) > 0)
        )  # quasi endgame
    ):
        EVAL = 0
        # Encourage trading when ahead
        if (num_global_white_pcs > num_global_black_pcs) and (
            num_wps > num_bps
        ):  # white is ahead
            EVAL += (num_global_total_pcs - num_local_total_pcs) * trading_boost
            EVAL -= (
                calculate_sum_distances(WP, BP, K) * distance_weight
            )  # white is penalized for being far from black
            EVAL -= double_corner_king_reward * count_bits(
                BP & K & MASK_32 & DOUBLE_CORNER
            )  # black is rewarded for having kings on double corner
        elif (num_global_black_pcs > num_global_white_pcs) and (
            num_bps > num_bps
        ):  # black is ahead
            EVAL -= (num_global_total_pcs - num_local_total_pcs) * trading_boost
            EVAL += (
                calculate_sum_distances(WP, BP, K) * distance_weight
            )  # black is penalized for being far from white
            EVAL += double_corner_king_reward * count_bits(
                WP & K & MASK_32 & DOUBLE_CORNER
            )  # white is rewarded for having kings on double corner

        EVAL += num_white_king * king_boost
        EVAL -= num_black_king * king_boost

        if not legal_moves:  # Lost game. Terminal State
            if turn == PlayerTurn.WHITE:
                EVAL -= 1000 + (700 - (depth * 20))  # delay loosing, expedite winning
            if turn == PlayerTurn.BLACK:
                EVAL += 1000 + (700 - (depth * 20))

    else:  # OPENING & MID GAME
        # HOME ROW
        white_home = count_bits(WP & MASK_32 & KING_ROW_BLACK)
        black_home = count_bits(BP & MASK_32 & KING_ROW_WHITE)

        # MID BOX
        white_center_box = count_bits(WP & MASK_32 & CENTER_8)
        black_center_box = count_bits(BP & MASK_32 & CENTER_8)

        # MID_ROW_NOT_MID_BOX
        white_mid_row = count_bits(WP & MASK_32 & MID_ROW_NOT_MID_BOX)
        black_mid_row = count_bits(BP & MASK_32 & MID_ROW_NOT_MID_BOX)

        EVAL += (
            (white_home * home_boost)
            + (white_center_box * center_box)
            + (white_mid_row * mid_row)
        )
        EVAL -= (
            (black_home * home_boost)
            + (black_center_box * center_box)
            + (black_mid_row * mid_row)
        )

        if num_black_man > 0:  # black still has men
            EVAL += defend_home_boost * white_home  # white should stay home

        if num_white_man > 0:  # white still has men
            EVAL -= defend_home_boost * black_home  # black should stay home

        # SAFETY SCORE
        EVAL += safety_weight * (
            calculate_safe_white_pieces(WP, K) - calculate_safe_black_pieces(BP, K)
        )

        # CAPTURE SCORE
        EVAL += capture_weight * (
            count_black_pieces_that_can_be_captured_by_white(
                WP, BP, K, kinged_mult=6, land_edge_mult=1, took_king_mult=3
            )
            - count_white_pieces_that_can_be_captured_by_black(
                WP, BP, K, kinged_mult=6, land_edge_mult=1, took_king_mult=2
            )
        )

        # VERGE KINGING
        EVAL += verge_king_weight * pieces_on_verge_of_kinging(WP, BP, K, turn=turn)

        # DISTANCE TO KINGS ROW
        EVAL += distance_weight * (
            calculate_total_distance_to_promotion_black(BP, K)
            - calculate_total_distance_to_promotion_white(WP, K)
        )

    EVAL += random.randint(-5, 5)

    return EVAL


def smart(WP, BP, K, turn, legal_moves, depth, global_board_state):
    # Board MiniMax is currently looking at.
    num_white_man = count_bits(WP & ~K & MASK_32)
    num_white_king = count_bits(WP & K & MASK_32)
    num_black_man = count_bits(BP & ~K & MASK_32)
    num_black_king = count_bits(BP & K & MASK_32)
    num_wps = num_white_man + num_white_king
    num_bps = num_black_king + num_black_man
    num_local_total_pcs = num_wps + num_bps

    # Board that Players are looking at.
    gwp, gbp, gk = global_board_state
    num_global_white_men = count_bits(gwp & ~gk & MASK_32)
    num_global_black_men = count_bits(gbp & ~gk & MASK_32)
    num_global_white_king = count_bits(gwp & gk & MASK_32)
    num_global_black_king = count_bits(gbp & gk & MASK_32)
    num_global_white_pcs = num_global_white_men + num_global_white_king
    num_global_black_pcs = num_global_black_men + num_global_black_king
    num_global_total_pcs = num_global_white_pcs + num_global_black_pcs

    EVAL = 0
    # MATERIAL
    EVAL += (155 * (num_white_king - num_black_king)) + (
        100 * (num_white_man - num_black_man)
    )

    if not legal_moves:  # delay loosing, expedite winning
        if turn == PlayerTurn.WHITE:
            EVAL -= 500 + (700 - (depth * 10))
        if turn == PlayerTurn.BLACK:
            EVAL += 500 + (700 - (depth * 10))

    # HOME ROW
    white_home = count_bits(
        WP & MASK_32 & KING_ROW_BLACK
    )  # white men or kings on home row
    black_home = count_bits(
        BP & MASK_32 & KING_ROW_WHITE
    )  # black men or kings on home row

    # MID BOX
    white_center_box = count_bits(WP & MASK_32 & CENTER_8)
    black_center_box = count_bits(BP & MASK_32 & CENTER_8)

    # MID_ROW_NOT_MID_BOX
    white_mid_row = count_bits(WP & MASK_32 & MID_ROW_NOT_MID_BOX)
    black_mid_row = count_bits(BP & MASK_32 & MID_ROW_NOT_MID_BOX)

    # ENDGAME
    if (
        (num_global_total_pcs <= 10)
        or (
            num_global_white_pcs * (2 / 3) >= num_global_black_pcs
        )  # black is loosing badly
        or (
            num_global_black_pcs * (2 / 3) >= num_global_white_pcs
        )  # white is loosing badly
        or (
            (num_global_total_pcs <= 14)
            and (abs(num_global_white_king - num_global_black_king) > 0)
        )  # quasi endgame
    ):
        # Encourage trading when ahead
        if (num_global_white_pcs > num_global_black_pcs) and (num_wps > num_bps):
            EVAL += (num_global_total_pcs - num_local_total_pcs) * 30
        if (num_global_black_pcs > num_global_white_pcs) and (num_bps > num_bps):
            EVAL -= (num_global_total_pcs - num_local_total_pcs) * 30

        EVAL += num_white_king * 20  # Kings more valuable in endgame
        EVAL -= num_black_king * 20

    else:  # OPENING/MID GAME
        EVAL += (white_home * 50) + (white_center_box * 50) + (white_mid_row * 10)
        EVAL -= (black_home * 50) + (black_center_box * 50) + (black_mid_row * 10)

    if num_global_black_pcs > 0:  # black still has men
        EVAL += 40 * white_home  # white should stay home

    if num_global_white_pcs > 0:  # white still has men
        EVAL -= 40 * black_home  # black should stay home

    EVAL += random.randint(-5, 5)

    return EVAL


# def new_heuristic(
#     WP,
#     BP,
#     K,
#     turn=None,
#     legal_moves=None,  # for cross compatability
#     depth=None,  # for cross compatability
#     global_board_state=None,  # for cross compatability
#     man_weight=537,
#     man_growth_decay=-0.4281918179959601,
#     king_weight=767,
#     king_growth_decay=0.38566206457925264,
#     back_row_weight=433,
#     back_growth_decay=-0.5293593518395029,
#     capture_weight=28,
#     capture_growth_decay=0.8371176184178525,
#     kinged_mult=2.5855513945298725,
#     land_edge_mult=2.9632331840446833,
#     took_king_mult=3.967469205341885,
#     distance_weight=94,
#     distance_growth_decay=0.41113123717822037,
#     mobility_weight=28,
#     mobility_jump_mult=2.475480348594868,
#     mobility_growth_decay=0.47741446189421444,
#     safety_weight=306,
#     safety_growth_decay=0.44064305472191034,
#     double_corner_bonus_weight=85,
#     turn_advantage_weight=110,
#     verge_weight=100,
#     verge_growth_decay=0.43223139573530184,
#     center_control_weight=183,
#     edge_weight=-66,
#     edge_growth_decay=0.30257399572546806,
#     kings_row_weight=4,
#     kings_row_growth_decay=-0.09583188804846465,
# ):
#     num_white_man = count_bits(WP & ~K & MASK_32)
#     num_white_king = count_bits(WP & K & MASK_32)
#     num_black_man = count_bits(BP & ~K & MASK_32)
#     num_black_king = count_bits(BP & K & MASK_32)
#     num_total_pieces = count_bits(WP) + count_bits(BP)
#     SUM_DISTANCE = 0
#     DOUBLE_CORNER_BONUS = 0
#     opening_thresh = 18
#     endgame_threshold = 6

#     man_adj_w = adjustment_factor(num_total_pieces, man_growth_decay) * man_weight
#     king_adj_w = adjustment_factor(num_total_pieces, king_growth_decay) * king_weight

#     PIECE_COUNT = (king_adj_w * (num_white_king - num_black_king)) + (
#         man_adj_w * (num_white_man - num_black_man)
#     )

#     back_row_adj_w = (
#         adjustment_factor(num_total_pieces, back_growth_decay) * back_row_weight
#     )

#     # added additional back row decay to make it less important in the mid/endgame
#     BACK_ROW = (
#         (num_total_pieces / 24)
#         * back_row_adj_w
#         * (
#             count_bits(WP & MASK_32 & KING_ROW_BLACK)  # WHITE HOME ROW
#             - count_bits(BP & MASK_32 & KING_ROW_WHITE)  # BLACK HOME ROW
#         )
#     )

#     capture_adj_w = (
#         adjustment_factor(num_total_pieces, capture_growth_decay) * capture_weight
#     )

#     CAPTURE = capture_adj_w * (
#         count_black_pieces_that_can_be_captured_by_white(WP, BP, K, 0, 0, 0)
#         - count_white_pieces_that_can_be_captured_by_black(  # white wants to maximize this
#             WP, BP, K, 0, 0, 0
#         )
#     )

#     mobility_adj_w = (
#         adjustment_factor(num_total_pieces, mobility_growth_decay) * mobility_weight
#     )

#     MOBILITY = mobility_adj_w * mobility_diff_score(WP, BP, K, jw=mobility_jump_mult)

#     safety_adj_w = (
#         adjustment_factor(num_total_pieces, safety_growth_decay) * safety_weight
#     )

#     SAFETY_SCORE = safety_adj_w * (
#         calculate_safe_white_pieces(WP, K) - calculate_safe_black_pieces(BP, K)
#     )

#     if turn == PlayerTurn.WHITE:
#         num_captures = count_black_pieces_that_can_be_captured_by_white(
#             WP, BP, K, kinged_mult, land_edge_mult, took_king_mult
#         )
#         TURN_ADVANTAGE = num_captures * turn_advantage_weight
#     else:
#         num_captures = count_white_pieces_that_can_be_captured_by_black(
#             WP, BP, K, kinged_mult, land_edge_mult, took_king_mult
#         )
#         TURN_ADVANTAGE = -1 * num_captures * turn_advantage_weight

#     verge_king_adj_w = (
#         adjustment_factor(num_total_pieces, verge_growth_decay) * verge_weight
#     )
#     VERGE_KINGING = verge_king_adj_w * pieces_on_verge_of_kinging(WP, BP, K, turn=turn)

#     edge_adj_w = adjustment_factor(num_total_pieces, edge_growth_decay) * edge_weight

#     EDGE_CONTROL = edge_adj_w * (
#         count_bits(WP & EDGES & MASK_32) - count_bits(BP & EDGES & MASK_32)
#     )

#     if (
#         num_total_pieces <= opening_thresh and num_total_pieces >= endgame_threshold
#     ):  # MIDGAME
#         kings_row_adj_w = (
#             adjustment_factor(num_total_pieces, kings_row_growth_decay)
#             * kings_row_weight
#         )
#         DISTANCE_TO_KINGS_ROW = kings_row_adj_w * (
#             calculate_total_distance_to_promotion_black(BP, K)
#             - calculate_total_distance_to_promotion_white(WP, K)
#         )
#     else:
#         DISTANCE_TO_KINGS_ROW = 0

#     if num_total_pieces >= opening_thresh:  # OPENING
#         CENTER_CONTROL = (
#             count_bits(WP & CENTER_8) - count_bits(BP & CENTER_8)
#         ) * center_control_weight
#     else:
#         CENTER_CONTROL = 0

#     if num_total_pieces <= endgame_threshold:  # ENDGAME / MAJORITY LOSS
#         if num_white_king > num_black_king:  # white has more kings
#             distance_adj_w = (
#                 adjustment_factor(num_total_pieces, distance_weight)
#                 * distance_growth_decay
#             ) * distance_weight

#             SUM_DISTANCE = (
#                 -1 * distance_adj_w * calculate_sum_distances(WP, BP)
#             )  # white wants to minimize chevychev distance and get closer to black.

#             DOUBLE_CORNER_BONUS = (
#                 -1
#                 * count_bits(  # black wants to maximize number of kings on double corner
#                     BP & K & DOUBLE_CORNER & MASK_32
#                 )
#                 * double_corner_bonus_weight
#             )

#         elif num_black_king > num_white_king:  # black has more kings
#             distance_adj_w = (
#                 adjustment_factor(num_total_pieces, distance_weight)
#                 * distance_growth_decay
#             ) * distance_weight

#             SUM_DISTANCE = distance_adj_w * calculate_sum_distances(
#                 WP, BP
#             )  # white wants to maximize chevychev distance and get further from black.

#             DOUBLE_CORNER_BONUS = (
#                 count_bits(  # white wants to maximize number of kings on double corner
#                     WP & K & DOUBLE_CORNER & MASK_32
#                 )
#                 * double_corner_bonus_weight
#             )

#     # print(f"PIECE_COUNT: {PIECE_COUNT}")
#     # print(f"BACK_ROW: {BACK_ROW}")
#     # print(f"CAPTURE: {CAPTURE}")
#     # print(f"MOBILITY: {MOBILITY}")
#     # print(f"SAFETY_SCORE: {SAFETY_SCORE}")
#     # print(f"TURN_ADVANTAGE: {TURN_ADVANTAGE}")
#     # print(f"VERGE_KINGING: {VERGE_KINGING}")
#     # print(f"CENTER_CONTROL: {CENTER_CONTROL}")
#     # print(f"EDGE_CONTROL: {EDGE_CONTROL}")
#     # print(f"DISTANCE_TO_KINGS_ROW: {DISTANCE_TO_KINGS_ROW}")
#     # print(f"SUM_DISTANCE: {SUM_DISTANCE}")
#     # print(f"DOUBLE_CORNER_BONUS: {DOUBLE_CORNER_BONUS}")

#     return (
#         PIECE_COUNT
#         + BACK_ROW
#         + CAPTURE
#         + MOBILITY
#         + SAFETY_SCORE
#         + TURN_ADVANTAGE
#         + VERGE_KINGING
#         + CENTER_CONTROL
#         + EDGE_CONTROL
#         + DISTANCE_TO_KINGS_ROW
#         + SUM_DISTANCE
#         + DOUBLE_CORNER_BONUS
#     )


# ----------------- ************* -----------------
# ---------------- HELPER FUNCTIONS -----------------
# ----------------- ************* -----------------


def adjustment_factor(num_pieces, control_float):
    """
    Calculates the growth/decay adjustment factor for the piece count score.

    Args:
    num_pieces (int): The number of pieces currently on the board.
    control_float (float): The control float determining the growth/decay behavior.
        A positive control float produces as positive rate of change for multiplier wrt. number of moves
        A negative control float produces as negative rate of change for multiplier wrt. number of moves
        A control float of 0 produces a constant multiplier wrt. number of moves

    Returns:
    float: The calculated adjustment factor.
    """
    # Ensuring the control_float does not cause extreme changes
    # and avoiding division by zero
    control_float = max(min(control_float, 1), -1)

    # Quadratic relationship for smoother transition
    multiplier = 1 + control_float * (1 - num_pieces / 24) ** 2

    # Cap the multiplier to avoid excessive skewing (optional, adjust as needed)
    # return max(min(multiplier, 2), 0.5)
    return multiplier


def pieces_on_verge_of_kinging(WP, BP, K, turn=None):
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


def bit_to_coordinates(bit_index):
    # Convert the single-dimensional bit index to 2D coordinates,
    # taking into account that the board is only half filled
    # and playable squares are zigzagged.
    x = (bit_index % 4) * 2 + ((bit_index // 4) % 2)
    y = bit_index // 4
    return (x, y)


def calculate_sum_distances(WP, BP, K):
    # distance between all pairs of kings
    total_distance = 0
    for w_index in find_set_bits(WP & K):
        w_coords = bit_to_coordinates(w_index)
        for b_index in find_set_bits(BP & K):
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


def count_black_pieces_that_can_be_captured_by_white(
    WP, BP, K, kinged_mult=1, land_edge_mult=1, took_king_mult=1
):
    white_jumpers = get_jumpers_white(WP, BP, K)

    if white_jumpers == 0:
        return 0

    white_jump_sequences = all_jump_sequences(
        WP, BP, K, white_jumpers, None, player=PlayerTurn.WHITE
    )
    edges = [0, 1, 2, 3, 7, 15, 23, 31, 30, 29, 28, 24, 16, 8]
    king_row_white = [0, 1, 2, 3]

    # Count the unique pieces that can be captured by white in the next turn
    # A set is used to ensure each piece is only counted once, even if it can be captured in multiple ways.
    capturable_pieces = set()
    mult = 1
    for sequence in white_jump_sequences:
        if sequence[-1] in king_row_white and is_set(
            WP & ~K & MASK_32, sequence[0]
        ):  # a white man started the jump seq and ended on the back row and became a king
            mult += kinged_mult
        if len(sequence) == 2:  # single jump
            jumped_pos = find_jumped_pos(sequence[0], sequence[1])
            capturable_pieces.add(jumped_pos)
            if sequence[-1] in edges:  # land on edge
                mult += land_edge_mult
            if is_set(BP & K, jumped_pos):  # white took a black king
                mult += took_king_mult
        else:  # more than one jump
            if sequence[-1] in edges:
                mult += land_edge_mult  # land on edge
            pairs = [[sequence[i], sequence[i + 1]] for i in range(len(sequence) - 1)]
            for p in pairs:
                jumped_pos = find_jumped_pos(p[0], p[1])  # jumped position of the pair
                capturable_pieces.add(jumped_pos)  # add to set
                if is_set(BP & K, jumped_pos):  # took a black king
                    mult += took_king_mult

    mult = max(1, mult)
    return mult * len(capturable_pieces)


def count_white_pieces_that_can_be_captured_by_black(
    WP, BP, K, kinged_mult=1, land_edge_mult=1, took_king_mult=1
):
    # Get blacks's jump sequences (potential captures)
    black_jumpers = get_jumpers_black(WP, BP, K)

    if black_jumpers == 0:
        return 0

    black_jump_sequences = all_jump_sequences(
        WP, BP, K, None, black_jumpers, player=PlayerTurn.BLACK
    )
    edges = [0, 1, 2, 3, 7, 15, 23, 31, 30, 29, 28, 24, 16, 8]
    king_row_black = [28, 29, 30, 31]

    # Count the unique pieces that can be captured by white in the next turn
    # A set is used to ensure each piece is only counted once, even if it can be captured in multiple ways.
    capturable_pieces = set()
    mult = 1
    for sequence in black_jump_sequences:
        if sequence[-1] in king_row_black and is_set(
            BP & ~K & MASK_32, sequence[0]
        ):  # a black man started the jump seq and ended on the back row and became a king
            mult += kinged_mult
        if len(sequence) == 2:  # single jump
            jumped_pos = find_jumped_pos(sequence[0], sequence[1])
            capturable_pieces.add(jumped_pos)
            if sequence[-1] in edges:  # land on edge
                mult += land_edge_mult
            if is_set(WP & K, jumped_pos):  # took a king
                mult += took_king_mult
        else:  # more than one jump
            if sequence[-1] in edges:
                mult += land_edge_mult  # land on edge
            pairs = [[sequence[i], sequence[i + 1]] for i in range(len(sequence) - 1)]
            for p in pairs:
                jumped_pos = find_jumped_pos(p[0], p[1])  # jumped position of the pair
                capturable_pieces.add(jumped_pos)  # add to set
                if is_set(WP & K, jumped_pos):  # took a king
                    mult += took_king_mult

    mult = max(1, mult)
    return mult * len(capturable_pieces)


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


def test1():
    # WP, BP, K = setup_board_from_position_lists(
    #     ["KD6", "KC3", "KF6", "KC1", "KB6"], ["KG1", "KG7", "KH8"]
    # )
    WP, BP, K, _, _ = load_game_from_sable_file("src/boards/sample-cb3.txt")

    # WP, BP, K = get_fresh_board()
    print_board(WP, BP, K)

    print(
        new_heuristic(WP, BP, K, turn=PlayerTurn.BLACK)
    )  # it should be negative for black
    print("----------------------------------------")
    print(
        new_heuristic(WP, BP, K, turn=PlayerTurn.WHITE)
    )  # it should be positive for white

    print(adjustment_factor(10, -1))


# test1()


def test2():
    WP, BP, K = setup_board_from_position_lists(
        ["D4", "F4", "KD2", "D6", "F6"], ["KC5", "E5", "KG3"]
    )

    print_board(WP, BP, K)

    print(
        f"BLACK TO MOVE: {smart(WP, BP, K, turn=PlayerTurn.BLACK, depth=1, legal_moves=generate_legal_moves(WP,BP,K, turn=PlayerTurn.BLACK), global_board_state=get_fresh_board())}"
    )  # it should be negative for black
    print("-" * 20)
    print(
        f"WHITE TO MOVE: {smart(WP, BP, K, turn=PlayerTurn.WHITE, depth=1, legal_moves=generate_legal_moves(WP,BP,K, turn=PlayerTurn.WHITE), global_board_state=get_fresh_board())}"
    )


if __name__ == "__main__":
    WP, BP, K = setup_board_from_position_lists(
        ["D4", "F4", "KD2", "D6", "F6"], ["KC5", "E5", "KG3", "KH8"]
    )

    print_board(WP, BP, K)
    print(
        experiment(
            WP,
            BP,
            K,
            turn=PlayerTurn.BLACK,
            depth=1,
            legal_moves=generate_legal_moves(WP, BP, K, turn=PlayerTurn.BLACK),
            global_board_state=get_fresh_board(),
        )
    )
