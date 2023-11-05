def generate_jump_moves_recursive(
    WP, BP, K, pos, jumped_over, moves, player="white", sequence=None
):
    king_directions = [
        BLACK_NORTHEAST,
        BLACK_NORTHWEST,
        WHITE_SOUTHWEST,
        WHITE_SOUTHEAST,
    ]

    if sequence is None:
        sequence = [(pos, jumped_over)]
    else:
        sequence.append((pos, jumped_over))

    # Define player-specific variables
    if player == "white":
        own_pieces = WP
        opponent_pieces = BP
        regular_directions = [WHITE_SOUTHWEST, WHITE_SOUTHEAST]
    else:
        own_pieces = BP
        opponent_pieces = WP
        regular_directions = [BLACK_NORTHEAST, BLACK_NORTHWEST]

    # Check if the current piece is a king
    is_king = K & (1 << pos) != 0
    directions = king_directions if is_king else regular_directions

    # Temporarily make the jump by updating bitboards
    own_pieces = own_pieces & ~(1 << pos) | (
        1 << jumped_over
    )  # Remove from old pos, add to new
    if len(sequence) > 1:  # Ensure there is a piece to remove
        opponent_pieces = opponent_pieces & ~(
            1 << sequence[-2][1]
        )  # Remove jumped opponent piece
    if is_king:
        K = K & ~(1 << pos) | (
            1 << jumped_over
        )  # Update king's position if it was a king

    further_jumps = False
    # Check all directions for possible further jumps
    for direction in directions:
        next_square = direction.get(jumped_over)
        if next_square is not None and is_set(opponent_pieces, next_square):
            jump_over_square = direction.get(next_square)
            if jump_over_square is not None and not is_set(
                own_pieces | opponent_pieces, jump_over_square
            ):
                # Recursive call to continue the jump sequence
                further_jumps = True
                generate_jump_moves_recursive(
                    WP,
                    BP,
                    K,
                    jumped_over,
                    jump_over_square,
                    moves,
                    player,
                    list(sequence),
                )

    # If no further jumps are possible, add the sequence to the moves list
    if not further_jumps and len(sequence) > 1:
        moves.append(sequence)


# Wrapper function to initiate the recursive jump generation
def generate_all_jump_moves(WP, BP, K, player="white"):
    jump_moves = []
    jumpers = (
        get_jumpers_white(WP, BP, K)
        if player == "white"
        else get_jumpers_black(WP, BP, K)
    )

    # Go through all jumpers and generate jump sequences
    for pos in find_set_bits(jumpers):
        generate_jump_moves_recursive(WP, BP, K, pos, pos, jump_moves, player)

    return jump_moves
