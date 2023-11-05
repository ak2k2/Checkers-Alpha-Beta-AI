from util.masks import (
    MASK_L3,
    MASK_L5,
    MASK_R3,
    MASK_R5,
    BLACK_NORTHEAST,
    BLACK_NORTHWEST,
    WHITE_SOUTHEAST,
    WHITE_SOUTHWEST,
    PDN_MAP,
    S,
    bitindex_to_coords,
    coords_to_bitindex,
    print_board,
    print_bin_strings,
)


def get_fresh_board():
    BP = 0b00000000000000000000111111111111  # Black pieces at the bottom
    WP = 0b11111111111100000000000000000000  # White pieces at the top
    KINGS = 0b00000000000000000000000000000000  # No kings at the start
    return WP, BP, KINGS


def get_empty_board():
    WP = 0b00000000000000000000000000000000
    BP = 0b00000000000000000000000000000000
    KINGS = 0b00000000000000000000000000000000
    return WP, BP, KINGS


def insert_piece(bitboard, index):
    mask = 1 << index
    print(bin(mask).zfill(32))
    return bitboard | mask


def remove_piece(bitboard, index):
    mask = ~(1 << index)
    return bitboard & mask


def make_move(move, WP, BP, K):
    # Extract source and destination from the move tuple
    src, dest = move

    # Convert FEN coordinates to bit indices
    src_index = coords_to_bitindex(src)
    dest_index = coords_to_bitindex(dest)

    # Determine if the source is a white or black piece and move it accordingly
    if WP & (1 << src_index):  # It's a white piece
        WP = remove_piece(WP, src_index)  # Remove from source
        WP = insert_piece(WP, dest_index)  # Insert to destination
    elif BP & (1 << src_index):  # It's a black piece
        BP = remove_piece(BP, src_index)  # Remove from source
        BP = insert_piece(BP, dest_index)  # Insert to destination
    else:
        raise ValueError("No piece at source location.")

    # Update kings if a king was moved
    if KINGS & (1 << src_index):
        KINGS = remove_piece(KINGS, src_index)  # Remove from source
        KINGS = insert_piece(
            KINGS, dest_index
        )  # Insert to destination (works for both white and black)

    return WP, BP, K


def get_movers_white(WP, BP, K):
    # Constants for masks, corrected for shifting direction
    nOcc = ~(WP | BP)  # Not Occupied
    WK = WP & K  # White Kings

    # Calculate potential moves for white non-kings downwards
    Movers = (nOcc << 4) & WP  # Move down 4
    Movers |= ((nOcc & MASK_L3) << 3) & WP  # Move down left 3
    Movers |= ((nOcc & MASK_L5) << 5) & WP  # Move down left 5

    # Calculate potential moves for white kings (which can move both up and down)
    if WK:
        Movers |= (nOcc >> 4) & WK  # Move up 4
        Movers |= ((nOcc & MASK_R3) >> 3) & WK  # Move up right 3
        Movers |= ((nOcc & MASK_R5) >> 5) & WK  # Move up right 5

    return Movers


def get_movers_black(WP, BP, K):
    # Constants for masks, assuming they prevent wraparound for upward moves
    nOcc = ~(WP | BP)  # Not Occupied
    BK = BP & K  # Black Kings

    # Calculate potential moves for black non-kings upwards
    Movers = (nOcc >> 4) & BP  # Move up 4
    Movers |= ((nOcc & MASK_R3) >> 3) & BP  # Move up right 3
    Movers |= ((nOcc & MASK_R5) >> 5) & BP  # Move up right 5

    # Calculate potential moves for black kings (which can move both up and down)
    if BK:
        Movers |= (nOcc << 4) & BK  # Move down 4
        Movers |= ((nOcc & MASK_L3) << 3) & BK  # Move down left 3
        Movers |= ((nOcc & MASK_L5) << 5) & BK  # Move down left 5

    return Movers


