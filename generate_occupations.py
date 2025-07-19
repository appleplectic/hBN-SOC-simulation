#!/usr/bin/env python3
"""
Parses a QE pw.x output, finds the HOMO→LUMO bands, and builds a fixed-OCCUPATIONS block
for an excited-state run. Detects both collinear (spin up/down) and noncollinear+SOC outputs.
"""

import sys
import re
import bisect

def build_occ_collinear_by_count(nbnd, n_up, n_dn, excite_channel="down"):
    occ_up = [1.0]*n_up   + [0.0]*(nbnd - n_up)
    occ_dn = [1.0]*n_dn   + [0.0]*(nbnd - n_dn)

    if excite_channel == "down":
        i_h = n_dn - 1
        i_l = n_dn
        occ_dn[i_h], occ_dn[i_l] = 0.0, 1.0
    else:
        i_h = n_up - 1
        i_l = n_up
        occ_up[i_h], occ_up[i_l] = 0.0, 1.0

    return occ_up + occ_dn


def build_occ_soc(bands, fermi):
    occ = [1.0 if e <= fermi else 0.0 for e in bands]

    i_h = bisect.bisect_right(bands, fermi) - 1
    i_l = i_h + 1
    occ[i_h] = 0.0
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
        elif "total magnetization" in line.lower():
            mag = float(re.search(r"magnetization\s*=.*?(-?[0-9]+\.[0-9]+) Bohr mag\/cell", line).group(1))

            
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
        if spin_ups and spin_downs:
            n_tot = electrons
            delta = int(round(mag))

            n_up = (n_tot + delta)//2
            n_dn = (n_tot - delta)//2

            occ = build_occ_collinear_by_count(nbnd, n_up, n_dn,
                                            excite_channel="down")
    elif overall:
        occ = build_occ_soc(overall[:nbnd], fermi_energy)
    else:
        raise ValueError("Failed to parse.")

    print("OCCUPATIONS")
    for i in range(0, len(occ), 10):
        chunk = occ[i:i+10]
        print("  " + " ".join(f"{o:.6f}" for o in chunk))
    print("! " + str(len(occ)) + " " + str(sum(occ)))

if __name__ == "__main__":
    main()
