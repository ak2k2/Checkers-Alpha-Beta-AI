___
## Informed Search Based Engine

- Play [English Draughts](https://en.wikipedia.org/wiki/English_draughts)  Against engine from the browser using the Replit below.

[![Run on Repl.it](https://replit.com/badge/github/ak2k2/Checkers-Alpha-Beta-AI)
___
## Programming Checkers in Python without abusing CPU and Memory.

In order to play the Game of Checkers (GC) a computer program must quickly access, parse and modify the game state. GC is perfect information, two player, turn taking board game. The the following information is sufficient to map to a valid game.

1. Five square states -> | White Pawn / White King / Black Pawn / Black King / Empty | 
2. PlayerTurn-> | White to Move / Black to Move |
   
We can define *U* as a container that holds all the data needed to represent GC at any given time index. time in this case is discrete and each time step flips the state of PlayerTurn.

A naïve approach might be to initialize an empty board as a 2d array.

```python
def get_fresh_board() -> List[List]:
	naive_board = [[0 for _ in range(8)] for _ in range(8)]
	return naive_board
```

We can then define functions to generate legal moves, preform static evaluation, detect GameOver and other terminating conditions, and handle IO operations. On a typical machine, a well crafted version of this approach can rapidly simulate dozens of thousands of instances of GC from start to finish.

### Space Considerations

Memory footprint of U is the board:

```python
def get_size(my_list):
	size = sys.getsizeof(my_list)
	for item in my_list:
		size += sys.getsizeof(item)
return size

get_size(naive_board) # 1080 bits 
```


### Time Considerations

- **Access Time**: Accessing an element requires two index accesses (one for the row and one for the column). \( O(c) \).
- **Move Operation**: Moving a piece involves changing the value at one index and setting another index to empty. This is also \( O(c) \), but with a slightly higher c due to two separate operations.
- **Searching and Checking Conditions**: Iterating over the array to find pieces or check square status is \( O(n^2) \), where \( n \) is the rank of the board matrix. Technically this is (O(c)) since N is fixed at 8.

___
## Bit Boards

Using [Bit Boards](https://3dkingdoms.com/checkers/bitboards.htm) to represent *U* leads uses much less space, and improves  **Searching and Checking Conditions** by an order of magnitude.

Instead of a 2D array, we utilize a bit board BB to represent the game state in Checkers. Each bit in a 32-bit integer represents an playable square on the Checkerboard. Only 32 out of 64 squares are playable. 

BB is defined as a 4x4 pseudo board with indices labeled as so.

```
   28  29  30  31 
 24  25  26  27
   20  21  22  23
 16  17  18  19
   12  13  14  15
 08  09  10  11  
   04  05  06  07 
 00  01  02  03
```

The board is stored in U using bit strings. A fresh board (12 WP on the first three tanks and 12 BP on the last three ranks) is defined like so.

```python
def get_fresh_board() -> tuple:
    """
    Returns a tuple of bitboards representing a fresh board.
    """
    BP = 0b00000000000000000000111111111111  # Move from South -> North
    WP = 0b11111111111100000000000000000000  # Move from North -> South
    K = 0b00000000000000000000000000000000  # K && WP or K && BP -> WK, BK
    return WP, BP, K
```

The BP, WP, K bit strings, read from right to left, correspond to 00, 01, ... 31. A row-major order traversal of BB. 

To determine the positions of all white pieces that can move we use the following scheme inspired by **Jonathan Kreuzer**.

```python
def get_movers_white(WP, BP, K):
	
	"""	
	Input: WP, BP, K.
	Output: 32 bit int of WP that can make a simple move but NOT a jump move.
	"""
	
	# Constants for masks, corrected for shifting direction
	nOcc = ~(WP | BP) # Not Occupied
	WK = WP & K # White Kings
	
	# Calculate potential moves for white non-kings downwards
	Movers = (nOcc << 4) & WP # Move down 4
	Movers |= ((nOcc & MASK_L3) << 3) & WP # Move down left 3
	Movers |= ((nOcc & MASK_L5) << 5) & WP # Move down left 5
	
	# Calculate potential moves for white kings (which can move both up and down)
	if WK:
		Movers |= (nOcc >> 4) & WK # Move up 4
		Movers |= ((nOcc & MASK_R3) >> 3) & WK # Move up right 3
		Movers |= ((nOcc & MASK_R5) >> 5) & WK # Move up right 5
	
	return Movers
```

To find jumpers we proceed similarly.

```python
  
def get_jumpers_white(WP, BP, K):
	"""
	Input: WP, BP, K.
	Output: WP that can make a jump move.
	"""
	
	nOcc = ~(WP | BP) & MASK_32 # Not Occupied
	WK = WP & K & MASK_32 # White Kings
	Jumpers = 0
	
	# Shift for normal pieces
	Temp = (nOcc << 4) & BP & MASK_32
	
	if Temp:
		Jumpers |= (((Temp & MASK_L3) << 3) | ((Temp & MASK_L5) << 5)) & WP & MASK_32
	  
	Temp = (((nOcc & MASK_L3) << 3) | ((nOcc & MASK_L5) << 5)) & BP & MASK_32
	Jumpers |= (Temp << 4) & WP & MASK_32
	
	# Shift for kings
	if WK:
		Temp = (nOcc >> 4) & BP & MASK_32
		if Temp:
			Jumpers |= (
			(((Temp & MASK_R3) >> 3) | ((Temp & MASK_R5) >> 5)) & WK & MASK_32
			)
		Temp = (((nOcc & MASK_R3) >> 3) | ((nOcc & MASK_R5) >> 5)) & BP & MASK_32
		if Temp:
			Jumpers |= (Temp >> 4) & WK & MASK_32
	
	return Jumpers
```


The helper functions operate via a series of simple logical operations and minimal branching. Wraparound and bound checking is preformed using the bit masks in uppercase chars.

  
```python
MASK_L3 = ( S[1] | S[2] | S[3] | S[9] | S[10] | S[11] | S[17] ...
```

Various other masks are defined for convenience and can be found in $ src/util/masks.py

- Inserting pieces

```python
def insert_piece(bitboard, index) -> int:
    """
    Inserts a piece at the given index on the bitboard.
    """
    mask = 1 << index
    return bitboard | mask
```


- Checking and Setting Squares

```python
def is_set(bitboard, index) -> bool:
	"""
	Is the bit at the given index set?
	"""
	return (bitboard & (1 << index) & MASK_32) != 0
	
def find_set_bits(bitboard) -> list:
	return [index for index in range(32) if (bitboard & (1 << index)) != 0]

def count_bits(bitboard: int) -> int:
	"""
	Counts the number of bits set on the bitboard.
	"""	
	return len(find_set_bits(bitboard))

def set_bit(bitboard, index) -> int:
	"""
	Returns the bitboard with the bit at the given index set to 1.
	"""
	return bitboard | (1 << index)
```

___

## The Agent

Iterative Deepning With Alpha Beta Pruning

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

- TERMINAL UI: '$python3 src/main.py' or '$pypy3 src/main.py'
- Pygame GUI: '$python3 src/gui.py
  
Follow the system prompts. Pytests are located in the tests directory. To run them: '$pytest'

## Mentions

- [Everything About Bitboards](https://3dkingdoms.com/checkers/bitboards.htm)

- Static Evaluation Tricks inspired by Andrew Lorber


