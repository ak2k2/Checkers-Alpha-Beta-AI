from enum import Enum

from util.helpers import (
    PDN_MAP,
    bitindex_to_coords,
    convert_move_list_to_pdn,
    coords_to_bitindex,
    find_set_bits,
    get_empty_board,
    get_fresh_board,
    insert_piece,
    insert_piece_by_pdntext,
    is_set,
    print_bin_strings,
    print_board,
    remove_piece,
    remove_piece_by_pdntext,
    set_bit,
)
from util.masks import (
    BLACK_JUMP_NORTHEAST,
    BLACK_JUMP_NORTHWEST,
    BLACK_NORTHEAST,
    BLACK_NORTHWEST,
    KING_ROW_BLACK,
    KING_ROW_WHITE,
    MASK_32,
    MASK_L3,
    MASK_L5,
    MASK_R3,
    MASK_R5,
    WHITE_JUMP_SOUTHEAST,
    WHITE_JUMP_SOUTHWEST,
    WHITE_SOUTHEAST,
    WHITE_SOUTHWEST,
    S,
)


class PlayerTurn(Enum):
    WHITE = 1
    BLACK = 2


def make_move(move, WP, BP, K):
    """
    Takes a move tuple and updates the board accordingly.
    """
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
    if K & (1 << src_index):
        K = remove_piece(K, src_index)  # Remove from source
        K = insert_piece(
            K, dest_index
        )  # Insert to destination (works for both white and black)

    return WP, BP, K


def get_movers_white(WP, BP, K):
    """
    Returns a binary int of all the white pieces that can make a "simple" move bit NOT a jump move)
        Input: WP, BP, K
        Output: white movers
    """
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
    """
    Returns a binary int of all the black pieces that can make a "simple" move but NOT a jump move)
        Input: WP, BP, K
        Output: black movers
    """
    # Constants for masks, assuming they prevent wraparound for upward moves
    nOcc = ~(WP | BP) & MASK_32  # Not Occupied
    BK = BP & K & MASK_32  # Black Kings

    # Calculate potential moves for black non-kings upwards
    Movers = (nOcc >> 4) & BP & MASK_32  # Move up 4
    Movers |= ((nOcc & MASK_R3) >> 3) & BP & MASK_32  # Move up right 3
    Movers |= ((nOcc & MASK_R5) >> 5) & BP & MASK_32  # Move up right 5

    # Calculate potential moves for black kings (which can move both up and down)
    if BK:
        Movers |= (nOcc << 4) & BK & MASK_32  # Move down 4
        Movers |= ((nOcc & MASK_L3) << 3) & BK & MASK_32  # Move down left 3
        Movers |= ((nOcc & MASK_L5) << 5) & BK & MASK_32  # Move down left 5

    return Movers


def get_jumpers_white(WP, BP, K):
    """
    Returns a binary int of all the white pieces that can make a jump move of some kind.
        Input: WP, BP, K
        Output: white jumpers
    """
    nOcc = ~(WP | BP) & MASK_32  # Not Occupied
    WK = WP & K & MASK_32  # White Kings
    Jumpers = 0

    # Shift for normal pieces
    Temp = (nOcc << 4) & BP & MASK_32
    if Temp:
        Jumpers |= (((Temp & MASK_L3) << 3) | ((Temp & MASK_L5) << 5)) & WP & MASK_32

    Temp = (((nOcc & MASK_L3) << 3) | ((nOcc & MASK_L5) << 5)) & BP & MASK_32
    Jumpers |= (Temp << 4) & WP & MASK_32

    # Shift for kings
    if WK:
        Temp = (nOcc >> 4) & BP & MASK_32
        if Temp:
            Jumpers |= (
                (((Temp & MASK_R3) >> 3) | ((Temp & MASK_R5) >> 5)) & WK & MASK_32
            )
        Temp = (((nOcc & MASK_R3) >> 3) | ((nOcc & MASK_R5) >> 5)) & BP & MASK_32
        if Temp:
            Jumpers |= (Temp >> 4) & WK & MASK_32

    return Jumpers


