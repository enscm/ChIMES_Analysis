import os
import numpy as np

def _read_matrix(structure):
    aa = np.loadtxt(structure+"A.txt",ndmin=1)
    bb = np.loadtxt(structure+"b.txt",ndmin=0)
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
        with open(structure+'/b-labeled.txt', 'r') as f:
            b_lines = f.readlines()
            for i, b_line in enumerate(b_lines, 0):
                if b_line.startswith('+1'):
                    keep_lines.append(i)
                    A = aa[keep_lines]
                    b = bb[keep_lines]
        np.savetxt(structure + '/' + prefix + 'A.txt', A, delimiter='\t')
        np.savetxt(structure + '/' + prefix + 'b.txt', b, delimiter='\t')

def main():
    print("		USAGE:	reduce_matrix structure_list	")
    print("")

if __name__ == "__main__":
    main()
