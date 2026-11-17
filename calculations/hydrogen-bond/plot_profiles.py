#!/usr/bin/env python3
"""Total density along the line between two atoms, from the Density Profile
panel's CSV exports (density-profile-*.csv, e/A^3), one panel each on the same
log scale, with the minimum between the two atoms marked.

    python3 plot_profiles.py <out.png> O1-O4 [Na1-Cl2]
"""
import csv, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
BOHR3 = 0.529177210903 ** 3  # A^3 per bohr^3
TITLE = {"O1-O4": "(H$_2$O)$_2$, O1 to O4", "Na1-Cl2": "Na$^+$Cl$^-$, Na1 to Cl2"}
# The minimum is looked for between these two atoms of the line (names as in the CSV).
BETWEEN = {"O1-O4": ("H2", "O4"), "Na1-Cl2": ("Na1", "Cl2")}


def load(name):
    atoms, s, rho = {}, [], []
    for line in open(os.path.join(HERE, "density-profile-%s.csv" % name)):
        if line.startswith("# atom"):
            w = line.split()
            atoms[w[2]] = float(w[-1])
        elif line[0] not in "#s":
            a, b = line.split(",")[:2]
            s.append(float(a)); rho.append(float(b) * BOHR3)
    return atoms, s, rho


names = sys.argv[2:]
fig, axes = plt.subplots(1, len(names), figsize=(4.3 * len(names), 3.3), squeeze=False, sharey=True)
for ax, name in zip(axes[0], names):
    atoms, s, rho = load(name)
    a, b = (atoms[k] for k in BETWEEN[name])
    i = min((k for k in range(len(s)) if a < s[k] < b), key=rho.__getitem__)
    print("%s: minimum %.4f e/bohr^3 at %.2f A from %s" % (name, rho[i], s[i] - a, BETWEEN[name][0]))
    ax.semilogy(s, rho, "-", color="#0072B2", lw=1.4)
    ax.plot([s[i]], [rho[i]], "o", color="#D55E00", ms=5)
    ax.annotate("%.4f" % rho[i], (s[i], rho[i]), textcoords="offset points", xytext=(0, -14),
                ha="center", fontsize=8, color="#D55E00")
    for k, x in atoms.items():
        ax.axvline(x, color="#999999", lw=0.7, ls=":")
        ax.text(x, 1.3e2, k, ha="center", fontsize=8)
    ax.set_ylim(1e-3, 3e2)
    ax.set_title(TITLE[name], fontsize=10.5, pad=14)
    ax.set_xlabel("distance along the line (Å)", fontsize=10)
    ax.tick_params(labelsize=9)
    ax.grid(color="#e6e6e6", lw=0.6)
axes[0][0].set_ylabel("total density (e/bohr$^3$)", fontsize=10)
fig.tight_layout()
fig.savefig(sys.argv[1], dpi=200, facecolor="white")
