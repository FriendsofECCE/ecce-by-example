#!/usr/bin/env python3
"""Interaction curves of four pairs: scan points, ECCE's Morse fit, separated partners.

    python3 plot_curves.py <out.png>

Reads curves/<pair>_{inward,outward}.csv (Relaxed Scan panel exports made by
oo_scan.py), curves/morse.json (ecce-morse's fit of the inward and outward
points together, made by fit_curves.py) and curves/monomers.csv (energies of
the separated partners). Every panel is drawn relative to the separated
partners; the Morse line only for the neutral pairs, whose curves level off
within the scan. Separate panels because the depths span 1 to 600 kJ/mol.
Prints the table rows.
"""
import csv, json, math, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
HARTREE = 2625.4996394799  # kJ/mol, as ecce-morse
MORSE = ("ar_dimer", "h2o_dimer")
PAIRS = [("ar_dimer", "Ar$_2$", "Ar–Ar", ("ar", "ar")),
         ("h2o_dimer", "(H$_2$O)$_2$", "O–O", ("h2o", "h2o")),
         ("na_h2o", "Na$^+$···H$_2$O", "Na–O", ("na", "h2o")),
         ("nacl_ion_pair", "Na$^+$Cl$^-$", "Na–Cl", ("na", "cl"))]


def rows(path):
    with open(path) as f:
        return list(csv.DictReader(l for l in f if not l.startswith("#")))


def load(pair):
    pts = {}
    for d in ("inward", "outward"):
        for row in rows(os.path.join(HERE, "curves", "%s_%s.csv" % (pair, d))):
            pts[round(float(row["coordinate_angstrom"]), 4)] = float(row["energy_hartree"])
    r = sorted(pts)
    return r, [pts[x] for x in r]


mono = {r["calculation"]: float(r["energy_hartree"]) for r in rows(os.path.join(HERE, "curves", "monomers.csv"))}
fits = json.load(open(os.path.join(HERE, "curves", "morse.json")))
fig, axes = plt.subplots(2, 2, figsize=(8, 6), sharex=True)
for ax, (pair, label, coord, parts) in zip(axes.flat, PAIRS):
    r, e = load(pair)
    f = fits[pair]
    einf = f["Einf_hartree"]
    sep = sum(mono[p] for p in parts)
    i = min(range(len(e)), key=e.__getitem__)
    print("%-14s Morse De %.1f re %.2f rms %.2f | dE(min) vs separated %.1f at %.2f | "
          "dE(Rmax) vs separated %.1f, vs Morse asymptote %.2f | Rmax %.2f, %d points"
          % (pair, f["De_kJ_per_mol"], f["re_A"], f["rms_kJ_per_mol"], (e[i] - sep) * HARTREE,
             r[i], (e[-1] - sep) * HARTREE, (e[-1] - einf) * HARTREE, r[-1], len(r)))
    De, a, re_ = f["De_kJ_per_mol"], f["a_per_A"], f["re_A"]
    shift = (einf - sep) * HARTREE
    ax.axhline(0, color="#D55E00", lw=1.0, ls="--", label="separated partners")
    ax.plot(r, [(x - sep) * HARTREE for x in e], "o", color="#0072B2", ms=3.5, mfc="white", mew=1.0,
            label="scan points")
    if pair in MORSE:
        xs = [r[0] + (r[-1] - r[0]) * k / 300 for k in range(301)]
        ax.plot(xs, [shift + De * ((1 - math.exp(-a * (x - re_))) ** 2 - 1) for x in xs], "-",
                color="#0072B2", lw=1.4, label="Morse fit")
    ax.set_title("%s (%s distance)" % (label, coord), fontsize=11)
    lo = min((x - sep) * HARTREE for x in e)
    ax.set_ylim(1.12 * lo, -0.25 * lo)
    ax.set_xlim(1.6, math.ceil(r[-1]) + 0.2)
    ax.tick_params(labelsize=9)
    ax.grid(color="#e6e6e6", lw=0.6)
    ax.set_axisbelow(True)
axes[0, 0].legend(fontsize=8, loc="lower right", frameon=False)
for ax in axes[1]:
    ax.set_xlabel("R (Å)", fontsize=10)
for ax in axes[:, 0]:
    ax.set_ylabel("ΔE (kJ/mol)", fontsize=10)
fig.tight_layout()
fig.savefig(sys.argv[1], dpi=200, facecolor="white")
