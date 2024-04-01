import os
import sys
import numpy as np
import shutil

"""
This script remove the  chimes_lsq generated force info from A.txt and b.txt matrix, 
which results in a force weight = 0 situation, the reduced matrix then can be "added-up" frame-by-frame through 'combine_matrix.py'.
"""

def _read_matrix(structure):
    aa = np.loadtxt(structure+'/' + "A.txt",ndmin=1)
    bb = np.loadtxt(structure+'/' + "b.txt", ndmin=0)
    os.remove(os.path.join(structure, "A.txt"))
    os.remove(os.path.join(structure, "b.txt"))
    return aa, bb

def _reduce_matrix(prefix=None,structure_list=None):
    with open(structure_list, "r") as f:
        lines = f.readlines()

    for line in lines:
        structure = line.strip().split()[0]
        root = os.getcwd()
        shutil.copy('fm_setup.in', structure)
        os.chdir(structure)
        os.system('bash /home/qwang01/bash_chimes.sh')
        os.chdir(root)
        aa, bb = _read_matrix(structure)
        A = aa[-1:]
        b = bb[-1]
        np.savetxt(structure + '/' + prefix + 'A.txt', A, delimiter='\t')
        b = np.array([b])
        np.savetxt(structure + '/' + prefix + 'b.txt', b, delimiter='\t')

def main():
    if len(sys.argv) != 3:
        print("USAGE: python reduce_matrix.py structure_list prefix")
        return

    structure_list = sys.argv[1]
    prefix = sys.argv[2]
    _reduce_matrix(prefix=prefix, structure_list=structure_list)

if __name__ == "__main__":
    main()
