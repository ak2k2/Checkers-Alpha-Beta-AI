import random

from checkers import *
from heuristic import *
from minimax_alphabeta import *
from util.helpers import *


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


# human_vs_AI(who_moves_first=PlayerTurn.BLACK, human_color=PlayerTurn.WHITE)
def human_vs_AI(who_moves_first, human_color):
    WP, BP, K = initialize_game()
    current_player = who_moves_first  # Start with the passed player
    ai_color = switch_player(human_color)
    move_count = 0
    max_depth = 7
    time_limit = 5

    print(
        f"Welcome to Checkers! You are playing as {human_color.name}. AI is playing as {ai_color.name}. {current_player.name} moves first."
    )
    print_board(WP, BP, K)
    while move_count < 100:
        if current_player == human_color:
            legal_moves = generate_legal_moves(WP, BP, K, current_player)

            if not legal_moves:
                print(f"GAME OVER. {human_color.name} LOSES!")
                break
            print(f"It's {human_color.name}'s Turn.\n")
            print_legal_moves(legal_moves)
            selected_move_index = int(input("Choose your move by index: "))

            if selected_move_index not in range(len(legal_moves)):
                print("Invalid index selected. Try again...")
                continue
            selected_move = legal_moves[selected_move_index]

            print(f"Move chosen: {convert_move_list_to_pdn([selected_move])}")
            WP, BP, K = do_move(WP, BP, K, selected_move, current_player)

        else:  # AI's turn
            print("AI: Thinking...")
            start_time = time.time()
            legal_moves = generate_legal_moves(WP, BP, K, current_player)
            immediate_move = len(legal_moves) == 1

            if immediate_move:
                print(f"AI: Chose the only move available.")
                best_move = legal_moves[0]
            else:
                best_move, depth_reached = AI(
                    (WP, BP, K), ai_color, max_depth, time_limit
                )

            end_time = time.time()
            elapsed_time = end_time - start_time
            if best_move is None:
                print(f"GAME OVER. {current_player.name} LOSES!")
                break

            move_description = convert_move_list_to_pdn([best_move])
            print(f"AI MOVED: {move_description}")
            WP, BP, K = do_move(WP, BP, K, best_move, current_player)

            if not immediate_move:
                if elapsed_time <= 4.99:
                    print(
                        f"AI searched to depth {depth_reached} in {elapsed_time:.2f} seconds."
                    )
                else:
                    print(f"AI hit the 'time limit' and reached depth {depth_reached}.")

        print(f"EVAL: {basic_heuristic(WP, BP, K)}")
        print_board(WP, BP, K)
        print("-" * 50 + "\n")

        current_player = switch_player(current_player)
        move_count += 1

    print(f"Game lasted {move_count} moves!")


def AI_vs_AI(who_moves_first, max_depth=7, time_limit=5):
    WP, BP, K = initialize_game()
    current_player = who_moves_first

    move_count = 0
    game_over = False

    print_board(WP, BP, K)
    while move_count < 100 and not game_over:
        print(f"It's {current_player.name}'s Turn.\n")
        start_time = time.time()

        legal_moves = generate_legal_moves(WP, BP, K, current_player)
        if not legal_moves:
            print(f"GAME OVER. {current_player.name} LOSES!")
            game_over = True
            break

        immediate_move = len(legal_moves) == 1
        if immediate_move:
            print(
                f"AI ({current_player.name}): Took immediate move due to only one legal move available."
            )
            best_move = legal_moves[0]
        else:
            best_move, depth_reached = AI(
                (WP, BP, K),
                current_player,
                max_depth,
                time_limit,
                heuristic="new_heuristic"
                if current_player == PlayerTurn.BLACK
                else "basic_heuristic",  # WHITE uses basic heuristic against BLACK using new heuristic
            )

        end_time = time.time()
        elapsed_time = end_time - start_time

        if best_move is None:
            print(f"GAME OVER. {current_player.name} LOSES!")
            game_over = True
            break

        move_description = convert_move_list_to_pdn([best_move])
        print(f"AI ({current_player.name}) MOVED: {move_description}")
        WP, BP, K = do_move(WP, BP, K, best_move, current_player)

        if not immediate_move:
            if elapsed_time <= time_limit:
                print(
                    f"AI ({current_player.name}) searched to depth {depth_reached} in {elapsed_time:.2f} seconds."
                )
            else:
                print(
                    f"AI ({current_player.name}) hit the 'time limit' and reached depth {depth_reached}."
                )

        print(f"EVAL: {basic_heuristic(WP, BP, K)}")
        print_board(WP, BP, K)
        print("-" * 50 + "\n")

        current_player = switch_player(current_player)
        move_count += 1

    if not game_over:
        print(f"GAME OVER in {move_count} moves! DRAW.")


# def random_vs_AI():
#     WP, BP, K = initialize_game()
#     current_player = PlayerTurn.BLACK
#     move_count = 0
#     max_depth = 5

#     print_board(WP, BP, K)
#     random.seed(2)
#     while move_count < 100:
#         if current_player == PlayerTurn.BLACK:
#             legal_moves = generate_legal_moves(WP, BP, K, current_player)

#             if not legal_moves:
#                 print(f"GAME OVER. {current_player.name} LOSES!")
#                 break

#             print(f"It's {current_player.name}'s Turn.\n")
#             print_legal_moves(legal_moves)

#             selected_move = random.choice(legal_moves)

#             print(f"Random Move chosen: {selected_move}")
#             WP, BP, K = do_move(WP, BP, K, selected_move, current_player)

#         else:  # AI's turn
#             print("AI is thinking...")
#             best_move = AI((WP, BP, K), max_depth)
#             if best_move is None:
#                 print(f"GAME OVER. {current_player.name} LOSES!")
#                 break
#             print(f"White chose move: {convert_move_list_to_pdn([best_move])}")
#             WP, BP, K = do_move(WP, BP, K, best_move, current_player)

#         print_board(WP, BP, K)
#         print(f"HEURISTIC: {basic_heuristic(WP, BP, K)}")

#         current_player = (
#             PlayerTurn.WHITE if current_player == PlayerTurn.BLACK else PlayerTurn.BLACK
#         )
#         move_count += 1

#     print(f"Game over in {move_count} moves.")


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
    AI_vs_AI(who_moves_first=PlayerTurn.BLACK, max_depth=9, time_limit=1)
    # human_vs_AI(who_moves_first=PlayerTurn.BLACK, human_color=PlayerTurn.WHITE)
    # random_vs_AI()
