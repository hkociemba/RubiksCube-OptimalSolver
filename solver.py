# ################### The SolverThread class solves implements the two phase algorithm #################################
import face
from defs import N_MOVE, N_FLIP, N_TWIST, N_PERM_4, BIG_TABLE
import cubie
import symmetries as sy
import coord
import enums as en
import moves as mv
import pruning as pr
import time

solfound = False  # global variable, True if solution is found
nodecount = 0  # number of nodes generated on certain level
cputime = 0  # optional for profiling purpose


def search(UD_flip, RL_flip, FB_flip, UD_twist, RL_twist, FB_twist, UD_slice_sorted, \
           RL_slice_sorted, FB_slice_sorted, corners, UD_dist, RL_dist, FB_dist, togo):
    global solfound, nodecount, cputime

    if solfound:
        return
    if togo == 0:
        if UD_slice_sorted == 0 and RL_slice_sorted == 0 and FB_slice_sorted == 0 and corners == 0:
            solfound = True
        return

    else:
        for m in en.Move:

            if len(sofar) > 0:
                diff = sofar[-1] // 3 - m // 3
                if diff in [0, 3]:  # successive moves on same face or on same axis with wrong order
                    continue

            nodecount += 1
            ################################################################################################################
            UD_twist1 = mv.twist_move[N_MOVE * UD_twist + m]
            UD_flip1 = mv.flip_move[N_MOVE * UD_flip + m]
            UD_slice_sorted1 = mv.slice_sorted_move[N_MOVE * UD_slice_sorted + m]

            fs = N_FLIP * (UD_slice_sorted1 // N_PERM_4) + UD_flip1  # raw new flip_slice coordinate
            # now representation as representant-symmetry pair
            fs_idx = sy.flipslice_classidx[fs]  # index of representant
            fs_sym = sy.flipslice_sym[fs]  # symmetry

            UD_dist1_mod3 = pr.get_flipslice_twist_depth3(N_TWIST * fs_idx + sy.twist_conj[(UD_twist1 << 4) + fs_sym])
            UD_dist1 = pr.distance[3 * UD_dist + UD_dist1_mod3]

            ################################################################################################################
            mrl = sy.conj_move[N_MOVE * 16 + m]  # move viewed from 120° rotated position

            RL_twist1 = mv.twist_move[N_MOVE * RL_twist + mrl]
            RL_flip1 = mv.flip_move[N_MOVE * RL_flip + mrl]
            RL_slice_sorted1 = mv.slice_sorted_move[N_MOVE * RL_slice_sorted + mrl]

            fs = N_FLIP * (RL_slice_sorted1 // N_PERM_4) + RL_flip1
            fs_idx = sy.flipslice_classidx[fs]
            fs_sym = sy.flipslice_sym[fs]

            RL_dist1_mod3 = pr.get_flipslice_twist_depth3(N_TWIST * fs_idx + sy.twist_conj[(RL_twist1 << 4) + fs_sym])
            RL_dist1 = pr.distance[3 * RL_dist + RL_dist1_mod3]
            ################################################################################################################
            mfb = sy.conj_move[N_MOVE * 32 + m]  # move viewed from 240° rotated position

            FB_twist1 = mv.twist_move[N_MOVE * FB_twist + mfb]
            FB_flip1 = mv.flip_move[N_MOVE * FB_flip + mfb]
            FB_slice_sorted1 = mv.slice_sorted_move[N_MOVE * FB_slice_sorted + mfb]

            fs = N_FLIP * (FB_slice_sorted1 // N_PERM_4) + FB_flip1
            fs_idx = sy.flipslice_classidx[fs]
            fs_sym = sy.flipslice_sym[fs]
            FB_dist1_mod3 = pr.get_flipslice_twist_depth3(N_TWIST * fs_idx + sy.twist_conj[(FB_twist1 << 4) + fs_sym])
            FB_dist1 = pr.distance[3 * FB_dist + FB_dist1_mod3]
            ################################################################################################################

            corners1 = mv.corners_move[N_MOVE * corners + m]
            co_dist1 = pr.corner_depth[corners1]

            dist_new = max(UD_dist1, RL_dist1, FB_dist1)
            if UD_dist1 != 0 and UD_dist1 == RL_dist1 and RL_dist1 == FB_dist1:
                dist_new += 1  # not obvious but true
            dist_new = max(dist_new, co_dist1)

            if dist_new >= togo:  # impossible to reach subgroup H in togo_phase1 - 1 moves
                continue
            # timex = time.perf_counter()
            sofar.append(m)
            # cputime += (time.perf_counter() - timex)
            search(UD_flip1, RL_flip1, FB_flip1, UD_twist1, RL_twist1, FB_twist1, UD_slice_sorted1,
                   RL_slice_sorted1, FB_slice_sorted1, corners1, UD_dist1, RL_dist1, FB_dist1, togo - 1)
            if solfound:
                return
            sofar.pop(-1)


def solve1(cubestring):
    """Solve a cube defined by its cube definition string.
     :param cubestring: The format of the string is given in the Facelet class defined in the file enums.py
    """
    global sofar  # the moves of the potential solution maneuver
    global solfound, nodecount, cputime
    fc = face.FaceCube()
    s = fc.from_string(cubestring)  # initialize fc
    if s != cubie.CUBE_OK:
        return s  # no valid cubestring, gives invalid facelet cube
    cc = fc.to_cubie_cube()
    s = cc.verify()
    if s != cubie.CUBE_OK:
        return s  # no valid facelet cube, gives invalid cubie cube

    coc = coord.CoordCube(cc)

    togo = max(coc.UD_phase1_depth, coc.RL_phase1_depth, coc.FB_phase1_depth)  # lower bound for distance to solved
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
               coc.UD_phase1_depth, coc.RL_phase1_depth, coc.FB_phase1_depth, togo)
        print('depth ' + str(togo) + ' done in ' + str(round(time.monotonic() - s_time, 2)) + ' s')
        if togo > 12:
            print('nodes generated in depth ' + str(togo) + ': ' + str(nodecount) + ', about ' + str(
                round(nodecount / (time.monotonic() - s_time))) + ' nodes/s')
            # print(cputime)
        togo += 1
    s = ''
    print('total time: ' + str(round(time.monotonic() - start_time, 2)) + ' s')
    print('total number of nodes generated: ' + str(totnodes + nodecount))
    print('average node generation: ' + str(
        round((totnodes + nodecount) / (time.monotonic() - start_time), 2)) + ' nodes/s')
    for m in sofar:
        s += m.name + ' '
    return s + '(' + str(len(s) // 3) + 'f)'


def solveto1(cubestring, goalstring):
    """Solve a cube defined by its cube definition string.
     :param cubestring: The format of the string is given in the Facelet class defined in the file enums.py
    """
    global sofar  # the moves of the potential solution maneuver
    global solfound, nodecount, cputime

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

    togo = max(coc.UD_phase1_depth, coc.RL_phase1_depth, coc.FB_phase1_depth)  # lower bound for distance to solved
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
               coc.UD_phase1_depth, coc.RL_phase1_depth, coc.FB_phase1_depth, togo)
        print('depth ' + str(togo) + ' done in ' + str(round(time.monotonic() - s_time, 2)) + ' s')
        if togo > 12:
            print('nodes generated in depth ' + str(togo) + ': ' + str(nodecount) + ', about ' + str(
                round(nodecount / (time.monotonic() - s_time))) + ' nodes/s')
            # print(cputime)
        togo += 1
    print('total time: ' + str(round(time.monotonic() - start_time, 2)) + ' s')
    print('total number of nodes generated: ' + str(totnodes + nodecount))
    print('average node generation: ' + str(
        round((totnodes + nodecount) / (time.monotonic() - start_time), 2)) + ' nodes/s')
    s = ''
    for m in sofar:
        s += m.name + ' '
    return s + '(' + str(len(s) // 3) + 'f)'


def search24(UD_flip, RL_flip, FB_flip, UD_twist, RL_twist, FB_twist, UD_slice_sorted, \
             RL_slice_sorted, FB_slice_sorted, corners, UD_dist, RL_dist, FB_dist, togo):
    global solfound, nodecount, cputime

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
            ################################################################################################################
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

            ################################################################################################################
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
            ################################################################################################################
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
            ################################################################################################################

            corners1 = mv.corners_move[N_MOVE * corners + m]
            co_dist1 = pr.corner_depth[corners1]

            dist_new = max(UD_dist1, RL_dist1, FB_dist1)
            if UD_dist1 != 0 and UD_dist1 == RL_dist1 and RL_dist1 == FB_dist1:
                dist_new += 1  # not obvious but true
            dist_new = max(dist_new, co_dist1)

            if dist_new >= togo:  # impossible to reach subgroup H in togo_phase1 - 1 moves
                continue
            # timex = time.perf_counter()
            sofar.append(m)
            # cputime += (time.perf_counter() - timex)
            search24(UD_flip1, RL_flip1, FB_flip1, UD_twist1, RL_twist1, FB_twist1, UD_slice_sorted1,
                     RL_slice_sorted1, FB_slice_sorted1, corners1, UD_dist1, RL_dist1, FB_dist1, togo - 1)
            if solfound:
                return
            sofar.pop(-1)


def solve24(cubestring):
    """Solve a cube defined by its cube definition string.
     :param cubestring: The format of the string is given in the Facelet class defined in the file enums.py
    """
    global sofar  # the moves of the potential solution maneuver
    global solfound, nodecount, cputime
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
        search24(coc.UD_flip, coc.RL_flip, coc.FB_flip, coc.UD_twist, coc.RL_twist, coc.FB_twist, \
                 coc.UD_slice_sorted, coc.RL_slice_sorted, coc.FB_slice_sorted, coc.corners, \
                 coc.UD_phasex24_depth, coc.RL_phasex24_depth, coc.FB_phasex24_depth, togo)
        print('depth ' + str(togo) + ' done in ' + str(round(time.monotonic() - s_time, 2)) + ' s')
        if togo > 12:
            print('nodes generated in depth ' + str(togo) + ': ' + str(nodecount) + ', about ' + str(
                round(nodecount / (time.monotonic() - s_time))) + ' nodes/s')
            # print(cputime)
        togo += 1
    print('total time: ' + str(round(time.monotonic() - start_time, 2)) + ' s')
    print('total number of nodes generated: ' + str(totnodes + nodecount))
    print('average node generation: ' + str(
        round((totnodes + nodecount) / (time.monotonic() - start_time), 2)) + ' nodes/s')
    s = ''
    for m in sofar:
        s += m.name + ' '
    return s + '(' + str(len(s) // 3) + 'f)'


def solveto24(cubestring, goalstring):
    """Solve a cube defined by its cube definition string.
     :param cubestring: The format of the string is given in the Facelet class defined in the file enums.py
    """
    global sofar  # the moves of the potential solution maneuver
    global solfound, nodecount, cputime

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
        # cputime = 0
        search24(coc.UD_flip, coc.RL_flip, coc.FB_flip, coc.UD_twist, coc.RL_twist, coc.FB_twist, \
                 coc.UD_slice_sorted, coc.RL_slice_sorted, coc.FB_slice_sorted, coc.corners, \
                 coc.UD_phasex24_depth, coc.RL_phasex24_depth, coc.FB_phasex24_depth, togo)
        print('depth ' + str(togo) + ' done in ' + str(round(time.monotonic() - s_time, 2)) + ' s')
        if togo > 12:
            print('nodes generated in depth ' + str(togo) + ': ' + str(nodecount) + ', about ' + str(
                round(nodecount / (time.monotonic() - s_time))) + ' nodes/s')
            # print(cputime)
        togo += 1
    print('total time: ' + str(round(time.monotonic() - start_time, 2)) + ' s')
    print('total number of nodes generated: ' + str(totnodes + nodecount))
    print('average node generation: ' + str(
        round((totnodes + nodecount) / (time.monotonic() - start_time), 2)) + ' nodes/s')
    s = ''
    for m in sofar:
        s += m.name + ' '
    return s + '(' + str(len(s) // 3) + 'f)'


def solve(cubestring):
    if BIG_TABLE:
        s = solve24(cubestring)
    else:
        s = solve1(cubestring)
    return s


def solveto(cubestring, goalstring):
    if BIG_TABLE:
        s = solveto24(cubestring, goalstring)
    else:
        s = solveto1(cubestring, goalstring)
    return s

########################################################################################################################
