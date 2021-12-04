# ##### The cube on the coordinate level. It is described by a 3-tuple of natural numbers in phase 1 and phase 2. ######

from os import path
import array as ar

import cubie as cb
import enums
import moves as mv
import pruning as pr
import symmetries as sy
from defs import N_U_EDGES_PHASE2, N_PERM_4, N_CHOOSE_8_4, N_FLIP, N_TWIST, N_UD_EDGES, N_MOVE
from enums import Edge as Ed

SOLVED = 0  # 0 is index of solved state (except for u_edges coordinate)
u_edges_plus_d_edges_to_ud_edges = None  # global variable


class CoordCube:
    """Represent a cube on the coordinate level.

    In phase 1 a state is uniquely determined by the three coordinates flip, twist and slice.
    In phase 2 a state is uniquely determined by the three coordinates corners, ud_edges and slice_sorted.
    """

    def __init__(self, cc: cb.CubieCube = None):  # init CoordCube from CubieCube
        if cc is None:  # ID-Cube
            # The phase 1 slice coordinate is given by slice_sorted // 24

            self.corners = SOLVED  # corner permutation.

            self.UD_twist = SOLVED  # twist of corners relative to UD-axis
            self.UD_flip = SOLVED  # flip of edges relative to UD-axis
            self.UD_slice_sorted = SOLVED  # Position of FR, FL, BL, BR edges (<11880)

            self.RL_twist = SOLVED  # twist of corners relative to RL-axis
            self.RL_flip = SOLVED  # flip of edges relative to RL-axis
            self.RL_slice_sorted = SOLVED  # Position of UF, UB, DB, DF edges (<11880)

            self.FB_twist = SOLVED  # twist of corners relative to FB-axis
            self.FB_flip = SOLVED  # flip of edges
            self.FB_slice_sorted = SOLVED  # Position of UR, DR, DL, UL edges (<11880)

            self.UD_phase1_depth = 0
            self.RL_phase1_depth = 0
            self.FB_phase1_depth = 0

            self.corner_depth = 0
        else:

            self.corners = cc.get_corners()

            self.UD_twist = cc.get_twist()
            self.UD_flip = cc.get_flip()
            self.UD_slice_sorted = cc.get_slice_sorted()

            syc = sy.symCube[16]  # 120° rotation along URF-DBL axis
            ss = cb.CubieCube(syc.cp, syc.co, syc.ep, syc.eo)  # create copy of symCube[16]
            ss.multiply(cc)
            ss.multiply(sy.symCube[32])  # ss = symCube[16]*cc*symCube[16]^-1
            self.RL_twist = ss.get_twist()
            self.RL_flip = ss.get_flip()
            self.RL_slice_sorted = ss.get_slice_sorted()

            syc = sy.symCube[32]  # -120° rotation along URF-DBL axis
            ss = cb.CubieCube(syc.cp, syc.co, syc.ep, syc.eo)  # create copy of symCube[32]
            ss.multiply(cc)
            ss.multiply(sy.symCube[16])  # ss = symCube[32]*cc*symCube[32]^-1
            self.FB_twist = ss.get_twist()
            self.FB_flip = ss.get_flip()
            self.FB_slice_sorted = ss.get_slice_sorted()


            # symmetry reduced flipslice coordinates, coord = sym^-1*rep*sym
            self.UD_flipslice_clsidx = sy.flipslice_classidx[N_FLIP * (self.UD_slice_sorted // N_PERM_4) + self.UD_flip]
            self.UD_flipslice_sym = sy.flipslice_sym[N_FLIP * (self.UD_slice_sorted // N_PERM_4) + self.UD_flip]
            self.UD_flipslice_rep = sy.flipslice_rep[self.UD_flipslice_clsidx]

            self.RL_flipslice_clsidx = sy.flipslice_classidx[N_FLIP * (self.RL_slice_sorted // N_PERM_4) + self.RL_flip]
            self.RL_flipslice_sym = sy.flipslice_sym[N_FLIP * (self.RL_slice_sorted // N_PERM_4) + self.RL_flip]
            self.RL_flipslice_rep = sy.flipslice_rep[self.RL_flipslice_clsidx]

            self.FB_flipslice_clsidx = sy.flipslice_classidx[N_FLIP * (self.FB_slice_sorted // N_PERM_4) + self.FB_flip]
            self.FB_flipslice_sym = sy.flipslice_sym[N_FLIP * (self.FB_slice_sorted // N_PERM_4) + self.FB_flip]
            self.FB_flipslice_rep = sy.flipslice_rep[self.FB_flipslice_clsidx]

            self.UD_phase1_depth = self.get_phase1_depth(0)  # since we store the depth mod 3, retrieving the initial
            self.RL_phase1_depth = self.get_phase1_depth(1)  # absolute depth is a bit involved
            self.FB_phase1_depth = self.get_phase1_depth(2)

            self.corner_depth = pr.corner_depth[self.corners]  # for corners we store just the depth


    def __str__(self):
        s = '(UD_twist: ' + str(self.UD_twist) + ', UD_flip: ' + str(self.UD_flip) + ', UD_slice: ' +\
            str(self.UD_slice_sorted // 24) + ', UD_slice_sorted: ' + str(self.UD_slice_sorted) + ')'
        s = s + '\n' +'UD classidx, sym, rep' + str(self.UD_flipslice_clsidx) + ' ' + \
            str(self.UD_flipslice_sym) + ' ' + str(self.UD_flipslice_rep)

        s = s + '\n' + '(RL_twist: ' + str(self.RL_twist) + ', RL_flip: ' + str(self.RL_flip) + ', RL_slice: ' +\
            str(self.RL_slice_sorted // 24) + ', RL_slice_sorted: ' + str(self.RL_slice_sorted) + ')'
        s = s + '\n' + 'RL classidx, sym, rep' + str(self.RL_flipslice_clsidx) + ' ' + \
            str(self.RL_flipslice_sym) + ' ' + str(self.RL_flipslice_rep)

        s = s + '\n' + '(FB_twist: ' + str(self.FB_twist) + ', FB_flip: ' + str(self.FB_flip) + ', FB_slice: ' +\
            str(self.FB_slice_sorted // 24) + ', FB_slice_sorted: ' + str(self.FB_slice_sorted) + ')'
        s = s + '\n' + ' FB_classidx, sym, rep' + str(self.FB_flipslice_clsidx) + ' ' + \
            str(self.FB_flipslice_sym) + ' ' + str(self.FB_flipslice_rep)

        s = s + '\n' + ', Cornerperm: ' + str(self.corners)

        return s

    def move(self, m):  # new coordinates when applying move m
        self.corners = mv.corners_move[N_MOVE * self.corners + m]

        self.UD_twist = mv.twist_move[N_MOVE * self.UD_twist + m]
        self.UD_flip = mv.flip_move[N_MOVE * self.UD_flip + m]
        self.UD_slice_sorted = mv.slice_sorted_move[N_MOVE * self.UD_slice_sorted + m]

        self.UD_flipslice_clsidx = sy.flipslice_classidx[N_FLIP * (self.UD_slice_sorted // N_PERM_4) + self.UD_flip]
        self.UD_flipslice_sym = sy.flipslice_sym[N_FLIP * (self.UD_slice_sorted // N_PERM_4) + self.UD_flip]
        self.UD_flipslice_rep = sy.flipslice_rep[self.UD_flipslice_clsidx]

        m = sy.conj_move[N_MOVE*16 + m]  # move changes too viewed from 120° rotated position
        self.RL_twist = mv.twist_move[N_MOVE * self.RL_twist + m]
        self.RL_flip = mv.flip_move[N_MOVE * self.RL_flip + m]
        self.RL_slice_sorted = mv.slice_sorted_move[N_MOVE * self.RL_slice_sorted + m]

        self.RL_flipslice_clsidx = sy.flipslice_classidx[N_FLIP * (self.RL_slice_sorted // N_PERM_4) + self.RL_flip]
        self.RL_flipslice_sym = sy.flipslice_sym[N_FLIP * (self.RL_slice_sorted // N_PERM_4) + self.RL_flip]
        self.RL_flipslice_rep = sy.flipslice_rep[self.RL_flipslice_clsidx]

        m = sy.conj_move[N_MOVE*16 + m] # move changes too viewed from 240° rotated position
        self.FB_twist = mv.twist_move[N_MOVE * self.FB_twist + m]
        self.FB_flip = mv.flip_move[N_MOVE * self.FB_flip + m]
        self.FB_slice_sorted = mv.slice_sorted_move[N_MOVE * self.FB_slice_sorted + m]

        self.FB_flipslice_clsidx = sy.flipslice_classidx[N_FLIP * (self.FB_slice_sorted // N_PERM_4) + self.FB_flip]
        self.FB_flipslice_sym = sy.flipslice_sym[N_FLIP * (self.FB_slice_sorted // N_PERM_4) + self.FB_flip]
        self.FB_flipslice_rep = sy.flipslice_rep[self.FB_flipslice_clsidx]

        self.UD_phase1_depth = self.get_phase1_depth(0)  # since we store the depth mod 3, retrieving the initial
        self.RL_phase1_depth = self.get_phase1_depth(1)  # absolute depth is a bit involved
        self.FB_phase1_depth = self.get_phase1_depth(2)

        self.corner_depth = pr.corner_depth[self.corners]  # for corners we store just the depth


    def get_phase1_depth(self, position):
        if position == 0:
            slice_ = self.UD_slice_sorted// N_PERM_4
            flip = self.UD_flip
            twist = self.UD_twist
        elif position == 1:
            slice_ = self.RL_slice_sorted// N_PERM_4
            flip = self.RL_flip
            twist = self.RL_twist
        else:
            slice_ = self.FB_slice_sorted// N_PERM_4
            flip = self.FB_flip
            twist = self.FB_twist

        flipslice = N_FLIP * slice_  + flip
        classidx = sy.flipslice_classidx[flipslice]
        sym = sy.flipslice_sym[flipslice]
        depth_mod3 = pr.get_flipslice_twist_depth3(N_TWIST * classidx + sy.twist_conj[(twist << 4) + sym])

        depth = 0
        while flip != SOLVED or slice_ != SOLVED or twist != SOLVED:
            if depth_mod3 == 0:
                depth_mod3 = 3
            for m in enums.Move:  # we can use the same m in all 3 rotational positions
                twist1 = mv.twist_move[N_MOVE * twist + m]
                flip1 = mv.flip_move[N_MOVE * flip + m]
                slice1 = mv.slice_sorted_move[N_MOVE * slice_ * N_PERM_4 + m] // N_PERM_4  # we may set perm=0 here
                flipslice1 = N_FLIP * slice1 + flip1
                classidx1 = sy.flipslice_classidx[flipslice1]
                sym = sy.flipslice_sym[flipslice1]
                if pr.get_flipslice_twist_depth3(
                        N_TWIST * classidx1 + sy.twist_conj[(twist1 << 4) + sym]) == depth_mod3 - 1:
                    depth += 1
                    twist = twist1
                    flip = flip1
                    slice_ = slice1
                    depth_mod3 -= 1
                    break
        return depth
########################################################################################################################

