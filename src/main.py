from util.helpers import (
    PDN_MAP,
    bitindex_to_coords,
    coords_to_bitindex,
    find_set_bits,
    get_empty_board,
    get_fresh_board,
    insert_piece,
    insert_piece_by_pdntext,
    is_set,
    set_bit,
    print_bin_strings,
    print_board,
    remove_piece,
    remove_piece_by_pdntext,
)

from util.masks import (
    BLACK_JUMP_NORTHEAST,
    BLACK_JUMP_NORTHWEST,
    BLACK_NORTHEAST,
    BLACK_NORTHWEST,
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
    if KINGS & (1 << src_index):
        KINGS = remove_piece(KINGS, src_index)  # Remove from source
        KINGS = insert_piece(
            KINGS, dest_index
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
    """
    Returns a binary int of all the white pieces that can make a jump move of some kind.
        Input: WP, BP, K
        Output: white jumpers
    """
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
    """
    Returns a binary int of all the black pieces that can make a jump move of some kind.
        Input: WP, BP, K
        Output: black jumpers
    """
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


def generate_simple_moves_black(
    WP, BP, K, black_movers
):  # TODO: Add black_movers as an argument
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


def generate_jump_moves(WP, BP, K, jumpers, player="white"):
    jump_moves = []

    # Choose the correct dictionaries based on the player and kings
    white_jump_directions = [WHITE_JUMP_SOUTHEAST, WHITE_JUMP_SOUTHWEST]
    black_jump_directions = [BLACK_JUMP_NORTHEAST, BLACK_JUMP_NORTHWEST]
    white_move_directions = [WHITE_SOUTHEAST, WHITE_SOUTHWEST]
    black_move_directions = [BLACK_NORTHEAST, BLACK_NORTHWEST]

    # Assign opponent pieces and directions based on the current player
    if player == "white":
        own_pieces = WP
        opponent_pieces = BP
        own_jump_directions = white_jump_directions
        own_move_directions = white_move_directions
        opp_jump_directions = black_jump_directions  # for kings
        opp_move_directions = black_move_directions  # for kings
    else:  # player == "black"
        own_pieces = BP
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
                    jump_moves.append((pos, landing_square))

    return jump_moves


def generate_all_jump_sequences(
    WP,
    BP,
    K,
    pos,
    is_king: bool,
    player: str,
    sequence=None,
    sequences=None,
    visited=None,
):
    if sequences is None:
        sequences = []
    if sequence is None:
        sequence = []
    if visited is None:
        visited = set()  # To keep track of visited squares in the current sequence

    # Determine if the current piece is kinged as a result of the last move
    if not is_king and is_piece_kinged(pos, player):
        is_king = True
    else:
        # Get all possible single jumps for the current position
        jumpers = insert_piece(0, pos)
        single_jumps = generate_jump_moves(WP, BP, K, jumpers, player)

        # Filter out the jumps that lead to previously visited squares
        single_jumps = [jump for jump in single_jumps if jump[1] not in visited]

        for _, landing_square in single_jumps:
            # Calculate the index of the jumped piece
            jumped_pos = (pos + landing_square) // 2

            # Make the jump and remove the jumped piece from the board
            new_WP, new_BP, new_K = WP, BP, K
            new_WP = remove_piece(new_WP, pos)
            new_BP = remove_piece(new_BP, pos)
            new_WP = (
                insert_piece(new_WP, landing_square) if player == "white" else new_WP
            )
            new_BP = (
                insert_piece(new_BP, landing_square) if player == "black" else new_BP
            )
            new_WP = remove_piece(new_WP, jumped_pos) if player == "black" else new_WP
            new_BP = remove_piece(new_BP, jumped_pos) if player == "white" else new_BP
            new_K = (K & ~insert_piece(0, pos)) | (
                insert_piece(0, landing_square) if is_king else 0
            )

            # Add this jump to the current sequence
            new_sequence = sequence + [landing_square]
            # Add the landing square to the visited set
            new_visited = visited | {landing_square}
            # Recursively generate the next jumps from the landing square
            generate_all_jump_sequences(
                new_WP,
                new_BP,
                new_K,
                landing_square,
                is_king or is_piece_kinged(landing_square, player),
                player,
                new_sequence,
                sequences,
                new_visited,
            )

    if sequence and not single_jumps:
        # If we have a sequence and there are no more jumps, we've reached the end of a sequence
        sequences.append(sequence)

    return sequences


def is_piece_kinged(pos, player):
    # This function determines if a piece should be kinged based on its position
    # and the player. For simplicity, assume the top row indices are 0 to 3 and
    # the bottom row indices are 28 to 31 for an 8x8 board.
    if player == "white" and pos in range(28, 32):
        return True
    elif player == "black" and pos in range(0, 4):
        return True
    return False


def all_jump_sequences(
    WP, BP, K, white_jumpers=None, black_jumpers=None, player="white"
):
    jump_sequences_pdn = []

    if player == "white":
        # Generate sequences for white pieces
        for pos in find_set_bits(white_jumpers):
            is_king = is_set(K, pos)
            sequences = generate_all_jump_sequences(WP, BP, K, pos, is_king, "white")
            for sequence in sequences:
                pdn_sequence = [bitindex_to_coords(pos)] + [
                    bitindex_to_coords(step) for step in sequence
                ]
                jump_sequences_pdn.append(pdn_sequence)
        return jump_sequences_pdn

    elif player == "black":
        # Generate sequences for black pieces
        for pos in find_set_bits(black_jumpers):
            is_king = is_set(K, pos)
            sequences = generate_all_jump_sequences(WP, BP, K, pos, is_king, "black")
            for sequence in sequences:
                pdn_sequence = [bitindex_to_coords(pos)] + [
                    bitindex_to_coords(step) for step in sequence
                ]
                jump_sequences_pdn.append(pdn_sequence)
        return jump_sequences_pdn


def generate_legal_moves(WP, BP, K, turn="white"):
    if turn == "white":
        # Check for jump moves first
        white_jumpers = get_jumpers_white(WP, BP, K)
        if white_jumpers:
            return all_jump_sequences(WP, BP, K, white_jumpers, None, "white")

        # If no jump moves, check for simple moves
        white_movers = get_movers_white(WP, BP, K)

        if white_movers:
            return generate_simple_moves_white(WP, BP, K, white_movers)

        # If no moves available, game over
        print("No moves available - game over for white.")
        return None

    elif turn == "black":
        black_jumpers = get_jumpers_black(WP, BP, K)
        if black_jumpers:
            return all_jump_sequences(WP, BP, K, None, black_jumpers, "black")

        black_movers = get_movers_black(WP, BP, K)
        if black_movers:
            return generate_simple_moves_black(WP, BP, K, black_movers)

        print("No moves available - game over for black.")
        return None

    else:
        raise ValueError("Invalid turn value. Use 'white' or 'black'.")


if __name__ == "__main__":
    WP, BP, K = get_empty_board()

    WP = insert_piece(WP, 17)
    WP = insert_piece(WP, 26)
    WP = insert_piece_by_pdntext(WP, "A5")
    K = insert_piece_by_pdntext(K, "A5")
    BP = insert_piece_by_pdntext(BP, "D2")
    K = insert_piece_by_pdntext(K, "D2")
    WP = insert_piece_by_pdntext(WP, "F8")
    WP = insert_piece_by_pdntext(WP, "C7")

    BP = insert_piece(BP, 12)
    BP = insert_piece_by_pdntext(BP, "F6")
    BP = insert_piece_by_pdntext(BP, "F2")
    BP = insert_piece_by_pdntext(BP, "H2")
    BP = insert_piece_by_pdntext(BP, "F4")
    BP = insert_piece_by_pdntext(BP, "D4")

    WP, BP, K = get_fresh_board()

    white_moves = generate_legal_moves(WP, BP, K, "white")
    black_moves = generate_legal_moves(WP, BP, K, "black")

    print_board(WP, BP, K)
    print(f"White moves: {white_moves}")
    print(f"Black moves: {black_moves}")

    # WP, BP, K = get_empty_board()
    # WP = insert_piece(WP, 17)
    # WP = insert_piece(WP, 26)
    # WP = insert_piece(WP, 27)
    # WP = insert_piece_by_pdntext(WP, "A5")
    # K = insert_piece_by_pdntext(K, "A5")
    # BP = insert_piece_by_pdntext(BP, "D2")
    # K = insert_piece_by_pdntext(K, "D2")
    # WP = insert_piece_by_pdntext(WP, "F8")

    # BP = insert_piece(BP, 12)
    # BP = insert_piece_by_pdntext(BP, "F6")
    # BP = insert_piece_by_pdntext(BP, "F2")
    # BP = insert_piece_by_pdntext(BP, "H2")
    # BP = insert_piece_by_pdntext(BP, "F4")

    # wj = get_jumpers_white(WP, BP, K)
    # wm = generate_simple_moves_white(WP, BP, K)
    # wj = get_jumpers_white(WP, BP, K)
    # bm = generate_simple_moves_black(WP, BP, K)

    # print_board(WP, BP, K)

    # print("White jumpers:")
    # print(wj)
    # print("Black jumpers:")
    # print(bj)

    # wm = generate_simple_moves_white(WP, BP, K)
    # bm = generate_simple_moves_black(WP, BP, K)

    # print_board(WP, BP, K)

    # print("White simple moves:")
    # print(wm)
    # for move in wm:
    #     print(f"{bitindex_to_coords(move[0])} -> {bitindex_to_coords(move[1])}")

    # print("Black simple moves:")
    # for move in bm:
    #     print(f"{bitindex_to_coords(move[0])} -> {bitindex_to_coords(move[1])}")

    # WP, BP, K = get_empty_board()

    # WP = insert_piece(WP, 17)
    # WP = insert_piece(WP, 26)
    # WP = insert_piece(WP, 27)
    # WP = insert_piece_by_pdntext(WP, "A5")
    # K = insert_piece_by_pdntext(K, "A5")
    # BP = insert_piece_by_pdntext(BP, "D2")
    # K = insert_piece_by_pdntext(K, "D2")
    # WP = insert_piece_by_pdntext(WP, "F8")

    # BP = insert_piece(BP, 12)
    # BP = insert_piece_by_pdntext(BP, "F6")
    # BP = insert_piece_by_pdntext(BP, "F2")
    # BP = insert_piece_by_pdntext(BP, "H2")
    # BP = insert_piece_by_pdntext(BP, "F4")

    # print("STARTING BOARD")
    # print_board(WP, BP, K)

    # print(bin(get_movers_white(WP, BP, K)))

    # wm = generate_simple_moves_white(
    #     get_movers_white(WP, BP, K), BP, K
    # )  # generate all the simple moves for white pieces that can do a simple move

    # bm = generate_simple_moves_black(
    #     WP, get_movers_black(WP, BP, K), K
    # )  # generate all the simple moves for black pieces that can do a simple move

    # print("White SIMPLE moves:")
    # for move in wm:
    #     print(f"{bitindex_to_coords(move[0])} -> {bitindex_to_coords(move[1])}")

    # print("Black SIMPLE moves:")
    # for move in bm:
    #     print(f"{bitindex_to_coords(move[0])} -> {bitindex_to_coords(move[1])}")

    # wjm = generate_jump_moves(WP, BP, K, get_jumpers_white(WP, BP, K))
    # print("White single JUMP moves:")
    # for ml in wjm:
    #     print(f"{bitindex_to_coords(ml[0])} -> {bitindex_to_coords(ml[1])}")

    # bjm = generate_jump_moves(WP, BP, K, get_jumpers_black(WP, BP, K), player="black")
    # print("Black single JUMP moves:")
    # for ml in bjm:
    #     print(f"{bitindex_to_coords(ml[0])} -> {bitindex_to_coords(ml[1])}")

    # print(test_jump_sequences(WP, BP, K))
