#!/usr/bin/env python3
"""
make_excited_occupations.py

Parses a QE pw.x output, finds the HOMO→LUMO bands, and builds a fixed-OCCUPATIONS block
for an excited-state run. Detects both collinear (spin up/down) and noncollinear+SOC outputs.
"""

import sys
import re

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 make_excited_occupations.py <QE_output_file>")
        sys.exit(1)

    f = sys.argv[1]
    with open(f) as fl:
        lines = fl.readlines()
    
    started_lines = -1
    spin_up_started = False
    spin_down_started = False
    fermi_energy = 0
    spin_ups = []
    spin_downs = []
    overall = []
    for line in lines:
        if "number of electrons" in line:
            electrons = int(float(re.search(r"number of electrons( *)=( *)(-?\d+.?\d+)", line).group(3)))
        elif "End of self-consistent calculation" in line:
            started_lines = 0
            continue
        elif "SPIN UP" in line:
            spin_up_started = True
            continue
        elif "SPIN DOWN" in line:
            spin_up_started = False
            spin_down_started = True
            continue
        elif "the Fermi energy is" in line:
            fermi_energy = float(re.search(r"energy is( *)(-?\d+.?\d+)", line).group(2))
            spin_down_started = False
            started_lines = -1
            continue
            
        if started_lines >= 0:
            if line.replace(" ", "") and not line.replace(" ", "").startswith("k"):
                for num in line.split():
                    if num.strip():
                        if spin_up_started:
                            spin_ups.append(float(num.strip()))
                        elif spin_down_started:
                            spin_downs.append(float(num.strip()))
                        else:
                            overall.append(float(num.strip()))
        
        if started_lines != -1:
            started_lines += 1
    
    if spin_ups and spin_downs:
        bands = spin_ups
        occ_per_band = 1
    else:
        bands = overall
        occ_per_band = 2

    occupied = [(i, e) for i, e in enumerate(bands) if e <= fermi_energy]
    virtual  = [(i, e) for i, e in enumerate(bands) if e >  fermi_energy]
    if not occupied or not virtual:
        sys.exit("Error: couldn’t identify HOMO or LUMO")
    homo_idx, homo_energy = max(occupied, key=lambda x: x[1])
    lumo_idx, lumo_energy = min(virtual,  key=lambda x: x[1])

    occs = [
        occ_per_band if energy <= fermi_energy else 0.0
        for energy in bands
    ]

    occs[homo_idx] -= 1
    occs[lumo_idx] += 1

    print("OCCUPATIONS")
    for i in range(0, len(occs), 10):
        chunk = occs[i:i+10]
        print("  " + " ".join(f"{o:.6f}" for o in chunk))

if __name__ == "__main__":
    main()
