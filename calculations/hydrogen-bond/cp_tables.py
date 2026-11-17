#!/usr/bin/env python3
"""Per-point counterpoise data of the scans as curves/<pair>_bsse.csv.

    python3 cp_tables.py <cp_scan.py out dir>

Reads <pair>-<scan>.SCANRAW, .SCANCP and .SCANBSSE (Hartree vectors, one value per
stored scan geometry, from the counterpoise calculation ECCE made with scan cpsingle)
and .SCANCOORD (the source scan).
"""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
D = sys.argv[1]


def vec(pair, scan, key):
    t = open(os.path.join(D, "%s-%s.%s" % (pair, scan, key))).read()
    return [float(x) for x in re.sub(r"<[^>]*>", " ", t).split()]


for pair in ("ar_dimer", "h2o_dimer", "na_h2o", "nacl_ion_pair"):
    out = ["# ECCE-QM B3LYP-D3(BJ)/def2-TZVP; counterpoise single points at every stored geometry of the",
           "# relaxed scans (Relaxed Scan panel, scan cpsingle). raw = E_AB(AB) - sum E_X(X),",
           "# cp = E_AB(AB) - sum E_X(AB), bsse = cp - raw; X at its geometry in the complex. Hartree.",
           "scan,point,coordinate_angstrom,raw_hartree,cp_hartree,bsse_hartree"]
    for scan in ("inward", "outward"):
        c, raw, cp, b = (vec(pair, scan, k) for k in ("SCANCOORD", "SCANRAW", "SCANCP", "SCANBSSE"))
        assert len(c) == len(raw) == len(cp) == len(b), (pair, scan, len(c), len(raw))
        out += ["%s,%d,%.6f,%.10f,%.10f,%.10f" % (scan, i + 1, *v) for i, v in enumerate(zip(c, raw, cp, b))]
    open(os.path.join(HERE, "curves", pair + "_bsse.csv"), "w").write("\n".join(out) + "\n")
    print(pair, len(out) - 4, "points")
