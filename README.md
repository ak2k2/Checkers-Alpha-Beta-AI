# RUN
pytests are in the tests folder. To run them, run `pytest` in the root directory.

simulating 'random legal games' using pypy is MUCH faster. To run this, run `pypy3 -m cProfile -s cumtime game.py`.



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
