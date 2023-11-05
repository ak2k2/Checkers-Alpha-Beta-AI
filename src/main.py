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


def generate_simple_moves_white(WP, BP, K):
    simple_moves = []
    white_positions = find_set_bits(WP)
    occupied = WP | BP  # Combine occupied positions for both white and black pieces

    for pos in white_positions:
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


def generate_simple_moves_black(WP, BP, K):
    simple_moves = []
    black_positions = find_set_bits(BP)
    occupied = WP | BP  # Combine occupied positions for both white and black pieces

    for pos in black_positions:
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

    # Define the direction maps based on the player
    if player == "white":
        own_pieces = WP
        opponent_pieces = BP
        regular_directions = [WHITE_SOUTHWEST, WHITE_SOUTHEAST]
        king_directions = [
            BLACK_NORTHEAST,
            BLACK_NORTHWEST,
            WHITE_SOUTHWEST,
            WHITE_SOUTHEAST,
        ]
    else:  # player == 'black'
        own_pieces = BP
        opponent_pieces = WP
        regular_directions = [BLACK_NORTHEAST, BLACK_NORTHWEST]
        king_directions = [
            BLACK_NORTHEAST,
            BLACK_NORTHWEST,
            WHITE_SOUTHWEST,
            WHITE_SOUTHEAST,
        ]

    # Go through all the jumpers and generate jumps
    for pos in find_set_bits(jumpers):
        # Determine if the piece is a king
        is_king = K & (1 << pos) != 0

        # Select the correct directions based on whether the piece is a king
        directions = king_directions if is_king else regular_directions

        # Check all directions for possible jumps
        for direction in directions:
            next_square = direction.get(pos)
            if next_square is not None and is_set(opponent_pieces, next_square):
                jump_over_square = direction.get(next_square)
                if jump_over_square is not None and not is_set(
                    own_pieces | opponent_pieces, jump_over_square
                ):
                    # Add the initial jump move to the list
                    jump_moves.append((pos, jump_over_square))
                    # Further jumps would be handled by the recursive part here

    return jump_moves


def generate_jump_moves_fast(WP, BP, K, jumpers, player="white"):
    jump_moves = []

    # Choose the correct dictionaries based on the player
    directions = []
    if player == "white":
        own_pieces = WP
        opponent_pieces = BP
        directions = [WHITE_JUMP_SOUTHEAST, WHITE_JUMP_SOUTHWEST]
        king_directions = [
            BLACK_JUMP_NORTHEAST,
            BLACK_JUMP_NORTHWEST,
            WHITE_JUMP_SOUTHEAST,
            WHITE_JUMP_SOUTHWEST,
        ]
    else:  # player == "black"
        own_pieces = BP
        opponent_pieces = WP
        directions = [BLACK_JUMP_NORTHEAST, BLACK_JUMP_NORTHWEST]
        king_directions = [
            BLACK_JUMP_NORTHEAST,
            BLACK_JUMP_NORTHWEST,
            WHITE_JUMP_SOUTHEAST,
            WHITE_JUMP_SOUTHWEST,
        ]

    occupied = WP | BP  # Combine occupied positions for both white and black pieces

    # Go through all the jumpers and generate jumps
    for pos in find_set_bits(jumpers):
        # Determine if the piece is a king
        is_king = is_set(K, pos)
        # Select the correct directions based on whether the piece is a king
        possible_directions = king_directions if is_king else directions

        # Check all possible directions for valid jumps
        for direction in possible_directions:
            jump_over_square = direction.get(pos)
            if jump_over_square is not None and is_set(
                opponent_pieces, jump_over_square
            ):
                landing_square = direction.get(jump_over_square)
                if landing_square is not None and not is_set(occupied, landing_square):
                    # Add the jump move to the list
                    jump_moves.append((pos, landing_square))
                    # Note: Further jumps would be handled by a recursive call or iterative process
                    # This is where you would check for additional jumps from the landing square

    return jump_moves


if __name__ == "__main__":
    WP, BP, K = get_empty_board()

    WP = insert_piece(WP, 17)
    WP = insert_piece(WP, 26)
    WP = insert_piece(WP, 27)
    WP = insert_piece_by_pdntext(WP, "A5")

    BP = insert_piece(BP, 12)
    BP = insert_piece_by_pdntext(BP, "F6")

    print("STARTING BOARD")
    print_board(WP, BP, K)

    print(bin(get_movers_white(WP, BP, K)))

    wm = generate_simple_moves_white(
        get_movers_white(WP, BP, K), BP, K
    )  # generate all the simple moves for white pieces that can do a simple move

    bp = generate_simple_moves_black(
        WP, get_movers_black(WP, BP, K), K
    )  # generate all the simple moves for black pieces that can do a simple move

    print("White SIMPLE moves:")
    for move in wm:
        print(f"{bitindex_to_coords(move[0])} -> {bitindex_to_coords(move[1])}")

    print("Black SIMPLE moves:")
    for move in bp:
        print(f"{bitindex_to_coords(move[0])} -> {bitindex_to_coords(move[1])}")

    wjm = generate_jump_moves(WP, BP, K, get_jumpers_white(WP, BP, K))
    print("White single JUMP moves:")
    for ml in wjm:
        print(f"{bitindex_to_coords(ml[0])} -> {bitindex_to_coords(ml[1])}")

    bjm = generate_jump_moves(WP, BP, K, get_jumpers_black(WP, BP, K), player="black")
    print("Black single JUMP moves:")
    for ml in bjm:
        print(f"{bitindex_to_coords(ml[0])} -> {bitindex_to_coords(ml[1])}")

    wjmf = generate_jump_moves_fast(WP, BP, K, get_jumpers_white(WP, BP, K))
    print("\n\nFAST White single JUMP moves:")
    for ml in wjm:
        print(f"{bitindex_to_coords(ml[0])} -> {bitindex_to_coords(ml[1])}")

    bjmf = generate_jump_moves_fast(
        WP, BP, K, get_jumpers_black(WP, BP, K), player="black"
    )
    print("FAST Black single JUMP moves:")
    for ml in bjm:
        print(f"{bitindex_to_coords(ml[0])} -> {bitindex_to_coords(ml[1])}")

    # allwjm = generate_all_jump_moves(WP, BP, K)
    # print("White JUMP moves:")
    # for ml in allwjm:
    #     print(ml)

    # allbjm = generate_all_jump_moves(WP, BP, K, player="black")
    # print("Black JUMP moves:")
    # for ml in allbjm:
    #     print(ml)

    # jm = generate_all_jump_moves(WP, BP, K, player="black")
    # print("Black JUMP moves:")
    # print(jm)
    # jmw = generate_all_jump_moves(WP, BP, K, player="white")
    # print("White JUMP moves:")
    # print(jmw)

    # # Black JUMP moves:
    # # [[(16, 16), (16, 25)], [(18, 18), (18, 25)]]
    # for move_list in jm:
    #     for move in move_list:
    #         print(f"{bitindex_to_coords(move[0])} -> {bitindex_to_coords(move[1])}")

    # for move in jm:
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