def get_jumpers_white(WP, BP, K):
    nOcc = ~(WP | BP)  # Not Occupied
    WK = WP & K  # White Kings
    Jumpers = 0

    # Shift for normal pieces
    Temp = (nOcc << 4) & BP
    if Temp:
        Jumpers |= (((Temp & MASK_L3) << 3) | ((Temp & MASK_L5) << 5)) & WP

    Temp = (((nOcc & MASK_L3) << 3) | ((nOcc & MASK_L5) << 5)) & BP
    Jumpers |= (Temp << 4) & WP

    # Shift for kings
    if WK:
        Temp = (nOcc >> 4) & BP
        if Temp:
            Jumpers |= (((Temp & MASK_R3) >> 3) | ((Temp & MASK_R5) >> 5)) & WK
        Temp = (((nOcc & MASK_R3) >> 3) | ((nOcc & MASK_R5) >> 5)) & BP
        if Temp:
            Jumpers |= (Temp >> 4) & WK

    return Jumpers


def get_jumpers_black(WP, BP, K):
    nOcc = ~(WP | BP)  # Not Occupied
    BK = BP & K  # Black Kings
    Jumpers = 0

    # Shift for normal pieces
    Temp = (nOcc >> 4) & WP
    if Temp:
        Jumpers |= (((Temp & MASK_R3) >> 3) | ((Temp & MASK_R5) >> 5)) & BP

    Temp = (((nOcc & MASK_R3) >> 3) | ((nOcc & MASK_R5) >> 5)) & WP
    Jumpers |= (Temp >> 4) & BP

    # Shift for kings
    if BK:
        Temp = (nOcc << 4) & WP
        if Temp:
            Jumpers |= (((Temp & MASK_L3) << 3) | ((Temp & MASK_L5) << 5)) & BK
        Temp = (((nOcc & MASK_L3) << 3) | ((nOcc & MASK_L5) << 5)) & WP
        if Temp:
            Jumpers |= (Temp << 4) & BK

    return Jumpers


def find_set_bits(bitboard):
    """
    Returns a list of indices of bits that are set to 1 in the bitboard.
    """
    set_bits = []
    while bitboard:
        ls1b_index = (bitboard & -bitboard).bit_length() - 1
        set_bits.append(ls1b_index)
        bitboard &= bitboard - 1
    return set_bits


def is_set(bitboard, index):
    return (bitboard & (1 << index)) != 0


def generate_simple_moves_white(WP, BP, K):
    simple_moves = []
    white_positions = find_set_bits(WP)

    for pos in white_positions:
        is_king = pos in find_set_bits(K)

        # If it's a king, it can also move using black's moves
        if is_king:
            potential_moves = [
                BLACK_NORTHEAST.get(pos),
                BLACK_NORTHWEST.get(pos),
                WHITE_SOUTHWEST.get(pos),
                WHITE_SOUTHEAST.get(pos),
            ]
        else:
            # Regular white pieces can only move Southwest or Southeast
            potential_moves = [
                WHITE_SOUTHWEST.get(pos),
                WHITE_SOUTHEAST.get(pos),
            ]

        for move in potential_moves:
            if move is not None and not is_set(WP | BP, move):
                simple_moves.append((pos, move))

    return simple_moves


# Function to generate simple moves for black pieces
def generate_simple_moves_black(WP, BP, K):
    simple_moves = []
    black_positions = find_set_bits(BP)

    for pos in black_positions:
        is_king = pos in find_set_bits(K)

        # If it's a king, it can move using both black's and white's moves
        if is_king:
            potential_moves = [
                BLACK_NORTHEAST.get(pos),
                BLACK_NORTHWEST.get(pos),
                WHITE_SOUTHWEST.get(pos),
                WHITE_SOUTHEAST.get(pos),
            ]
        else:
            # Regular black pieces can only move Northeast or Northwest
            potential_moves = [
                BLACK_NORTHEAST.get(pos),
                BLACK_NORTHWEST.get(pos),
            ]

        for move in potential_moves:
            if move is not None and not is_set(WP | BP, move):
                simple_moves.append((pos, move))

    return simple_moves


# def get_jump_moves(bitboard, jumpers, opponent_pieces, is_king):
#     jump_moves = []
#     for pos in find_set_bits(jumpers):
#         # Define jump directions based on whether the piece is a king
#         if is_king:
#             directions = [
#                 BLACK_NORTHEAST,
#                 BLACK_NORTHWEST,
#                 WHITE_SOUTHWEST,
#                 WHITE_SOUTHEAST,
#             ]
#         else:
#             directions = [
#                 BLACK_NORTHEAST,
#                 BLACK_NORTHWEST,
#             ]  # or the equivalent for white pieces

