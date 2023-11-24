# Checkers AI

An informed search-based checkers-playing agent written in Python.

[![Run on Repl.it](https://replit.com/badge/github/ak2k2/Checkers-Alpha-Beta-AI)](https://replit.com/new/github/ak2k2/Checkers-Alpha-Beta-AI)

## Features

- **Game Modes**: Supports Human vs Human, Human vs Computer, and Computer vs Computer.
- **Adjustable Difficulty**: Alter the game's difficulty by modifying the time limit for the iterative deepening search or the search depth.
- **Advanced AI**: Uses minimax search with alpha-beta pruning and time-limited iterative deepening to search the game tree.
- **Heuristic Function**: Employs a custom heuristic function for evaluating board positions.
- **Optimized Move Generation**: Sorts generated legal moves by the heuristic function to improve the likelihood of alpha-beta cutoffs. 
- **Dynamic Performance**: Iterative deepening supports early stopping, exiting the minimax search if the current 'best score' has not improved in a set number of moves.
- **Testing and Debugging**: Unit tests for all core logic, facilitating rapid prototyping and debugging.
- **Interactive Display**: Features a colored ASCII board and move history.
- **Game State Management**: Ability to read a pre-existing game (board state, turn, time limit) from a file (`ECE-469/boards`).

## Heuristic Function

The heuristic function is based on the evaluation of two arguments: the board state and the turn.

- **Board State**: Represented by three 32-bit binary integers (WP, BP, K), with each bit indicating a playable square's occupancy.
- **Turn**: An ENUM indicating the current turn (WHITE or BLACK).

The function comprises several elements:

- `pieces_on_verge_of_kinging`: Analyzes pieces on the verge of kinging for both white and black, returning the difference in their counts.
- `calculate_sum_distances`: Determines the sum of Chebyshev distances between all white and black pieces.
- `mobility_diff_score`: Calculates mobility scores for each color based on available moves and jump sequences.
- `piece_count_diff_score`: Compares the number of men and kings for each color, assigning higher weights to kings.
- `calculate_total_distance_to_promotion`: Calculates the sum of distances for each non-king piece to its promotion row.
- `count_black_pieces_that_can_be_captured_by_white` and vice versa: Counts the number of opponent pieces that can be captured in the next move.
- `calculate_safe_white_pieces` and `calculate_safe_black_pieces`: Counts the number of pieces for each color that are not vulnerable to capture in the next move.
- Other functions include edge and corner penalties/rewards, and adjustments for regime shifts after significant win/loss conditions.

The `adjustment_factor` function dynamically alters evaluation criteria weights, adapting to different game phases. This non-linearity, along with all other weights, was fine-tuned using Optuna's TPE sampler through AI tournaments in `arena.py`.

## Running the Program

- '$python3 main.py' or '$pypy3 main.py' (faster)
  
Follow the system prompts. Pytests are located in the tests directory. To run them: '$pytest'

## Mentions

- [Everything About Bitboards](https://3dkingdoms.com/checkers/bitboards.htm)

- Worked closely with my classmate, Nicolette Thiro, to write test cases, perform bit manipulation, validate move generator, and more.


