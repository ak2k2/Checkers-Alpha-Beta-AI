PDN_MAP = {
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

REVERSE_PDN_MAP = {v: k for k, v in PDN_MAP.items()}


def print_board(WP, BP, kings):
    # File names
    print("\n")
    print("    " + "   ".join(["A", "B", "C", "D", "E", "F", "G", "H"]))
    print("  +" + "---+" * 8)

    for row in range(8):
        # Rank numbers on the left side
        row_str = f"{8-row} |"

        for col in range(8):
            # Index from 32-bit board representation
            if row % 2 != col % 2:
                index = (7 - row) * 4 + (col // 2)
                if WP & (1 << index):
                    char = "W" if kings & (1 << index) else "w"
                elif BP & (1 << index):
                    char = "B" if kings & (1 << index) else "b"
                else:
                    char = " "  # Playable empty square
            else:
                char = " "  # Unplayable square (white square)

            row_str += f" {char} |"

        print(row_str)
        print("  +" + "---+" * 8)  # Print the row separator
    print("\n")


def print_bin_strings(WP, BP, KINGS):
    print(f"White Pieces: {bin(WP)[2:].zfill(32)}")
    print(f"Black Pieces: {bin(BP)[2:].zfill(32)}")
    print(f"Kings:        {bin(KINGS)[2:].zfill(32)}")


def bitindex_to_coords(index):
    return PDN_MAP[index]


def coords_to_bitindex(coords):
    for key, value in PDN_MAP.items():
        if value == coords:
            return key


def get_fresh_board():
    BP = 0b00000000000000000000111111111111  # Black pieces start SOUTH and move NORTH
    WP = 0b11111111111100000000000000000000  # White pieces start NORTH and move SOUTH
    K = 0b00000000000000000000000000000000  # Kings are ANDed with WP and BP.
    return WP, BP, K


def get_empty_board():
    WP = 0b00000000000000000000000000000000
    BP = 0b00000000000000000000000000000000
    K = 0b00000000000000000000000000000000
    return WP, BP, K


def insert_piece(bitboard, index):
    """
    Returns the bitboard with the bit at the given index set to 1.
    """
    mask = 1 << index
    return bitboard | mask


def insert_piece_by_pdntext(bitboard, pdn_text):
    """
    Takes pdn coordinates (e.g. 'A1') and inserts a piece at the corresponding index (e.g. 0).
    """
    if pdn_text not in REVERSE_PDN_MAP:
        raise ValueError(f"{pdn_text} is not a valid PDN coordinate.")
    index = coords_to_bitindex(pdn_text)
    return insert_piece(bitboard, index)


def remove_piece(bitboard, index):
    """
    Returns the bitboard with the bit at the given index set to 0.
    """
    mask = ~(1 << index)
    return bitboard & mask


def remove_piece_by_pdntext(bitboard, pdn_text):
    """
    Takes pdn coordinates (e.g. 'A1') and removes a piece at the corresponding index (e.g. 0).
    """
    if pdn_text not in REVERSE_PDN_MAP:
        raise ValueError(f"{pdn_text} is not a valid PDN coordinate.")

    index = coords_to_bitindex(pdn_text)
    return remove_piece(bitboard, index)


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
    """
    Returns True if the bit at the given index is set to 1 in the bitboard.
    """
    return (bitboard & (1 << index)) != 0


def set_bit(bitboard, index):
    """
    Returns the bitboard with the bit at the given index set to 1.
    """
    return bitboard | (1 << index)