#         for direction in directions:
#             # Check if the adjacent square in the jump direction is an opponent's piece
#             # and the square after that is empty (indicated by None)
#             next_square = direction.get(pos)
#             if next_square is not None and is_set(opponent_pieces, next_square):
#                 jump_over_square = direction.get(next_square)
#                 if jump_over_square is not None and not is_set(
#                     bitboard, jump_over_square
#                 ):
#                     # Add the initial jump move to the list
#                     jump_moves.append((pos, jump_over_square))
#                     # Recursively check for further jumps from jump_over_square
#                     # This will be implemented next

#     return jump_moves


def generate_jump_moves(WP, BP, K, jumpers, player="white"):
    jump_moves = []

    # Define the direction maps based on the player
    if player == "white":
        own_pieces = WP
        opponent_pieces = BP
        regular_directions = [WHITE_SOUTHWEST, WHITE_SOUTHEAST]
        king_directions = [
            BLACK_NORTHEAST,
            BLACK_NORTHWEST,
            WHITE_SOUTHWEST,
            WHITE_SOUTHEAST,
        ]
    else:  # player == 'black'
        own_pieces = BP
        opponent_pieces = WP
        regular_directions = [BLACK_NORTHEAST, BLACK_NORTHWEST]
        king_directions = [
            BLACK_NORTHEAST,
            BLACK_NORTHWEST,
            WHITE_SOUTHWEST,
            WHITE_SOUTHEAST,
        ]

    # Go through all the jumpers and generate jumps
    for pos in find_set_bits(jumpers):
        # Determine if the piece is a king
        is_king = K & (1 << pos) != 0

        # Select the correct directions based on whether the piece is a king
        directions = king_directions if is_king else regular_directions

        # Check all directions for possible jumps
        for direction in directions:
            next_square = direction.get(pos)
            if next_square is not None and is_set(opponent_pieces, next_square):
                jump_over_square = direction.get(next_square)
                if jump_over_square is not None and not is_set(
                    own_pieces | opponent_pieces, jump_over_square
                ):
                    # Add the initial jump move to the list
                    jump_moves.append((pos, jump_over_square))
                    # Further jumps would be handled by the recursive part here

    return jump_moves


def generate_jump_moves_recursive(
    WP, BP, K, pos, jumped_over, moves, player="white", sequence=None
):
    if sequence is None:
        sequence = [(pos, jumped_over)]
    else:
        sequence.append((pos, jumped_over))

    # Define player-specific variables
    if player == "white":
        own_pieces = WP
        opponent_pieces = BP
        regular_directions = [WHITE_SOUTHWEST, WHITE_SOUTHEAST]
        king_directions = [
            BLACK_NORTHEAST,
            BLACK_NORTHWEST,
            WHITE_SOUTHWEST,
            WHITE_SOUTHEAST,
        ]
    else:
        own_pieces = BP
        opponent_pieces = WP
        regular_directions = [BLACK_NORTHEAST, BLACK_NORTHWEST]
        king_directions = [
            BLACK_NORTHEAST,
            BLACK_NORTHWEST,
            WHITE_SOUTHWEST,
            WHITE_SOUTHEAST,
        ]

    # Check if the current piece is a king
    is_king = K & (1 << pos) != 0
    directions = king_directions if is_king else regular_directions

    # Temporarily make the jump by updating bitboards
    own_pieces = own_pieces & ~(1 << pos) | (
        1 << jumped_over
    )  # Remove from old pos, add to new
    opponent_pieces = opponent_pieces & ~(
        1 << sequence[-2][1]
    )  # Remove jumped opponent piece
    if is_king:
        K = K & ~(1 << pos) | (
            1 << jumped_over
        )  # Update king's position if it was a king

    further_jumps = False
    # Check all directions for possible further jumps
    for direction in directions:
        next_square = direction.get(jumped_over)
        if next_square is not None and is_set(opponent_pieces, next_square):
            jump_over_square = direction.get(next_square)
            if jump_over_square is not None and not is_set(
                own_pieces | opponent_pieces, jump_over_square
            ):
                # Recursive call to continue the jump sequence
                further_jumps = True
                generate_jump_moves_recursive(
                    WP,
                    BP,
                    K,
                    jumped_over,
                    jump_over_square,
                    moves,
                    player,
                    list(sequence),
                )

    # If no further jumps are possible, add the sequence to the moves list
    if not further_jumps and len(sequence) > 1:
        moves.append(sequence)

    # Backtrack is not necessary as we're not modifying the global state


