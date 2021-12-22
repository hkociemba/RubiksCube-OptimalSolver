# ################### Movetables describe the transformation of the coordinates by cube moves. #########################

from os import path
import array as ar
import optimal.cubie as cb
import optimal.enums as enums
from optimal.defs import N_TWIST, N_FLIP, N_SLICE_SORTED, N_CORNERS,  N_MOVE

a = cb.CubieCube()
# ######################################### Move table for the twists of the corners. ##################################

# The twist coordinate describes the 3^7 = 2187 possible orientations of the 8 corners
# 0 <= twist < 2187
fname = "move_twist"
if not path.isfile(fname):
    print("creating " + fname + " table...")
    twist_move = ar.array('H', [0 for i in range(N_TWIST * N_MOVE)])
    for i in range(N_TWIST):
        a.set_twist(i)
        for j in enums.Color:  # six faces U, R, F, D, L, B
            for k in range(3):  # three moves for each face, for example U, U2, U3 = U'
                a.corner_multiply(cb.basicMoveCube[j])
                twist_move[N_MOVE * i + 3 * j + k] = a.get_twist()
            a.corner_multiply(cb.basicMoveCube[j])  # 4. move restores face
    fh = open(fname, "wb")
    twist_move.tofile(fh)
else:
    print("loading " + fname + " table...")
    fh = open(fname, "rb")
    twist_move = ar.array('H')
    twist_move.fromfile(fh, N_TWIST * N_MOVE)
fh.close()
########################################################################################################################

# ####################################  Move table for the flip of the edges. ##########################################

# The flip coordinate describes the 2^11 = 2048 possible orientations of the 12 edges
# 0 <= flip < 2048
fname = "move_flip"
if not path.isfile(fname):
    print("creating " + fname + " table...")
    flip_move = ar.array('H', [0 for i in range(N_FLIP * N_MOVE)])
    for i in range(N_FLIP):
        a.set_flip(i)
        for j in enums.Color:
            for k in range(3):
                a.edge_multiply(cb.basicMoveCube[j])
                flip_move[N_MOVE * i + 3 * j + k] = a.get_flip()
            a.edge_multiply(cb.basicMoveCube[j])
    fh = open(fname, "wb")
    flip_move.tofile(fh)
else:
    print("loading " + fname + " table...")
    fh = open(fname, "rb")
    flip_move = ar.array('H')
    flip_move.fromfile(fh, N_FLIP * N_MOVE)
fh.close()
########################################################################################################################

# ###################### Move table for the four UD-slice edges FR, FL, Bl and BR. #####################################

# The slice_sorted coordinate describes the 12!/8! = 11880 possible positions of the FR, FL, BL and BR edges.
# 0 <= slice_sorted < 11880
fname = "move_slice_sorted"
if not path.isfile(fname):
    print("creating " + fname + " table...")
    slice_sorted_move = ar.array('H', [0 for i in range(N_SLICE_SORTED * N_MOVE)])
    for i in range(N_SLICE_SORTED):
        if i % 200 == 0:
            print('.', end='', flush=True)
        a.set_slice_sorted(i)
        for j in enums.Color:
            for k in range(3):
                a.edge_multiply(cb.basicMoveCube[j])
                slice_sorted_move[N_MOVE * i + 3 * j + k] = a.get_slice_sorted()
            a.edge_multiply(cb.basicMoveCube[j])
    fh = open(fname, "wb")
    slice_sorted_move.tofile(fh)
    print()
else:
    print("loading " + fname + " table...")
    fh = open(fname, "rb")
    slice_sorted_move = ar.array('H')
    slice_sorted_move.fromfile(fh, N_SLICE_SORTED * N_MOVE)
fh.close()
########################################################################################################################

# ########################################## Move table for the corners. ###############################################

# The corners coordinate describes the 8! = 40320 permutations of the corners.
# 0 <= corners < 40320
fname = "move_corners"
if not path.isfile(fname):
    print("creating " + fname + " table...")
    corners_move = ar.array('H', [0 for i in range(N_CORNERS * N_MOVE)])
    for i in range(N_CORNERS):
        if (i+1) % 200 == 0:
            print('.', end='', flush=True)
        if(i+1) % 16000 == 0:
            print('')
        a.set_corners(i)
        for j in enums.Color:
            for k in range(3):
                a.corner_multiply(cb.basicMoveCube[j])
                corners_move[N_MOVE * i + 3 * j + k] = a.get_corners()
            a.corner_multiply(cb.basicMoveCube[j])
    fh = open(fname, "wb")
    corners_move.tofile(fh)
    fh.close()
    print()
else:
    print("loading " + fname + " table...")
    fh = open(fname, "rb")
    corners_move = ar.array('H')
    corners_move.fromfile(fh, N_CORNERS * N_MOVE)
fh.close()
########################################################################################################################
