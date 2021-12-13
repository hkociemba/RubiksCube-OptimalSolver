import face  # though not used in this module we get circular when we omit the import
from cubie import CubieCube
import solver as sv

cc = CubieCube()
cc.randomize()
fc = cc.to_facelet_cube()
fl = fc.to_string()  # fl holds the cube definition string. For the format see enums.py
#print('Solve random cube with cube definition string ' + fl)
# print(sv.solve(fl))


# random cubes used for performance testing

f01 = 'FLLUUBUUDLDUFRRBRLRFFUFDRLUDBRLDBRDBLBFFLLDFFBDUUBRDRB'
f02 = 'BRBBUFFLLFLDBRDFLFRDDFFRBFRDDULDBBUURDDULULURLFURBRLBU'
f03 = 'DBLRUULUUFFBLRDFLBBRLUFFDFRFDUDDUBBRLFURLBUBRDRFLBDDLR'
f04 = 'UFBDULRLULDDRRRFDUBBBLFFLFLUUDRDFRBRRBDRLUFBFLLFUBDBUD'
f05 = 'BLURULUBBDFRRRBDDDRDRRFFFURLFFUDLDDLUUFLLDFBUBBLRBUBFL'
f06 = 'FRRRUFDBFLLBURBRBDLUUUFRDDFBRDDDDLDBUBFLLFULLUFRLBURFB'
f07 = 'FBBDUFRDDBUURRRLFUDBLRFBBLUDFBUDRDULUFFDLUFLRRLRDBLFBL'
f08 = 'UDFDULRFRBUUDRRLLLFRDRFBFRBDBDBDFDUUBFULLDRULLLRUBBBFF'
f09 = 'BDFBURLUDFBLRRUBDFDLRRFDRRRUFDFDLLBRULBULUFLBDFLFBBUDU'
f10 = 'RUUFUBFRRFUBBRRBLLRFULFDFDRLFDLDDFRBUUDULBLFULLBBBRDDD'

flist = [f01, f02, f03, f04, f05, f06, f07, f08, f09, f10]
for f in flist:
    print('Solve random cube with cube definition string ' + f)
    print(sv.solve(f))
