# ################### The SolverThread class solves implements the two phase algorithm #################################
import face
from defs import N_MOVE, N_FLIP, N_TWIST
import cubie
import symmetries as sy
import coord
import enums as en
import moves as mv
import pruning as pr
import time

solfound = False  # global variable, True if solution is found
nodecount = 0  # number of nodes generated on certain level
sofar = []


def search(UD_flip, RL_flip, FB_flip, UD_twist, RL_twist, FB_twist, UD_slice_sorted,
           RL_slice_sorted, FB_slice_sorted, corners, UD_dist, RL_dist, FB_dist, togo):
    global solfound, nodecount

    if solfound:
        return
    if togo == 0:
        if corners == 0:  # slicesorte should all be 0
            solfound = True
        return

    else:
        for m in en.Move:

            if len(sofar) > 0:
                diff = sofar[-1] // 3 - m // 3
                if diff in [0, 3]:  # successive moves on same face or on same axis with wrong order
                    continue

            nodecount += 1
            ############################################################################################################
            corners1 = mv.corners_move[N_MOVE * corners + m]
            co_dist1 = pr.corner_depth[corners1]
            if co_dist1 >= togo:  # impossible to reach subgroup H in togo - 1 moves
                continue
            ############################################################################################################
            UD_twist1 = mv.twist_move[N_MOVE * UD_twist + m]
            UD_flip1 = mv.flip_move[N_MOVE * UD_flip + m]
            UD_slice_sorted1 = mv.slice_sorted_move[N_MOVE * UD_slice_sorted + m]

            fs = N_FLIP * UD_slice_sorted1 + UD_flip1  # raw new flip_slicesorted coordinate
            # now representation as representant-symmetry pair
            fs_idx = sy.flipslicesorted_classidx[fs]  # index of representant
            fs_sym = sy.flipslicesorted_sym[fs]  # symmetry

            UD_dist1_mod3 = pr.get_flipslicesorted_twist_depth3(
                N_TWIST * fs_idx + sy.twist_conj[(UD_twist1 << 4) + fs_sym])
            UD_dist1 = pr.distance[3 * UD_dist + UD_dist1_mod3]

            if UD_dist1 >= togo:
                continue
            ############################################################################################################
            mrl = sy.conj_move[N_MOVE * 16 + m]  # move viewed from 120° rotated position

            RL_twist1 = mv.twist_move[N_MOVE * RL_twist + mrl]
            RL_flip1 = mv.flip_move[N_MOVE * RL_flip + mrl]
            RL_slice_sorted1 = mv.slice_sorted_move[N_MOVE * RL_slice_sorted + mrl]

            fs = N_FLIP * RL_slice_sorted1 + RL_flip1
            fs_idx = sy.flipslicesorted_classidx[fs]
            fs_sym = sy.flipslicesorted_sym[fs]

            RL_dist1_mod3 = pr.get_flipslicesorted_twist_depth3(
                N_TWIST * fs_idx + sy.twist_conj[(RL_twist1 << 4) + fs_sym])
            RL_dist1 = pr.distance[3 * RL_dist + RL_dist1_mod3]

            if RL_dist1 >= togo:
                continue
            ############################################################################################################
            mfb = sy.conj_move[N_MOVE * 32 + m]  # move viewed from 240° rotated position

            FB_twist1 = mv.twist_move[N_MOVE * FB_twist + mfb]
            FB_flip1 = mv.flip_move[N_MOVE * FB_flip + mfb]
            FB_slice_sorted1 = mv.slice_sorted_move[N_MOVE * FB_slice_sorted + mfb]

            fs = N_FLIP * FB_slice_sorted1 + FB_flip1
            fs_idx = sy.flipslicesorted_classidx[fs]
            fs_sym = sy.flipslicesorted_sym[fs]

            FB_dist1_mod3 = pr.get_flipslicesorted_twist_depth3(
                N_TWIST * fs_idx + sy.twist_conj[(FB_twist1 << 4) + fs_sym])
            FB_dist1 = pr.distance[3 * FB_dist + FB_dist1_mod3]

            if FB_dist1 >= togo:
                continue
            ############################################################################################################
            if UD_dist1 != 0 and UD_dist1 == RL_dist1 and RL_dist1 == FB_dist1:
                if UD_dist1 + 1 >= togo:
                    continue  # due to design of coordinate

            sofar.append(m)
            search(UD_flip1, RL_flip1, FB_flip1, UD_twist1, RL_twist1, FB_twist1, UD_slice_sorted1,
                   RL_slice_sorted1, FB_slice_sorted1, corners1, UD_dist1, RL_dist1, FB_dist1, togo - 1)
            if solfound:
                return
            sofar.pop(-1)


