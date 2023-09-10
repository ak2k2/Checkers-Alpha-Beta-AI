def display_board_terminal(board):
    print("\n" + "*" * 70 + "\n")
    print(" ", end="  ")
    for col in range(8):
        print(col, end="    ")
    print()
    for row in range(8):
        for _ in range(2):  # Make each square 2 lines high
            print(
                row if _ == 1 else " ", end=" "
            )  # Display row number at the middle line
            for col in range(8):
                if (row + col) % 2 == 0:
                    background_color = "\033[48;5;16m"  # ANSI code for black background
                else:
                    background_color = "\033[48;5;1m"  # ANSI code for red background

                piece = board[row][col]
                if piece == ".":
                    piece = " "
                elif piece == "X":
                    piece = "\u25CB"  # Unicode white circle
                elif piece == "O":
                    piece = "\u25CF"  # Unicode black circle

                if _ == 1:  # Middle line
                    print(
                        background_color + "  " + piece + "  " + "\033[0m",
                        end="",
                    )  # \033[0m resets the color
                else:  # Top and Bottom line
                    print(
                        background_color + "     " + "\033[0m", end=""
                    )  # \033[0m resets the color
            print()