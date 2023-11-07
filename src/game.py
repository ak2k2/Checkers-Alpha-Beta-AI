import random

from heuristic import *
from checkers import *
from util.helpers import *

from minimax_alphabeta import *


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
            best_move = AI((WP, BP, K), max_depth)
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


# def AI_vs_AI():
#     WP, BP, K = initialize_game()
#     current_player = PlayerTurn.BLACK
#     move_count = 0
#     max_depth = 7

#     print_board(WP, BP, K)

#     while move_count < 100:
#         if current_player == PlayerTurn.BLACK:
#             legal_moves = generate_legal_moves(WP, BP, K, current_player)

#             if not legal_moves:
#                 print(f"GAME OVER. {current_player.name} LOSES!")
#                 break
#             print(f"It's {current_player.name}'s Turn.\n")
#             print_legal_moves(legal_moves)
#             selected_move = legal_moves[int(input("Choose your move by index: "))]

#             print(f"Move chosen: {convert_move_list_to_pdn([selected_move])}")
#             WP, BP, K = do_move(WP, BP, K, selected_move, current_player)

#         else:  # AI's turn
#             print("AI is thinking...")
#             best_move = AI((WP, BP, K), max_depth)
#             if best_move is None:
#                 print(f"GAME OVER. {current_player.name} LOSES!")
#                 break
#             print(f"AI chose move: {convert_move_list_to_pdn([best_move])}")
#             WP, BP, K = do_move(WP, BP, K, best_move, current_player)

#         print(f"HEURISTIC: {basic_heuristic(WP, BP, K)}")
#         print_board(WP, BP, K)
#         print("-" * 50 + "\n")

#         current_player = (
#             PlayerTurn.WHITE if current_player == PlayerTurn.BLACK else PlayerTurn.BLACK
#         )
#         move_count += 1

#     print(f"Game over in {move_count} moves.")


def random_vs_AI():
    WP, BP, K = initialize_game()
    current_player = PlayerTurn.BLACK
    move_count = 0
    max_depth = 5

    print_board(WP, BP, K)
    random.seed(2)
    while move_count < 100:
        if current_player == PlayerTurn.BLACK:
            legal_moves = generate_legal_moves(WP, BP, K, current_player)

            if not legal_moves:
                print(f"GAME OVER. {current_player.name} LOSES!")
                break

            print(f"It's {current_player.name}'s Turn.\n")
            print_legal_moves(legal_moves)

            selected_move = random.choice(legal_moves)

            print(f"Random Move chosen: {selected_move}")
            WP, BP, K = do_move(WP, BP, K, selected_move, current_player)

        else:  # AI's turn
            print("AI is thinking...")
            best_move = AI((WP, BP, K), max_depth)
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
                break

            # Select a random move from the legal moves
            move = random.choice(legal_moves)
            WP, BP, K = do_move(WP, BP, K, move, current_player)

            # Switch players
            current_player = switch_player(current_player)
            move_count += 1


if __name__ == "__main__":
    # simulate_random_games(10000, first_player=PlayerTurn.WHITE)
    # human_vs_human()
    # human_vs_AI()
    random_vs_AI()
