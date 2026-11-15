#!/usr/bin/env python3
"""Numbers for NOTES from the run_l1c.py hbond outputs (ORCA .orcaout).

    python3 analyse_l1c.py <dir holding phenol-water-optfreq, phenol-optfreq, water-optfreq>
"""
import glob, math, os, re, sys

EH = 2625.4996  # kJ/mol per Eh
KCAL = 4.184


def out(d):
    return open(glob.glob(os.path.join(d, "Outputs", "*.orcaout"))[0], errors="replace").read()


def last(pat, t, cast=float):
    m = re.findall(pat, t, re.M)
    return cast(m[-1]) if m else None


def geom(t):
    i = t.rfind("CARTESIAN COORDINATES (ANGSTROEM)")
    g = []
    for line in t[i:].splitlines()[2:]:
        w = line.split()
        if len(w) != 4:
            break
        g.append((w[0], float(w[1]), float(w[2]), float(w[3])))
    return g


def angle(a, b, c):
    u = [a[k] - b[k] for k in range(3)]; v = [c[k] - b[k] for k in range(3)]
    return math.degrees(math.acos(sum(u[k] * v[k] for k in range(3)) /
                                  math.dist(a, b) / math.dist(c, b)))


def npa(t):
    i = t.rfind("Summary of Natural Population Analysis")
    if i < 0:
        return []
    rows = re.findall(r"^\s+([A-Z][a-z]?)\s+(\d+)\s+(-?\d+\.\d+)\s+\d+\.\d+", t[i:i + 4000], re.M)
    return ["%s%s %s" % r for r in rows]


root = os.path.abspath(sys.argv[1])
res = {}
for name in ("phenol-water-optfreq", "phenol-optfreq", "water-optfreq"):
    d = os.path.join(root, name)
    t = out(d if os.path.isdir(d) else os.path.join(root, "orca-" + name))
    freqs = [float(x) for x in re.findall(r"^\s+\d+:\s+(-?\d+\.\d+) cm\*\*-1", t[t.rfind("VIBRATIONAL FREQUENCIES"):], re.M)]
    r = dict(E=last(r"FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)", t),
             ZPE=last(r"Zero point energy\s+\.\.\.\s+(-?\d+\.\d+) Eh", t),
             H=last(r"Total Enthalpy\s+\.\.\.\s+(-?\d+\.\d+) Eh", t),
             G=last(r"Final Gibbs free energy\s+\.\.\.\s+(-?\d+\.\d+) Eh", t),
             mu=last(r"Magnitude \(Debye\)\s+:\s+(-?\d+\.\d+)", t),
             nimag=sum(1 for f in freqs if f < 0),
             lowest=min([f for f in freqs if abs(f) > 1e-3] or [0.0]),
             npa=npa(t), geom=geom(t))
    res[name] = r
    print("%s: E %.8f Eh, ZPE %s, H %s, G %s, dipole %s D, imaginary %d, lowest %.2f cm-1"
          % (name, r["E"], r["ZPE"], r["H"], r["G"], r["mu"], r["nimag"], r["lowest"]))
    print("  NPA: " + ", ".join(r["npa"]))
c, p, w = (res[k] for k in ("phenol-water-optfreq", "phenol-optfreq", "water-optfreq"))
for key, label in (("E", "electronic (De, incl. D3BJ)"), ("ZPE", None), ("H", "enthalpy 298 K"), ("G", "Gibbs 298 K")):
    if key == "ZPE":
        dE = (c["E"] + c["ZPE"]) - (p["E"] + p["ZPE"]) - (w["E"] + w["ZPE"]); label = "ZPE-corrected (D0)"
    else:
        dE = c[key] - p[key] - w[key]
    print("Interaction %s: %.6f Eh = %.2f kJ/mol = %.2f kcal/mol" % (label, dE, dE * EH, dE * EH / KCAL))
g = [a[1:] for a in c["geom"]]
print("H8...O14 %.3f A, O7...O14 %.3f A, O7-H8 %.4f A (phenol alone %.4f A), angle O7-H8...O14 %.1f deg"
      % (math.dist(g[7], g[13]), math.dist(g[6], g[13]), math.dist(g[6], g[7]),
         math.dist(p["geom"][6][1:], p["geom"][7][1:]), angle(g[6], g[7], g[13])))
