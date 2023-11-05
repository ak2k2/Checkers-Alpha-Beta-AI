S = [1 << i for i in range(32)]

# MASKS FROM: https://3dkingdoms.com/checkers/bitboards.htm

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


# Black moving to the top right (Northeast)
BLACK_NORTHEAST = {
    0: 4,
    1: 5,
    2: 6,
    3: 7,
    4: 9,
    5: 10,
    6: 11,
    7: None,
    8: 12,
    9: 13,
    10: 14,
    11: 15,
    12: 17,
    13: 18,
    14: 19,
    15: None,
    16: 20,
    17: 21,
    18: 22,
    19: 23,
    20: 25,
    21: 26,
    22: 27,
    23: None,
    24: 28,
    25: 29,
    26: 30,
    27: 31,
    28: None,
    29: None,
    30: None,
    31: None,
}

# Black moving to the top left (Northwest)
BLACK_NORTHWEST = {
    0: None,
    1: 4,
    2: 5,
    3: 6,
    4: 8,
    5: 9,
    6: 10,
    7: 11,
    8: None,
    9: 12,
    10: 13,
    11: 14,
    12: 16,
    13: 17,
    14: 18,
    15: 19,
    16: None,
    17: 20,
    18: 21,
    19: 22,
    20: 24,
    21: 25,
    22: 26,
    23: 27,
    24: None,
    25: 28,
    26: 29,
    27: 30,
    28: None,
    29: None,
    30: None,
    31: None,
}

# White moving to the bottom right (Southwest)
WHITE_SOUTHWEST = {
    0: None,
    1: None,
    2: None,
    3: None,
    4: 0,
    5: 1,
    6: 2,
    7: 3,
    8: None,
    9: 4,
    10: 5,
    11: 6,
    12: 8,
    13: 9,
    14: 10,
    15: 11,
    16: None,
    17: 12,
    18: 13,
    19: 14,
    20: 16,
    21: 17,
    22: 18,
    23: 19,
    24: None,
    25: 20,
    26: 21,
    27: 22,
    28: 24,
    29: 25,
    30: 26,
    31: 27,
}

# White moving to the bottom left (Southeast)
WHITE_SOUTHEAST = {
    0: None,
    1: None,
    2: None,
    3: None,
    4: 1,
    5: 2,
    6: 3,
    7: None,
    8: 4,
    9: 5,
    10: 6,
    11: 7,
    12: 9,
    13: 10,
    14: 11,
    15: None,
    16: 12,
    17: 13,
    18: 14,
    19: 15,
    20: 17,
    21: 18,
    22: 19,
    23: None,
    24: 20,
    25: 21,
    26: 22,
    27: 23,
    28: 25,
    29: 26,
    30: 27,
    31: None,
}


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
