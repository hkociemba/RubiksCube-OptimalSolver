# #################### Symmetry related functions. Symmetry considerations increase the performance of the solver.######

from os import path
import array as ar
import optimal.cubie as cb
from optimal.defs import N_TWIST, N_SYM, N_SYM_D4h, N_FLIP, N_SLICE, N_SLICE_SORTED, N_MOVE, \
    N_FLIPSLICE_CLASS, N_FLIPSLICESORTED_CLASS, BIG_TABLE
from optimal.enums import Corner as Co, Edge as Ed, Move as Mv, BS

INVALID = 65535
INVALID32 = 4294967295
#  #################### Permutations and orientation changes of the basic symmetries ###################################

# 120° clockwise rotation around the long diagonal URF-DBL
cpROT_URF3 = [Co.URF, Co.DFR, Co.DLF, Co.UFL, Co.UBR, Co.DRB, Co.DBL, Co.ULB]  # corner permutation
coROT_URF3 = [1, 2, 1, 2, 2, 1, 2, 1]  # corner orientation
epROT_URF3 = [Ed.UF, Ed.FR, Ed.DF, Ed.FL, Ed.UB, Ed.BR, Ed.DB, Ed.BL, Ed.UR, Ed.DR, Ed.DL, Ed.UL]  # edge permutation
eoROT_URF3 = [1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1]  # edge orientation

# 180° rotation around the axis through the F and B centers
cpROT_F2 = [Co.DLF, Co.DFR, Co.DRB, Co.DBL, Co.UFL, Co.URF, Co.UBR, Co.ULB]
coROT_F2 = [0, 0, 0, 0, 0, 0, 0, 0]
epROT_F2 = [Ed.DL, Ed.DF, Ed.DR, Ed.DB, Ed.UL, Ed.UF, Ed.UR, Ed.UB, Ed.FL, Ed.FR, Ed.BR, Ed.BL]
eoROT_F2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# 90° clockwise rotation around the axis through the U and D centers
cpROT_U4 = [Co.UBR, Co.URF, Co.UFL, Co.ULB, Co.DRB, Co.DFR, Co.DLF, Co.DBL]
coROT_U4 = [0, 0, 0, 0, 0, 0, 0, 0]
epROT_U4 = [Ed.UB, Ed.UR, Ed.UF, Ed.UL, Ed.DB, Ed.DR, Ed.DF, Ed.DL, Ed.BR, Ed.FR, Ed.FL, Ed.BL]
eoROT_U4 = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1]

# reflection at the plane through the U, D, F, B centers
cpMIRR_LR2 = [Co.UFL, Co.URF, Co.UBR, Co.ULB, Co.DLF, Co.DFR, Co.DRB, Co.DBL]
coMIRR_LR2 = [3, 3, 3, 3, 3, 3, 3, 3]
epMIRR_LR2 = [Ed.UL, Ed.UF, Ed.UR, Ed.UB, Ed.DL, Ed.DF, Ed.DR, Ed.DB, Ed.FL, Ed.FR, Ed.BR, Ed.BL]
eoMIRR_LR2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

basicSymCube = [cb.CubieCube()] * 4
basicSymCube[BS.ROT_URF3] = cb.CubieCube(cpROT_URF3, coROT_URF3, epROT_URF3, eoROT_URF3)
basicSymCube[BS.ROT_F2] = cb.CubieCube(cpROT_F2, coROT_F2, epROT_F2, eoROT_F2)
basicSymCube[BS.ROT_U4] = cb.CubieCube(cpROT_U4, coROT_U4, epROT_U4, eoROT_U4)
basicSymCube[BS.MIRR_LR2] = cb.CubieCube(cpMIRR_LR2, coMIRR_LR2, epMIRR_LR2, eoMIRR_LR2)
# ######################################################################################################################

# ######################################## Fill SymCube list ###########################################################

# 48 CubieCubes will represent the 48 cube symmetries
symCube = []
cc = cb.CubieCube()  # Identity cube
idx = 0
for urf3 in range(3):
    for f2 in range(2):
        for u4 in range(4):
            for lr2 in range(2):
                symCube.append(cb.CubieCube(cc.cp, cc.co, cc.ep, cc.eo))
                idx += 1
                cc.multiply(basicSymCube[BS.MIRR_LR2])
            cc.multiply(basicSymCube[BS.ROT_U4])
        cc.multiply(basicSymCube[BS.ROT_F2])
    cc.multiply(basicSymCube[BS.ROT_URF3])
########################################################################################################################

