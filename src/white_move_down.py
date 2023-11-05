from util.masks import (
    MASK_L3,
    MASK_L5,
    MASK_R3,
    MASK_R5,
    PDN_MAP,
    S,
    bitindex_to_coords,
    coords_to_bitindex,
    print_board,
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


def print_bin_strings(WP, BP, KINGS):
    print(f"White Pieces: {bin(WP)[2:].zfill(32)}")
    print(f"Black Pieces: {bin(BP)[2:].zfill(32)}")
    print(f"Kings:        {bin(KINGS)[2:].zfill(32)}")


def insert_piece(bitboard, index):
    mask = 1 << index
    print(bin(mask).zfill(32))
    return bitboard | mask


def remove_piece(bitboard, index):
    mask = ~(1 << index)
    return bitboard & mask


def make_move(move, WP, BP, KINGS):
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

    return WP, BP, KINGS


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
    Movers = 0

    # Shift for normal pieces
    Temp = (nOcc << 4) & BP
    if Temp:
        Movers |= (((Temp & MASK_L3) << 3) | ((Temp & MASK_L5) << 5)) & WP

    Temp = (((nOcc & MASK_L3) << 3) | ((nOcc & MASK_L5) << 5)) & BP
    Movers |= (Temp << 4) & WP

    # Shift for kings
    if WK:
        Temp = (nOcc >> 4) & BP
        if Temp:
            Movers |= (((Temp & MASK_R3) >> 3) | ((Temp & MASK_R5) >> 5)) & WK
        Temp = (((nOcc & MASK_R3) >> 3) | ((nOcc & MASK_R5) >> 5)) & BP
        if Temp:
            Movers |= (Temp >> 4) & WK

    return Movers


def get_jumpers_black(WP, BP, K):
    nOcc = ~(WP | BP)  # Not Occupied
    BK = BP & K  # Black Kings
    Movers = 0

    # Shift for normal pieces
    Temp = (nOcc >> 4) & WP
    if Temp:
        Movers |= (((Temp & MASK_R3) >> 3) | ((Temp & MASK_R5) >> 5)) & BP

    Temp = (((nOcc & MASK_R3) >> 3) | ((nOcc & MASK_R5) >> 5)) & WP
    Movers |= (Temp >> 4) & BP

    # Shift for kings
    if BK:
        Temp = (nOcc << 4) & WP
        if Temp:
            Movers |= (((Temp & MASK_L3) << 3) | ((Temp & MASK_L5) << 5)) & BK
        Temp = (((nOcc & MASK_L3) << 3) | ((nOcc & MASK_L5) << 5)) & WP
        if Temp:
            Movers |= (Temp << 4) & BK

    return Movers


def find_set_bits(bitboard):
    set_bits = []
    while bitboard:
        # Find the index of the least significant set bit
        ls1b_index = (bitboard & -bitboard).bit_length() - 1
        set_bits.append(ls1b_index)
        # Clear the least significant set bit
        bitboard &= bitboard - 1
    return set_bits


def generate_simple_moves_white(WP, BP, K):
    moves = []
    nOcc = ~(WP | BP)  # Not Occupied
    movers = get_movers_white(WP, BP, K)  # Get white movers
    mover_indices = find_set_bits(movers)  # Get indices of white movers

    for index in mover_indices:
        # Calculate the bitboard index for simple moves
        if index % 4 != 0:  # Not on A file
            # Check bottom left
            if nOcc & (1 << (index - 4)):
                moves.append((index, index - 4))
        if index % 4 != 3:  # Not on H file
            # Check bottom right
            if nOcc & (1 << (index - 3)):
                moves.append((index, index - 3))

        # If it's a king, check upward moves as well
        if K & (1 << index):
            if index % 4 != 0:  # Not on A file
                # Check top left
                if nOcc & (1 << (index + 3)):
                    moves.append((index, index + 3))
            if index % 4 != 3:  # Not on H file
                # Check top right
                if nOcc & (1 << (index + 4)):
                    moves.append((index, index + 4))

    return moves


# def generate_jump_moves_for_white(WP, BP, K):
#     nOcc = ~(WP | BP)  # Not Occupied squares
#     jump_moves = []

#     # Get the bit indices of all white pieces that can jump
#     jumper_indices = find_set_bits(get_jumpers_white(WP, BP, K))

#     # Loop through each jumper piece
#     for index in jumper_indices:
#         # Calculate potential jump positions
#         if index % 8 > 1:  # Can potentially jump left
#             jump_left = index + 9
#             if jump_left < 32 and (
#                 nOcc & (1 << jump_left)
#             ):  # Check bounds and occupancy
#                 jump_moves.append((index, jump_left))

#         if index % 8 < 6:  # Can potentially jump right
#             jump_right = index + 7
#             if jump_right < 32 and (
#                 nOcc & (1 << jump_right)
#             ):  # Check bounds and occupancy
#                 jump_moves.append((index, jump_right))

#     return jump_moves


# def generate_jump_moves_for_black(WP, BP, K):
#     nOcc = ~(WP | BP)  # Not Occupied squares
#     jump_moves = []

#     # Get the bit indices of all black pieces that can jump
#     jumper_indices = find_set_bits(get_jumpers_black(WP, BP, K))

#     # Loop through each jumper piece
#     for index in jumper_indices:
#         # Calculate potential jump positions
#         if index % 8 > 1:  # Can potentially jump right
#             jump_right = index - 7
#             if jump_right >= 0 and (
#                 nOcc & (1 << jump_right)
#             ):  # Check bounds and occupancy
#                 jump_moves.append((index, jump_right))

#         if index % 8 < 6:  # Can potentially jump left
#             jump_left = index - 9
#             if jump_left >= 0 and (
#                 nOcc & (1 << jump_left)
#             ):  # Check bounds and occupancy
#                 jump_moves.append((index, jump_left))

#     return jump_moves


WP, BP, K = get_empty_board()
WP = insert_piece(WP, 1)
K = insert_piece(K, 1)

WP = insert_piece(WP, 21)
WP = insert_piece(WP, 24)
WP = insert_piece(WP, 24)
WP = insert_piece(WP, 13)
WP = insert_piece(WP, 20)

BP = insert_piece(BP, 5)
BP = insert_piece(BP, 18)
# BP = insert_piece(BP, 17)
BP = insert_piece(BP, 16)

print("STARTING BOARD")
print_board(WP, BP, K)
wm = generate_simple_moves_white(WP, BP, K)
# bm = generate_simple_moves_for_black(WP, BP, K)

print("White moves:")
for move in wm:
    print(f"{bitindex_to_coords(move[0])} -> {bitindex_to_coords(move[1])}")

# print("Black moves:")
# for move in bm:
#     print(f"{bitindex_to_coords(move[0])} -> {bitindex_to_coords(move[1])}")


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
