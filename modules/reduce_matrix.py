import os
import sys
import numpy as np

"""
This script reduce the chimes_lsq generated A.txt and b.txt matrix (the huge energies and 3-times repeated forces lines are removed, 
which results in a energy weight = 0 situation with much smaller cpu demands in following chimes parameter generation step and allows using thousands bigger dataset volume.).
Those reduced matrix then can be "added-up" frame-by-frame through 'combine_matrix.py'.
"""


def _read_matrix(structure):
    aa = np.loadtxt(structure+'/' + "A.txt",ndmin=1)
    bb = np.loadtxt(structure+'/' + "b.txt", ndmin=1)
    os.remove(structure+'/' + "A.txt")
    os.remove(structure+'/' + "b.txt")
    return aa, bb

def _reduce_matrix(prefix=None,structure_list=None):
    with open(structure_list, "r") as f:
        lines = f.readlines()

    for line in lines:
        structure = line.strip().split()[0]
        aa, bb = _read_matrix(structure)
        A = aa[-1:]
        b = bb[-1:]
        np.savetxt(structure + '/' + prefix + 'A.txt', A, delimiter='\t')
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
