# ##################### The pruning tables cut the search tree during the search. ######################################
# ############ The pruning values are stored modulo 3 for phase 1 table which saves a lot of memory. ###################

import defs
import enums
import moves as mv
import symmetries as sy
import cubie as cb
from os import path
import time
import array as ar

flipslice_twist_depth3 = None  # global variables, initialized during pruning table creation
flipslicesorted_twist_depth3 = None
corner_depth = None


# ####################### functions to extract or set values in the pruning tables #####################################


def get_flipslice_twist_depth3(ix):
    """get_fst_depth3(ix) is *exactly* the number of moves % 3 to solve phase 1 of a cube with index ix"""
    y = flipslice_twist_depth3[ix // 16]
    y >>= (ix % 16) * 2
    return y & 3


def set_flipslice_twist_depth3(ix, value):
    shift = (ix % 16) * 2
    base = ix >> 4
    flipslice_twist_depth3[base] &= ~(3 << shift) & 0xffffffff
    flipslice_twist_depth3[base] |= value << shift


def get_flipslicesorted_twist_depth3(ix):
    """get_fsst_depth3(ix) is *exactly* the number of moves % 3 to solve phase1x24 of a cube with index ix"""
    y = flipslicesorted_twist_depth3[ix // 16]
    y >>= (ix % 16) * 2
    return y & 3


def set_flipslicesorted_twist_depth3(ix, value):
    shift = (ix % 16) * 2
    base = ix >> 4
    flipslicesorted_twist_depth3[base] &= ~(3 << shift) & 0xffffffff
    flipslicesorted_twist_depth3[base] |= value << shift


########################################################################################################################


def create_phase1_prun_table():
    """Create/load the flipslice_twist_depth3 pruning table for phase 1."""
    global flipslice_twist_depth3
    total = defs.N_FLIPSLICE_CLASS * defs.N_TWIST
    fname = "phase1_prun"
    if not path.isfile(fname):
        print("creating " + fname + " table...")
        print('This may take 20 minutes or even longer, depending on the hardware.')

        flipslice_twist_depth3 = ar.array('L', [0xffffffff] * (total // 16 + 1))
        # #################### create table with the symmetries of the flipslice classes ###############################
        cc = cb.CubieCube()
        fs_sym = ar.array('H', [0] * defs.N_FLIPSLICE_CLASS)
        for i in range(defs.N_FLIPSLICE_CLASS):
            if (i + 1) % 1000 == 0:
                print('.', end='', flush=True)
            rep = sy.flipslice_rep[i]
            cc.set_slice(rep // defs.N_FLIP)
            cc.set_flip(rep % defs.N_FLIP)

            for s in range(defs.N_SYM_D4h):
                ss = cb.CubieCube(sy.symCube[s].cp, sy.symCube[s].co, sy.symCube[s].ep,
                                  sy.symCube[s].eo)  # copy cube
                ss.edge_multiply(cc)  # s*cc
                ss.edge_multiply(sy.symCube[sy.inv_idx[s]])  # s*cc*s^-1
                if ss.get_slice() == rep // defs.N_FLIP and ss.get_flip() == rep % defs.N_FLIP:
                    fs_sym[i] |= 1 << s
        print()
        # ##################################################################################################################

        fs_classidx = 0  # value for solved phase 1
        twist = 0
        set_flipslice_twist_depth3(defs.N_TWIST * fs_classidx + twist, 0)
        done = 1
        depth = 0
        backsearch = False
        print('depth:', depth, 'done: ' + str(done) + '/' + str(total))
        while done != total:
            depth3 = depth % 3
            if depth == 9:
                # backwards search is faster for depth >= 9
                print('flipping to backwards search...')
                backsearch = True
            idx = 0
            for fs_classidx in range(defs.N_FLIPSLICE_CLASS):
                if (fs_classidx + 1) % 200 == 0:
                    print('.', end='', flush=True)
                if (fs_classidx + 1) % 16000 == 0:
                    print('')

                twist = 0
                while twist < defs.N_TWIST:

                    # ########## if table entries are not populated, this is very fast: ################################
                    if not backsearch and idx % 16 == 0 and flipslice_twist_depth3[idx // 16] == 0xffffffff \
                            and twist < defs.N_TWIST - 16:
                        twist += 16
                        idx += 16
                        continue
                    ####################################################################################################

                    if backsearch:
                        match = (get_flipslice_twist_depth3(idx) == 3)
                    else:
                        match = (get_flipslice_twist_depth3(idx) == depth3)

                    if match:
                        flipslice = sy.flipslice_rep[fs_classidx]
                        flip = flipslice % 2048  # defs.N_FLIP = 2048
                        slice_ = flipslice >> 11  # // defs.N_FLIP
                        for m in enums.Move:
                            twist1 = mv.twist_move[18 * twist + m]  # defs.N_MOVE = 18
                            flip1 = mv.flip_move[18 * flip + m]
                            slice1 = mv.slice_sorted_move[432 * slice_ + m] // 24  # defs.N_PERM_4 = 24, 18*24 = 432
                            flipslice1 = (slice1 << 11) + flip1
                            fs1_classidx = sy.flipslice_classidx[flipslice1]
                            fs1_sym = sy.flipslice_sym[flipslice1]
                            twist1 = sy.twist_conj[(twist1 << 4) + fs1_sym]
                            idx1 = 2187 * fs1_classidx + twist1  # defs.N_TWIST = 2187
                            if not backsearch:
                                if get_flipslice_twist_depth3(idx1) == 3:  # entry not yet filled
                                    set_flipslice_twist_depth3(idx1, (depth + 1) % 3)
                                    done += 1
                                    # ####symmetric position has eventually more than one representation ###############
                                    sym = fs_sym[fs1_classidx]
                                    if sym != 1:
                                        for j in range(1, 16):
                                            sym >>= 1
                                            if sym % 2 == 1:
                                                twist2 = sy.twist_conj[(twist1 << 4) + j]
                                                # fs2_classidx = fs1_classidx due to symmetry
                                                idx2 = 2187 * fs1_classidx + twist2
                                                if get_flipslice_twist_depth3(idx2) == 3:
                                                    set_flipslice_twist_depth3(idx2, (depth + 1) % 3)
                                                    done += 1
                                    ####################################################################################

                            else:  # backwards search
                                if get_flipslice_twist_depth3(idx1) == depth3:
                                    set_flipslice_twist_depth3(idx, (depth + 1) % 3)
                                    done += 1
                                    break
                    twist += 1
                    idx += 1  # idx = defs.N_TWIST * fs_class + twist

            depth += 1
            print()
            print('depth:', depth, 'done: ' + str(done) + '/' + str(total))

        fh = open(fname, "wb")
        flipslice_twist_depth3.tofile(fh)
    else:
        print("loading " + fname + " table...")
        fh = open(fname, "rb")
        flipslice_twist_depth3 = ar.array('L')
        flipslice_twist_depth3.fromfile(fh, total // 16 + 1)
    fh.close()


def create_phase1x24_prun_table():
    """Create/load the flipslicesorted_twist_depth3 pruning table, 24x the phase1 table."""
    global flipslicesorted_twist_depth3
    total = defs.N_FLIPSLICESORTED_CLASS * defs.N_TWIST
    fname = "phase1x24_prun"
    if not path.isfile(fname):
        print("creating " + fname + " table...")
        print('This may take 8 hours or even longer, depending on the hardware and the Python version.')
        print('Using PyPy instead of CPython gives a table creation speedup by a factor of about 20.')

        flipslicesorted_twist_depth3 = ar.array('L', [0xffffffff] * (total // 16 + 1))
        # #################### create table with the symmetries of the flipslicesorted classes #########################
        cc = cb.CubieCube()
        fs_sym = ar.array('L', [0] * defs.N_FLIPSLICESORTED_CLASS)
        for i in range(defs.N_FLIPSLICESORTED_CLASS):
            if (i + 1) % 24000 == 0:
                print('.', end='', flush=True)
            rep = sy.flipslicesorted_rep[i]
            cc.set_slice_sorted(rep // defs.N_FLIP)
            cc.set_flip(rep % defs.N_FLIP)

            for s in range(defs.N_SYM_D4h):
                ss = cb.CubieCube(sy.symCube[s].cp, sy.symCube[s].co, sy.symCube[s].ep,
                                  sy.symCube[s].eo)  # copy cube
                ss.edge_multiply(cc)  # s*cc
                ss.edge_multiply(sy.symCube[sy.inv_idx[s]])  # s*cc*s^-1
                if ss.get_slice_sorted() == rep // defs.N_FLIP and ss.get_flip() == rep % defs.N_FLIP:
                    fs_sym[i] |= 1 << s
        print()
        # ##################################################################################################################

        fs_classidx = 0  # value for solved phase1x24
        twist = 0
        set_flipslicesorted_twist_depth3(defs.N_TWIST * fs_classidx + twist, 0)
        done = 1
        depth = 0
        backsearch = False
        print('depth:', depth, 'done: ' + str(done) + '/' + str(total))
        while done != total:
            depth3 = depth % 3
            if depth == 10:
                # backwards search is faster for depth >= 9     ANPASSEN!!!
                print('flipping to backwards search...')
                backsearch = True

            idx = 0
            for fs_classidx in range(defs.N_FLIPSLICESORTED_CLASS):
                if (fs_classidx + 1) % 20000 == 0:
                    print('.', end='', flush=True)
                if (fs_classidx + 1) % 1600000 == 0:
                    print('')

                twist = 0
                while twist < defs.N_TWIST:

                    # ########## if table entries are not populated, this is very fast: ################################
                    if not backsearch and idx % 16 == 0 and flipslicesorted_twist_depth3[idx // 16] == 0xffffffff \
                            and twist < defs.N_TWIST - 16:
                        twist += 16
                        idx += 16
                        continue
                    ####################################################################################################

                    if backsearch:
                        match = (get_flipslicesorted_twist_depth3(idx) == 3)
                    else:
                        match = (get_flipslicesorted_twist_depth3(idx) == depth3)

                    if match:
                        flipslicesorted = sy.flipslicesorted_rep[fs_classidx]
                        flip = flipslicesorted % 2048  # defs.N_FLIP = 2048
                        slicesorted = flipslicesorted >> 11  # // defs.N_FLIP
                        for m in enums.Move:
                            twist1 = mv.twist_move[18 * twist + m]  # defs.N_MOVE = 18
                            flip1 = mv.flip_move[18 * flip + m]
                            slicesorted1 = mv.slice_sorted_move[18 * slicesorted + m]
                            flipslicesorted1 = (slicesorted1 << 11) + flip1
                            fs1_classidx = sy.flipslicesorted_classidx[flipslicesorted1]
                            fs1_sym = sy.flipslicesorted_sym[flipslicesorted1]
                            twist1 = sy.twist_conj[(twist1 << 4) + fs1_sym]
                            idx1 = 2187 * fs1_classidx + twist1  # defs.N_TWIST = 2187
                            if not backsearch:
                                if get_flipslicesorted_twist_depth3(idx1) == 3:  # entry not yet filled
                                    set_flipslicesorted_twist_depth3(idx1, (depth + 1) % 3)
                                    done += 1
                                    # ####symmetric position has eventually more than one representation ###############
                                    sym = fs_sym[fs1_classidx]
                                    if sym != 1:
                                        for j in range(1, 16):
                                            sym >>= 1
                                            if sym % 2 == 1:
                                                twist2 = sy.twist_conj[(twist1 << 4) + j]
                                                # fs2_classidx = fs1_classidx due to symmetry
                                                idx2 = 2187 * fs1_classidx + twist2
                                                if get_flipslicesorted_twist_depth3(idx2) == 3:
                                                    set_flipslicesorted_twist_depth3(idx2, (depth + 1) % 3)
                                                    done += 1
                                    ####################################################################################

                            else:  # backwards search
                                if get_flipslicesorted_twist_depth3(idx1) == depth3:
                                    set_flipslicesorted_twist_depth3(idx, (depth + 1) % 3)
                                    done += 1
                                    break
                    twist += 1
                    idx += 1  # idx = defs.N_TWIST * fs_class + twist

            depth += 1
            print()
            print('depth:', depth, 'done: ' + str(done) + '/' + str(total))

        fh = open(fname, "wb")
        flipslicesorted_twist_depth3.tofile(fh)
    else:
        print("loading " + fname + " table...")
        fh = open(fname, "rb")
        flipslicesorted_twist_depth3 = ar.array('L')
        flipslicesorted_twist_depth3.fromfile(fh, total // 16 + 1)
    fh.close()


def create_cornerprun_table():
    """Create/load the corner_depth pruning table. Entry gives the number of moves which are at least necessary
    to restore the corners."""
    fname = "cornerprun"
    global corner_depth
    if not path.isfile(fname):
        print("creating " + fname + " table...")
        corner_depth = ar.array('b', [-1] * (defs.N_CORNERS))
        corners = 0  # value for solved corners
        corner_depth[corners] = 0
        done = 1
        depth = 0
        while done != defs.N_CORNERS:
            for corners in range(defs.N_CORNERS):
                if corner_depth[corners] == depth:
                    for m in enums.Move:
                        corners1 = mv.corners_move[18 * corners + m]
                        if corner_depth[corners1] == -1:  # entry not yet filled
                            corner_depth[corners1] = depth + 1
                            done += 1
                            if done % 1000 == 0:
                                print('.', end='', flush=True)

            depth += 1
        print()
        fh = open(fname, "wb")
        corner_depth.tofile(fh)
    else:
        print("loading " + fname + " table...")
        fh = open(fname, "rb")
        corner_depth = ar.array('b')
        corner_depth.fromfile(fh, defs.N_CORNERS)
    fh.close()


# # array distance computes the new distance from the old_distance i and the new_distance_mod3 j. ######################
# # We need this array because the pruning tables only store the distances mod 3. ######################################
# # The advantage of storing distances mod 3 is that we need only 2 bit per entry to store values 0, 1 or 2 and still
# # have value 3 left to indicate a still empty entry in the tables during table creation.

distance = ar.array('b', [0 for i in range(60)])
for i in range(20):
    for j in range(3):
        distance[3 * i + j] = (i // 3) * 3 + j
        if i % 3 == 2 and j == 0:
            distance[3 * i + j] += 3
        elif i % 3 == 0 and j == 2:
            distance[3 * i + j] -= 3


create_phase1x24_prun_table()
create_cornerprun_table()
