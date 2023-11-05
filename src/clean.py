S = [1 << i for i in range(32)]

MASK_L3 = (
    S[1]
    | S[2]
    | S[3]
    | S[9]
    | S[10]
    | S[11]
    | S[17]
    | S[18]
    | S[19]
    | S[25]
    | S[26]
    | S[27]
)
MASK_L5 = S[4] | S[5] | S[6] | S[12] | S[13] | S[14] | S[20] | S[21] | S[22]
MASK_R3 = (
    S[28]
    | S[29]
    | S[30]
    | S[20]
    | S[21]
    | S[22]
    | S[12]
    | S[13]
    | S[14]
    | S[4]
    | S[5]
    | S[6]
)
MASK_R5 = S[25] | S[26] | S[27] | S[17] | S[18] | S[19] | S[9] | S[10] | S[11]


def print_board(WP, BP, kings):
    # Print column indices
    print("\n")
    print("    " + "   ".join(["A", "B", "C", "D", "E", "F", "G", "H"]))
    print("  +" + "---+" * 8)

    for row in range(8):
        # Start each row with the row number (indices on the left)
        row_str = f"{8-row} |"

        for col in range(8):
            # Calculate the index in the 32-bit board representation
            if row % 2 != col % 2:
                index = (7 - row) * 4 + (col // 2)
                if WP & (1 << index):
                    char = "Ø" if kings & (1 << index) else "o"  # Player 1's piece
                elif BP & (1 << index):
                    char = "∆" if kings & (1 << index) else "x"  # Player 2's piece
                else:
                    char = " "  # Playable empty square
            else:
                char = " "  # Unplayable square (white square)

            row_str += f" {char} |"

        print(row_str)
        print("  +" + "---+" * 8)  # Print the row separator
    print("\n")


# You can define a get_fresh_board function which also returns a single kings bitboard
def get_fresh_board():
    WP = 0b00000000000000000000111111111111
    BP = 0b11111111111100000000000000000000
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


def bitindex_to_coords(index):
    map = {
        0: "A1",
        1: "C1",
        2: "E1",
        3: "G1",
        4: "B2",
        5: "D2",
        6: "F2",
        7: "H2",
        8: "A3",
        9: "C3",
        10: "E3",
        11: "G3",
        12: "B4",
        13: "D4",
        14: "F4",
        15: "H4",
        16: "A5",
        17: "C5",
        18: "E5",
        19: "G5",
        20: "B6",
        21: "D6",
        22: "F6",
        23: "H6",
        24: "A7",
        25: "C7",
        26: "E7",
        27: "G7",
        28: "B8",
        29: "D8",
        30: "F8",
        31: "H8",
    }
    return map[index]


def coords_to_bitindex(coords):
    map = {
        0: "A1",
        1: "C1",
        2: "E1",
        3: "G1",
        4: "B2",
        5: "D2",
        6: "F2",
        7: "H2",
        8: "A3",
        9: "C3",
        10: "E3",
        11: "G3",
        12: "B4",
        13: "D4",
        14: "F4",
        15: "H4",
        16: "A5",
        17: "C5",
        18: "E5",
        19: "G5",
        20: "B6",
        21: "D6",
        22: "F6",
        23: "H6",
        24: "A7",
        25: "C7",
        26: "E7",
        27: "G7",
        28: "B8",
        29: "D8",
        30: "F8",
        31: "H8",
    }

    for key, value in map.items():
        if value == coords:
            return key


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

    # Calculate potential moves for white non-kings upwards
    Movers = (nOcc >> 4) & WP  # Move up 4
    Movers |= ((nOcc & MASK_R3) >> 3) & WP  # Move up right 3
    Movers |= ((nOcc & MASK_R5) >> 5) & WP  # Move up right 5

    # Calculate potential moves for white kings (which can move both up and down)
    if WK:
        Movers |= (nOcc << 4) & WK  # Move down 4
        Movers |= ((nOcc & MASK_L3) << 3) & WK  # Move down left 3
        Movers |= ((nOcc & MASK_L5) << 5) & WK  # Move down left 5

    return Movers


WP, BP, K = get_fresh_board()
print_board(WP, BP, K)
# WP, BP, K = make_move(("B6", "C5"), WP, BP, K)
# print_board(WP, BP, K)
white_movers = get_movers_white(WP, BP, K)
print(bin(white_movers)[2:].zfill(32))
print_board(white_movers, BP, K)


# white_movers = get_movers_white(WP, BP, K)
# bin_white_movers = bin(white_movers)[2:].zfill(32)

# print_bin_strings(WP, BP, K)
# print(bin_white_movers)

# print_board(white_movers, BP, K)
