#!/usr/bin/env python3
"""Interaction curve of one or more pairs: scan points, Morse fit, separated partners.

    python3 plot_curves.py <out.png> <pair> [<pair> ...]

<pair> is ar_dimer, h2o_dimer, na_h2o or nacl_ion_pair; one panel each, side
by side. Reads curves/<pair>_{inward,outward}.csv (Relaxed Scan panel exports
made by oo_scan.py), curves/morse.json (ecce-morse's fit of the inward and
outward points together, made by fit_curves.py) and curves/monomers.csv
(energies of the separated partners). The water dimer is the relaxed scan of
O1...O4 drawn against the H2...O4 distance measured at each point, with its
own fit (curves/h2o_dimer_hb.json, made by hb_geometry.py). Zero is the separated partners. The
Morse line is drawn for the neutral pairs only, whose curves level off within
the scan; the NaCl panel also gets the Coulomb energy of two whole charges as
a reference curve and the separated neutral atoms. Prints the table rows.
"""
import csv, json, math, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
HARTREE = 2625.4996394799  # kJ/mol, as ecce-morse
COULOMB = 1389.35  # kJ/mol Å, e^2/(4 pi eps0) per mole
PAIRS = {"ar_dimer": ("Ar$_2$", "Ar–Ar", ("ar", "ar")),
         "h2o_dimer": ("(H$_2$O)$_2$", "H···O", ("h2o", "h2o")),
         "na_h2o": ("Na$^+$···H$_2$O", "Na–O", ("na", "h2o")),
         "nacl_ion_pair": ("Na$^+$Cl$^-$", "Na–Cl", ("na", "cl"))}
MORSE = ("ar_dimer", "h2o_dimer")


def rows(path):
    with open(path) as f:
        return list(csv.DictReader(l for l in f if not l.startswith("#")))


def load(pair):
    if pair == "h2o_dimer":
        hb = json.load(open(os.path.join(HERE, "curves", "h2o_dimer_hb.json")))
        pts = {round(p["HO_A"], 4): p["energy_hartree"] for p in hb["points"]
               if p["scan"] == "outward" or p["angle_deg"] >= hb["min_angle_deg"]}
        r = sorted(pts)
        return r, [pts[x] for x in r]
    pts = {}
    for d in ("inward", "outward"):
        for row in rows(os.path.join(HERE, "curves", "%s_%s.csv" % (pair, d))):
            pts[round(float(row["coordinate_angstrom"]), 4)] = float(row["energy_hartree"])
    r = sorted(pts)
    return r, [pts[x] for x in r]


mono = {r["calculation"]: float(r["energy_hartree"]) for r in rows(os.path.join(HERE, "curves", "monomers.csv"))}
fits = json.load(open(os.path.join(HERE, "curves", "morse.json")))
fits["h2o_dimer"] = json.load(open(os.path.join(HERE, "curves", "h2o_dimer_hb.json")))["fit"]
pairs = sys.argv[2:]
fig, axes = plt.subplots(1, len(pairs), figsize=(4.3 * len(pairs), 3.4), squeeze=False)
for ax, pair in zip(axes[0], pairs):
    label, coord, parts = PAIRS[pair]
    r, e = load(pair)
    f = fits[pair]
    sep = sum(mono[p] for p in parts)
    de = [(x - sep) * HARTREE for x in e]
    i = min(range(len(e)), key=e.__getitem__)
    print("%-14s R_min %.2f dE_min %.1f | dE(R_max) %.2f R_max %.2f | Morse r_e %.2f D_e %.1f rms %.2f | %d points"
          % (pair, r[i], de[i], de[-1], r[-1], f["re_A"], f["De_kJ_per_mol"], f["rms_kJ_per_mol"], len(r)))
    ax.axhline(0, color="#D55E00", lw=1.0, ls="--",
               label="separated ions" if pair == "nacl_ion_pair" else "separated partners")
    ax.plot(r, de, "o", color="#0072B2", ms=3.5, mfc="white", mew=1.0, label="scan points")
    lo = min(de)
    if pair in MORSE:
        De, a, re_ = f["De_kJ_per_mol"], f["a_per_A"], f["re_A"]
        shift = (f["Einf_hartree"] - sep) * HARTREE
        xs = [r[0] + (r[-1] - r[0]) * k / 300 for k in range(301)]
        ax.plot(xs, [shift + De * ((1 - math.exp(-a * (x - re_))) ** 2 - 1) for x in xs], "-",
                color="#0072B2", lw=1.4, label="Morse fit")
    if pair == "nacl_ion_pair":
        xs = [3.0 + (r[-1] - 3.0) * k / 300 for k in range(301)]
        ax.plot(xs, [-COULOMB / x for x in xs], ":", color="#555555", lw=1.4,
                label="reference: charges $\\pm1$, Coulomb only")
        if "na0" in mono and "cl0" in mono:
            atoms = (mono["na0"] + mono["cl0"] - sep) * HARTREE
            print("  separated neutral atoms relative to the separated ions: %.1f kJ/mol" % atoms)
            ax.axhline(atoms, color="#009E73", lw=1.0, ls="-.", label="separated atoms (Na + Cl)")
    ax.legend(fontsize=7.5, loc="lower right", frameon=False)
    ax.set_title(label, fontsize=10.5)
    ax.set_ylim(1.12 * lo, -0.2 * lo)
    ax.set_xlim(1.4, math.ceil(r[-1]) + 0.2)
    ax.set_xlabel("%s distance (Å)" % coord, fontsize=10)
    ax.tick_params(labelsize=9)
    ax.grid(color="#e6e6e6", lw=0.6)
    ax.set_axisbelow(True)
axes[0][0].set_ylabel("ΔE (kJ/mol)", fontsize=10)
fig.tight_layout()
fig.savefig(sys.argv[1], dpi=200, facecolor="white")
