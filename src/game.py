import random

from heuristic import basic_heuristic
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
    insert_piece,
    remove_piece,
)

import minimax_alphabeta

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


def do_move(WP, BP, K, moves, player):
    if len(moves) == 1:
        move = [(moves)]
    else:
        # selected_move looks like [(31, 22, 15, 6)] and we want [(31, 22), (22, 15), (15, 6)]
        moves = [(moves[i], moves[i + 1]) for i in range(len(moves) - 1)]

    for move in moves:
        # Extract starting and ending positions from the move
        start_pos, end_pos = move  # Assuming move is a tuple like (start_pos, end_pos)

        # Determine if this is a jump move by checking the distance # NOTE: seems correct
        is_jump = abs(start_pos - end_pos) > 5

        # Create a mask for the starting and ending positions
        start_mask = (1 << start_pos) & MASK_32
        end_mask = (1 << end_pos) & MASK_32

        # Update the board based on the player's move
        if player == PlayerTurn.WHITE:
            WP = remove_piece(
                WP, start_pos
            )  # Remove the piece from the starting position
            WP = insert_piece(WP, end_pos)  # Insert the piece at the ending position

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


def switch_player(player):
    return PlayerTurn.BLACK if player == PlayerTurn.WHITE else PlayerTurn.WHITE


def simulate_random_games(n, first_player=PlayerTurn.WHITE):
    random.seed(0)
    for _ in range(n):
        # Initialize the board
        WP, BP, K = initialize_game()
        current_player = first_player

        move_count = 0

        while move_count < 100:
            legal_moves = generate_legal_moves(WP, BP, K, current_player)
            if not legal_moves:
                # print(f"GAME OVER. {current_player.name} LOOSES!")
                break

            # Select a random move from the legal moves
            move = random.choice(legal_moves)
            WP, BP, K = do_move(WP, BP, K, move, current_player)

            # print_board(WP, BP, K)

            # Switch players
            current_player = switch_player(current_player)
            move_count += 1


def human_vs_human():
    WP, BP, K = initialize_game()
    current_player = PlayerTurn.BLACK
    move_count = 0
    print_board(WP, BP, K)  # Assuming print_board() function to display the board

    while move_count < 100:
        legal_moves = generate_legal_moves(WP, BP, K, current_player)

        if not legal_moves:
            print(f"GAME OVER. {current_player.name} LOOSES!")
            break

        print(f"It's {current_player.name}'s Turn.\n")
        print_legal_moves(legal_moves)
        selected_move = legal_moves[int(input("Choose your move by index: "))]

        WP, BP, K = do_move(WP, BP, K, selected_move, current_player)

        print_board(WP, BP, K)
        print(f"HEURISTIC: {basic_heuristic(WP, BP, K)}")

        current_player = switch_player(current_player)
        move_count += 1

    print(f"Game over in {move_count} moves.")


def human_vs_AI():
    WP, BP, K = initialize_game()
    current_player = PlayerTurn.BLACK
    move_count = 0
    max_depth = 7

    print_board(WP, BP, K)  # Assuming print_board() function to display the board

    while move_count < 100:  # or some other termination condition like a draw
        if current_player == PlayerTurn.BLACK:
            legal_moves = generate_legal_moves(WP, BP, K, current_player)

            if not legal_moves:
                print(f"GAME OVER. {current_player.name} LOSES!")
                break
            print(f"It's {current_player.name}'s Turn.\n")
            print_legal_moves(legal_moves)
            selected_move = legal_moves[int(input("Choose your move by index: "))]

            print(f"Move chosen: {convert_move_list_to_pdn([selected_move])}")
            WP, BP, K = do_move(WP, BP, K, selected_move, current_player)

        else:  # AI's turn
            print("AI is thinking...")
            best_move = minimax_alphabeta.AI((WP, BP, K), max_depth)
            if best_move is None:
                print(f"GAME OVER. {current_player.name} LOSES!")
                break
            print(f"AI chose move: {convert_move_list_to_pdn([best_move])}")
            WP, BP, K = do_move(WP, BP, K, best_move, current_player)

        print(f"HEURISTIC: {basic_heuristic(WP, BP, K)}")
        print_board(WP, BP, K)
        print("-" * 50 + "\n")

        current_player = (
            PlayerTurn.WHITE if current_player == PlayerTurn.BLACK else PlayerTurn.BLACK
        )
        move_count += 1

    print(f"Game over in {move_count} moves.")


def random_vs_AI():
    WP, BP, K = initialize_game()
    current_player = PlayerTurn.BLACK
    move_count = 0
    max_depth = 12

    print_board(WP, BP, K)  # Assuming print_board() function to display the board
    random.seed(2)
    while move_count < 100:  # or some other termination condition like a draw
        if current_player == PlayerTurn.BLACK:
            legal_moves = generate_legal_moves(WP, BP, K, current_player)

            if not legal_moves:
                print(f"GAME OVER. {current_player.name} LOSES!")
                break

            print(f"It's {current_player.name}'s Turn.\n")
            print_legal_moves(legal_moves)
            # selected_move = legal_moves[int(input("Choose your move by index: "))]
            selected_move = random.choice(legal_moves)

            print(f"Random Move chosen: {selected_move}")
            WP, BP, K = do_move(WP, BP, K, selected_move, current_player)

        else:  # AI's turn
            print("AI is thinking...")
            best_move = minimax_alphabeta.AI((WP, BP, K), max_depth)
            if best_move is None:
                print(f"GAME OVER. {current_player.name} LOSES!")
                break
            print(f"White chose move: {convert_move_list_to_pdn([best_move])}")
            WP, BP, K = do_move(WP, BP, K, best_move, current_player)

        print_board(WP, BP, K)
        print(f"HEURISTIC: {basic_heuristic(WP, BP, K)}")

        current_player = (
            PlayerTurn.WHITE if current_player == PlayerTurn.BLACK else PlayerTurn.BLACK
        )
        move_count += 1

    print(f"Game over in {move_count} moves.")


if __name__ == "__main__":
    # simulate_random_games(10000, first_player=PlayerTurn.WHITE)
    # human_vs_human()
    # human_vs_AI()
    random_vs_AI()
