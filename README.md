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

## Performance results

We solved 8 random cubes in four scenarios. Actually the 8th was the first one which happened to have an
optimal solution with 19 moves. All computations were done on a Windows 10 machine with an AMD Ryzen 7 3700X 3.59 GHz.   
We distinguish between computations with the standard CPython interpreter and computation with PyPy (pypy3) which
includes a Just-in-Time compiler and gives a speedup by a factor of about 10.   

The 4 values in each row give the results of the combinations   
PyPy + 794 MB table, PyPy + 34 MB table, CPython + 794 MB table, CPython + 34 MB table

####Table creation time (to be performed only once)

less than a minute, 13 minutes, 20 minutes, 8 hours

#### Solving statistics


position: FLLUUBUUDLDUFRRBRLRFFUFDRLUDBRLDBRDBLBFFLLDFFBDUUBRDRB   
solution: R3 U1 R2 L2 U2 F2 R1 U3 L2 F2 R1 U3 F3 U2 D3 B2 U1 F1 (18f)  
total time: 889 s, 4003 s   
total number of nodes generated: 1.780.007.241, 13.253.835.078  
average node generation: 2.001.483 nodes/s, 3.310.626 nodes/s 


position: BRBBUFFLLFLDBRDFLFRDDFFRBFRDDULDBBUURDDULULURLFURBRLBU  
solution: U2 D1 F3 R3 B3 L3 B3 D1 L3 B2 R3 F1 R3 B2 D1 B1 U1 L2 (18f)  
total time: 346 s, 1634 s   
total number of nodes generated: 657.376.166, 5.300.060.699  
average node generation: 1.901.734 nodes/s, 3.243.053 nodes/s   


position: DBLRUULUUFFBLRDFLBBRLUFFDFRFDUDDUBBRLFURLBUBRDRFLBDDLR  
solution: U2 F2 L1 D2 B3 R1 B3 D3 F1 L2 F3 B2 L3 D3 F2 U3 R3 (17f)
total time: 34 s, 164 s  
total number of nodes generated: 65.991.378, 546.715.500    
average node generation: 1916237 nodes/s, 3324125 nodes/s   


position: UFBDULRLULDDRRRFDUBBBLFFLFLUUDRDFRBRRBDRLUFBFLLFUBDBUD  
solution: L1 D3 R3 U1 R3 D2 F2 D1 L3 F1 B2 R1 D3 L2 F2 L3 U2 B1 (18f)  
total time: 1564 s, 6899 s  
total number of nodes generated: 3.094.714.173, 25.817.184.981  
average node generation: 1.978.915 nodes/s, 3.742.045 nodes/s  



position: BLURULUBBDFRRRBDDDRDRRFFFURLFFUDLDDLUUFLLDFBUBBLRBUBFL  
solution: F1 R1 B3 U2 F1 U3 D1 B2 D2 L3 U2 R2 B2 L1 F3 R3 F2 R2 (18f)  
total time: 630 s, 3109 s  
total number of nodes generated: 1338106263, 10944349014  
average node generation: 2123873 nodes/s, 3520198 nodes/s  



position: FRRRUFDBFLLBURBRBDLUUUFRDDFBRDDDDLDBUBFLLFULLUFRLBURFB  
solution: U2 D3 L3 F3 L3 D1 L1 U1 F2 U2 L3 B2 D1 L3 D1 B2 D2 B3 (18f) 
total time: 354 s, 1460 s    
total number of nodes generated: 645.578.747, 5.249.269.931    
average node generation: 1.824.555 nodes/s 3.595.546 nodes/s   



position: FBBDUFRDDBUURRRLFUDBLRFBBLUDFBUDRDULUFFDLUFLRRLRDBLFBL  
solution: U2 D2 B2 R1 B1 R2 B2 R2 D3 L3 D2 L3 B3 R1 U1 F2 L3 F1 (18f)  
total time: 472 s, 2261 s  
total number of nodes generated: 921.263.634, 7.121.017.212  
average node generation: 1953705 nodes/s, 3150087 nodes/s    


position: UDFDULRFRBUUDRRLLLFRDRFBFRBDBDBDFDUUBFULLDRULLLRUBBBFF  
solution: U1 L2 F2 L2 F3 U2 D3 B1 D3 F2 B3 R3 L2 D1 L2 B2 L3 B3 D3 (19f)   
total time: 4473 s, 17343 s   
total number of nodes generated: 8.042.012.221, 62.657.640.307    
average node generation: 1.797.989 nodes/s, 3.612.882 nodes/s    
 
 