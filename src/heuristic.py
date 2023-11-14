import random

from checkers import *
from util.fen_pdn_helper import *
from util.helpers import *
from util.masks import *


def new_heuristic(WP, BP, K, turn=None):
    return 100 * (count_bits(WP) - count_bits(BP)) + random.randint(0, 10)


def evolve_base_B(
    WP,
    BP,
    K,
    turn=None,
    man_weight=846,
    man_growth_decay=-0.06391419392169503,
    king_weight=1998,
    king_growth_decay=0.5338273313800478,
    back_row_weight=355,
    back_growth_decay=-0.9656932017524094,
    capture_weight=150,
    capture_growth_decay=0.6101024153593047,
    kinged_mult=2.6491261712071887,
    land_edge_mult=3.2985404559984834,
    took_king_mult=2.3723031948039734,
    distance_weight=20,  # make this optimal for endgame
    distance_growth_decay=1.0,
    mobility_weight=18,
    mobility_jump_mult=2.0325348153712053,
    mobility_growth_decay=-0.5104406412313335,
    safety_weight=61,
    safety_growth_decay=0.6296397316731904,
    double_corner_bonus_weight=43,
    endgame_threshold=7,
    turn_advantage_weight=397,
    majority_loss_weight=0,
    verge_weight=24,
    verge_growth_decay=-0.8782934201475908,
    opening_thresh=23,
    center_control_weight=66,
    edge_weight=-103,
    edge_growth_decay=-0.3049190835985922,
    kings_row_weight=198,
    kings_row_growth_decay=-0.4284882105970266,
):
    num_white_man = count_bits(WP & ~K & MASK_32)
    num_white_king = count_bits(WP & K & MASK_32)
    num_black_man = count_bits(BP & ~K & MASK_32)
    num_black_king = count_bits(BP & K & MASK_32)
    num_total_pieces = count_bits(WP) + count_bits(BP)
    SUM_DISTANCE = 0
    DOUBLE_CORNER_BONUS = 0

    man_adj_w = adjustment_factor(num_total_pieces, man_growth_decay) * man_weight
    king_adj_w = adjustment_factor(num_total_pieces, king_growth_decay) * king_weight

    PIECE_COUNT = (king_adj_w * (num_white_king - num_black_king)) + (
        man_adj_w * (num_white_man - num_black_man)
    )

    back_row_adj_w = (
        adjustment_factor(num_total_pieces, back_growth_decay) * back_row_weight
    )

    BACK_ROW = back_row_adj_w * (
        count_bits(WP & MASK_32 & KING_ROW_BLACK)  # WHITE HOME ROW
        - count_bits(BP & MASK_32 & KING_ROW_WHITE)  # BLACK HOME ROW
    )

    capture_adj_w = (
        adjustment_factor(num_total_pieces, capture_growth_decay) * capture_weight
    )

    CAPTURE = capture_adj_w * (
        count_black_pieces_that_can_be_captured_by_white(WP, BP, K, 0, 0, 0)
        - count_white_pieces_that_can_be_captured_by_black(  # white wants to maximize this
            WP, BP, K, 0, 0, 0
        )
    )

    mobility_adj_w = (
        adjustment_factor(num_total_pieces, mobility_growth_decay) * mobility_weight
    )

    MOBILITY = mobility_adj_w * mobility_diff_score(WP, BP, K, jw=mobility_jump_mult)

    safety_adj_w = (
        adjustment_factor(num_total_pieces, safety_growth_decay) * safety_weight
    )

    SAFETY_SCORE = safety_adj_w * (
        calculate_safe_white_pieces(WP, K) - calculate_safe_black_pieces(BP, K)
    )

    if turn == PlayerTurn.WHITE:
        num_captures = count_black_pieces_that_can_be_captured_by_white(
            WP, BP, K, kinged_mult, land_edge_mult, took_king_mult
        )
        TURN_ADVANTAGE = num_captures * turn_advantage_weight
    else:
        num_captures = count_white_pieces_that_can_be_captured_by_black(
            WP, BP, K, kinged_mult, land_edge_mult, took_king_mult
        )
        TURN_ADVANTAGE = -1 * num_captures * turn_advantage_weight

    verge_king_adj_w = (
        adjustment_factor(num_total_pieces, verge_growth_decay) * verge_weight
    )
    VERGE_KINGING = verge_king_adj_w * pieces_on_verge_of_kinging(WP, BP, K, turn=turn)

    edge_adj_w = adjustment_factor(num_total_pieces, edge_growth_decay) * edge_weight
    EDGE_CONTROL = edge_adj_w * (
        count_bits(WP & EDGES & MASK_32) - count_bits(BP & EDGES & MASK_32)
    )

    if (
        num_total_pieces <= opening_thresh and num_total_pieces >= endgame_threshold
    ):  # MIDGAME
        kings_row_adj_w = (
            adjustment_factor(num_total_pieces, kings_row_growth_decay)
            * kings_row_weight
        )
        DISTANCE_TO_KINGS_ROW = kings_row_adj_w * (
            calculate_total_distance_to_promotion_black(BP, K)
            - calculate_total_distance_to_promotion_white(WP, K)
        )
    else:
        DISTANCE_TO_KINGS_ROW = 0

    loosing_substantially = (num_black_man + num_black_king) < (
        majority_loss_weight * (num_white_man + num_white_king)
    ) or (num_white_man + num_white_king) < (
        majority_loss_weight * (num_black_man + num_black_king)
    )

    if num_total_pieces >= opening_thresh:  # OPENING
        CENTER_CONTROL = (
            count_bits(WP & CENTER_8) - count_bits(BP & CENTER_8)
        ) * center_control_weight
    else:
        CENTER_CONTROL = 0

    if (
        num_total_pieces <= endgame_threshold or loosing_substantially
    ):  # ENDGAME / MAJORITY LOSS
        if num_white_king > num_black_king:  # white has more kings
            distance_adj_w = (
                adjustment_factor(num_total_pieces, distance_weight)
                * distance_growth_decay
            ) * distance_weight

            SUM_DISTANCE = (
                -1 * distance_adj_w * calculate_sum_distances(WP, BP)
            )  # white wants to minimize chevychev distance and get closer to black.

            DOUBLE_CORNER_BONUS = (
                -1
                * count_bits(  # black wants to maximize number of kings on double corner
                    BP & K & DOUBLE_CORNER & MASK_32
                )
                * double_corner_bonus_weight
            )

        elif num_black_king > num_white_king:  # black has more kings
            distance_adj_w = (
                adjustment_factor(num_total_pieces, distance_weight)
                * distance_growth_decay
            ) * distance_weight

            SUM_DISTANCE = distance_adj_w * calculate_sum_distances(
                WP, BP
            )  # white wants to maximize chevychev distance and get further from black.

            DOUBLE_CORNER_BONUS = (
                count_bits(  # white wants to maximize number of kings on double corner
                    WP & K & DOUBLE_CORNER & MASK_32
                )
                * double_corner_bonus_weight
            )

    # print(f"PIECE_COUNT: {PIECE_COUNT}")
    # print(f"BACK_ROW: {BACK_ROW}")
    # print(f"CAPTURE: {CAPTURE}")
    # print(f"MOBILITY: {MOBILITY}")
    # print(f"SAFETY_SCORE: {SAFETY_SCORE}")
    # print(f"TURN_ADVANTAGE: {TURN_ADVANTAGE}")
    # print(f"VERGE_KINGING: {VERGE_KINGING}")
    # print(f"CENTER_CONTROL: {CENTER_CONTROL}")
    # print(f"EDGE_CONTROL: {EDGE_CONTROL}")
    # print(f"DISTANCE_TO_KINGS_ROW: {DISTANCE_TO_KINGS_ROW}")
    # print(f"SUM_DISTANCE: {SUM_DISTANCE}")
    # print(f"DOUBLE_CORNER_BONUS: {DOUBLE_CORNER_BONUS}")

    return (
        PIECE_COUNT
        + BACK_ROW
        + CAPTURE
        + MOBILITY
        + SAFETY_SCORE
        + TURN_ADVANTAGE
        + VERGE_KINGING
        + CENTER_CONTROL
        + EDGE_CONTROL
        + DISTANCE_TO_KINGS_ROW
        + SUM_DISTANCE
        + DOUBLE_CORNER_BONUS
    )