def solve(cubestring):
    """Solve a cube defined by its cube definition string.
     :param cubestring: The format of the string is given in the Facelet class defined in the file enums.py
    """
    global sofar  # the moves of the potential solution maneuver
    global solfound, nodecount
    fc = face.FaceCube()
    s = fc.from_string(cubestring)  # initialize fc
    if s != cubie.CUBE_OK:
        return s  # no valid cubestring, gives invalid facelet cube
    cc = fc.to_cubie_cube()
    s = cc.verify()
    if s != cubie.CUBE_OK:
        return s  # no valid facelet cube, gives invalid cubie cube

    coc = coord.CoordCube(cc)

    togo = max(coc.UD_phasex24_depth, coc.RL_phasex24_depth,
               coc.FB_phasex24_depth)  # lower bound for distance to solved
    solfound = False
    start_time = time.monotonic()
    totnodes = 0
    nodecount = 0
    while not solfound:
        sofar = []
        s_time = time.monotonic()
        totnodes += nodecount
        nodecount = 0
        # cputime = 0
        search(coc.UD_flip, coc.RL_flip, coc.FB_flip, coc.UD_twist, coc.RL_twist, coc.FB_twist,
               coc.UD_slice_sorted, coc.RL_slice_sorted, coc.FB_slice_sorted, coc.corners,
               coc.UD_phasex24_depth, coc.RL_phasex24_depth, coc.FB_phasex24_depth, togo)
        if togo > 12:
            t = time.monotonic() - s_time + 0.0001
            print('depth ' + str(togo) + ' done in ' + str(round(t, 2)) + ' s, ' + str(
                nodecount) + ' nodes generated, ' + 'about ' + str(round(nodecount / t)) + ' nodes/s')
        togo += 1
    print('total time: ' + str(
        round(time.monotonic() - start_time, 2)) + ' s, ' + 'nodes generated: ' + str(
        totnodes + nodecount))
    s = ''
    for m in sofar:
        s += m.name + ' '
    return s + '(' + str(len(s) // 3) + 'f*)'


def solveto(cubestring, goalstring):
    """Solve a cube defined by its cube definition string.
     :param cubestring: The format of the string is given in the Facelet class defined in the file enums.py
     :param goalstring: The definition string of the goalcube
    """
    global sofar  # the moves of the potential solution maneuver
    global solfound, nodecount

    fc0 = face.FaceCube()
    fcg = face.FaceCube()
    s = fc0.from_string(cubestring)
    if s != cubie.CUBE_OK:
        return 'first cube ' + s  # no valid cubestring, gives invalid facelet cube
    s = fcg.from_string(goalstring)
    if s != cubie.CUBE_OK:
        return 'second cube ' + s  # no valid goalstring, gives invalid facelet cube
    cc0 = fc0.to_cubie_cube()
    s = cc0.verify()
    if s != cubie.CUBE_OK:
        return 'first cube ' + s  # no valid facelet cube, gives invalid cubie cube
    ccg = fcg.to_cubie_cube()
    s = ccg.verify()
    if s != cubie.CUBE_OK:
        return 'second cube ' + s  # no valid facelet cube, gives invalid cubie cube
    # cc0 * S = ccg  <=> (ccg^-1 * cc0) * S = Id
    cc = cubie.CubieCube()
    ccg.inv_cubie_cube(cc)
    cc.multiply(cc0)

    coc = coord.CoordCube(cc)

    togo = max(coc.UD_phasex24_depth, coc.RL_phasex24_depth, coc.FB_phasex24_depth)  # lower bound for dist to solved
    solfound = False
    start_time = time.monotonic()
    totnodes = 0
    nodecount = 0
    while not solfound:
        sofar = []
        s_time = time.monotonic()
        totnodes += nodecount
        nodecount = 0
        search(coc.UD_flip, coc.RL_flip, coc.FB_flip, coc.UD_twist, coc.RL_twist, coc.FB_twist,
               coc.UD_slice_sorted, coc.RL_slice_sorted, coc.FB_slice_sorted, coc.corners,
               coc.UD_phasex24_depth, coc.RL_phasex24_depth, coc.FB_phasex24_depth, togo)
        if togo > 12:
            t = time.monotonic() - s_time + 0.0001
            print('depth ' + str(togo) + ' done in ' + str(round(t, 2)) + ' s, ' + str(
                nodecount) + ' nodes generated, ' + 'about ' + str(round(nodecount / t)) + ' nodes/s')
        togo += 1
    print('total time: ' + str(
        round(time.monotonic() - start_time, 2)) + ' s, ' + 'nodes generated: ' + str(
        totnodes + nodecount))
    s = ''
    for m in sofar:
        s += m.name + ' '
    return s + '(' + str(len(s) // 3) + 'f*)'
########################################################################################################################
