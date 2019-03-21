Author: Donald Nikkessen

The following external libraries are require to run the code:
 - numpy
 - openpyxl

 Running the code for all configurations is done using the command:
 $  python circuit_board.py
 The results are then created as text files in the current folder.

 The code is split into three files:

 - read_board.py
 This file contains all the functions needed to read the supplied files
 into a usable form for our program.

 - a_star.py
 This file contains an implementation of the A* algorithm which is used
 to find the best path between two gates.

 - circuit_board.py
 This file implements the circuit_board class, which can then be solved
 using the A* algorithm.

 # Notes:

 The current implementation processes the connections for each board in the
 order they are stored in the input file. Trying all possible permutations
 would require an enormous amount of time, which means a breadth-first approach
 should be used to reduce runtime by not expanding boards that are more
 expensive than the current best board.
