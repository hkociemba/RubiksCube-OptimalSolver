import face  # though not used in this module we get circular when we omit the import
from cubie import CubieCube
import solver as sv


# ######################################################################################################################
# ######IMPORTANT#####IMPORTANT#####SET BIG_TABLE True/False in defs.py!#####IMPORTANT#####IMPORTANT#####IMPORTANT######
########################################################################################################################



cc = CubieCube()
cc.randomize()
fc = cc.to_facelet_cube()
fl = fc.to_string()  # fl holds the cube definition string. For the format see enums.py
print('Solve random cube with cube definition string ' + fl)
print(sv.solve(fl))

# random cubes used for performance testing

#f1='FLLUUBUUDLDUFRRBRLRFFUFDRLUDBRLDBRDBLBFFLLDFFBDUUBRDRB'
#f2='BRBBUFFLLFLDBRDFLFRDDFFRBFRDDULDBBUURDDULULURLFURBRLBU'
#f3='DBLRUULUUFFBLRDFLBBRLUFFDFRFDUDDUBBRLFURLBUBRDRFLBDDLR'
#f4='UFBDULRLULDDRRRFDUBBBLFFLFLUUDRDFRBRRBDRLUFBFLLFUBDBUD'
#f5='BLURULUBBDFRRRBDDDRDRRFFFURLFFUDLDDLUUFLLDFBUBBLRBUBFL'
#f6='FRRRUFDBFLLBURBRBDLUUUFRDDFBRDDDDLDBUBFLLFULLUFRLBURFB'
#f7='FBBDUFRDDBUURRRLFUDBLRFBBLUDFBUDRDULUFFDLUFLRRLRDBLFBL'
#f8='UDFDULRFRBUUDRRLLLFRDRFBFRBDBDBDFDUUBFULLDRULLLRUBBBFF'
#print('Solve random cube with cube definition string ' + f3)
#print(sv.solve(f3))