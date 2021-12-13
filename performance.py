from optimal.cubie import CubieCube
import optimal.solver as sv


def test(n):
    """
    Optimally solve n random cubes with information about the solving process
    :param n: THe number of random cubes to solve
    """
    cc = CubieCube()
    for i in range(n):
        cc.randomize()
        fc = cc.to_facelet_cube()
        s = fc.to_string()
        print(s)
        s = sv.solve(s)
        print(s)
        print()


