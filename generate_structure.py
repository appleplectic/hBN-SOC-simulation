#!/usr/bin/env python3
"""
Build 2D h-BN monolayer with a B-vacancy and write QE input.
"""

from ase import Atoms
from ase.build import make_supercell
from ase.io import write
import numpy as np

REP = 6
VAC = 20.0

a = 2.504  # in-plane lattice constant
c = VAC  # vacuum along z

positions = [
    (0.000, 0.000, 0.0),        # B
    (1.446, 0.000, 0.0),        # N (1.446 ≈ a / sqrt(3))
]
symbols = ['B', 'N']

cell = [
    [a, 0.0, 0.0],
    [a/2, a * np.sqrt(3)/2, 0.0],
    [0.0, 0.0, c],
]

prim = Atoms(symbols=symbols, positions=positions, cell=cell, pbc=[True, True, False])
prim.center(axis=2)

P = np.identity(3) * [REP, REP, 1]
supercell = make_supercell(prim, P)

for i, atom in enumerate(supercell):
    if atom.symbol == 'B':
        del supercell[i]
        break

write('hbn_vb.atoms', supercell, format='espresso-in', pseudopotentials={
    'B': 'B.rel-pbe-n-rrkjus_psl.1.0.0.UPF',
    'N': 'N.rel-pbe-n-rrkjus_psl.1.0.0.UPF'
})
print("Wrote 'hbn_vb.atoms' with one B-vacancy.")
