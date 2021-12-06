# RubiksCube-OptimalSolver
## Overview 
This project tries to find out if an optimal solver for Rubik's cube in Python makes any sense. An optimal solver has to generate
in principle all possible solving maneuvers with increasing length until a solution is found. Since the increase of the
maneuver length by 1 increases the number of maneuvers by a factor of about 13.3 the computation of all maneuvers of
length 17 or 18 - which will be necessary for the majority of cube positions - is not possible.  

Pruning tables give you some heuristics value for each position how many moves there are *at least*
still necessary to solve that position. If you are searching for 17 move solutions for example and you generated the
first 10 moves of a potential solution you may stop if the pruning table tells you that you need at least 8 more moves.
So with a good heuristics you have to generate only much shorter maneuvers in most cases.  

The time to optimally solve a cube then depends on two factors:
1. The quality of the pruning table which increases with the number of its entries and hence with its size.  
2. The number of positions ('nodes') generated per second.

Korf 1997 (Finding Optimal Solutions to Rubik’s Cube Using Pattern Databases) used a Sun Ultra-Spare Model 1 workstation
and was the first who computed optimal solutions to 10 random cubes. The pruning tables had a size of about 80 MB and 
the program generated about 700.000 nodes/s. The number of nodes for a full depth 17 search which had to be generated
were about 120.000.000.000 and took 2 days.

Michael Reid 1997 https://www.cflmath.com/Rubik/optimal_solver.html proposed a superior method. He used the
pruning table for the first phase of the two-phase algorithm. Since the target group of phase 1 exhibits 16-fold 
symmetry of the D4h point group the corresponding pruning table also can be compressed by a factor about 16. 
Moreover, it is possible to apply this pruning table simultaneously in three directions which increases the quality of
the heuristics. 

We use Reid's approach with a pruning table size of 34 MB and alternatively a pruning table 24 times larger in size.
The latter belongs to a target group where the four UD-slice edges are solved and all corner- and edge orientations are 0.
This pruning table also can be applied in three directions amd then leaves only the corner permutation undetermined.

The speed of the standard CPython is very slow compared to a compiled language. We alternatively also use PyPy 
https://www.pypy.org/ which has a Just-in-Time compiler and compare the performance of the four possible combinations
of pruning table size and Python version.  


## Usage
Put the *.py files into your path and do an "import example" from the Python Console. This generates necessary tables
and solves a random cube. The cube is solved and information about the solving process are displayed.

IMPORTANT: The constant BIG_TABLE in the file defs.py determines if you generate and use the
big pruning table with a size of 794 MB or the small 34 MB pruning table. See the results below how table creation time
and performance depend on this parameter.

## Results

work in progress...
