import cProfile

from main import (
    BLACK_JUMP_NORTHEAST,
    BLACK_JUMP_NORTHWEST,
    BLACK_NORTHEAST,
    BLACK_NORTHWEST,
    KING_ROW_BLACK,
    KING_ROW_WHITE,
    MASK_32,
    WHITE_JUMP_SOUTHEAST,
    WHITE_JUMP_SOUTHWEST,
    WHITE_SOUTHEAST,
    WHITE_SOUTHWEST,
    PlayerTurn,
    convert_move_list_to_pdn,
    generate_legal_moves,
    get_empty_board,
    get_fresh_board,
    insert_piece_by_pdntext,
    print_board,
)

# from heuristic import heuristic

# Assuming these masks are defined correctly elsewhere:
# WHITE_JUMP_SOUTHEAST, WHITE_JUMP_SOUTHWEST, BLACK_JUMP_NORTHEAST, BLACK_JUMP_NORTHWEST
# WHITE_SOUTHEAST, WHITE_SOUTHWEST, BLACK_NORTHEAST, BLACK_NORTHWEST

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


# Function to determine the jumped position given the start and end positions
def find_jumped_pos(start_pos, end_pos):
    for direction, jump_mask in JUMP_MASKS.items():
        if jump_mask[start_pos] == end_pos:
            # Get the mask for the move to find the jumped square
            move_mask = MOVE_MASKS[DIRECTION_MAP[direction]]
            return move_mask[start_pos]
    # If no direction is found, return None or an appropriate value
    return None


def do_move(WP, BP, K, move, player):
    # Extract starting and ending positions from the move
    start_pos, end_pos = move  # Assuming move is a tuple like (start_pos, end_pos)

    # Determine if this is a jump move by checking the distance # NOTE: seems correct
    is_jump = abs(start_pos - end_pos) > 5

    # Create a mask for the starting and ending positions
    start_mask = 1 << start_pos
    end_mask = 1 << end_pos

    # Update the board based on the player's move
    if player == PlayerTurn.WHITE:
        WP &= ~start_mask  # Remove the piece from the starting position
        WP |= end_mask  # Place the piece at the ending position

        # If a jump is made, remove the jumped piece from the opponent
        if is_jump:
            jumped_pos = find_jumped_pos(start_pos, end_pos)
            BP &= ~(1 << jumped_pos)  # Remove the opponent's piece

        # Check for kinging
        if end_mask & KING_ROW_WHITE:
            K |= end_mask  # Make the piece a king

    elif player == PlayerTurn.BLACK:
        BP &= ~start_mask  # Same logic for black player
        BP |= end_mask

        if is_jump:
            jumped_pos = find_jumped_pos(start_pos, end_pos)
            WP &= ~(1 << jumped_pos)

        if end_mask & KING_ROW_BLACK:
            K |= end_mask

    # Update the kings bitboard if a king has been moved
    if start_mask & K:
        K &= ~start_mask
        K |= end_mask

    # No need to enforce 32-bit size for the bitboards if all operations are on 32-bit masks
    return WP, BP, K


def initialize_game_puzzle():
    WP, BP, K = get_empty_board()

    WP = insert_piece_by_pdntext(WP, "H8")
    K = insert_piece_by_pdntext(K, "H8")
    BP = insert_piece_by_pdntext(BP, "C7")
    BP = insert_piece_by_pdntext(BP, "E7")
    BP = insert_piece_by_pdntext(BP, "G7")
    BP = insert_piece_by_pdntext(BP, "C5")
    BP = insert_piece_by_pdntext(BP, "E5")
    BP = insert_piece_by_pdntext(BP, "G5")
    BP = insert_piece_by_pdntext(BP, "C3")
    BP = insert_piece_by_pdntext(BP, "E3")
    BP = insert_piece_by_pdntext(BP, "G3")

    return WP, BP, K


def initialize_game():
    (
        WP,
        BP,
        K,
    ) = (
        get_fresh_board()
    )  # Assuming you have a function that sets up the initial position
    return WP, BP, K


