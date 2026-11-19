"""The ten VSEPR structures, each after viewall and the same fixed zoom; R (the
radius of the padded atom box) is what scale_group.py uses to bring them to
one scale afterwards."""
import glob, math, os, runpy
A = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "spec_a.py"))
W, VS = A["W"], A["VS"]
REPO = os.environ.get("ECCE_SRC", os.getcwd())
PAD = 0.4
VIEW = {"BeCl2": ["rotate 90"], "BF3": [], "H2O": ["rotate 90"], "ClF3": ["rotate 90"],
        "CH4": ["rotate 20", "rotatex 30"], "NH3": ["rotate 20", "rotatex 30"],
        "PF5": ["rotatex 30", "rotate 20"], "SF4": ["rotate 20", "rotatex 30"],
        "SF6": ["rotate 45", "rotatex 35"], "BrF5": ["rotate 20", "rotatex 30"]}


def radius(name):
    mvm = glob.glob(os.path.join(REPO, "data", "client", "examples", VS, "ecceqm-" + name,
                                 "stored", "*", "Parameters", "chemsys.mvm"))[0]
    lines = open(mvm).read().splitlines()
    n = int(next(l for l in lines if l.startswith("num_atoms:")).split()[1])
    k = next(i for i, l in enumerate(lines) if l.startswith("atom_list:"))
    xyz = [[float(x) for x in l.split()[1:4]] for l in lines[k + 1:k + 1 + n]]
    span = [max(p[i] for p in xyz) - min(p[i] for p in xyz) + 2 * PAD for i in range(3)]
    return 0.5 * math.sqrt(sum(s * s for s in span))


R = {m: radius(m) for m in VIEW}
RMAX = max(R.values())
JOBS = {"f-" + m.lower(): (VS + "ecceqm-" + m, None,
                           W + VIEW[m] + ["viewall", "zoom 1.15",
                                          "saveimage {png}/scaled-%s.png 2 white" % m.lower()])
        for m in VIEW}
