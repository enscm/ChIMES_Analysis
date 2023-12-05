import os
import sys
import numpy as np

def _read_matrix(structure):
    aa = np.loadtxt(structure+"A.txt",dtype='float')
    bb = np.loadtxt(structure+"b.txt",dtype='float')
    os.remove("A.txt")
    os.remove("b.txt")
    return aa, bb

def _reduce_matrix(prefix=None,structure_list=None):
    with open(structure_list, "r") as f:
        lines = f.readlines()

    keep_lines = []
    for line in lines:
        structure = line.strip().split()[0]
        aa, bb = _read_matrix(structure)
        A = aa[-1]
        b = bb[-1]
        np.savetxt(structure + '/' + prefix + 'A.txt', A, delimiter='\t')
        np.savetxt(structure + '/' + prefix + 'b.txt', b, delimiter='\t')

def main():
    print("		USAGE:	reduce_matrix structure_list	")
    print("")
    structure_list = sys.argv[1]
    prefix = sys.argv[2]
    _reduce_matrix(prefix=prefix, structure_list=structure_list)

if __name__ == "__main__":
    main()
