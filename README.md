# RubiksCube-OptimalSolver
## Overview 
This project tried to find out if an optimal solver for Rubik's cube in Python makes any sense. An optimal solver has to generate
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

Michael Reid 1997 https://www.cflmath.com/Rubik/optimal_solver.html proposed the method implemented here and he used the
pruning table for the first phase the two-phase algorithm. By reducing the table size by 16 of the 48 cube symmetries and
applying this pruning table simultaneously in three directions he got a much more powerful heuristics with the phase 1 
pruning table which has a size of only 34 MB in the implementation given here.  

The number of nodes which needs to be generated for a full depth 17 search is much less compared to Korf's method and
only about 2.000.000.000. With the standard CPython only about 150.000 nodes/s are done which is unsatisfactory.  
But with PyPy https://www.pypy.org/index.html I got more than 3.000.000 nodes/s and a full depth 17 search took only 
less than 15 minutes.

##Conclusion
Using pypy3 the majority of Rubik's cube can be solved within a reasonable time (minutes, hours) using only the pruning
table of phase 1 of the two-phase algorithm.

## Usage
Put the *.py files into your path and do an "import test" from the Python Console. This generates a Random Cube and shows
information about the solving process.

##Todo
Implement a 24 times larger pruning table which takes into account also the 24 permutations of the 4 edges used for the
"slice coordinate"

