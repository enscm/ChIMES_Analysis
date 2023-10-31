import os
from ase.io.vasp import read_vasp_out, read_vasp
import numpy as np
from os.path import exists
import json
import sys

def traj(structure_list=None):
    """ This function reads energy and force information either from OUTCAR if exists
    or from size-reduced file "outcar" (for energy) and "force" (for force info);
    and read other geometrical information.
    then construct a trajectory file with ChiMES format, named as "one_frame.xyzf"
    """
    eVtoKcal = 23.06035
    f_convert = 0.194469064593167E-01  # convert eV/A to Hatree/Bohr

    with open('atomic_energy_list.json', "r") as file:
        data = json.load(file)
    # Extract the dictionaries
    atom_dft = data["atom_dft"]
    atom_dftb = data["atom_dftb"]

    f = open(structure_list,'r')
    lines=f.readlines()
    f.close()

    for line in lines:
        structure = line.strip().split()[0]

        if not exists(structure+'/OUTCAR'):
            info = read_vasp('/POSCAR')
            nb = len(info.get_positions())
            a = info.get_cell()
            cell = [a[0][0], a[0][1], a[0][2], a[1][0], a[1][1], a[1][2], a[2][0], a[2][1], a[2][2]]
            symbols = info.get_chemical_symbols()
            positions = info.get_positions()
            # Count the number of each atom symbol
            atom_count = {}
            for atom in info:
                symbol = atom.symbol
                if symbol in atom_count:
                    atom_count[symbol] += 1
                else:
                    atom_count[symbol] = 1
            match_B = 'Extrapolated to 0'
            match_C = 'Total Forces'
            forces_dftb = []
            forces = []
            with open(structure+'/force') as f:
                lines = f.readlines()[0:nb]
                for _ in range(len(lines)):
                    pos = lines[_].strip().split()
                    force = [float(pos[0]), float(pos[1]), float(pos[2])]
                    forces.append(force)

            with open(structure+'/outcar') as f:
                E_tot_DFT = float(f.readlines()[0].strip().split()[-1])

            with open(structure+'/detailed.out') as f:
                for num, line in enumerate(f, 0):
                    if match_B in line:
                        tot = float(line.strip().split()[5])
                    if match_C in line:
                        lines = f.readlines()[0:nb]
                        for _ in range(len(lines)):
                            pos = lines[_].strip().split()
                            fdftb = [float(pos[1]), float(pos[2]), float(pos[3])]
                            forces_dftb.append(fdftb)
            edft = 0
            edftb = 0
            for s, n in atom_count.items():
                e0 = atom_dft[s] * n
                e1 = atom_dftb[s] * n
                edft += e0
                edftb += e1
            dft = (E_tot_DFT - edft) * eVtoKcal
            dftb = (tot - edftb) * eVtoKcal

            input = open(structure+'/one_frame.xyzf', 'w')

            input.write(str(nb) + '\n' + 'NON_ORTHO ' + str(cell).replace(",", "")[1:-1] + ' ' + str(dft - dftb) + '\n')

            forces_dftb = np.array(forces_dftb)
            forces = np.array(forces)
            force_diffs = forces - forces_dftb

            for _ in range(0, nb):
                symbol = symbols[_]
                position = positions[_].tolist()
                force_diff = force_diffs[_].tolist()
                input.write(
                    symbol + ' ' + str(position).replace(",", "")[1:-1] + ' ' + str(force_diff).replace(",", "")[1:-1] + '\n')
        else:
            out = read_vasp_out(structure+'/OUTCAR')
            # Count the number of each atom symbol
            atom_count = {}
            for atom in out:
                symbol = atom.symbol
                if symbol in atom_count:
                    atom_count[symbol] += 1
                else:
                    atom_count[symbol] = 1
            nb = len(out.get_positions())
            a = out.get_cell()
            cell = [a[0][0], a[0][1], a[0][2], a[1][0], a[1][1], a[1][2], a[2][0], a[2][1], a[2][2]]
            E_tot_DFT = out.get_potential_energy()
            symbols = out.get_chemical_symbols()
            positions = out.get_positions()
            forces = out.get_forces(apply_constraint=False) * f_convert

            match_B = 'Extrapolated to 0'
            match_C = 'Total Forces'
            forces_dftb = []
            with open(structure+'/detailed.out') as f:
                for num, line in enumerate(f, 0):
                    if match_B in line:
                        tot = float(line.strip().split()[5])
                    if match_C in line:
                        lines = f.readlines()[0:nb]
                        for _ in range(len(lines)):
                            pos = lines[_].strip().split()
                            fdftb = [float(pos[1]), float(pos[2]), float(pos[3])]
                            forces_dftb.append(fdftb)
            edft = 0
            edftb = 0
            for s, n in atom_count.items():
                e0 = atom_dft[s] * n
                e1 = atom_dftb[s] * n
                edft += e0
                edftb += e1
            dft = (E_tot_DFT-edft) * eVtoKcal
            dftb = (tot-edftb)* eVtoKcal
            input = open(structure+'/one_frame.xyzf', 'w')
            input.write(str(nb) + '\n' + 'NON_ORTHO ' + str(cell).replace(",", "")[1:-1] + ' ' + str(dft - dftb) + '\n')
            forces_dftb = np.array(forces_dftb)

            force_diffs = forces - forces_dftb
            for _ in range(0, nb):
                symbol = symbols[_]
                position = positions[_].tolist()
                force_diff = force_diffs[_].tolist()
                input.write(
                    symbol + ' ' + str(position).replace(",", "")[1:-1] + ' ' + str(force_diff).replace(",", "")[                                                                          1:-1] + '\n')
            input.close()

def main():
    structure_list = sys.argv[1]
    traj(structure_list=structure_list)

if __name__ == "__main__":
    main()
