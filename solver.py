# ################### The SolverThread class solves implements the two phase algorithm #################################
import face
from defs import N_MOVE, N_FLIP, N_TWIST, N_PERM_4
import threading as thr
import cubie
import symmetries as sy
import coord
import enums as en
import moves as mv
import pruning as pr
import time

solfound = False  # Globale Variable, True wenn Lösung gefunden

def search(UD_flip, RL_flip, FB_flip, UD_twist, RL_twist, FB_twist, UD_slice_sorted,\
           RL_slice_sorted, FB_slice_sorted, UD_dist, RL_dist, FB_dist, togo):
    global solfound
    if togo == 0:  # cube solved
        solfound = True
        return

    else:
        for m in en.Move:

            if len(sofar) > 0:
                diff = sofar[-1] // 3 - m // 3
                if diff in [0, 3]:  # successive moves on same face or on same axis with wrong order
                    continue
        ################################################################################################################
            UD_twist1 = mv.twist_move[N_MOVE * UD_twist + m]
            UD_flip1= mv.flip_move[N_MOVE * UD_flip + m]
            UD_slice_sorted1= mv.slice_sorted_move[N_MOVE * UD_slice_sorted + m]

            fs = N_FLIP * (UD_slice_sorted1 // N_PERM_4) + UD_flip1  # raw new flip_slice coordinate
            # now representation as representant-symmetry pair
            fs_idx = sy.flipslice_classidx[fs]  # index of representant
            fs_sym = sy.flipslice_sym[fs]   # symmetry

            UD_dist1_mod3 = pr.get_flipslice_twist_depth3(N_TWIST * fs_idx + sy.twist_conj[(UD_twist1 << 4) + fs_sym])
            UD_dist1 = pr.distance[3 * UD_dist + UD_dist1_mod3]
        ################################################################################################################
            mrl = sy.conj_move[m, 16]  # move viewed from 120° rotated position
            RL_twist1 = mv.twist_move[N_MOVE * RL_twist + mrl]
            RL_flip1 = mv.flip_move[N_MOVE * RL_flip + mrl]
            RL_slice_sorted1 = mv.slice_sorted_move[N_MOVE * RL_slice_sorted + mrl]

            fs = N_FLIP * (RL_slice_sorted1 // N_PERM_4) + RL_flip1
            fs_idx = sy.flipslice_classidx[fs]
            fs_sym = sy.flipslice_sym[fs]

            RL_dist1_mod3 = pr.get_flipslice_twist_depth3(N_TWIST * fs_idx + sy.twist_conj[(RL_twist1 << 4) + fs_sym])
            RL_dist1 = pr.distance[3 * RL_dist + RL_dist1_mod3]
        ################################################################################################################
            mfb = sy.conj_move[m, 32]  # move viewed from 240° rotated position
            FB_twist1 = mv.twist_move[N_MOVE * FB_twist + mfb]
            FB_flip1 = mv.flip_move[N_MOVE * FB_flip + mfb]
            FB_slice_sorted1 = mv.slice_sorted_move[N_MOVE * FB_slice_sorted + mfb]

            fs = N_FLIP * (FB_slice_sorted1 // N_PERM_4) + FB_flip1
            fs_idx = sy.flipslice_classidx[fs]
            fs_sym = sy.flipslice_sym[fs]

            FB_dist1_mod3 = pr.get_flipslice_twist_depth3(N_TWIST * fs_idx + sy.twist_conj[(FB_twist1 << 4) + fs_sym])
            FB_dist1 = pr.distance[3 * FB_dist + FB_dist1_mod3]
        ################################################################################################################
            dist_new = max(UD_dist1, RL_dist1, FB_dist1)
            if UD_dist1 != 0 and UD_dist1 == RL_dist1 and RL_dist1 == FB_dist1:
                dist_new += 1

            if dist_new >= togo:  # impossible to reach subgroup H in togo_phase1 - 1 moves
                continue

            sofar.append(m)
            search(UD_flip1, RL_flip1, FB_flip1, UD_twist1, RL_twist1, FB_twist1, UD_slice_sorted1, \
                   RL_slice_sorted1, FB_slice_sorted1, UD_dist1, RL_dist1, FB_dist1, togo - 1)
            if solfound:
                return
            sofar.pop(-1)




def solve(cubestring):
    """Solve a cube defined by its cube definition string.
     :param cubestring: The format of the string is given in the Facelet class defined in the file enums.py
    """
    global sofar  # the moves of the potential solution maneuver
    global solfound
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
    while not solfound:
        sofar = []
        search(coc.UD_flip, coc.RL_flip, coc.FB_flip, coc.UD_twist, coc.RL_twist, coc.FB_twist, \
               coc.UD_slice_sorted, coc.RL_slice_sorted, coc.FB_slice_sorted, \
               coc.UD_phase1_depth, coc.RL_phase1_depth, coc.FB_phase1_depth,  togo)
        togo += 1
    s = ''
    for m in sofar:
        s += m.name + ' '
    return s + '(' + str(len(s) // 3) + 'f)'


########################################################################################################################

def solveto(cubestring, goalstring, max_length=20, timeout=3):
    """Solve a cube defined by cubstring to a position defined by goalstring.
     :param cubestring: The format of the string is given in the Facelet class defined in the file enums.py
     :param goalstring: The format of the string is given in the Facelet class defined in the file enums.py
     :param max_length: The function will return if a maneuver of length <= max_length has been found
     :param timeout: If the function times out, the best solution found so far is returned. If there has not been found
     any solution yet the computation continues until a first solution appears.
    """
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

    my_threads = []
    s_time = time.monotonic()

    # these mutable variables are modidified by all six threads
    s_length = [999]
    solutions = []
    terminated = thr.Event()
    terminated.clear()
    syms = cc.symmetries()
    if len(list({16, 20, 24, 28} & set(syms))) > 0:  # we have some rotational symmetry along a long diagonal
        tr = [0, 3]  # so we search only one direction and the inverse
    else:
        tr = range(6)  # This means search in 3 directions + inverse cube
    if len(list(set(range(48, 96)) & set(syms))) > 0:  # we have some antisymmetry so we do not search the inverses
        tr = list(filter(lambda x: x < 3, tr))
    for i in tr:
        th = SolverThread(cc, i % 3, i // 3, max_length, timeout, s_time, solutions, terminated, [999])
        my_threads.append(th)
        th.start()
    for t in my_threads:
        t.join()  # wait until all threads have finished
    s = ''
    if len(solutions) > 0:
        for m in solutions[-1]:  # the last solution is the shortest
            s += m.name + ' '
    return s + '(' + str(len(s) // 3) + 'f)'
########################################################################################################################
