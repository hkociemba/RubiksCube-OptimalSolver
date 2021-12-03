import face
import cubie as cb
import solver as sv
from enums import Move as mv


cc = cb.CubieCube()
#cc.move(mv.U1)
#cc.move(mv.R1)
#cc.move(mv.F1)
#cc.move(mv.D1)
cc.randomize()
fc = cc.to_facelet_cube()
fl = fc.to_string()
print(fl)
#fl='DFFLUBFDRDUUDRLBFUDLFRFRDBLRLUDDRBUFBULULBUBBLDLFBRRFR'
# First results show, that Python is quite slow with the 35 MB pruning table size. A full depth 15 search takes roughly
# 1 minute, and a full depth d search then takes about 13.3^(d-15) minutes. So a full depth 18 search (which is
# sufficient for the majority of the cubes) may take more than a day. With a compiled language like C++ speeds are
# about 50 times higher
print(sv.solve(fl))