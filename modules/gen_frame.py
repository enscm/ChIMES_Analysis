import os
from ase.io.vasp import read_vasp_out, read_vasp
import numpy as np
from os.path import exists
import json
import sys

""" This script reads energy and force information either from OUTCAR if exists
    or from size-reduced file "outcar" (for energy) and "force" (for force info);
    and read other geometrical information.
    then construct either trajectory files in ChIMES format, named as "one_frame.xyzf" under corresponding folders (mode split)
    or construct one trajectory file named as "combine_total_"+len(number_of_frames)+"_frames.xyzf" containing all trajectories of listed structures.
"""
def _read_data(structure):
    eVtoKcal = 23.06035
    f_convert = 0.194469064593167E-01  # convert eV/A to Hatree/Bohr

    match_B = 'Extrapolated to 0'
    match_C = 'Total Forces'

    with open('atomic_energy_list.json', "r") as file:
        data = json.load(file)
    # Extract the dictionaries
    atom_dft = data["atom_dft"]
    atom_dftb = data["atom_dftb"]

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

        one_frame=[]
        multi_frames=[]

        one_frame.append(str(nb) + '\n' + 'NON_ORTHO ' + str(cell).replace(",", "")[1:-1] + ' ' + str(dft - dftb) + '\n')

        multi_frames.append(str(nb) + '\n' + 'NON_ORTHO ' + str(cell).replace(",", "")[1:-1] + ' ' + str(dft - dftb) + '\n')

        forces_dftb = np.array(forces_dftb)
        forces = np.array(forces)
        force_diffs = forces - forces_dftb

        for _ in range(0, nb):
            symbol = symbols[_]
            position = positions[_].tolist()
            force_diff = force_diffs[_].tolist()

            one_frame.append(symbol + ' ' + str(position).replace(",", "")[1:-1] + ' ' + str(force_diff).replace(",", "")[1:-1] + '\n')

            multi_frames.append(symbol + ' ' + str(position).replace(",", "")[1:-1] + ' ' + str(force_diff).replace(",", "")[1:-1] + '\n')

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

        one_frame=[]
        multi_frames=[]

        one_frame.append(str(nb) + '\n' + 'NON_ORTHO ' + str(cell).replace(",", "")[1:-1] + ' ' + str(dft - dftb) + '\n')

        multi_frames.append(str(nb) + '\n' + 'NON_ORTHO ' + str(cell).replace(",", "")[1:-1] + ' ' + str(dft - dftb) + '\n')

        forces_dftb = np.array(forces_dftb)

        force_diffs = forces - forces_dftb
        for _ in range(0, nb):
            symbol = symbols[_]
            position = positions[_].tolist()
            force_diff = force_diffs[_].tolist()

            one_frame.append(symbol + ' ' + str(position).replace(",", "")[1:-1] + ' ' + str(force_diff).replace(",", "")[1:-1] + '\n')

            multi_frames.append(symbol + ' ' + str(position).replace(",", "")[1:-1] + ' ' + str(force_diff).replace(",", "")[1:-1] + '\n')

    return one_frame, multi_frames

def _write_frame(mode=None,structure_list=None):

    with open(structure_list,"r") as f:
        lines=f.readlines()

    for line in lines:
        structure = line.strip().split()[0]
        one,multi = _read_data(structure)
        if (mode=="split"):
            with open(structure + "/one_frame.xyzf","w") as one_out:
                one_out.writelines(one)
        if (mode=="combine"):
            with open("combine_total_"+str(len(lines))+"_frames.xyzf") as multi_out:
                multi_out.writelines(multi)

def main():
    print("             USAGE:  gen_frame [MODE] structure_list ")
    print("             Available mode:                                 ")
    print("                                             mode split: split (string)                      ")
    print("                                             mode combine: combine (string)                  ")
    print("")

    mode = sys.argv[1]
    structure_list = sys.argv[2]

    if (mode=="split"):
        _write_frame(mode=mode,structure_list=structure_list)

    if (mode=="combine"):
        _write_frame(mode=mode,structure_list=structure_list)

if __name__ == "__main__":
    main()
