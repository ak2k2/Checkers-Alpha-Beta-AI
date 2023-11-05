# Initialize bitboards for black and white pieces
# The least significant bit represents the bottom-left corner of the board
# The most significant bit represents the top-right corner of the board

# Initial setup for black pieces (bottom three rows)
black_pieces = int('0000000000000000000000000000000000001111111111111111111111111111', 2)

# Initial setup for white pieces (top three rows)
white_pieces = int('1111111111111111111111111111000000000000000000000000000000000000', 2)

# Function to print the board
def print_board(black_pieces, white_pieces):
    for i in range(7, -1, -1):
        for j in range(8):
            pos = 8 * i + j
            if (black_pieces >> pos) & 1:
                print('X', end=' ')
            elif (white_pieces >> pos) & 1:
                print('O', end=' ')
            else:
                print('.', end=' ')
        print()

# Test the print_board function
print_board(black_pieces, white_pieces)