def get_jumpers_black(WP, BP, K):
    """
    Returns a binary int of all the black pieces that can make a jump move of some kind.
        Input: WP, BP, K
        Output: black jumpers
    """

    nOcc = ~(WP | BP) & MASK_32  # Not Occupied
    BK = BP & K & MASK_32  # Black Kings
    Jumpers = 0

    # Shift for normal pieces
    Temp = (nOcc >> 4) & WP & MASK_32
    if Temp:
        Jumpers |= (((Temp & MASK_R3) >> 3) | ((Temp & MASK_R5) >> 5)) & BP & MASK_32

    Temp = (((nOcc & MASK_R3) >> 3) | ((nOcc & MASK_R5) >> 5)) & WP & MASK_32
    Jumpers |= (Temp >> 4) & BP & MASK_32

    # Shift for kings
    if BK:
        Temp = (nOcc << 4) & WP & MASK_32
        if Temp:
            Jumpers |= (
                (((Temp & MASK_L3) << 3) | ((Temp & MASK_L5) << 5)) & BK & MASK_32
            )
        Temp = (((nOcc & MASK_L3) << 3) | ((nOcc & MASK_L5) << 5)) & WP & MASK_32
        if Temp:
            Jumpers |= (Temp << 4) & BK & MASK_32

    return Jumpers


def generate_simple_moves_white(WP, BP, K, white_movers):
    """
    Returns a list of tuples representing all the simple moves (i.e. not jump moves) for white pieces.
        Input: Should take in White movers
    """
    simple_moves = []
    occupied = WP | BP  # Combine occupied positions for both white and black pieces

    white_mover_positions = find_set_bits(white_movers)

    for pos in white_mover_positions:
        is_king = is_set(K, pos)

        # Define potential moves based on whether the piece is a king
        if is_king:
            directions = [
                WHITE_SOUTHWEST,
                WHITE_SOUTHEAST,
                BLACK_NORTHEAST,
                BLACK_NORTHWEST,
            ]
        else:
            directions = [WHITE_SOUTHWEST, WHITE_SOUTHEAST]

        # Pre-filter None values and make sure the move is not occupied
        potential_moves = [
            direction.get(pos)
            for direction in directions
            if direction.get(pos) is not None
        ]
        valid_moves = [move for move in potential_moves if not is_set(occupied, move)]

        # Append valid moves to the simple_moves list
        simple_moves.extend([(pos, move) for move in valid_moves])

    return simple_moves


def generate_simple_moves_black(WP, BP, K, black_movers):
    """
    Returns a list of tuples representing all the simple moves (i.e. not jump moves) for black pieces.
    """
    simple_moves = []
    occupied = WP | BP  # Combine occupied positions for both white and black pieces
    black_mover_positions = find_set_bits(black_movers)

    for pos in black_mover_positions:
        is_king = is_set(K, pos)

        # Define potential moves based on whether the piece is a king
        if is_king:
            directions = [
                BLACK_NORTHEAST,
                BLACK_NORTHWEST,
                WHITE_SOUTHWEST,
                WHITE_SOUTHEAST,
            ]
        else:
            directions = [BLACK_NORTHEAST, BLACK_NORTHWEST]

        # Pre-filter None values and make sure the move is not occupied
        potential_moves = [
            direction.get(pos)
            for direction in directions
            if direction.get(pos) is not None
        ]
        valid_moves = [move for move in potential_moves if not is_set(occupied, move)]

        # Append valid moves to the simple_moves list
        simple_moves.extend([(pos, move) for move in valid_moves])

    return simple_moves


def generate_jump_moves(WP, BP, K, jumpers, player):
    jump_moves = []

    # Choose the correct dictionaries based on the player and kings
    white_jump_directions = [WHITE_JUMP_SOUTHEAST, WHITE_JUMP_SOUTHWEST]
    black_jump_directions = [BLACK_JUMP_NORTHEAST, BLACK_JUMP_NORTHWEST]
    white_move_directions = [WHITE_SOUTHEAST, WHITE_SOUTHWEST]
    black_move_directions = [BLACK_NORTHEAST, BLACK_NORTHWEST]

    # Assign opponent pieces and directions based on the current player
    if player == PlayerTurn.WHITE:
        opponent_pieces = BP
        own_jump_directions = white_jump_directions
        own_move_directions = white_move_directions
        opp_jump_directions = black_jump_directions  # for kings
        opp_move_directions = black_move_directions  # for kings
    elif player == PlayerTurn.BLACK:
        opponent_pieces = WP
        own_jump_directions = black_jump_directions
        own_move_directions = black_move_directions
        opp_jump_directions = white_jump_directions  # for kings
        opp_move_directions = white_move_directions  # for kings

    occupied = WP | BP  # Combine occupied positions for both white and black pieces

    # Go through all the jumpers and generate jumps
    for pos in find_set_bits(jumpers):
        # Determine if the piece is a king
        is_king = is_set(K, pos)

        # Kings can jump in all directions, so we use both sets of directions
        if is_king:
            possible_jump_directions = own_jump_directions + opp_jump_directions
            possible_move_directions = own_move_directions + opp_move_directions
        else:
            possible_jump_directions = own_jump_directions
            possible_move_directions = own_move_directions

        # Check all possible directions for valid jumps
        for jump_dir, move_dir in zip(
            possible_jump_directions, possible_move_directions
        ):
            intermediate_square = move_dir.get(pos)
            landing_square = jump_dir.get(pos)
            if intermediate_square is not None and landing_square is not None:
                # Check if the intermediate square has an opponent piece and the landing square is empty
                if is_set(opponent_pieces, intermediate_square) and not is_set(
                    occupied, landing_square
                ):
                    # Add the jump move to the list
                    jump_moves.append((pos, intermediate_square, landing_square))

    return jump_moves


