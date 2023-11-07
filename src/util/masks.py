MASK_32 = 0xFFFFFFFF  # To explicitly invoke 32-bit integers.

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

BLACK_JUMP_NORTHEAST = {
    0: 9,
    1: 10,
    2: 11,
    3: None,
    4: 13,
    5: 14,
    6: 15,
    7: None,
    8: 17,
    9: 18,
    10: 19,
    11: None,
    12: 21,
    13: 22,
    14: 23,
    15: None,
    16: 25,
    17: 26,
    18: 27,
    19: None,
    20: 29,
    21: 30,
    22: 31,
    23: None,
    24: None,
    25: None,
    26: None,
    27: None,
    28: None,
    29: None,
    30: None,
    31: None,
}

BLACK_JUMP_NORTHWEST = {
    0: None,
    1: 8,
    2: 9,
    3: 10,
    4: None,
    5: 12,
    6: 13,
    7: 14,
    8: None,
    9: 16,
    10: 17,
    11: 18,
    12: None,
    13: 20,
    14: 21,
    15: 22,
    16: None,
    17: 24,
    18: 25,
    19: 26,
    20: None,
    21: 28,
    22: 29,
    23: 30,
    24: None,
    25: None,
    26: None,
    27: None,
    28: None,
    29: None,
    30: None,
    31: None,
}

WHITE_JUMP_SOUTHEAST = {
    0: None,
    1: None,
    2: None,
    3: None,
    4: None,
    5: None,
    6: None,
    7: None,
    8: 1,
    9: 2,
    10: 3,
    11: None,
    12: 5,
    13: 6,
    14: 7,
    15: None,
    16: 9,
    17: 10,
    18: 11,
    19: None,
    20: 13,
    21: 14,
    22: 15,
    23: None,
    24: 17,
    25: 18,
    26: 19,
    27: None,
    28: 21,
    29: 22,
    30: 23,
    31: None,
}

WHITE_JUMP_SOUTHWEST = {
    0: None,
    1: None,
    2: None,
    3: None,
    4: None,
    5: None,
    6: None,
    7: None,
    8: None,
    9: 0,
    10: 1,
    11: 2,
    12: None,
    13: 4,
    14: 5,
    15: 6,
    16: None,
    17: 8,
    18: 9,
    19: 10,
    20: None,
    21: 12,
    22: 13,
    23: 14,
    24: None,
    25: 16,
    26: 17,
    27: 18,
    28: None,
    29: 20,
    30: 21,
    31: 22,
}

# To find the jumped position given the start and end positions # TODO: can be simplified at the expense of modifying move representation
JUMP_MASKS = {
    "JSE": WHITE_JUMP_SOUTHEAST,
    "JSW": WHITE_JUMP_SOUTHWEST,
    "JNE": BLACK_JUMP_NORTHEAST,
    "JNW": BLACK_JUMP_NORTHWEST,
}

MOVE_MASKS = {
    "MSE": WHITE_SOUTHEAST,
    "MSW": WHITE_SOUTHWEST,
    "MNE": BLACK_NORTHEAST,
    "MNW": BLACK_NORTHWEST,
}

DIRECTION_MAP = {"JSE": "MSE", "JSW": "MSW", "JNE": "MNE", "JNW": "MNW"}

S = [1 << i for i in range(32)]

# L3, L5, R3, R5 MASKS inspired by: https://3dkingdoms.com/checkers/bitboards.htm

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

# MASKS for the center and corners and terminal ranks
CENTER_8 = S[9] | S[10] | S[13] | S[14] | S[17] | S[18] | S[21] | S[22]

DOUBLE_CORNER = S[3] | S[7] | S[24] | S[28]
SINGLE_CORNER = S[0] | S[31]

KING_ROW_WHITE = S[0] | S[1] | S[2] | S[3]
KING_ROW_BLACK = S[28] | S[29] | S[30] | S[31]

EDGES = (
    S[0]
    | S[1]
    | S[2]
    | S[3]
    | S[7]
    | S[15]
    | S[23]
    | S[31]
    | S[30]
    | S[29]
    | S[28]
    | S[24]
    | S[16]
    | S[8]
)

ATTACK_ROWS_WHITE = S[16] | S[17] | S[18] | S[19] | S[20] | S[21] | S[22] | S[23]

ATTACK_ROWS_BLACK = S[8] | S[9] | S[10] | S[11] | S[12] | S[13] | S[14] | S[15]

MAIN_DIAGONAL = S[0] | S[4] | S[9] | S[13] | S[18] | S[22] | S[27] | S[31]

DOUBLE_DIAGONAL = (
    S[3]
    | S[6]
    | S[10]
    | S[13]
    | S[17]
    | S[20]
    | S[24]
    | S[7]
    | S[11]
    | S[14]
    | S[18]
    | S[21]
    | S[25]
    | S[28]
)
