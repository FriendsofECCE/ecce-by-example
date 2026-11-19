"""One-scale shots: VSEPR structures (spec_f), the hybridisation bond orbitals at
the same scale, bond-dipole arrows of the dipole topic (Dipole Moment panel,
Builder script hook "bonddipoles on ESPFIT") at one scale of their own, and the
Relaxed Scan plot of the H2 curve."""
import glob, math, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__))
F = runpy.run_path(os.path.join(HERE, "spec_f.py"))
W, VS, R, RMAX, VIEW = F["W"], F["VS"], F["R"], F["RMAX"], F["VIEW"]
EX = os.environ.get("EX_ROOT", "/nonexistent")
POL = os.path.join(EX, "polar-bonds-and-dipole-moments")
PAD = 0.4


def radius_of(mvm):
    lines = open(mvm).read().splitlines()
    n = int(next(l for l in lines if l.startswith("num_atoms:")).split()[1])
    k = next(i for i, l in enumerate(lines) if l.startswith("atom_list:"))
    xyz = [[float(x) for x in l.split()[1:4]] for l in lines[k + 1:k + 1 + n]]
    span = [max(p[i] for p in xyz) - min(p[i] for p in xyz) + 2 * PAD for i in range(3)]
    return 0.5 * math.sqrt(sum(s * s for s in span))


JOBS = dict(F["JOBS"]) if os.environ.get("WITH_SHAPES") else {}
# bond dipoles
DVIEW = {"CO2": ["rotate 90"], "SO2": ["rotate 90"], "H2O_dipole": ["rotate 90", "rotatex 90"],
         "BF3_dipole": [], "NH3_dipole": ["rotate 20", "rotatex 30"], "CH3F": ["rotate 90"]}
DR = {}
for m in DVIEW:
    g = glob.glob(os.path.join(POL, "ecceqm-" + m, "stored", m, "Parameters", "chemsys.mvm"))
    DR[m] = radius_of(g[0]) if g else 1.0
DMAX = max(DR.values()) * 1.25          # room for the arrows
for m, view in DVIEW.items():
    JOBS["g-dip-" + m.lower()] = (os.path.join(POL, "ecceqm-" + m, "stored", m), "Dipole Moment", [
        "SCRIPT", "wait 4000", "background 1 1 1"] + view + [
        "viewall", "zoom 1.3", "wait 1500", "bonddipoles on ESPFIT", "wait 1500",
        "vector DIPOLE", "wait 1000", "saveimage {png}/dip-%s.png 2 white" % m.lower(),
        "rotatex 90", "viewall", "zoom 1.3", "wait 1000", "saveimage {png}/dip-%s-x.png 2 white" % m.lower(),
        "rotate 90", "viewall", "zoom 1.3", "wait 1000", "saveimage {png}/dip-%s-y.png 2 white" % m.lower(), "wait 1000"])
# the H2 curve as the Relaxed Scan panel draws it
JOBS["g-h2curve"] = ("genchem/bond-formation/orca-h2_bond_curve", "Relaxed Scan",
                     W + ["hold 8", "plotshot h2-curve 1000 700 Relaxed Scan", "hold 2"])
