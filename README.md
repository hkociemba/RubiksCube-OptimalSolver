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
were about 120,000,000,000 and the computation took 2 days.

Michael Reid 1997 https://www.cflmath.com/Rubik/optimal_solver.html proposed a superior method. He used the
pruning table for the first phase of the two-phase algorithm. Since the target group of phase 1 exhibits 16-fold 
symmetry of the D4h point group the corresponding pruning table also can be compressed by a factor about 16. 
Moreover, it is possible to apply this pruning table simultaneously in three directions which increases the quality of
the heuristics. 
## Speeding up Python
It became clear that using Reid's approach with a pruning table size of 34 MB is not best suited for Python.
Today's hardware with several GB of RAM allows the usage of a pruning table 24 times larger which can compensate the
relative slowness of the Python interpreter. We get a speedup by a factor of about 7 in this way.   

This bigger pruning table belongs to a target subgroup where the four UD-slice edges are not only in their slice but
also in their correct position. The edge and corner orientation also have to be 0, like in the phase 1 subgroup.
The bigger pruning table also can be applied in three directions and the intersection of the three subgroups is the
group where only the corner permutations still are not fixed.

Another performance boost is given by the replacement of the standard CPython with PyPy (https://www.pypy.org/) which
has a Just-in-Time compiler and gives an additional speedup by a factor of about 13. We strongly recommend to use PyPy,
the combined overall performance boost factor then is about 100. 


## Usage
The package is published on PyPI and can be installed with

```$ pip install RubikOptimal``` 

or using PyPy 

```$ pypy3 -m pip install RubikOptimal```

Once installed, you can import the module optimal.solver into your code:

```python
>>> import optimal.solver as sv
```
There are several tables which must be created, but only on the first run. These need about 955 MB of disk space, and it
takes about 8 hour or even longer to create them with CPython and about 15 minutes with PyPy, depending on the used 
hardware.
But only with these computational relative expensive tables the algorithm works highly effective and will find optimal
solutions to Rubik's cube in a decent time.

A cube is defined by its cube definition string. A solved cube has the string 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'.   
```python
>>> cubestring = 'DUUBULDBFRBFRRULLLBRDFFFBLURDBFDFDRFRULBLUFDURRBLBDUDL'
```
See https://github.com/hkociemba/RubiksCube-TwophaseSolver/blob/master/enums.py for the exact  format.
```python
>>> sv.solve(cubestring)
```
This optimally solves the cube described by the definition string. After a couple of minutes (using PyPy) we get
```python
'U1 B2 D3 B3 R3 L3 U1 L2 B2 R1 D3 R3 B1 L3 U2 B2 R1 D3 (18f*)'
```
U, R, F, D, L and B denote the Up, Right, Front, Down, Left and Back face of the cube. 1, 2, and 3 denote a 90°, 180°
and 270° clockwise rotation of the corresponding face. (18f*) means that the solution has 18 moves in the face turn
metric and the star indicates that it is an optimal solution.

You also have the possibility to solve a cube not to the solved position but to some favorite pattern represented by
goalstring.
```python
>>> sv.solveto(cubestring,goalstring)
```
will find an optimal solution for this transformation.   

You can test the performance of the algorithm on your machine with something similar to
```python
>>> import optimal.performance as pf
>>> pf.test(10)
```
This will for example generate 10 random cubes and gives information about the solving process. 

## Performance results

We solved 10 random cubes with CPython and with PyPy (pypy3), the latter including a Just-in-Time compiler which gives a
speedup by a factor of more than 10. All computations were done on a Windows 10 machine with an AMD Ryzen 7 3700X 3.59 GHz.

#### Table creation time (to be performed only once)
PyPy: 13 minutes
CPython:  8 hours   

#### Solving statistics

A full depth 17 search typically takes about 1/2 hour using CPython and less than 3 minutes with PyPy.   
The number of nodes that have to be generated for a full depth 17 search has an average of 280,000,000.
This is more than 400 times less than the 120,000,000,000 in Korf's approach who of course did not have 
1 GB of RAM in 1997 but only about 100 MB.
The average time to solve 10 random cubes (1x17 moves, 7x18 moves and 2x19 moves) with PyPy was about 20 min/cube
and ranged from 36 s for the 17 move solution to 2447 s and 4389 s for the two 19 move solutions.   
The program generated about 1.8 million nodes/s.

#### Conclusion:
Optimally solving Rubik's Cube with Python using the standard CPython interpreter is not recommended.
With PyPy and the 794 MB table the computation for optimally solving a Rubik's cube in Python is done within 
minutes up to a couple of hours.



 
 