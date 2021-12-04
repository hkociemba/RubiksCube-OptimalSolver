import face  # though not used in this module we get circular when we omit the import
from cubie import CubieCube
import solver as sv


cc = CubieCube()
cc.randomize()
fc = cc.to_facelet_cube()
fl = fc.to_string()  # fl holds the cube definition string. For the format see enums.py
print('Solve random cube with cube definition string ' + fl)
print(sv.solve(fl))

#other examples

# cubestr = 'UUUUUUUUURRRFRRRRRFFFLFRFFFDDDDDDDDDLLLLLFLLLBBBBBBBBB'
# goalstr = 'UUUUUUUFURRRRRRRRRFUFFFFFDFDFDDDDDDDLLLLLLLLLBBBBBBBBB'
# solve cubstr to goalstr
# print(sv.solveto(cubestr, goalstr))

#superflip = 'UBULURUFURURFRBRDRFUFLFRFDFDFDLDRDBDLULBLFLDLBUBRBLBDB'
#print('Solve superflip cube with cube definition string ' + superflip)
#print('This is really hard to solve optimally with Python and will take a couple of days...')
#print(sv.solve(superflip)) #  this is hard one and needs 20 moves
