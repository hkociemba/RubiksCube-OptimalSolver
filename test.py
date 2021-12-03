import face
import cubie as cb
import solver as sv




cc = cb.CubieCube()
cc.randomize()
fc = cc.to_facelet_cube()
fl = fc.to_string()
# First results show, that Python is quite slow with 40 MB pruning table size.
print(sv.solve(fl))