# ########################################## Fill the inv_idx array ####################################################

# Indices for the inverse symmetries: SymCube[inv_idx[idx]] == SymCube[idx]^(-1)
inv_idx = [0] * N_SYM
for j in range(N_SYM):
    for i in range(N_SYM):
        cc = cb.CubieCube(symCube[j].cp, symCube[j].co, symCube[j].ep, symCube[j].eo)
        cc.corner_multiply(symCube[i])
        if cc.cp[Co.URF] == Co.URF and cc.cp[Co.UFL] == Co.UFL and cc.cp[Co.ULB] == Co.ULB:
            inv_idx[j] = i
            break
########################################################################################################################


# #### Generate the table for the conjugation of a move m by a symmetry s. conj_move[N_MOVE*s + m] = s*m*s^-1 ##########
conj_move = ar.array('H', [0] * (N_MOVE * N_SYM))
for s in range(N_SYM):
    for m in Mv:
        ss = cb.CubieCube(symCube[s].cp, symCube[s].co, symCube[s].ep, symCube[s].eo)  # copy cube
        ss.multiply(cb.moveCube[m])  # s*m
        ss.multiply(symCube[inv_idx[s]])  # s*m*s^-1
        for m2 in Mv:
            if ss == cb.moveCube[m2]:
                conj_move[N_MOVE * s + m] = m2
########################################################################################################################

# ###### Generate the phase 1 table for the conjugation of the twist t by a symmetry s. twist_conj[t, s] = s*t*s^-1 ####
fname = "conj_twist"
if not path.isfile(fname):
    print('On the first run, several tables will be created. This may take 8 hours using CPython '
          '(depending on the hardware). ')
    print('Using PyPy reduces the time to about 15 minutes.')
    print('All tables are stored in ' + path.dirname(path.abspath(fname)))
    print()
    print("creating " + fname + " table...")
    twist_conj = ar.array('H', [0] * (N_TWIST * N_SYM_D4h))
    for t in range(N_TWIST):
        cc = cb.CubieCube()
        cc.set_twist(t)
        for s in range(N_SYM_D4h):
            ss = cb.CubieCube(symCube[s].cp, symCube[s].co, symCube[s].ep, symCube[s].eo)  # copy cube
            ss.corner_multiply(cc)  # s*t
            ss.corner_multiply(symCube[inv_idx[s]])  # s*t*s^-1
            twist_conj[N_SYM_D4h * t + s] = ss.get_twist()
    fh = open(fname, "wb")
    twist_conj.tofile(fh)
else:
    print("loading " + fname + " table...")
    fh = open(fname, 'rb')
    twist_conj = ar.array('H')
    twist_conj.fromfile(fh, N_TWIST * N_SYM_D4h)

fh.close()
# ######################################################################################################################

# ############## Generate the tables to handle the symmetry reduced flip-slice coordinate ##############################
fname1 = "fs_classidx"
fname2 = "fs_sym"
fname3 = "fs_rep"
if not (path.isfile(fname1) and path.isfile(fname2) and path.isfile(fname3)):
    print("creating " + "flipslice sym-tables...")
    flipslice_classidx = ar.array('H', [INVALID] * (N_FLIP * N_SLICE))  # idx -> classidx
    flipslice_sym = ar.array('B', [0] * (N_FLIP * N_SLICE))  # idx -> symmetry
    flipslice_rep = ar.array('L', [0] * N_FLIPSLICE_CLASS)  # classidx -> idx of representant

    classidx = 0
    cc = cb.CubieCube()
    for slc in range(N_SLICE):
        cc.set_slice(slc)
        for flip in range(N_FLIP):
            cc.set_flip(flip)
            idx = N_FLIP * slc + flip
            if (idx + 1) % 4000 == 0:
                print('.', end='', flush=True)
            if (idx + 1) % 320000 == 0:
                print('')

            if flipslice_classidx[idx] == INVALID:
                flipslice_classidx[idx] = classidx
                flipslice_sym[idx] = 0
                flipslice_rep[classidx] = idx
            else:
                continue
            for s in range(N_SYM_D4h):  # conjugate representant by all 16 symmetries
                ss = cb.CubieCube(symCube[inv_idx[s]].cp, symCube[inv_idx[s]].co, symCube[inv_idx[s]].ep,
                                  symCube[inv_idx[s]].eo)  # copy cube
                ss.edge_multiply(cc)
                ss.edge_multiply(symCube[s])  # s^-1*cc*s
                idx_new = N_FLIP * ss.get_slice() + ss.get_flip()
                if flipslice_classidx[idx_new] == INVALID:
                    flipslice_classidx[idx_new] = classidx
                    flipslice_sym[idx_new] = s
            classidx += 1
    print('')
    fh = open(fname1, 'wb')
    flipslice_classidx.tofile(fh)
    fh.close()
    fh = open(fname2, 'wb')
    flipslice_sym.tofile(fh)
    fh.close()
    fh = open(fname3, 'wb')
    flipslice_rep.tofile(fh)
    fh.close()

