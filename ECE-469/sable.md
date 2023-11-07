I am providing my own game playing executables and sample boards.

If you want to use the cygwin executables on a PC, but
you do not have cygwin installed, download the three provided .dll files
and place them in the same directory as the executables. The Ubuntu 
executables should run without additional support on an Ubuntu 20.04
machine. The text files do not vary between systems.

You can load a sample board at the start of a game.
The first 8 rows of a file represent the state of the board.
The spacing is not important; I spaced them to make them readable.
For Checkers, 0, 1, 2, 3, and 4 represent an empty square,
a regular piece for player 1, a regular piece for player 2,
a king for player 1, and a king for player 2, respectively.
For Othello, 0, 1, and 2 represent an emtpy square,
a piece for player 1, and a piece for player 2, respectively.
For both games, the numbers in the final two rows represent
whose turn it is (player 1 or player 2), and the time limit
(for any turn played by the computer).