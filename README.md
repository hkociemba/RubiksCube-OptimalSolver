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
the program generated about 700,000 nodes/s. The number of nodes for a full depth 17 search which had to be generated
were about 120,000,000,000 and the computation took 2 days.

Michael Reid 1997 https://www.cflmath.com/Rubik/optimal_solver.html proposed a superior method. He used the
pruning table for the first phase of the two-phase algorithm (Kociemba's algorithm). Since the target group of phase 1 exhibits 16-fold 
symmetry of the D4h point group the corresponding pruning table also can be compressed by a factor about 16. 
Moreover, it is possible to apply this pruning table simultaneously in three directions which increases the quality of
the heuristics. 
## Speeding up Python
It became clear that using Reid's approach with a pruning table size of 34 MB is not best suited for Python.
Today's hardware with several GB of RAM allows the usage of a 794 MB pruning table (24 times larger) which can compensate the
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
***
A little GUI-program may help to define the cube definition string interactively and run the solver. It seems to work
with PyPy (and we recommend using PyPy for performance reasons) without problems.
```python
>>> import optimal.client_gui
```

![](gui.jpg "")
***
## Performance results

We solved 10 random cubes with PyPy (pypy3). All computations were done on a Windows 10 machine with an AMD Ryzen 7 3700X 3.59 GHz.

#### Table creation time (to be performed only once)
PyPy: 13 minutes  
CPython:  8 hours   

#### Solving statistics for 10 random cubes using PyPy
The optimal solving time was in a range between 37 s and 1167 s, the total time for the 10 cubes was 3841 s. The average
optimal solving length was 17.80

1. FDDLURBFDRFRLRDFBRLDBRFFBBLURDBDLLFBUUDDLUFULFBRLBRUUU  
depth 15 done in 0.75 s, 1290873 nodes generated, about 1720935 nodes/s  
depth 16 done in 7.06 s, 17831301 nodes generated, about 2524572 nodes/s  
depth 17 done in 98.06 s, 245464971 nodes generated, about 2503158 nodes/s  
depth 18 done in 231.27 s, 574900111 nodes generated, about 2485881 nodes/s  
total time: 337.39 s, nodes generated: 839588899  
R1 U2 L1 U2 L2 B2 R2 D3 L3 B2 U1 F3 B1 D1 R3 L1 F3 U1 (18f*)  


2. FFDFUUBBDRBFLRRLUURDBFFUBBBURDBDFFDLULURLDDLLLRRUBDFLR  
depth 15 done in 0.99 s, 1928430 nodes generated, about 1957598 nodes/s  
depth 16 done in 9.92 s, 25418349 nodes generated, about 2561791 nodes/s  
depth 17 done in 130.17 s, 334597977 nodes generated, about 2570428 nodes/s  
depth 18 done in 33.42 s, 88752397 nodes generated, about 2655580 nodes/s  
total time: 174.86 s, nodes generated: 450855850  
U1 R3 B3 R2 F3 R2 L3 D2 B1 D1 F2 L3 B3 D3 L1 F2 D3 L2 (18f*)  


3. BLRBUDDLBUFULRUURBBDLDFBDLLLUFUDFRURRRLDLBFRFFFUBBRDFD  
depth 15 done in 1.25 s, 3311061 nodes generated, about 2648637 nodes/s  
depth 16 done in 15.28 s, 39782112 nodes generated, about 2603184 nodes/s  
depth 17 done in 186.5 s, 485952603 nodes generated, about 2605643 nodes/s  
depth 18 done in 60.28 s, 150996678 nodes generated, about 2504876 nodes/s  
total time: 263.44 s, nodes generated: 680347653  
U1 D2 B1 L2 B3 L2 B2 R3 D3 F3 U3 R3 D1 L3 F3 L1 F3 B3 (18f*)  


4. DULDULDDLFUBDRFBBRRRDDFBURLFUURDLRBUFLBLLFBBLDFRRBFFUU  
depth 15 done in 0.8 s, 1853697 nodes generated, about 2325551 nodes/s  
depth 16 done in 10.13 s, 24440712 nodes generated, about 2413874 nodes/s  
depth 17 done in 25.59 s, 63001023 nodes generated, about 2461545 nodes/s  
total time: 36.58 s, nodes generated: 89445969  
R1 F1 R2 L2 U1 B1 D3 B2 L1 F3 U2 L3 F2 L1 D3 F2 U3 (17f*)  


5. DBDBUFURUBLFBRLFFLFDRRFUBLDDDRBDURUUBDLDLFULRLRLUBFBRF  
depth 15 done in 0.55 s, 1335570 nodes generated, about 2441181 nodes/s  
depth 16 done in 7.5 s, 18770952 nodes generated, about 2502760 nodes/s  
depth 17 done in 103.77 s, 260113815 nodes generated, about 2506756 nodes/s  
depth 18 done in 1055.2 s, 2624360711 nodes generated, about 2487065 nodes/s  
total time: 1167.05 s, nodes generated: 2904680714  
L1 D1 L2 U2 F1 U1 D2 F2 U1 R1 F1 B1 R2 U3 R1 F1 U3 F3 (18f*)  


6. RBBRURRDLDFLLRUUFDDLBFFFRDLUBFBDUFBFBDFRLDRUBULDLBULRU  
depth 15 done in 0.55 s, 1374786 nodes generated, about 2512861 nodes/s  
depth 16 done in 7.39 s, 19053294 nodes generated, about 2577870 nodes/s  
depth 17 done in 101.86 s, 262000026 nodes generated, about 2572181 nodes/s  
depth 18 done in 34.55 s, 90387572 nodes generated, about 2616358 nodes/s  
total time: 144.38 s, nodes generated: 372925295  
U1 F2 U3 D1 F2 L1 B3 D2 F1 R1 D3 L2 D1 F2 D1 B3 U3 F3 (18f*)  


7. UDLRURDBBDFUBRLFDRBLRBFUFLURULRDBFDUBDLFLRLUDBFRFBUFLD  
depth 15 done in 0.58 s, 1491219 nodes generated, about 2579517 nodes/s  
depth 16 done in 8.09 s, 20304783 nodes generated, about 2508591 nodes/s  
depth 17 done in 108.34 s, 276363516 nodes generated, about 2550818 nodes/s  
depth 18 done in 53.97 s, 137953480 nodes generated, about 2556157 nodes/s  
total time: 171.05 s, nodes generated: 436229374  
U1 D2 R3 L3 B2 R2 D1 L1 D1 F3 U2 D2 R1 B1 U1 D1 F2 D2 (18f*)  


8. BRFRULFUBUFLLRBBRRULLLFBBDDDFLBDULRFRDRULDFURDFUDBFDBU  
depth 15 done in 0.44 s, 1050312 nodes generated, about 2397425 nodes/s  
depth 16 done in 6.11 s, 15184191 nodes generated, about 2485504 nodes/s  
depth 17 done in 88.06 s, 217674717 nodes generated, about 2471804 nodes/s  
depth 18 done in 1050.7 s, 2611603965 nodes generated, about 2485577 nodes/s  
total time: 1145.34 s, nodes generated: 2845590837  
L3 B2 D1 B2 U1 L3 U1 L2 U1 R1 U2 B1 D1 L3 F2 R1 F3 R3 (18f*)  


9. FUBFUBBBDRLDFRFBDRURBBFUUDUFLRUDRFFURLLULDLRLLBDRBLFDD    
depth 15 done in 0.63 s, 1561818 nodes generated, about 2498509 nodes/s  
depth 16 done in 8.23 s, 20984124 nodes generated, about 2548442 nodes/s  
depth 17 done in 83.0 s, 211311256 nodes generated, about 2545916 nodes/s  
total time: 91.91 s, nodes generated: 233985349  
L1 B2 U1 D1 R1 F1 B1 D2 L3 U2 D1 F3 U2 F3 U1 R1 B2 (17f*)  


10. BRLLUFLDRBUUURLDUFURDDFBLLFDFLLDRRFRRUFBLFFBBBBUDBDURD  
depth 15 done in 0.59 s, 1500297 nodes generated, about 2525327 nodes/s  
depth 16 done in 8.08 s, 20394183 nodes generated, about 2524626 nodes/s  
depth 17 done in 110.7 s, 275572329 nodes generated, about 2489292 nodes/s  
depth 18 done in 189.89 s, 483624333 nodes generated, about 2546851 nodes/s  
total time: 309.31 s, nodes generated: 781208901  
U3 R2 B2 U2 B3 D3 L1 D1 L2 U2 D2 R3 U1 D1 R3 D1 B3 U1 (18f*)  

And because you can bet that you never will see a random cube which needs 20 moves (the chance is in the order of 
1/10^11) we add the solving information for the "superflip" where  all edges and corners are in position but all edges
are flipped. This was the first position which was proved to need 20 moves. It takes about 7 hours to find the 20 move
solution with our solver.

superflip: UBULURUFURURFRBRDRFUFLFRFDFDFDLDRDBDLULBLFLDLBUBRBLBDB   
depth 14 done in 0.24 s, 185949 nodes generated, about 790936 nodes/s   
depth 15 done in 1.02 s, 2734515 nodes generated, about 2693838 nodes/s   
depth 16 done in 10.95 s, 35007363 nodes generated, about 3196115 nodes/s   
depth 17 done in 150.14 s, 442849923 nodes generated, about 2949558 nodes/s   
depth 18 done in 1978.36 s, 5537992239 nodes generated, about 2799286 nodes/s   
depth 19 done in 24197.75 s, 68794215435 nodes generated, about 2843000 nodes/s   
depth 20 done in 88.06 s, 234395758 nodes generated, about 2661680 nodes/s   
total time: 26426.64 s, nodes generated: 75047390029   
U1 R1 U2 R1 F2 L1 U2 R1 F3 B3 R2 D1 R3 L1 U2 F2 D2 F1 R2 D1 (20f*)

And here the optimal solve for the hardest position from https://www.cube20.org/ which takes about 3 hours:  

RBFLURBFLBUUFRBBDDRUURFLRDDBFLLDRRBFFUUBLFFDDLUULBRLDD  
depth 14 done in 0.08 s, 13425 nodes generated, about 171895 nodes/s  
depth 15 done in 0.3 s, 277653 nodes generated, about 934544 nodes/s  
depth 16 done in 2.17 s, 5247552 nodes generated, about 2415889 nodes/s  
depth 17 done in 35.17 s, 91161960 nodes generated, about 2591883 nodes/s  
depth 18 done in 596.05 s, 1481591235 nodes generated, about 2485695 nodes/s  
depth 19 done in 9230.55 s, 23094251484 nodes generated, about 2501937 nodes/s  
depth 20 done in 1846.67 s, 4750476338 nodes generated, about 2572453 nodes/s  
total time: 11710.99 s, nodes generated: 29423019926  
U1 R3 L3 F2 U1 B3 R2 D1 R2 U1 F2 U1 F1 L3 F2 B1 D3 R3 U2 F1 (20f*)

#### Conclusion:
Optimally solving Rubik's Cube with Python using the standard CPython interpreter is not recommended.
With PyPy and the 794 MB pruning table the computation for optimally solving a Rubik's cube in Python is done within 
minutes up to a couple of hours (for the rare and difficult 20 move positions) .


## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=hkociemba/RubiksCube-OptimalSolver&type=Date)](https://star-history.com/#hkociemba/RubiksCube-OptimalSolver&Date)

 
 
