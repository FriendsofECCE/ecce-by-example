#!/usr/bin/env python3
"""Numbers for NOTES.txt from the run_l1b.py outputs (ORCA's own printout):
final energies, H, S term, G at 298.15 K, imaginary frequencies, the forming
C1-C11 / C4-C12 distances, IRC end points, and the reaction profile against
the separated reactants (gauche butadiene + ethene).

    python3 analyse_l1b.py <outdir of run_l1b.py>
"""
import glob, math, os, re, sys

D = os.path.abspath(sys.argv[1])
EH = 2625.4996  # kJ/mol per Eh


def out(name):
    f = glob.glob(os.path.join(D, name, "Outputs", "*.orcaout"))
    return open(f[0], errors="replace").read() if f else ""


def last(pat, t):
    m = re.findall(pat, t)
    return float(m[-1]) if m else None


def geom(t):
    i = t.rfind("CARTESIAN COORDINATES (ANGSTROEM)")
    a = []
    for l in t[i:].splitlines()[2:]:
        w = l.split()
        if len(w) != 4:
            break
        a.append([float(x) for x in w[1:]])
    return a


def xyz(path):
    l = open(path).read().splitlines()
    return [[float(x) for x in s.split()[1:4]] for s in l[2:2 + int(l[0])]]


def bonds(g):
    return "C1-C11 %.3f A, C4-C12 %.3f A" % (math.dist(g[0], g[10]), math.dist(g[3], g[11]))


rows = {}
for name in ("da-butadiene-gauche-optfreq", "da-ethene-optfreq", "da-reactant-complex",
             "da-cyclohexene-optfreq", "da-ts-nebts", "da-ts-irc"):
    t = out(name)
    if not t:
        print("%s: no output" % name); continue
    e = last(r"FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)", t)
    h = last(r"Total Enthalpy\s+\.\.\.\s+(-?\d+\.\d+)", t)
    ts = last(r"Final entropy term\s+\.\.\.\s+(-?\d+\.\d+)", t)
    g = last(r"Final Gibbs free energy\s+\.\.\.\s+(-?\d+\.\d+)", t)
    imag = re.findall(r"^\s*\d+:\s+(-\d+\.\d+) cm\*\*-1\s+\*\*\*imaginary mode\*\*\*", t, re.M)
    rows[name] = (e, h, ts, g)
    print("%s: E %s Eh, H %s Eh, T*S %s Eh, G %s Eh, imaginary %s" % (name, e, h, ts, g, imag or "none"))
    if name not in ("da-butadiene-gauche-optfreq", "da-ethene-optfreq") and len(geom(t)) == 16:
        print("   final geometry: " + bonds(geom(t)))
    if name == "da-ts-irc":
        for f in sorted(glob.glob(os.path.join(D, name, "rundir", "**", "*IRC_[FB]*.xyz"), recursive=True)):
            print("   %s: %s" % (os.path.basename(f), bonds(xyz(f))))
        m = re.search(r"IRC PATH SUMMARY(.*?)(?:\n\n\n|Timings)", t, re.S)
        if m:
            print("   IRC summary:" + m.group(1)[:3000])

sep = ("da-butadiene-gauche-optfreq", "da-ethene-optfreq")
if all(n in rows for n in sep):
    r = [rows[sep[0]][k] + rows[sep[1]][k] if None not in (rows[sep[0]][k], rows[sep[1]][k]) else None
         for k in range(4)]
    print("\nAgainst separated reactants, kJ/mol (298.15 K, 1 atm, ORCA RRHO):")
    for n, lab in (("da-ts-nebts", "activation (TS)"), ("da-cyclohexene-optfreq", "reaction (product)"),
                   ("da-reactant-complex", "complex (E only)")):
        if n in rows:
            v = rows[n]
            d = ["%.1f" % ((v[k] - r[k]) * EH) if None not in (v[k], r[k]) else "-" for k in range(4)]
            tds = (v[2] - r[2]) * EH if None not in (v[2], r[2]) else None
            print("  %-20s dE %s  dH %s  dS %s J/(mol K)  dG %s" % (lab, d[0], d[1],
                  "%.1f" % (tds / 298.15 * 1000) if tds is not None else "-", d[3]))
