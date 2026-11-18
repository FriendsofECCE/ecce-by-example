#!/usr/bin/env python3
"""The fraction of an electron moved, q/e = mu/(4.803 R), of six diatomics on
one scale from shared (0) to two whole ions (1), from ECCE-QM outputs; measured
values (table of the chapter) as open circles.

    python3 plot_charge_scale.py <out.png> <name>=<file.qmout>[:<measured q/e>] ...
"""
import re, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def qe(path):
    t = open(path).read()
    g = re.findall(r"begin geometry[^\n]*\n(.*?)end geometry", t, re.S)[-1].split("\n")
    xyz = np.array([[float(x) for x in l.split()[2:5]] for l in g if l.strip()])
    mu = float(re.findall(r"^dipole_debye .* ([-\d.]+)$", t, re.M)[-1])
    return mu / (4.80321 * np.linalg.norm(xyz[1] - xyz[0]))


rows = []
for arg in sys.argv[2:]:
    name, rest = arg.split("=", 1)
    path, _, meas = rest.partition(":")
    rows.append((name, qe(path), float(meas) if meas else None))
fig, ax = plt.subplots(figsize=(6.6, 2.7))
ax.axhline(0, color="#999999", lw=1)
for k, (name, q, m) in enumerate(sorted(rows, key=lambda r: r[1])):
    y = 0.28 if k % 2 == 0 else -0.28
    label = "".join("$_%s$" % c if c.isdigit() else c for c in name)
    ax.plot([q, q], [0, y * 0.75], color="#0072B2", lw=0.8)
    ax.plot(q, 0, "o", color="#0072B2", ms=8, zorder=3)
    if m is not None:
        ax.plot(m, 0, "o", mfc="none", mec="#D55E00", mew=1.5, ms=12, zorder=4)
    ax.text(q, y, "%s\n%.2f" % (label, q), ha="center", va="center", fontsize=9)
ax.text(0, -0.62, "electrons shared\nequally", ha="center", va="center", fontsize=8.5, color="#333333")
ax.text(1, -0.62, "one whole electron\nmoved: two ions", ha="center", va="center", fontsize=8.5, color="#333333")
ax.plot([], [], "o", color="#0072B2", label="calculated")
ax.plot([], [], "o", mfc="none", mec="#D55E00", mew=1.5, label="measured")
ax.legend(loc="lower center", fontsize=8, frameon=False, ncol=2)
ax.set_xlim(-0.08, 1.08)
ax.set_ylim(-0.8, 0.5)
ax.set_yticks([])
ax.set_xlabel("fraction of an electron moved, $q/e$", fontsize=10)
for side in ("left", "right", "top"):
    ax.spines[side].set_visible(False)
fig.tight_layout()
fig.savefig(sys.argv[1], dpi=200, facecolor="white")
