import random

from checkers import *
from heuristic import *
from minimax_alphabeta import *
from util.helpers import *


def load_board():
    return setup_board_from_position_lists(["KB8", "KF8", "KH8"], ["D6"])


def load_game_from_sable_file(file_path):
    WP, BP, K = get_empty_board()

    with open(file_path, "r") as file:
        board_lines = file.readlines()

    # We expect the first 8 lines to contain the board state.
    for row, line in enumerate(board_lines[:8]):
        # Extracting pieces from the text line
        pieces = line.strip().split()

        for col, piece in enumerate(pieces):
            # Calculate the bit index
            bit_index = (7 - row) * 4 + col

            # Mapping the piece to the correct bitboard
            if piece == "1":
                WP = insert_piece(WP, bit_index)
            elif piece == "2":
                BP = insert_piece(BP, bit_index)
            elif piece == "3":
                WP = insert_piece(WP, bit_index)
                K = insert_piece(K, bit_index)
            elif piece == "4":
                BP = insert_piece(BP, bit_index)
                K = insert_piece(K, bit_index)

    # The 9th line should contain the current player's turn.
    current_player = int(board_lines[8].strip())

    # The 10th line should contain the time limit for the computer's turn.
    time_limit = int(board_lines[9].strip())

    return WP, BP, K, current_player, time_limit


def human_vs_human():
    WP, BP, K = get_fresh_board()
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
        print(f"HEURISTIC: {old_heuristic(WP, BP, K)}")

        current_player = switch_player(current_player)
        move_count += 1

    print(f"Game over in {move_count} moves.")


# human_vs_AI(who_moves_first=PlayerTurn.BLACK, human_color=PlayerTurn.WHITE)
def human_vs_AI(
    who_moves_first=None, human_color=None, initial_board=None, time_limit=None
):
    if initial_board is None:
        (WP, BP, K) = get_fresh_board()
    else:
        WP, BP, K = initial_board

    if time_limit is None:
        time_limit = 5
    if who_moves_first is None:
        who_moves_first = PlayerTurn.BLACK
    if human_color is None:
        human_color = PlayerTurn.BLACK

    current_player = who_moves_first
    ai_color = switch_player(human_color)
    move_count = 0
    max_depth = 20

    print(
        f"\nWelcome to Checkers! You are playing as {human_color.name}. AI is playing as {ai_color.name}. {current_player.name} moves first. The AI has {time_limit} seconds to make a move."
    )
    print_board(WP, BP, K)
    while move_count < 150:
        if current_player == human_color:
            legal_moves = generate_legal_moves(WP, BP, K, current_player)

            if not legal_moves:  # No legal moves left for human
                print(f"\nGame Over... {switch_player(current_player).name} won!")
                break

            print(f"It's {human_color.name}'s Turn.\n")
            print_legal_moves(legal_moves)

            selected_move_index = None

            while True:
                print("Choose your move by index: ")
                user_input = input("-> ")

                try:
                    selected_move_index = int(user_input)
                    if selected_move_index not in range(len(legal_moves)):
                        print("Invalid index selected. Try again...")
                    else:
                        break  # Break the loop if a valid index has been selected
                except ValueError:
                    print("Invalid input! Please enter a number.")

            selected_move = legal_moves[selected_move_index]
            print(f"Move chosen: {selected_move}")

            print(f"Move chosen: {convert_move_list_to_pdn([selected_move])}")
            WP, BP, K = do_move(WP, BP, K, selected_move, current_player)

        else:  # AI's turn
            print("AI: Thinking...")
            start_time = time.time()
            legal_moves = generate_legal_moves(WP, BP, K, current_player)

            if not legal_moves:  # No legal moves left for AI
                print(f"\nGame Over... {switch_player(current_player).name} won!")
                break

            immediate_move = len(legal_moves) == 1
            if immediate_move:
                print(f"AI: Chose the only move available.")
                best_move = legal_moves[0]
            else:
                best_move, depth_reached = AI(
                    (WP, BP, K),
                    ai_color,
                    max_depth,
                    time_limit,
                    heuristic="new_heuristic",
                )

            end_time = time.time()
            elapsed_time = end_time - start_time
            if best_move is None:
                print(f"\nGame Over... {switch_player(current_player)} WINS!")
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

        print_board(WP, BP, K)
        print(f"EVAL (new heuristic): {new_heuristic(WP, BP, K)}")
        print(f"Number of White Men: {count_bits(WP & ~K)}")
        print(f"Number of White Kings: {count_bits(WP & K)}")
        print(f"Number of Black Men: {count_bits(BP & ~K)}")
        print(f"Number of Black Kings: {count_bits(BP & K)}")
        print("-" * 50 + "\n")

        current_player = switch_player(current_player)
        move_count += 1

    print(f"\nGame lasted {move_count} moves.")


