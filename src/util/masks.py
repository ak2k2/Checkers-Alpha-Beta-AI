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
