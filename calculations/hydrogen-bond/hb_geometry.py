#!/usr/bin/env python3
"""H2...O4 distance and O1-H2...O4 angle at every point of the stored O1...O4
relaxed scans of the water dimer (Props/SCANGEOM), and ecce-morse's fit of the
energies against H2...O4, leaving out inward points bent below MIN_ANGLE.

    ECCE_TEST_HOME=<install> python3 hb_geometry.py <data dir>/h2o_dimer > curves/h2o_dimer_hb.json
"""
import importlib.machinery, importlib.util, json, math, os, re, sys
B = os.environ.get("ECCE_TEST_HOME", "/opt/ecce")
ld = importlib.machinery.SourceFileLoader("ecce_morse", os.path.join(B, "bin", "ecce-morse"))
M = importlib.util.module_from_spec(importlib.util.spec_from_loader("ecce_morse", ld)); ld.exec_module(M)
MIN_ANGLE = 150.0
pts = []
for d in ("inward", "outward"):
    calc = os.path.join(sys.argv[1], "users/local/qm", d)
    r, e = M.read_scan(calc)
    t = open(os.path.join(calc, "Props", "SCANGEOM")).read()
    for (n, b), oo, en in zip(re.findall(r'<step number="(\d+)">(.*?)</step>', t, re.S), r, e):
        v = [float(x) for x in b.split()]
        a = [v[i:i + 3] for i in range(0, 18, 3)]
        hb = math.dist(a[1], a[3])
        u = [x - y for x, y in zip(a[0], a[1])]; w = [x - y for x, y in zip(a[3], a[1])]
        ang = math.degrees(math.acos(sum(p * q for p, q in zip(u, w)) / math.dist(a[0], a[1]) / hb))
        pts.append({"scan": d, "step": int(n), "OO_A": oo, "HO_A": hb, "angle_deg": ang, "energy_hartree": en})
# Only the compressed inward points bend; far out the angle drifts as the molecules turn.
use = [p for p in pts if p["scan"] == "outward" or p["angle_deg"] >= MIN_ANGLE]
res = M.analyse([p["HO_A"] for p in use], [p["energy_hartree"] for p in use], 1.00783 * 15.9949 / (1.00783 + 15.9949))
keep = ("points_used", "points_total", "De_kJ_per_mol", "a_per_A", "re_A", "Einf_hartree", "rms_kJ_per_mol")
json.dump({"min_angle_deg": MIN_ANGLE, "fit": {k: res[k] for k in keep}, "points": pts}, sys.stdout, indent=1)
