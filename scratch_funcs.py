# def generate_all_jump_sequences(
#     WP,
#     BP,
#     K,
#     pos,
#     is_king: bool,
#     player: str,
#     sequence=None,
#     sequences=None,
#     visited=None,
# ):
#     if sequences is None:
#         sequences = []
#     if sequence is None:
#         sequence = [pos]
#     if visited is None:
#         visited = set()  # To keep track of visited squares in the current sequence

#     # Determine if the current piece is kinged as a result of the last move
#     if not is_king and is_piece_kinged(pos, player):
#         is_king = True
#     else:
#         # Get all possible single jumps for the current position
#         jumpers = insert_piece(0, pos)
#         single_jumps = generate_jump_moves(WP, BP, K, jumpers, player)

#         # Filter out the jumps that lead to previously visited squares
#         single_jumps = [jump for jump in single_jumps if jump[1] not in visited]

#         for _, landing_square in single_jumps:
#             # Calculate the index of the jumped piece
#             jumped_pos = (pos + landing_square) // 2

#             # Make the jump and remove the jumped piece from the board
#             new_WP, new_BP, new_K = WP, BP, K
#             new_WP = remove_piece(new_WP, pos)
#             new_BP = remove_piece(new_BP, pos)
#             new_WP = (
#                 insert_piece(new_WP, landing_square) if player == "white" else new_WP
#             )
#             new_BP = (
#                 insert_piece(new_BP, landing_square) if player == "black" else new_BP
#             )
#             new_WP = remove_piece(new_WP, jumped_pos) if player == "black" else new_WP
#             new_BP = remove_piece(new_BP, jumped_pos) if player == "white" else new_BP
#             new_K = (K & ~insert_piece(0, pos)) | (
#                 insert_piece(0, landing_square) if is_king else 0
#             )

#             # Add this jump to the current sequence
#             new_sequence = sequence + [landing_square]
#             # Add the landing square to the visited set
#             new_visited = visited | {landing_square}
#             # Recursively generate the next jumps from the landing square
#             generate_all_jump_sequences(
#                 new_WP,
#                 new_BP,
#                 new_K,
#                 landing_square,
#                 is_king or is_piece_kinged(landing_square, player),
#                 player,
#                 new_sequence,
#                 sequences,
#                 new_visited,
#             )

#     if sequence and not single_jumps:
#         # If we have a sequence and there are no more jumps, we've reached the end of a sequence
#         sequences.append(sequence)
#     print(f"Sequences: {sequences}")
#     return sequences


# ----------------------------------------------------------------------

# def generate_jump_moves_recursive(
#     WP, BP, K, pos, jumped_over, moves, player="white", sequence=None
# ):
#     king_directions = [
#         BLACK_NORTHEAST,
#         BLACK_NORTHWEST,
#         WHITE_SOUTHWEST,
#         WHITE_SOUTHEAST,
#     ]

#     if sequence is None:
#         sequence = [(pos, jumped_over)]
#     else:
#         sequence.append((pos, jumped_over))

#     # Define player-specific variables
#     if player == "white":
#         own_pieces = WP
#         opponent_pieces = BP
#         regular_directions = [WHITE_SOUTHWEST, WHITE_SOUTHEAST]
#     else:
#         own_pieces = BP
#         opponent_pieces = WP
#         regular_directions = [BLACK_NORTHEAST, BLACK_NORTHWEST]

#     # Check if the current piece is a king
#     is_king = K & (1 << pos) != 0
#     directions = king_directions if is_king else regular_directions

#     # Temporarily make the jump by updating bitboards
#     own_pieces = own_pieces & ~(1 << pos) | (
#         1 << jumped_over
#     )  # Remove from old pos, add to new
#     if len(sequence) > 1:  # Ensure there is a piece to remove
#         opponent_pieces = opponent_pieces & ~(
#             1 << sequence[-2][1]
#         )  # Remove jumped opponent piece
#     if is_king:
#         K = K & ~(1 << pos) | (
#             1 << jumped_over
#         )  # Update king's position if it was a king

#     further_jumps = False
#     # Check all directions for possible further jumps
#     for direction in directions:
#         next_square = direction.get(jumped_over)
#         if next_square is not None and is_set(opponent_pieces, next_square):
#             jump_over_square = direction.get(next_square)
#             if jump_over_square is not None and not is_set(
#                 own_pieces | opponent_pieces, jump_over_square
#             ):
#                 # Recursive call to continue the jump sequence
#                 further_jumps = True
#                 generate_jump_moves_recursive(
#                     WP,
#                     BP,
#                     K,
#                     jumped_over,
#                     jump_over_square,
#                     moves,
#                     player,
#                     list(sequence),
#                 )

#     # If no further jumps are possible, add the sequence to the moves list
#     if not further_jumps and len(sequence) > 1:
#         moves.append(sequence)


# # Wrapper function to initiate the recursive jump generation
# def generate_all_jump_moves(WP, BP, K, player="white"):
#     jump_moves = []
#     jumpers = (
#         get_jumpers_white(WP, BP, K)
#         if player == "white"
#         else get_jumpers_black(WP, BP, K)
#     )

#     # Go through all jumpers and generate jump sequences
#     for pos in find_set_bits(jumpers):
#         generate_jump_moves_recursive(WP, BP, K, pos, pos, jump_moves, player)

#     return jump_moves


# def old_generate_jump_moves(WP, BP, K, jumpers, player="white"):
#     jump_moves = []

#     # Define the direction maps based on the player
#     if player == "white":
#         own_pieces = WP
#         opponent_pieces = BP
#         regular_directions = [WHITE_SOUTHWEST, WHITE_SOUTHEAST]
#         king_directions = [
#             BLACK_NORTHEAST,
#             BLACK_NORTHWEST,
#             WHITE_SOUTHWEST,
#             WHITE_SOUTHEAST,
#         ]
#     else:  # player == 'black'
#         own_pieces = BP
#         opponent_pieces = WP
#         regular_directions = [BLACK_NORTHEAST, BLACK_NORTHWEST]
#         king_directions = [
#             BLACK_NORTHEAST,
#             BLACK_NORTHWEST,
#             WHITE_SOUTHWEST,
#             WHITE_SOUTHEAST,
#         ]

#     # Go through all the jumpers and generate jumps
#     for pos in find_set_bits(jumpers):
#         # Determine if the piece is a king
#         is_king = K & (1 << pos) != 0

#         # Select the correct directions based on whether the piece is a king
#         directions = king_directions if is_king else regular_directions

#         # Check all directions for possible jumps
#         for direction in directions:
#             next_square = direction.get(pos)
#             if next_square is not None and is_set(opponent_pieces, next_square):
#                 jump_over_square = direction.get(next_square)
#                 if jump_over_square is not None and not is_set(
#                     own_pieces | opponent_pieces, jump_over_square
#                 ):
#                     # Add the initial jump move to the list
#                     jump_moves.append((pos, jump_over_square))
#                     # Further jumps would be handled by the recursive part here

#     return jump_moves
