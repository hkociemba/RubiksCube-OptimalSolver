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
print(fl)  # fl holds the cube definition string. For the format see enums.py
#fl='DFFLUBFDRDUUDRLBFUDLFRFRDBLRLUDDRBUFBULULBUBBLDLFBRRFR'
print(sv.solve(fl))