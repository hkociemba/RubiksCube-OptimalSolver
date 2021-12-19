from cubie import CubieCube
import solver as sv
import time


def test(n):
    """
    Optimally solve n random cubes with information about the solving process
    :param n: THe number of random cubes to solve
    """
    start_time = time.monotonic()
    cc = CubieCube()
    cnt = [0] * 31
    for i in range(n):
        cc.randomize()
        fc = cc.to_facelet_cube()
        s = fc.to_string()
        print(str(i+1) + '. ' + s)
        s = sv.solve(s)
        print(s)
        print()
        cnt[int(s.split('(')[1].split('f')[0])] += 1
    avr = 0
    for i in range(31):
        avr += i * cnt[i]
    avr /= n
    print('average ' + '%.2f' % avr + ' moves', dict(zip(range(31), cnt)))
    print('total time for ' + str(n) + ' cubes: ' + str(round(time.monotonic() - start_time, 2)) + ' s')
