#!/usr/bin/env python3
"""Bond dipoles and the molecular dipole moment drawn on flat structures, from
ECCE-QM outputs (.qmout): optimised geometry, CHELPG charges, dipole moment.

    python3 plot_bond_dipoles.py <out.png> <name>=<file.qmout> ...

Each molecule has one central atom (atom 1). The bond dipole of the bond to
terminal atom i is q_i (r_i - r_1), with q_i its CHELPG charge; for a neutral
molecule these add up exactly to the dipole of the point charges. Arrows are
drawn in the chemists' convention, pointing to the negative end. The thick
arrow is the molecular dipole moment from the calculated charge distribution,
drawn from the centre of the nuclei. The molecule is drawn in its own plane;
a non-planar one in the plane through its dipole axis and atom 2.
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle

EA_TO_D = 4.80321
COLOUR = {"H": "#f2f2f2", "C": "#808080", "N": "#3050f8", "O": "#e8312a", "F": "#90e050",
          "S": "#e8c830", "B": "#ffb5b5", "Cl": "#1ff01f", "Br": "#a62929", "Li": "#cc80ff",
          "Na": "#ab5cf2"}
RADIUS = {"H": 0.22, "Li": 0.36, "Na": 0.4}
BOND_C = "#0072B2"
MOL_C = "#D55E00"
SCALE = 0.42   # Angstrom of arrow per debye


def read(path):
    text = open(path).read().splitlines()
    atoms, q, mu = [], [], None
    for i, line in enumerate(text):
        if line.startswith("begin atoms"):
            atoms = []
            for l in text[i + 1:]:
                if l.startswith("end"):
                    break
                f = l.split()
                atoms.append((f[1], np.array([float(x) for x in f[3:6]])))
        elif line.startswith("begin charges chelpg"):
            q = []
            for l in text[i + 1:]:
                if l.startswith("end"):
                    break
                q.append(float(l.split()[2]))
        elif line.startswith("dipole_debye"):
            mu = np.array([float(x) for x in line.split()[1:4]])
    return atoms, np.array(q), mu


def frame(atoms, mu):
    """Two in-plane unit vectors: the molecule's plane, or its dipole axis and atom 2."""
    xyz = np.array([a[1] for a in atoms]) - atoms[0][1]
    _, s, vt = np.linalg.svd(xyz - xyz.mean(0))
    planar = len(atoms) <= 3 or s[2] < 1e-3
    if np.linalg.norm(mu) > 1e-3 and not planar:
        u = -mu / np.linalg.norm(mu)
        v = xyz[1] - np.dot(xyz[1], u) * u
        v /= np.linalg.norm(v)
        # seen 25 degrees from above that plane, so atoms behind it show
        w = np.cross(v, u)
        t = np.radians(25)
        return v, np.cos(t) * u + np.sin(t) * w
    a, b = vt[0], vt[1]
    if np.linalg.norm(mu) > 1e-3:          # dipole axis drawn upwards
        b = -mu / np.linalg.norm(mu)
        a = np.cross(b, vt[2]) if planar else a
        a /= np.linalg.norm(a)
    return a, b


def draw(ax, name, atoms, q, mu):
    a, b = frame(atoms, mu)
    p = lambda r: np.array([np.dot(r - atoms[0][1], a), np.dot(r - atoms[0][1], b)])
    pts = [p(r) for _, r in atoms]
    # depth order so nearer atoms are drawn last
    depth = [np.dot(r - atoms[0][1], np.cross(a, b)) for _, r in atoms]
    for i in range(1, len(atoms)):
        ax.plot(*zip(pts[0], pts[i]), color="#606060", lw=3, zorder=1, solid_capstyle="round")
    for i in sorted(range(len(atoms)), key=lambda k: depth[k]):
        el = atoms[i][0]
        ax.add_patch(Circle(pts[i], RADIUS.get(el, 0.32), facecolor=COLOUR.get(el, "#c0c0c0"),
                            edgecolor="#333333", lw=0.8, zorder=2 + depth[i] * 0.01 + 1))
        ax.text(*pts[i], el, ha="center", va="center", fontsize=8, zorder=5)
    for i in range(1, len(atoms)):
        d = pts[i] - pts[0]
        bond = q[i] * (atoms[i][1] - atoms[0][1]) * EA_TO_D       # debye, + to -
        tip = -np.array([np.dot(bond, a), np.dot(bond, b)]) * SCALE  # chemists' arrow: to the - end
        n = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-9) * 0.30
        mid = pts[0] + d / 2 + n
        ax.add_patch(FancyArrowPatch(mid - tip / 2, mid + tip / 2, arrowstyle="-|>", mutation_scale=10,
                                     color=BOND_C, lw=1.4, zorder=6))
    m = -np.array([np.dot(mu, a), np.dot(mu, b)]) * SCALE
    centre = np.array([1.75, np.mean([q[1] for q in pts])])   # beside the molecule
    if np.linalg.norm(m) > 0.05:
        ax.add_patch(FancyArrowPatch(centre - m / 2, centre + m / 2, arrowstyle="-|>", mutation_scale=16,
                                     color=MOL_C, lw=3.0, zorder=7))
    name = "".join("$_%s$" % c if c.isdigit() else c for c in name)
    label = "%s\n$\\mu$ = %.2f D" % (name, np.linalg.norm(mu)) if np.linalg.norm(mu) > 0.005 else "%s\n$\\mu$ = 0" % name
    ax.set_title(label, fontsize=10)
    ax.set_aspect("equal")
    ax.set_xlim(-1.9, 2.2)
    ax.set_ylim(-1.9, 1.9)
    ax.axis("off")


def main():
    out, pairs = sys.argv[1], [x.split("=", 1) for x in sys.argv[2:]]
    cols = (len(pairs) + 1) // 2
    fig, axes = plt.subplots(2, cols, figsize=(2.6 * cols, 5.0))
    for ax, (name, path) in zip(np.ravel(axes), pairs):
        atoms, q, mu = read(path)
        draw(ax, name, atoms, q, mu)
        bonds = [q[i] * np.linalg.norm(atoms[i][1] - atoms[0][1]) * EA_TO_D for i in range(1, len(atoms))]
        print(name, "mu=%.3f D" % np.linalg.norm(mu), "q=", np.round(q, 3), "bond dipoles (D)=", np.round(bonds, 2),
              "sum of bond dipoles=%.3f D" % np.linalg.norm(sum(q[i] * (atoms[i][1] - atoms[0][1]) for i in range(1, len(atoms))) * EA_TO_D))
    fig.tight_layout()
    fig.savefig(out, dpi=200, facecolor="white")


if __name__ == "__main__":
    main()