def generate_all_jump_sequences(
    WP, BP, K, pos, is_king: bool, player: str, sequence=None, sequences=None
):
    if sequences is None:
        sequences = []
    if sequence is None:
        sequence = [pos]

    # Determine if the current piece is kinged as a result of the last move
    if not is_king and is_piece_kinged(pos, player):
        is_king = True

    # Get all possible simple jumps for the current position
    jumpers = insert_piece(0, pos)
    single_jumps = generate_jump_moves(WP, BP, K, jumpers, player)

    for _, intermediate_square, landing_square in single_jumps:
        # Here, instead of creating new bitboards, modify and then restore the original ones
        original_WP, original_BP, original_K = WP, BP, K

        # Make the jump and update the board state without creating new variables
        WP = remove_piece(WP, pos)
        BP = remove_piece(BP, pos)
        WP = insert_piece(WP, landing_square) if player == PlayerTurn.WHITE else WP
        BP = insert_piece(BP, landing_square) if player == PlayerTurn.BLACK else BP
        WP = remove_piece(WP, intermediate_square) if player == PlayerTurn.BLACK else WP
        BP = remove_piece(BP, intermediate_square) if player == PlayerTurn.WHITE else BP
        K = (K & ~insert_piece(0, pos)) | (
            insert_piece(0, landing_square) if is_king else 0
        )

        # Append to the current sequence instead of creating a new one
        sequence.append(landing_square)

        # Recursive call with the modified sequence
        generate_all_jump_sequences(
            WP, BP, K, landing_square, is_king, player, sequence, sequences
        )

        # Restore the original board state and sequence
        WP, BP, K = original_WP, original_BP, original_K
        sequence.pop()  # Remove the last element to restore the original sequence

    # If no further jumps are possible or the piece was just kinged, then finalize the sequence.
    if not single_jumps or (not is_king and is_piece_kinged(pos, player)):
        sequences.append(
            list(sequence)
        )  # Make a copy of the sequence to store it independently

    return sequences


def is_piece_kinged(pos, player):
    return (player == PlayerTurn.WHITE and (S[pos] & KING_ROW_WHITE)) or (
        player == PlayerTurn.BLACK and (S[pos] & KING_ROW_BLACK)
    )


def all_jump_sequences(
    WP, BP, K, white_jumpers=None, black_jumpers=None, player=PlayerTurn.WHITE
):
    jump_sequences = []

    if player == PlayerTurn.WHITE:
        # Generate sequences for white pieces
        for pos in find_set_bits(white_jumpers):
            is_king = is_set(K, pos)
            jump_sequences.extend(
                generate_all_jump_sequences(WP, BP, K, pos, is_king, player)
            )
        return jump_sequences

    elif player == PlayerTurn.BLACK:
        # Generate sequences for black pieces
        for pos in find_set_bits(black_jumpers):
            # print(f"Generating sequences for black piece at {bitindex_to_coords(pos)}")
            is_king = is_set(K, pos)
            jump_sequences.extend(
                generate_all_jump_sequences(WP, BP, K, pos, is_king, player)
            )
        return jump_sequences


def generate_legal_moves(WP, BP, K, turn):
    if turn == PlayerTurn.WHITE:
        # Check for jump moves first
        white_jumpers = get_jumpers_white(WP, BP, K)
        if white_jumpers:
            return all_jump_sequences(WP, BP, K, white_jumpers, None, turn)

        # If no jump moves, check for simple moves
        white_movers = get_movers_white(WP, BP, K)

        if white_movers:
            return generate_simple_moves_white(WP, BP, K, white_movers)

        # If no moves available, game over
        # print("No moves available - game over for white.")
        return None

    elif turn == PlayerTurn.BLACK:
        black_jumpers = get_jumpers_black(WP, BP, K)
        if black_jumpers:
            return all_jump_sequences(WP, BP, K, None, black_jumpers, turn)

        black_movers = get_movers_black(WP, BP, K)
        if black_movers:
            return generate_simple_moves_black(WP, BP, K, black_movers)

        # print("No moves available - game over for black.")
        return None


if __name__ == "__main__":
    WP, BP, K = get_fresh_board()
    print_board(WP, BP, K)