def AI_vs_AI(who_moves_first, max_depth=20, time_limit=None, initial_board=None):
    if time_limit is None:
        time_limit = 5
    if who_moves_first is None:
        who_moves_first = PlayerTurn.BLACK

    if initial_board is None:
        WP, BP, K = get_fresh_board()
    else:
        WP, BP, K = initial_board

    current_player = who_moves_first

    move_count = 0
    game_over = False
    print(
        f"\nWelcome to Checkers! AI vs AI mode! {current_player.name} moves first. The AIs each have {time_limit} seconds to make a move."
    )

    print_board(WP, BP, K)
    while move_count < 200 and not game_over:
        print(f"It's {current_player.name}'s Turn.\n")
        start_time = time.time()

        legal_moves = generate_legal_moves(WP, BP, K, current_player)
        if not legal_moves:
            print(
                f"GAME OVER. {switch_player(current_player).name} WON in {move_count} moves!"
            )
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
                heuristic="old_heuristic"
                if current_player == PlayerTurn.BLACK
                else "new_heuristic",
            )

        end_time = time.time()
        elapsed_time = end_time - start_time

        if best_move is None:
            print(
                f"GAME OVER. {switch_player(current_player).name} WON in {move_count} moves!"
            )
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

        print(f"NEW Heuristic: {new_heuristic(WP, BP, K)}")
        print(f"OLD Heuristic: {old_heuristic(WP, BP, K)}")
        print_board(WP, BP, K)
        print("-" * 50 + "\n")

        current_player = switch_player(current_player)
        move_count += 1

    if not game_over:
        print(f"GAME OVER in {move_count} moves! DRAW.")


if __name__ == "__main__":
    from_file = input("Would you like to load a game from a file (Y/N)? ")

    if from_file.upper() == "Y":
        print("Got it. Loading game state from file...\n")
        mode = input("Human vs AI (HA) or AI vs AI (AA)? ")
        if mode.upper() == "HA":
            board_file_path = "src/boards/sample-cb2.txt"
            WP, BP, K, current_player, time_limit = load_game_from_sable_file(
                board_file_path
            )
            print(f"\nLoaded board from {board_file_path}.\n")

            human_color = input("What color should the human play as? (W/B): ")

            if human_color.upper() == "W":
                human_color = PlayerTurn.WHITE
            else:
                human_color = PlayerTurn.BLACK

            human_vs_AI(
                who_moves_first=PlayerTurn.BLACK
                if current_player == 1
                else PlayerTurn.WHITE,
                human_color=human_color,
                initial_board=(WP, BP, K),
                time_limit=time_limit,
            )
        elif mode.upper() == "AA":
            board_file_path = "src/boards/sample-cb2.txt"
            WP, BP, K, current_player, time_limit = load_game_from_sable_file(
                board_file_path
            )
            print(f"\nLoaded board from {board_file_path}.")

            AI_vs_AI(
                who_moves_first=PlayerTurn.BLACK
                if current_player == 1
                else PlayerTurn.WHITE,
                time_limit=time_limit,
                initial_board=(WP, BP, K),
            )
        else:
            print("Invalid input. Exiting...")
    elif from_file.upper() == "N":
        print("\nGot it. Loading starting position...\n")
        time_limit = int(
            input("How many seconds should the AI have to make a move? (integer) ")
        )
        print("\n")
        mode = input("Human vs AI (HA) or AI vs AI (AA)? ")
        if mode.upper() == "HA":
            human_color = input("\nWhat color should the human play as? (W/B): ")
            moves_first = input("\nWho moves first? (W/B): ")

            if human_color.upper() == "W":
                human_color = PlayerTurn.WHITE
            else:
                human_color = PlayerTurn.BLACK

            if moves_first.upper() == "W":
                moves_first = PlayerTurn.WHITE
            else:
                moves_first = PlayerTurn.BLACK

            human_vs_AI(
                human_color=human_color,
                who_moves_first=moves_first,
                time_limit=time_limit,
            )

        elif mode.upper() == "AA":
            moves_first = input("\nWho moves first? (W/B): ")

            if moves_first.upper() == "W":
                moves_first = PlayerTurn.WHITE
            else:
                moves_first = PlayerTurn.BLACK

            AI_vs_AI(who_moves_first=moves_first, time_limit=time_limit)

        else:
            print("Invalid input. Exiting...")
    else:
        print("Invalid input. Exiting...")
