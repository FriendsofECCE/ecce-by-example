"""One scale per figure for orbital, ESP and NCI pictures: viewall on the atoms
before any surface is drawn, then zoom by M * R_max / R (R the radius of the
padded atom box, R_max the largest in the figure, M room for the surfaces), so
every picture of a figure has the same camera height."""
import glob, math, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__))
F = runpy.run_path(os.path.join(HERE, "spec_f.py"))
W, VS, VIEW = F["W"], F["VS"], F["VIEW"]
REPO = os.environ.get("ECCE_SRC", os.getcwd())
EX = os.environ.get("EX_ROOT", "/nonexistent")
PAD = 0.4


def mvm(path):
    return glob.glob(os.path.join(path, "stored", "*", "Parameters", "chemsys.mvm"))[0]


def radius(path):
    lines = open(mvm(path)).read().splitlines()
    n = int(next(l for l in lines if l.startswith("num_atoms:")).split()[1])
    k = next(i for i, l in enumerate(lines) if l.startswith("atom_list:"))
    xyz = [[float(x) for x in l.split()[1:4]] for l in lines[k + 1:k + 1 + n]]
    span = [max(p[i] for p in xyz) - min(p[i] for p in xyz) + 2 * PAD for i in range(3)]
    return 0.5 * math.sqrt(sum(s * s for s in span))


def stored(path):
    return [d for d in glob.glob(os.path.join(path, "stored", "*")) if os.path.isdir(d)][0]


GC = os.path.join(REPO, "data", "client", "examples", "genchem")
DIA = os.path.join(GC, "molecular-orbitals-of-diatomics")
VSP = os.path.join(GC, "vsepr")
POL = os.path.join(EX, "polar-bonds-and-dipole-moments")
JOBS = {}


def group(tag, margin, items):
    """items: [(job, example dir, view steps, [(field, panel cmd, moselect or None, picture)])]"""
    rmax = max(radius(p) for _, p, _, _ in items)
    for job, path, view, shots in items:
        z = 1.0 / margin   # the scene zoom divides the view height: < 1 zooms out
        lines = list(W) + view + ["viewall", "zoom %.4f" % z]
        for field, cmd, n, pic in shots:
            lines += ["mofield " + field] + (["moselect %d" % n] if n else []) + \
                     ["mopanel " + cmd, "hold 8", "saveimage {png}/%s.png 2 white" % pic]
        if tag in os.environ.get("GROUPS", tag).split(","):
            JOBS["%s-%s" % (tag, job)] = (stored(path), "MOs", lines)


R90 = ["rotate 90"]
group("pb", 2.4, [
    ("hf", os.path.join(DIA, "ecceqm-HF"), R90, [("MO", "compute", n, "hf-" + t) for n, t in ((3, "sigma"), (4, "pi"), (6, "sigmastar"))]),
    ("lih", os.path.join(DIA, "ecceqm-LiH"), R90, [("MO", "compute", n, "lih-" + t) for n, t in ((2, "sigma"), (3, "lumo"))]),
    ("co", os.path.join(DIA, "ecceqm-CO"), R90, [("MO", "compute", n, "co-" + t) for n, t in ((4, "sigma"), (5, "pi"), (7, "homo"), (8, "pistar"))])])
group("da", 1.5, [
    ("n2", os.path.join(DIA, "ecceqm-N2"), R90, [("MO", "compute", 7, "n2-sigma"), ("MO", "compute", 5, "n2-pi")]),
    ("f2", os.path.join(DIA, "ecceqm-F2"), R90, [("MO", "compute", 5, "f2-sigma"), ("MO", "compute", 7, "f2-pi")])])
group("hy", 1.0, [
    (m.lower(), os.path.join(VSP, "ecceqm-" + m), VIEW[m], [("Localised MO", "compute", n, "hy-%s-bond" % m.lower())])
    for m, n in (("BeCl2", 12), ("BF3", 5), ("CH4", 2))])
group("dp", 2.2, [
    ("co2", os.path.join(POL, "ecceqm-CO2"), R90, [("ESP on Density", "esp", None, "co2-esp")]),
    ("so2", os.path.join(POL, "ecceqm-SO2"), R90, [("ESP on Density", "esp", None, "so2-esp")]),
    ("h2o", os.path.join(POL, "ecceqm-H2O_dipole"), ["rotate 90", "rotatex 90"], [("ESP on Density", "esp", None, "h2o-esp")])])
group("pi", 2.4, [
    ("nacl", os.path.join(POL, "ecceqm-NaCl_dipole"), ["rotate 60"], [("NCI", "nci", None, "nacl-nci")]),
    ("naclesp", os.path.join(POL, "ecceqm-NaCl_dipole"), R90, [("ESP on Density", "esp", None, "nacl-esp")]),
    ("hf", os.path.join(POL, "ecceqm-HF_dipole"), R90, [("NCI", "nci", None, "hf-nci"), ("ESP on Density", "esp", None, "hf-esp")])])