else:
    print("loading " + "flipslice sym-tables...")

    fh = open(fname1, 'rb')
    flipslice_classidx = ar.array('H')
    flipslice_classidx.fromfile(fh, N_FLIP * N_SLICE)
    fh.close()
    fh = open(fname2, 'rb')
    flipslice_sym = ar.array('B')
    flipslice_sym.fromfile(fh, N_FLIP * N_SLICE)
    fh.close()
    fh = open(fname3, 'rb')
    flipslice_rep = ar.array('L')
    flipslice_rep.fromfile(fh, N_FLIPSLICE_CLASS)
    fh.close()


# ############## Generate the tables to handle the symmetry reduced flip-slicesorted coordinate ########################
if BIG_TABLE:  # load or generate only when BIG_TABLE is defined True
    fname1 = "fs24_classidx"
    fname2 = "fs24_sym"
    fname3 = "fs24_rep"
    if not (path.isfile(fname1) and path.isfile(fname2) and path.isfile(fname3)):
        print("creating " + "flipslicesorted sym-tables...")
        print("This may take about 15 minutes.")
        flipslicesorted_classidx = ar.array('L', [INVALID32] * (N_FLIP * N_SLICE_SORTED))  # idx -> classidx
        flipslicesorted_sym = ar.array('B', [0] * (N_FLIP * N_SLICE_SORTED))  # idx -> symmetry
        flipslicesorted_rep = ar.array('L', [0] * N_FLIPSLICESORTED_CLASS)  # classidx -> idx of representant ANPASSEN

        classidx = 0
        cc = cb.CubieCube()
        for slc in range(N_SLICE_SORTED):
            cc.set_slice_sorted(slc)
            for flip in range(N_FLIP):
                cc.set_flip(flip)
                idx = N_FLIP * slc + flip
                if (idx + 1) % 40000 == 0:
                    print('.', end='', flush=True)
                if (idx + 1) % 3200000 == 0:
                    print('')

                if flipslicesorted_classidx[idx] == INVALID32:
                    flipslicesorted_classidx[idx] = classidx
                    flipslicesorted_sym[idx] = 0
                    flipslicesorted_rep[classidx] = idx
                else:
                    continue
                for s in range(N_SYM_D4h):  # conjugate representant by all 16 symmetries
                    ss = cb.CubieCube(symCube[inv_idx[s]].cp, symCube[inv_idx[s]].co, symCube[inv_idx[s]].ep,
                                      symCube[inv_idx[s]].eo)  # copy cube
                    ss.edge_multiply(cc)
                    ss.edge_multiply(symCube[s])  # s^-1*cc*s
                    idx_new = N_FLIP * ss.get_slice_sorted() + ss.get_flip()
                    if flipslicesorted_classidx[idx_new] == INVALID32:
                        flipslicesorted_classidx[idx_new] = classidx
                        flipslicesorted_sym[idx_new] = s
                classidx += 1

        print('')
        fh = open(fname1, 'wb')
        flipslicesorted_classidx.tofile(fh)
        fh.close()
        fh = open(fname2, 'wb')
        flipslicesorted_sym.tofile(fh)
        fh.close()
        fh = open(fname3, 'wb')
        flipslicesorted_rep.tofile(fh)
        fh.close()

    else:
        print("loading " + "flipslicesorted sym-tables...")

        fh = open(fname1, 'rb')
        flipslicesorted_classidx = ar.array('L')
        flipslicesorted_classidx.fromfile(fh, N_FLIP * N_SLICE_SORTED)
        fh.close()
        fh = open(fname2, 'rb')
        flipslicesorted_sym = ar.array('B')
        flipslicesorted_sym.fromfile(fh, N_FLIP * N_SLICE_SORTED)
        fh.close()
        fh = open(fname3, 'rb')
        flipslicesorted_rep = ar.array('L')
        flipslicesorted_rep.fromfile(fh, N_FLIPSLICESORTED_CLASS)
        fh.close()

########################################################################################################################