# Wrapper function to initiate the recursive jump generation
def generate_all_jump_moves(WP, BP, K, player="white"):
    jump_moves = []
    jumpers = (
        get_jumpers_white(WP, BP, K)
        if player == "white"
        else get_jumpers_black(WP, BP, K)
    )

    # Go through all jumpers and generate jump sequences
    for pos in find_set_bits(jumpers):
        generate_jump_moves_recursive(WP, BP, K, pos, pos, jump_moves, player)

    return jump_moves


if __name__ == "__main__":
    WP, BP, K = get_empty_board()

    WP = insert_piece(WP, 1)
    K = insert_piece(K, 1)

    WP = insert_piece(WP, 19)
    K = insert_piece(K, 19)

    WP = insert_piece(WP, 21)
    WP = insert_piece(WP, 24)
    WP = insert_piece(WP, 29)
    WP = insert_piece(WP, 13)
    WP = insert_piece(WP, 20)

    BP = insert_piece(BP, 5)
    BP = insert_piece(BP, 4)
    BP = insert_piece(BP, 18)
    BP = insert_piece(BP, 16)

    BP = insert_piece(BP, 12)
    K = insert_piece(K, 12)

    print("STARTING BOARD")
    print_board(WP, BP, K)

    wm = generate_simple_moves_white(
        get_movers_white(WP, BP, K), BP, K
    )  # generate all the simple moves for white pieces that can do a simple move

    bp = generate_simple_moves_black(
        WP, get_movers_black(WP, BP, K), K
    )  # generate all the simple moves for black pieces that can do a simple move

    print("White SIMPLE moves:")
    for move in wm:
        print(f"{bitindex_to_coords(move[0])} -> {bitindex_to_coords(move[1])}")

    print("Black SIMPLE moves:")
    for move in bp:
        print(f"{bitindex_to_coords(move[0])} -> {bitindex_to_coords(move[1])}")

    wj = get_jumpers_white(WP, BP, K)
    bj = get_jumpers_black(WP, BP, K)

    # print("White JUMPERS:")
    # print_board(wj, BP, K)

    jm = generate_jump_moves(WP, BP, K, bj, player="black")
    print("Black JUMP moves:")
    for move in jm:
        print(f"{bitindex_to_coords(move[0])} -> {bitindex_to_coords(move[1])}")

    # # WP, BP, K = get_fresh_board()
    # WP, BP, K = get_empty_board()
    # # WP = insert_piece(WP, 12)
    # # WP = insert_piece(WP, 16)
    # # WP = insert_piece(WP, 14)
    # BP = insert_piece(BP, 0)
    # # BP = insert_piece(BP, 6)
    # # K = insert_piece(K, 6)
    # BP = insert_piece(BP, 2)
    # K = insert_piece(K, 2)
    # BP = insert_piece(BP, 5)
    # BP = insert_piece(BP, 4)
    # BP = insert_piece(BP, 10)

    # WP = insert_piece(WP, 13)
    # # WP = insert_piece(WP, 25)
    # WP = insert_piece(WP, 18)

    # BP = insert_piece(BP, 17)
    # K = insert_piece(K, 17)

    # WP = insert_piece(WP, 27)
    # BP = insert_piece(BP, 21)
    # BP = insert_piece(BP, 28)

    # BP = insert_piece(BP, 11)

    # print("STARTING BOARD")
    # print_board(WP, BP, K)
    # black_movers = get_movers_black(WP, BP, K)
    # black_jumpers = get_jumpers_black(WP, BP, K)
    # print(bin(black_movers)[2:].zfill(32))
    # print_board(WP, black_movers, K)
    # print(bin(black_jumpers)[2:].zfill(32))
    # print("Black jumpers:")
    # print_board(WP, black_jumpers, K)
    # white_jumpers = get_jumpers_white(WP, BP, K)
    # print(bin(white_jumpers)[2:].zfill(32))
    # print("White jumpers:")
    # print_board(white_jumpers, BP, K)
