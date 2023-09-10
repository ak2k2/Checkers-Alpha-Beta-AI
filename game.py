from checkerboard_gui import CheckerBoardGUI


def get_blank_board():
    board = [["." for row in range(8)] for col in range(8)]
    return board


def setup_board(board):
    for row in range(3):
        for col in range(8):
            if (row + col) % 2 != 0:
                board[row][col] = "X"

    for row in range(5, 8):
        for col in range(8):
            if (row + col) % 2 != 0:
                board[row][col] = "O"
    return board


def check_legal_move(board, player, move) -> tuple:
    assert len(move.split("->")) == 2, "Invalid move format."
    assert player == "X" or player == "O", "Invalid player."

    current_pos, new_pos = move.split("->")[0], move.split("->")[1]

    assert len(current_pos.split(",")) == 2, "Invalid current position format."
    assert len(new_pos.split(",")) == 2, "Invalid new position format."

    current_row = int(current_pos.split(",")[0])
    current_col = int(current_pos.split(",")[1])

    new_row = int(new_pos.split(",")[0])
    new_col = int(new_pos.split(",")[1])

    # ensure that the current position and new position are bounded by the board
    assert 0 <= current_row <= 7, "Invalid current row."
    assert 0 <= current_col <= 7, "Invalid current column."
    assert 0 <= new_row <= 7, "Invalid new row."
    assert 0 <= new_col <= 7, "Invalid new column."

    if board[current_row][current_col] == ".":
        print("That is an empty space.")
        return
    elif board[current_row][current_col] != player:
        print("That is not your piece.")
        return
    if board[new_row][new_col] == player:
        print("You cannot move to a space you already occupy.")
        return
    elif board[new_row][new_col] != ".":
        print("You cannot move into O's piece.")
        return
    elif player == "X" and new_row < current_row:
        print("You cannot move backwards.")
        return
    elif player == "O" and new_row > current_row:
        print("You cannot move backwards.")
        return
    elif abs(new_row - current_row) == 0 and abs(new_col - current_col) == 0:
        print("You did not move.")
        return
    elif abs(new_row - current_row) == 1 and abs(new_col - current_col) == 0:
        print("You did not move sideways.")
        return
    elif abs(new_row - current_row) == 0 and abs(new_col - current_col) == 1:
        print("You did not move forward.")
        return
    elif abs(new_row - current_row) == abs(
        new_col - current_col
    ):  # moved in a legal diagonal direction (1 space for a standard move or 2 spaces for a capture)
        if abs(new_row - current_row) == 1:  # moved 1 space diagonally
            print("Moved the piece 1 space diagonally.")
        elif abs(new_row - current_row) == 2:  # moved 2 spaces diagonally
            print("Moved the piece 2 spaces diagonally (CAPTURED A PIECE).")
        return (current_row, current_col), (new_row, new_col)
    else:
        print("Invalid move.")
        return


def check_capture_or_make_move(
    current_row, current_col, new_row, new_col, board, player
):
    if abs(new_row - current_row) == 2 and abs(new_col - current_col) == 2:
        if player == "X":
            if board[(new_row + current_row) // 2][(new_col + current_col) // 2] == "O":
                board[(new_row + current_row) // 2][
                    (new_col + current_col) // 2
                ] = "."  # replace the captured O with an empty space
            else:
                print("There is no 'O' piece to capture.")
                return
        elif player == "O":
            if board[(new_row + current_row) // 2][(new_col + current_col) // 2] == "X":
                board[(new_row + current_row) // 2][(new_col + current_col) // 2] = "."
            else:
                print("There is no 'X' piece to capture.")
                return

    board[current_row][current_col] = "."
    board[new_row][new_col] = player
    return board


def do_move(board, move, player):
    while True:
        try:
            (current_row, current_col), (new_row, new_col) = check_legal_move(
                board, player, move
            )
            break
        except:
            move = input("Please try again: ")

    # it is now gauranteed that the player has chosed their own piece and moved it to an empty space, in the correct direction, and either
    # 1 or 2 spaces diagonally

    board = check_capture_or_make_move(
        current_row, current_col, new_row, new_col, board, player
    )

    return board


def display_board(board, checker_board_gui):
    checker_board_gui.board = board
    checker_board_gui.update_board()
    checker_board_gui.root.update_idletasks()
    checker_board_gui.root.update()


def play_sequence_of_moves(board, moves, checker_board_gui):
    player = "X"  # Starting player is 'X'
    for move in moves:
        input("Press Enter for next move...")
        print(f"\n{player}'s turn with move {move}")
        board = do_move(board, move, player)  # Replace with your move applying logic
        display_board(board, checker_board_gui)

        # Switch player for the next round
        if player == "X":
            player = "O"
        else:
            player = "X"


if __name__ == "__main__":
    board = get_blank_board()
    board = setup_board(board)
    checker_board_gui = CheckerBoardGUI(board)

    while True:
        display_board(board, checker_board_gui)
        X_move = input("'X' to move i,j -> i,j: ")
        board = do_move(board, X_move, "X")
        display_board(board, checker_board_gui)
        O_move = input("'O' to move i,j -> i,j: ")
        board = do_move(board, O_move, "O")

    # moves = ["2,1->3,2", "5,2->4,3", "2,3->3,4", "5,0->4,1", "3,4->5,2"]
    # play_sequence_of_moves(board, moves, checker_board_gui)