# ----------------- ************* -----------------
# ----------------- OLD HEURISTIC -----------------
# ----------------- ************* -----------------


# def old_heuristic(WP, BP, K, turn=None):  # trusty old heuristic
#     num_white_man = count_bits(WP & ~K & MASK_32)
#     num_white_king = count_bits(WP & K & MASK_32)
#     num_black_man = count_bits(BP & ~K & MASK_32)
#     num_black_king = count_bits(BP & K & MASK_32)
#     piece_count_score = (500 * num_white_man + 775 * num_white_king) - (
#         500 * num_black_man + 775 * num_black_king
#     )
#     return piece_count_score + random.randint(-20, 20)


def old_heuristic(WP, BP, K, turn=None):
    num_white_man = count_bits(WP & ~K & MASK_32)
    num_white_king = count_bits(WP & K & MASK_32)
    num_black_man = count_bits(BP & ~K & MASK_32)
    num_black_king = count_bits(BP & K & MASK_32)

    piece_count_score = (500 * num_white_man + 775 * num_white_king) - (
        500 * num_black_man + 775 * num_black_king
    )

    back_row = 400 * (count_bits(WP & MASK_32) - count_bits(BP & MASK_32))

    # mobility_score = mobility_diff_score(WP, BP, K)
    # promotion_score = calculate_total_distance_to_promotion_white(
    #     WP & ~K
    # ) - calculate_total_distance_to_promotion_black(BP & ~K)

    # chebychev_distance = calculate_sum_distances(WP, BP)

    capture_score = 300 * count_black_pieces_that_can_be_captured_by_white(
        WP, BP, K
    ) - count_white_pieces_that_can_be_captured_by_black(  # white wants to maximize this
        WP, BP, K
    )

    return piece_count_score + back_row + capture_score


