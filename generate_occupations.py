#!/usr/bin/env python3
"""
Parses a QE pw.x output, finds the HOMO→LUMO bands, and builds a fixed-OCCUPATIONS block
for an excited-state run. Detects both collinear (spin up/down) and noncollinear+SOC outputs.
"""

import sys
import re
import bisect

def build_occ_collinear(spin_up, spin_dn, fermi, excite_channel="down"):
    """Return a 300‑element OCCUPATIONS list for nbnd = 150."""
    nbnd = min(len(spin_up), len(spin_dn))
    spin_up, spin_dn = spin_up[:nbnd], spin_dn[:nbnd]

    # 1. Ground‑state pattern
    occ_up = [1.0 if e <= fermi else 0.0 for e in spin_up]
    occ_dn = [1.0 if e <= fermi else 0.0 for e in spin_dn]

    # 2. Choose which channel to excite
    target = spin_dn if excite_channel == "down" else spin_up
    occ_tgt = occ_dn if excite_channel == "down" else occ_up

    # index of last ε <= E_F  (HOMO)
    i_h = bisect.bisect_right(target, fermi) - 1
    i_l = i_h + 1                               # first ε  > E_F

    # 3. Apply the promotion
    occ_tgt[i_h] = 0.0
    occ_tgt[i_l] = 1.0

    return occ_up + occ_dn                      # 300 numbers

def build_occ_soc(bands, fermi):
    """Return a 300‑element OCCUPATIONS list for nbnd = 300."""
    occ = [2.0 if e <= fermi else 0.0 for e in bands]

    i_h = bisect.bisect_right(bands, fermi) - 1
    i_l = i_h + 1
    occ[i_h] = 1.0
    occ[i_l] = 1.0
    return occ


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 make_excited_occupations.py <QE_output_file> <nbnd>")
        sys.exit(1)

    f = sys.argv[1]
    nbnd = int(sys.argv[2])
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
        occ = build_occ_collinear(spin_ups[:nbnd], spin_downs[:nbnd], fermi_energy)
        """n_spin_ups = spin_ups.copy()
        n_spin_ups.append(fermi_energy)
        n_spin_ups = sorted(n_spin_ups)
        idx = n_spin_ups.index(fermi_energy)
        homo_up = n_spin_ups[idx-1]
        lumo_up = n_spin_ups[idx+1]

        homo_up_i = spin_ups.index(homo_up)
        lumo_up_i = spin_ups.index(lumo_up)

        occ_up = []
        occ_down = []

        for eps in spin_ups:
            occ_up.append(1.0 if eps <= fermi_energy else 0.0)
        
        for eps in spin_downs:
            occ_down.append(1.0 if eps <= fermi_energy else 0.0)
        
        occ_up[homo_up_i] = 0.0
        occ_up[lumo_up_i] = 1.0

        occ = occ_up"""
    elif overall:
        occ = build_occ_soc(overall[:nbnd], fermi_energy)
        """n_overall = overall.copy()
        n_overall.append(fermi_energy)
        n_overall = sorted(n_overall)
        idx = n_overall.index(fermi_energy)
        homo = n_overall[idx-1]
        lumo = n_overall[idx+1]

        homo_i = overall.index(homo)
        lumo_i = overall.index(lumo)

        occ = []
        for eps in overall:
            occ.append(2.0 if eps <= fermi_energy else 0.0)

        occ[homo_i] -= 1
        occ[lumo_i] += 1"""
    else:
        raise ValueError("Failed to parse.")

    print("OCCUPATIONS")
    for i in range(0, len(occ), 10):
        chunk = occ[i:i+10]
        print("  " + " ".join(f"{o:.6f}" for o in chunk))
    print(len(occ), sum(occ))

if __name__ == "__main__":
    main()
