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
Put the *.py files into the path of your project and do  
```python
>>> import solver  as sv
```
from the Python Console.   
A cube is defined by its cube definition string. A solved cube has the string
'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'.   
```python
>>> cubestring = 'DUUBULDBFRBFRRULLLBRDFFFBLURDBFDFDRFRULBLUFDURRBLBDUDL'
```
See https://github.com/hkociemba/RubiksCube-TwophaseSolver/blob/master/enums.py for the exact  format.
```python
>>> sv.solve(cubestring)
```
This solves the cube described by the definition string optimally and displays information about the solving process.

IMPORTANT: The constant BIG_TABLE in the file defs.py determines whether you generate and use the
big pruning table with a size of 794 MB or the small 34 MB pruning table. See the results below how table creation time
and performance depend on this parameter. The default is BIG_TABLE = True.

## Performance results

We solved 8 random cubes in four scenarios. Actually the 8th was the first one which happened to have an
optimal solution with 19 moves. All computations were done on a Windows 10 machine with an AMD Ryzen 7 3700X 3.59 GHz.   
We distinguish between computations with the standard CPython interpreter and computation with PyPy (pypy3) which
includes a Just-in-Time compiler and gives a speedup by a factor of about 10.   

####Table creation time (to be performed only once)
PyPy + 794 MB table: 13 minutes  
PyPy + 34 MB table: less than a minute  
CPython + 794 MB table:  8 hours  
CPython + 34 MB table: 20 minutes   

#### Solving statistics

We created 8 random cubes and solved them using the 4 different scenarios. The solution lengths were 1 x 17 moves,
6 x 18 moves and 1 x 19  moves.  

 1. It shows that in all cases the number of nodes which need to be visited until an optimal solution is found is between 
7.3 and 8.4 times higher with the 34 MB table compared to the 794 MB table. This does not seem to depend on the solution
length.  
 2. The highest node generation rate is achieved with PyPy and the 34 MB table with about 3.400.000 nodes/s. With the 794 MB
table it drops to about 2.000.000 nodes/s. We think this is the result of the 32 MB L3-cache which leads to much more
cache misses with the large table.
The node generation rate with CPython is relatively poor compared with PyPy. It is only about 155.000 nodes/s with the 
34 MB table and about 146.000 nodes/s with the 784 MB table. So here the impact of the large table is much less. 

Combining 1. and 2. and setting the performance index of the combination CPython + 34 MB table to 1 we get the following
performance indices:

PyPy + 794 MB table: about 100  
PyPy + 34 MB table: about 22  
CPython + 794 MB table:  about 7 
CPython + 34 MB table: 1 

Here the solution for the 17 move solve, the four numbers in the row sorted by decreasing performance index:   

position: DBLRUULUUFFBLRDFLBBRLUFFDFRFDUDDUBBRLFURLBUBRDRFLBDDLR  
solution: U2 F2 L1 D2 B3 R1 B3 D3 F1 L2 F3 B2 L3 D3 F2 U3 R3 (17f)  
total time: 34 s, 164 s, 444 s, 3493 s  
total number of nodes generated: 65,991,378, 546,715,500, 65,991,378, 546,715,500    
average node generation: 1,916,237 nodes/s, 3,324,125 nodes/s, 148,379 nodes/s, 156,535 nodes/s   

And here the solution for the 19 move solve, we only used PyPy and estimated the CPython total time:   

position: UDFDULRFRBUUDRRLLLFRDRFBFRBDBDBDFDUUBFULLDRULLLRUBBBFF  
solution: U1 L2 F2 L2 F3 U2 D3 B1 D3 F2 B3 R3 L2 D1 L2 B2 L3 B3 D3 (19f)   
total time: 4,473 s, 17,343 s, 55,000 s (estimated), 400,000 s (estimated)    
total number of nodes generated: 8,042,012,221, 62,657,640,307    
average node generation: 1,797,989 nodes/s, 3,612,882 nodes/s 

#### Conclusion:
Optimally solving Rubik's Cube with Python using the standard CPython interpreter and the 34 MB table cannot be
recommended since the solution time can take several days in worst case. With PyPy and the 794 MB table the computation
time may even exceed the performance of some other optimal solvers written in a compiled language.


 
 