# def old_heuristic(
#     WP,
#     BP,
#     K,
#     turn=None,
#     man_weight=830.626813121065,
#     man_growth_decay=0.6626220134649203,
#     king_weight=2089.0576481578714,
#     king_growth_decay=-0.4044765517723363,
#     back_row_weight=371.2937563800801,
#     back_growth_decay=-0.27626818177029244,
#     capture_weight=53.60771469653369,
#     capture_growth_decay=0.5937019448758429,
#     kinged_mult=3.092120706449105,
#     land_edge_mult=3.329843409771888,
#     took_king_mult=1.1541559965005888,
#     distance_weight=30.455963377434735,
#     distance_growth_decay=0.6346339022307796,
#     mobility_weight=330.7892809568642,
#     mobility_jump_mult=5.380924824632848,
#     mobility_growth_decay=-0.2881193486220337,
#     safety_weight=7.875583635868932,
#     safety_growth_decay=0.011471137839038414,
#     double_corner_bonus_weight=233.14698595613837,
#     endgame_threshold=9,
#     turn_advantage_weight=177.56687320354825,
#     majority_loss_weight=0.36600752102404854,
#     verge_weight=81.00234807852138,
#     verge_growth_decay=0.031220778542601302,
#     opening_thresh=22,
#     center_control_weight=168.71659228455573,
#     edge_weight=183.50393867064952,
#     edge_growth_decay=-0.1165058526807734,
#     kings_row_weight=145.37634461314647,
#     kings_row_growth_decay=0.6523349940788987,
# ):
#     num_white_man = count_bits(WP & ~K & MASK_32)
#     num_white_king = count_bits(WP & K & MASK_32)
#     num_black_man = count_bits(BP & ~K & MASK_32)
#     num_black_king = count_bits(BP & K & MASK_32)
#     num_total_pieces = count_bits(WP) + count_bits(BP)
#     SUM_DISTANCE = 0
#     DOUBLE_CORNER_BONUS = 0

#     man_adj_w = adjustment_factor(num_total_pieces, man_growth_decay) * man_weight
#     king_adj_w = adjustment_factor(num_total_pieces, king_growth_decay) * king_weight

#     PIECE_COUNT = (king_adj_w * (num_white_king - num_black_king)) + (
#         man_adj_w * (num_white_man - num_black_man)
#     )

