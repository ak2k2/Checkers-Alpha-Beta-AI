from enum import Enum

MASK_32 = 0xFFFFFFFF  # To explicitly invoke 32-bit integers.


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


class PlayerTurn(Enum):
    WHITE = 1
    BLACK = 2


def load_game_from_sable_file(file_path):
    WP, BP, K = get_empty_board()

    with open(file_path, "r") as file:
        board_lines = file.readlines()

    # We expect the first 8 lines to contain the board state.
    for row, line in enumerate(board_lines[:8]):
        # Extracting pieces from the text line
        pieces = line.strip().split()

        for col, piece in enumerate(pieces):
            # Calculate the bit index
            bit_index = (7 - row) * 4 + col

            # Mapping the piece to the correct bitboard
            if piece == "1":
                WP = insert_piece(WP, bit_index)
            elif piece == "2":
                BP = insert_piece(BP, bit_index)
            elif piece == "3":
                WP = insert_piece(WP, bit_index)
                K = insert_piece(K, bit_index)
            elif piece == "4":
                BP = insert_piece(BP, bit_index)
                K = insert_piece(K, bit_index)

    # The 9th line should contain the current player's turn.
    current_player = int(board_lines[8].strip())

    # The 10th line should contain the time limit for the computer's turn.
    time_limit = int(board_lines[9].strip())

    return WP, BP, K, current_player, time_limit


def bitboard_to_pdn_positions(bitboard):
    pdn_positions = [bitindex_to_coords(index) for index in find_set_bits(bitboard)]
    return pdn_positions


def print_bin_strings(WP, BP, KINGS) -> None:
    print(f"White Pieces: {bin(WP)[2:].zfill(32)}")
    print(f"Black Pieces: {bin(BP)[2:].zfill(32)}")
    print(f"Kings:        {bin(KINGS)[2:].zfill(32)}")


def bitindex_to_coords(index) -> str:
    """
    Takes a bit index (e.g. 0) and returns the corresponding PDN coordinates (e.g. 'A1').
    """
    return PDN_MAP[index]


def coords_to_bitindex(coords) -> int:
    """clea
    Takes PDN coordinates (e.g. 'A1') and returns the corresponding index (e.g. 0).
    """
    for key, value in PDN_MAP.items():
        if value == coords:
            return key


def get_fresh_board() -> tuple:
    """
    Returns a tuple of bitboards representing a fresh board.
    """
    BP = 0b00000000000000000000111111111111  # Black pieces start SOUTH and move NORTH
    WP = 0b11111111111100000000000000000000  # White pieces start NORTH and move SOUTH
    K = 0b00000000000000000000000000000000  # Kings are ANDed with WP and BP.
    return WP, BP, K


def get_empty_board() -> tuple:
    WP = 0b00000000000000000000000000000000
    BP = 0b00000000000000000000000000000000
    K = 0b00000000000000000000000000000000
    return WP, BP, K


def insert_piece(bitboard, index) -> int:
    """
    Returns the bitboard with the bit at the given index set to 1.
    """
    mask = 1 << index
    return bitboard | mask & MASK_32


def insert_piece_by_pdntext(bitboard, pdn_text) -> int:
    """
    Takes pdn coordinates (e.g. 'A1') and inserts a piece at the corresponding index (e.g. 0).
    """
    if pdn_text not in REVERSE_PDN_MAP:
        raise ValueError(f"{pdn_text} is not a valid PDN coordinate.")
    index = coords_to_bitindex(pdn_text)
    return insert_piece(bitboard, index)


def remove_piece(bitboard, index) -> int:
    """
    Returns the bitboard with the bit at the given index set to 0.
    """
    mask = ~(1 << index)
    return bitboard & mask & MASK_32


def remove_piece_by_pdntext(bitboard, pdn_text) -> int:
    """
    Takes pdn coordinates (e.g. 'A1') and removes a piece at the corresponding index (e.g. 0).
    """
    if pdn_text not in REVERSE_PDN_MAP:
        raise ValueError(f"{pdn_text} is not a valid PDN coordinate.")

    index = coords_to_bitindex(pdn_text)
    return remove_piece(bitboard, index)


def find_set_bits(bitboard) -> list:
    """
    Returns a list of indices of bits that are set to 1 in the bitboard using list comprehension.
    """
    return [index for index in range(32) if (bitboard & (1 << index)) != 0]


def count_bits(bitboard: int) -> int:
    """
    Counts the number of bits set to 1 in the bitboard.
    """
    return len(find_set_bits(bitboard))


def is_set(bitboard, index) -> bool:
    """
    Returns True if the bit at the given index is set to 1 in the bitboard.
    """
    return (bitboard & (1 << index) & MASK_32) != 0


def set_bit(bitboard, index) -> int:
    """
    Returns the bitboard with the bit at the given index set to 1.
    """
    return bitboard | (1 << index)


def switch_player(player):
    return PlayerTurn.BLACK if player == PlayerTurn.WHITE else PlayerTurn.WHITE


def print_legal_moves(legal_moves):
    print(
        f"Legal moves - {[f'{i}: {m}' for i,m in enumerate(convert_move_list_to_pdn(legal_moves))]}"
    )


def print_board(WP, BP, kings) -> None:
    """
    Prints a visual representation of the board to the console with colored squares.
    Regular pieces are lowercase, kings are uppercase.
    """
    # ANSI escape codes for colors and styles
    RED = "\033[41m"
    RESET = "\033[0m"

    # File names
    print("\n    " + "   ".join(["A", "B", "C", "D", "E", "F", "G", "H"]))
    print("  +" + "---+" * 8)

    for row in range(8):
        # Rank numbers on the left side
        row_str = f"{8-row} |"

        for col in range(8):
            # Index from 32-bit board representation
            index = (7 - row) * 4 + (col // 2)
            is_king = kings & (1 << index)

            if row % 2 != col % 2:
                # Playable square
                if WP & (1 << index):
                    char = "(W)" if is_king else " w "
                elif BP & (1 << index):
                    char = "(B)" if is_king else " b "
                else:
                    char = "   "
            else:
                # Unplayable square (red square)
                char = RED + "   " + RESET

            row_str += f"{char}|"

        print(row_str)
        print("  +" + "---+" * 8)  # Print the row separator
    print("\n")


def get_ascii_board(WP, BP, kings) -> str:
    """
    Returns a simple ASCII string representation of the board with HTML line breaks.
    Regular pieces are lowercase, kings are uppercase.
    """
    board_str = ""

    for row in range(8):
        row_str = "|"
        for col in range(8):
            # Index from 32-bit board representation
            index = (7 - row) * 4 + (col // 2)
            is_king = kings & (1 << index)

            if row % 2 != col % 2:
                # Playable square
                if WP & (1 << index):
                    char = "(W)" if is_king else " w "
                elif BP & (1 << index):
                    char = "(B)" if is_king else " b "
                else:
                    char = "   "
            else:
                # Unplayable square
                char = "   "

            row_str += f" {char} |"

        board_str += row_str
        board_str += "<br>" + "+" + "----+" * 8 + "<br>"  # Use HTML line break

    return board_str


def convert_move_list_to_pdn(move_list) -> None:
    """
    Converts a list of move lists into PDN coordinates.
    """
    if move_list is None:
        return []
    pdn_moves = []
    for move in move_list:
        coords = [bitindex_to_coords(index) for index in move]
        pdn_moves.append("->".join(coords))
    return pdn_moves


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
