import numpy as np
import sys

def _combine_matrix(prefix=None,structure_list=None):

    with open(structure_list, "r") as f:
        lines = f.readlines()

    A = []
    b = []
    for line in lines:
        structure = line.strip().split()[0]

        try:
            with open(structure+'/'+prefix + "A.txt") as f:
                for l in f:
                    a = l.strip().split()
                    A.append([float(ele) for ele in a])
            with open(structure+'/'+prefix + "b.txt") as f:
                for l in f:
                    bb = l.strip().split()
                    b.append([float(ele) for ele in bb])
        except Exception as e:
            print(f"Error reading from {structure}: {e}")

    A = np.array(A)
    b = np.array(b)
    np.savetxt(f'combined_{prefix}A.txt', A, delimiter='\t')
    np.savetxt(f'combined_{prefix}b.txt', b, delimiter='\t')


def main():
    if len(sys.argv) != 3:
        print("USAGE: python combine_matrix.py structure_list prefix")
        return

    structure_list = sys.argv[1]
    prefix = sys.argv[2]
    _combine_matrix(prefix=prefix, structure_list=structure_list)

if __name__ == "__main__":
    main()