#     back_row_adj_w = (
#         adjustment_factor(num_total_pieces, back_growth_decay) * back_row_weight
#     )
#     BACK_ROW = back_row_adj_w * (
#         count_bits(WP & MASK_32 & KING_ROW_BLACK)  # WHITE HOME ROW
#         - count_bits(BP & MASK_32 & KING_ROW_WHITE)  # BLACK HOME ROW
#     )

#     capture_adj_w = (
#         adjustment_factor(num_total_pieces, capture_growth_decay) * capture_weight
#     )

#     CAPTURE = capture_adj_w * (
#         count_black_pieces_that_can_be_captured_by_white(
#             WP, BP, K, kinged_mult, land_edge_mult, took_king_mult
#         )
#         - count_white_pieces_that_can_be_captured_by_black(  # white wants to maximize this
#             WP, BP, K, kinged_mult, land_edge_mult, took_king_mult
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

#     loosing_substantially = (num_black_man + num_black_king) < (
#         majority_loss_weight * (num_white_man + num_white_king)
#     ) or (num_white_man + num_white_king) < (
#         majority_loss_weight * (num_black_man + num_black_king)
#     )

#     if num_total_pieces >= opening_thresh:  # OPENING
#         CENTER_CONTROL = (
#             count_bits(WP & CENTER_8) - count_bits(BP & CENTER_8)
#         ) * center_control_weight
#     else:
#         CENTER_CONTROL = 0

#     if (
#         num_total_pieces <= endgame_threshold or loosing_substantially
#     ):  # ENDGAME / MAJORITY LOSS
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
#                 * (  # black wants to maximize number of kings on double corner
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
#                 (  # white wants to maximize number of kings on double corner
#                     WP & K & DOUBLE_CORNER & MASK_32
#                 )
#                 * double_corner_bonus_weight
#             )

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
    WP, BP, K = setup_board_from_position_lists(
        ["KD6", "KC3", "KF6", "KC1", "KB6"], ["KG1", "KG7", "KH8"]
    )

    # WP, BP, K = get_fresh_board()
    print_board(WP, BP, K)

    print(
        new_heuristic(WP, BP, K, turn=PlayerTurn.BLACK)
    )  # it should be negative for black
    print("----------------------------------------")
    print(
        new_heuristic(WP, BP, K, turn=PlayerTurn.WHITE)
    )  # it should be positive for white


# test1()


def test2():
    WP, BP, K = get_fresh_board()
    WP = insert_piece_by_pdntext(WP, "E5")
    WP = remove_piece_by_pdntext(WP, "F6")
    BP = remove_piece_by_pdntext(BP, "E3")

    print_board(WP, BP, K)

    # print(
    #     count_black_pieces_that_can_be_captured_by_white(
    #         WP, BP, K, took_king_mult=10, land_edge_mult=2, kinged_mult=10
    #     )
    # )
    # print(
    #     count_white_pieces_that_can_be_captured_by_black(
    #         WP, BP, K, took_king_mult=10, land_edge_mult=2, kinged_mult=10
    #     )
    # )

    # print(calculate_safe_white_pieces(WP, K))
    print(
        f"BLACK TO MOVE: {new_heuristic(WP, BP, K, turn=PlayerTurn.BLACK)}"
    )  # it should be negative for black
    print("-" * 20)
    print(
        f"WHITE TO MOVE: {new_heuristic(WP, BP, K, turn=PlayerTurn.WHITE)}"
    )  # it should be negative for black
    print(f"negative factor (24,-1): {adjustment_factor(24, -1)}")
    print(f"negative factor (15,-1): {adjustment_factor(15, -1)}")
    print(f"negative factor (10,-1): {adjustment_factor(10, -1)}")
    print(f"negative factor (5,-1): {adjustment_factor(5, -1)}")
    print(f"negative factor (1,-1): {adjustment_factor(1, -1)}")

    print(f"positive factor (24,1): {adjustment_factor(24, 1)}")
    print(f"positive factor (15,1): {adjustment_factor(15, 1)}")
    print(f"positive factor (10,1): {adjustment_factor(10, 1)}")
    print(f"positive factor (5,1): {adjustment_factor(5, 1)}")
    print(f"positive factor (1,1): {adjustment_factor(1, 1)}")


if __name__ == "__main__":
    test1()
