# Checkers AI
- Checkers program written in Python. 

- Uses minimax search with alpha-beta pruning and time limited iterative deepening to search the game tree. A custome heuristic function is used to evaluate board positions and preform leaf node evaluations. Generated legal moves are sorted by the heuristic function to improve the liklihoof of alpha-beta cuttoffs. Iterative deepning supports early stoppping and can exit the minimax search if the current 'best score' has not improved in N arbritrary moves.

## Features
- Supports Human vs Human, Human vs Computer, and Computer vs Computer.
- Different difficulty levels can be achieved by changing the time limit for the iterative deepening search or the search depth.
- Unit tests for all core logic, rapid prototyping, and debugging.
- Displays colored ASCII board and move history.
- Can read a pre-exisiting game (board state, turn, time limit) from a file (`ECE-469/boards`)

## Heuristic Function

An evaluation if a function of two things.

1. Board state: Three 32 bit binary integers (WP, BP, K). Each bit represents a playable square on the board. A 1 indicates a piece is present and a 0 indicates an empty square. The least significant bit represents the bottom left square and the most significant bit represents the top right square. The board state is typically packed into a tuple of three integers (WP, BP, K).

2. Turn: An ENUM representing the current turn. Either WHITE or BLACK.

---

PIECE_COUNT, BACK_ROW, CAPTURE, MOBILITY, SAFETY_SCORE, TURN_ADVANTAGE, VERGE_KINGING, CENTER_CONTROL, EDGE_CONTROL, DISTANCE_TO_KINGS_ROW, SUM_DISTANCE, DOUBLE_CORNER_BONUS








## Requirements
- Python 3.6+
- Pytest (optional for testing)
- Pypy3 (optional for faster simulations)





# Running
Pytests are in the tests directory. To run them, run `pytest` in the root directory.

Simulating N 'random legal games' is faster, `pypy3 main.py`.


## RANDOM NOTES:
### Two kings vs one King on corner
- (number of pieces player is ahead) / (number of pieces player is behind) * C
- if the computer is behind it substracts and if it is ahead it adds. This solves the force trades when ahead and avoid trades when behind. 

### Debugging/Notes
- print ASCII search tree for debugging
- make legal move sequences multiple tuples to represent branches of forced captures. 
- ex. (1,2) -> (2,3) and then (2,3) -> (3,4) will become ((1,2),(2,3),(3,4)) 

### Decent Heuristics
- MIDDLE-GAME: Kings are worth slightly less than 2 (maybe 5/3) and regular pieces are worth one.
- END-GAME: Double corners
