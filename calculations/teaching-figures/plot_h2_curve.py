#!/usr/bin/env python3
"""The H2 bond curve of the General Chemistry example h2_bond_curve, from its
stored SCANCOORD and SCANENERGY, each computed point drawn as a dot, relative to the point at 5.0 A (the two atoms
apart), with the bond length and bond energy marked.

    python3 plot_h2_curve.py <stored calc Props dir> <out.png>
"""
import os, re, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HARTREE = 2625.4996   # kJ/mol


def vec(path):
    text = open(path).read()
    return [float(x) for x in re.sub(r"<[^>]*>", " ", text.split("?>", 1)[1]).split()]


props, out = sys.argv[1:3]
r = vec(os.path.join(props, "SCANCOORD"))
e = vec(os.path.join(props, "SCANENERGY"))
far = e[r.index(max(r))]
de = [(x - far) * HARTREE for x in e]
i = de.index(min(de))
print("minimum %.3f A %.1f kJ/mol" % (r[i], de[i]))
for want in (4.0, 3.0, 2.5, 2.0, 1.5, 1.2, 1.0, 0.8, 0.75, 0.7, 0.5, 0.4):
    k = min(range(len(r)), key=lambda k: abs(r[k] - want))
    print("%.2f %.1f" % (r[k], de[k]))

fig, ax = plt.subplots(figsize=(6.4, 3.9))
ax.axhline(0, color="#555555", lw=1.0, ls="--")
# a dot for every computed point, so the curve is visibly made of them
ax.plot(r, de, "-o", color="#0072B2", lw=1.4, ms=3.5, label="computed point")
ax.legend(loc="lower right", fontsize=9, frameon=False)
ax.plot([r[i]], [de[i]], "o", color="#D55E00", ms=6, zorder=5)
ax.plot([r[i], 3.3], [de[i], de[i]], ":", color="#D55E00", lw=1.2)
ax.annotate("", xy=(3.3, de[i]), xytext=(3.3, 0),
            arrowprops=dict(arrowstyle="<->", color="#D55E00", lw=1.4))
ax.text(3.38, de[i] / 2, "bond energy\n%.0f kJ/mol" % -de[i], color="#D55E00", fontsize=9, va="center")
ax.annotate("bond length %.2f Å" % r[i], xy=(r[i], de[i]), xytext=(r[i] + 0.25, de[i] - 30),
            fontsize=9, color="#D55E00", va="top")
ax.text(4.0, 25, "atoms apart:\nno attraction", fontsize=9, ha="center", va="bottom", color="#333333")
ax.text(1.62, -330, "electrons drawn\nto both nuclei", fontsize=9, ha="left", color="#333333")
ax.text(0.47, 60, "nuclei\nrepel", fontsize=9, ha="left", color="#333333")
ax.set_xlim(0.3, 5.05)
ax.set_ylim(-520, 110)
ax.set_xlabel("H–H distance (Å)", fontsize=10)
ax.set_ylabel("energy (kJ/mol)", fontsize=10)
ax.grid(color="#e6e6e6", lw=0.6)
fig.tight_layout()
fig.savefig(out, dpi=200, facecolor="white")
