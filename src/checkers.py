from util.helpers import *
from util.masks import *


def do_move(WP, BP, K, moves, player):
    if len(moves) == 1:
        move = [(moves)]
    else:
        moves = [(moves[i], moves[i + 1]) for i in range(len(moves) - 1)]

    for move in moves:
        start_pos, end_pos = move  # Move is a tuple: (start_pos, end_pos)

        # Determine if this is a jump move
        is_jump = abs(start_pos - end_pos) > 5

        # Create a mask for the starting and ending positions
        start_mask = (1 << start_pos) & MASK_32
        end_mask = (1 << end_pos) & MASK_32

        # Update the board based on the player's move
        if player == PlayerTurn.WHITE:
            WP = remove_piece(WP, start_pos)
            WP = insert_piece(WP, end_pos)

            # If a jump is made, remove the jumped piece from the opponent and UPDATE KING BITBOARD!
            if is_jump:
                jumped_pos = find_jumped_pos(start_pos, end_pos)
                BP = remove_piece(BP, jumped_pos)
                K = remove_piece(K, jumped_pos)  # UPDATE KING BITBOARD!

            # Check for kinging
            if end_mask & KING_ROW_WHITE:
                K = insert_piece(K, end_pos)

        elif player == PlayerTurn.BLACK:
            BP = remove_piece(BP, start_pos)
            BP = insert_piece(BP, end_pos)

            if is_jump:
                jumped_pos = find_jumped_pos(start_pos, end_pos)
                # WP &= ~(1 << jumped_pos) & MASK_32
                WP = remove_piece(WP, jumped_pos)
                K = remove_piece(K, jumped_pos)  # UPDATE KING BITBOARD!

            if end_mask & KING_ROW_BLACK:
                K = insert_piece(K, end_pos)

        # Update the kings bitboard if a king has been moved
        if start_mask & K:
            K = remove_piece(K, start_pos)
            K = insert_piece(K, end_pos)

    return WP, BP, K


def generate_legal_moves(WP, BP, K, turn):
    """
    Returns a list of all legal moves for the given player. If no moves are available, returns None.
    """
    if turn == PlayerTurn.WHITE:
        # Check for jump moves first
        white_jumpers = get_jumpers_white(WP, BP, K)
        if white_jumpers:
            return all_jump_sequences(WP, BP, K, white_jumpers, None, turn)

        # If no jump moves, check for simple moves
        white_movers = get_movers_white(WP, BP, K)

        if white_movers:
            return generate_simple_moves_white(WP, BP, K, white_movers)

        return None  # No moves available - game over for white.

    elif turn == PlayerTurn.BLACK:
        black_jumpers = get_jumpers_black(WP, BP, K)
        if black_jumpers:
            return all_jump_sequences(WP, BP, K, None, black_jumpers, turn)

        black_movers = get_movers_black(WP, BP, K)
        if black_movers:
            return generate_simple_moves_black(WP, BP, K, black_movers)

        return None  # No moves available - game over for black.


def find_jumped_pos(start_pos, end_pos):
    """
    Returns the position of the jumped piece given the start and end positions of a move.
    """

    for direction, jump_mask in JUMP_MASKS.items():
        if jump_mask[start_pos] == end_pos:
            # Get the mask for the move to find the jumped square
            move_mask = MOVE_MASKS[DIRECTION_MAP[direction]]
            return move_mask[start_pos]
    # Will never happen unless the start and end positions are invalid
    return None


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
        Input: White movers.
        Output: List of tuples representing all the simple moves for white pieces. ex. [(20, 16), (21, 18), (22, 18), (22, 19), (23, 19)]
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
        Input: Black movers.
        Output: List of tuples representing all the simple moves for Black pieces. ex. [(20, 16), (21, 18), (22, 18), (22, 19), (23, 19)]
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
    """
    Returns a list of tuples representing all the single jump moves for the given player
        Input: jumpers, player
        Output: List of tuples representing all the jump moves for the given player.
                ex. [(20, 17, 13), (20, 25, 29), (21, 17, 12)]
                where (20, 17, 13) means a piece at 20 jumps over a piece at 17 and lands at 13.
    """
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
    """
    Returns a list of all possible jump sequences for the given piece.
        Input: WP, BP, K, pos, is_king, player, sequence, sequences
        Output: List of all possible jump sequences for the given piece.
                ex. [[20, 17, 13], [20, 25, 29], [21, 17, 12]]
                where [20, 17, 13] means a piece at 20 jumps over a piece at 17 and lands at 13.

    """
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
            list(sequence)  # TODO: this data structure is not ideal
        )  # Make a copy of the sequence to store it independently

    return sequences


def is_piece_kinged(pos, player):
    return (player == PlayerTurn.WHITE and (S[pos] & KING_ROW_WHITE)) or (
        player == PlayerTurn.BLACK and (S[pos] & KING_ROW_BLACK)
    )


def all_jump_sequences(
    WP, BP, K, white_jumpers=None, black_jumpers=None, player=PlayerTurn.WHITE
):
    """
    Returns a list of all possible jump sequences for the given player.
        Input: WP, BP, K, white_jumpers, black_jumpers, player
        Output: List of all possible jump sequences for the given player.
                ex. [[8, 17, 26], [0, 9, 18, 27]]
                [0, 9, 18, 27] means a piece at 0 jumps over a piece at 4 and lands at 9, then jumps over a piece at 13 and lands at 18.
    """
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


# if __name__ == "__main__":
#     WP, BP, K = get_fresh_board()
#     print_board(WP, BP, K)