def print_legal_moves(legal_moves):
    print(
        f"Legal moves - {[f'{i}: {m}' for i,m in enumerate(convert_move_list_to_pdn(legal_moves))]}"
    )


def choose_move(selected_move):
    if len(selected_move) == 1:
        return [(selected_move)]
    else:
        # selected_move looks like [(31, 22, 15, 6)] and we want [(31, 22), (22, 15), (15, 6)]
        return [
            (selected_move[i], selected_move[i + 1])
            for i in range(len(selected_move) - 1)
        ]


def switch_player(player):
    return PlayerTurn.BLACK if player == PlayerTurn.WHITE else PlayerTurn.WHITE


def is_terminal_condition_met(WP, BP, K):
    # Logic to check for game end conditions
    return False


import random


def simulate_random_games(n, first_player=PlayerTurn.WHITE):
    for game_number in range(n):
        # print(f"Starting Game {game_number + 1}")

        # Initialize the board
        WP, BP, K = initialize_game()
        current_player = first_player

        move_count = 0

        while move_count < 100:
            legal_moves = generate_legal_moves(WP, BP, K, current_player)
            if not legal_moves:
                # If no legal moves, the game ends
                # print(f"{current_player.name} has no legal moves. Game over.")
                break

            # Select a random move from the legal moves
            move = random.choice(legal_moves)
            parsed_moves = choose_move(move)

            # Apply the move(s) to the board
            for m in parsed_moves:
                WP, BP, K = do_move(WP, BP, K, m, current_player)

            # Print board after move - comment this out if you don't want to see each intermediate state
            # print_board(WP, BP, K)

            # Switch players
            current_player = switch_player(current_player)
            move_count += 1

        # print(f"Game over in {move_count} moves.")


# def game_loop():
#     WP, BP, K = initialize_game_puzzle()
#     current_player = PlayerTurn.WHITE
#     move_count = 0
#     print_board(WP, BP, K)  # Assuming print_board() function to display the board

#     while True:
#         legal_moves = generate_legal_moves(WP, BP, K, current_player)
#         if not legal_moves:
#             print(f"{current_player.name} has no legal moves. Game over.")
#             break

#         print(f"It's {current_player.name}'s Turn.\n")
#         print_legal_moves(legal_moves)
#         choice = int(input("Choose your move by index: "))

#         selected_move = legal_moves[choice]
#         print(selected_move)
#         move = choose_move(selected_move)

#         print(f"Move chosen: {move}")
#         for m in move:
#             WP, BP, K = do_move(WP, BP, K, m, current_player)
#             print_board(WP, BP, K)

#         current_player = switch_player(current_player)
#         move_count += 1

#         if move_count > 100:
#             print("100 Move Limit... Game Over!")
#             break

#     print(f"Game over in {move_count} moves.")


def game_loop_with_heuristic():
    WP, BP, K = initialize_game_puzzle()
    current_player = PlayerTurn.WHITE
    move_count = 0
    print_board(WP, BP, K)  # Assuming print_board() function to display the board

    while True:
        legal_moves = generate_legal_moves(WP, BP, K, current_player)
        if not legal_moves:
            print(f"{current_player.name} has no legal moves. Game over.")
            break

        print(f"It's {current_player.name}'s Turn.\n")
        print_legal_moves(legal_moves)
        choice = int(input("Choose your move by index: "))

        selected_move = legal_moves[choice]
        print(selected_move)
        move = choose_move(selected_move)

        print(f"Move chosen: {move}")
        for m in move:
            WP, BP, K = do_move(WP, BP, K, m, current_player)
            print_board(WP, BP, K)

            # Call the heuristic function and print the evaluation
            heuristic_evaluation = heuristic(WP, BP, K)
            print(
                f"Heuristic Evaluation from White's perspective: {heuristic_evaluation}"
            )

        current_player = switch_player(current_player)
        move_count += 1

        if move_count > 100:
            print("100 Move Limit... Game Over!")
            break

    print(f"Game over in {move_count} moves.")


if __name__ == "__main__":
    # simulate_random_games(10000, first_player=PlayerTurn.WHITE)
    game_loop_with_heuristic()
