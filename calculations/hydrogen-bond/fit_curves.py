#!/usr/bin/env python3
"""Morse fit of each pair's inward and outward scans together, with ecce-morse's own code.

    ECCE_TEST_HOME=<install> python3 fit_curves.py <data dir> > curves/morse.json

<data dir> holds one oo_scan.py --data folder per pair. ecce-morse <calc> takes
one calculation and needs points on both sides of the minimum, which neither
scan direction has alone, so its fit (analyse) is called on the union.
"""
import importlib.machinery, importlib.util, json, os, sys
B = os.environ.get("ECCE_TEST_HOME", "/opt/ecce")
ld = importlib.machinery.SourceFileLoader("ecce_morse", os.path.join(B, "bin", "ecce-morse"))
M = importlib.util.module_from_spec(importlib.util.spec_from_loader("ecce_morse", ld)); ld.exec_module(M)
D = sys.argv[1]
MU = {"ar_dimer": (39.9624, 39.9624), "h2o_dimer": (1.00783, 15.9949),
      "na_h2o": (22.9898, 15.9949), "nacl_ion_pair": (22.9898, 34.9689)}
# The water dimer is scanned along the hydrogen bond H2...O4, in its own data folder.
FOLDER = {"h2o_dimer": "h2o_dimer_hb"}
out = {}
for pair, (m1, m2) in MU.items():
    r, e = [], []
    for d in ("inward", "outward"):
        a, b = M.read_scan(os.path.join(D, FOLDER.get(pair, pair), "users/local/qm", d))
        r += a; e += b
    res = M.analyse(r, e, m1 * m2 / (m1 + m2))
    res["points"] = sorted(zip(r, e))
    out[pair] = res
json.dump(out, sys.stdout, indent=1)
