#!/usr/bin/env python3
"""Interaction curves of four pairs from ECCE's Relaxed Scan CSV exports.

    python3 plot_curves.py <out.png>

Reads curves/<pair>_{inward,outward}.csv (made by oo_scan.py), draws one panel
per pair with ΔE relative to that pair's largest-R point, and prints the
table rows (R_eq, depth, largest R). Separate panels because the depths span
1 to 300 kJ/mol; the Relaxed Scan panel's Compare... draws every curve
relative to its own lowest point, which is not the reference wanted here.
"""
import csv, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
HARTREE = 2625.499639  # kJ/mol
PAIRS = [("ar_dimer", "Ar$_2$", "Ar–Ar"),
         ("h2o_dimer", "(H$_2$O)$_2$", "O–O"),
         ("na_h2o", "Na$^+$···H$_2$O", "Na–O"),
         ("nacl_ion_pair", "NaCl ion pair", "Na–Cl")]


def load(pair):
    pts = {}
    for d in ("inward", "outward"):
        with open(os.path.join(HERE, "curves", "%s_%s.csv" % (pair, d))) as f:
            for row in csv.reader(l for l in f if not l.startswith("#")):
                if row[0] == "point":
                    continue
                pts[round(float(row[1]), 4)] = float(row[2])
    r = sorted(pts)
    return r, [pts[x] for x in r]


fig, axes = plt.subplots(2, 2, figsize=(8, 6), sharex=True)
for ax, (pair, label, coord) in zip(axes.flat, PAIRS):
    r, e = load(pair)
    de = [(x - e[-1]) * HARTREE for x in e]
    i = min(range(len(de)), key=de.__getitem__)
    print("%-14s R_eq %.2f  depth %.1f kJ/mol  (largest R %.2f, %d points)"
          % (pair, r[i], -de[i], r[-1], len(r)))
    ax.axhline(0, color="#999999", lw=0.8)
    ax.plot(r, de, "-o", color="#0072B2", lw=1.5, ms=4)
    ax.set_title("%s (%s distance)" % (label, coord), fontsize=11)
    ax.set_xlim(1.6, 7.2)
    ax.tick_params(labelsize=9)
    ax.grid(color="#e6e6e6", lw=0.6)
    ax.set_axisbelow(True)
for ax in axes[1]:
    ax.set_xlabel("R (Å)", fontsize=10)
for ax in axes[:, 0]:
    ax.set_ylabel("ΔE (kJ/mol)", fontsize=10)
fig.tight_layout()
fig.savefig(sys.argv[1], dpi=200, facecolor="white")
