"""Teaching figures from stored examples that the redo does not change."""
import os
G = "genchem/"
DIA = G + "molecular-orbitals-of-diatomics/"
VS = G + "vsepr/"
HERE = os.path.dirname(os.path.abspath(__file__))
W = ["background 1 1 1", "hold 3"]


def mos(name, orbs, field=None, pre=("rotate 90",)):
    """Scene lines: each orbital of orbs {number: tag} drawn and saved."""
    lines = list(W) + list(pre)
    if field:
        lines.append("mofield " + field)
    for n, tag in orbs.items():
        lines += ["moselect %d" % n, "mopanel compute", "viewall", "saveimage {png}/%s-%s.png 2 white" % (name, tag)]
    return lines


def diagram(name):
    return W + ["modioptions 0", "plotshot %s-diagram 1000 700 MO Diagram" % name, "hold 2"]


VIEWS = (("a", []), ("b", ["rotate 90"]), ("c", ["rotatex 90"]), ("d", ["rotate 35", "rotatex 20"]))


def views(name):
    lines = list(W)
    for tag, steps in VIEWS:
        undo = [("rotatex " if s.startswith("rotatex") else "rotate ") + str(-float(s.split()[1]))
                for s in reversed(steps)]
        lines += steps + ["viewall", "saveimage {png}/%s-%s.png 2 white" % (name, tag)] + undo
    return lines


JOBS = {
    # polarised bonds
    "hf": (DIA + "ecceqm-HF", "MOs", mos("hf", {3: "sigma", 4: "pi", 6: "sigmastar"}) + diagram("hf")[2:]),
    "lih": (DIA + "ecceqm-LiH", "MOs", mos("lih", {2: "sigma", 3: "lumo"}) + diagram("lih")[2:]),
    "co": (DIA + "ecceqm-CO", "MOs", mos("co", {4: "sigma", 5: "pi", 7: "homo", 8: "pistar"}) + diagram("co")[2:]),
    # bond order
    "h2": (DIA + "ecceqm-H2", "MOs", mos("h2", {1: "sigma", 2: "sigmastar"}) + diagram("h2")[2:]),
    "he2": (DIA + "ecceqm-He2", "MOs", diagram("he2")),
    # second-period diatomics
    "n2": (DIA + "ecceqm-N2", "MOs", mos("n2", {7: "sigma", 5: "pi"}) + diagram("n2")[2:]),
    "f2": (DIA + "ecceqm-F2", "MOs", mos("f2", {5: "sigma", 6: "pi"}) + diagram("f2")[2:]),
    "o2": (DIA + "ecceqm-O2", "MOs", mos("o2", {8: "pistar"}) + diagram("o2")[2:]),
    # shapes: structures from four views; localised lone pairs
    **{"s-" + m.lower(): (VS + "ecceqm-" + m, None, views("shape-" + m.lower()))
       for m in ("BeCl2", "BF3", "CH4", "NH3", "H2O", "PF5", "SF4", "ClF3", "SF6", "BrF5")},
    "sf4-lp": (VS + "ecceqm-SF4", "MOs", mos("sf4", {10: "lp"}, "Localised MO", ("rotate 35", "rotatex 20"))),
    "nh3-lp": (VS + "ecceqm-NH3", "MOs", mos("nh3", {2: "lp"}, "Localised MO", ("rotate 35", "rotatex 20"))),
    # hybridisation: one localised bond each
    "ch4-bond": (VS + "ecceqm-CH4", "MOs", mos("ch4", {2: "bond"}, "Localised MO", ("rotate 35", "rotatex 20"))),
    "bf3-bond": (VS + "ecceqm-BF3", "MOs", mos("bf3", {5: "bond"}, "Localised MO", ())),
    "becl2-bond": (VS + "ecceqm-BeCl2", "MOs", mos("becl2", {12: "bond"}, "Localised MO", ("rotate 90",))),
    # the H2 curve as ECCE plots it
    "h2curve": (G + "bond-formation/orca-h2_bond_curve", "Relaxed Scan",
                W + ["hold 8", "plotshot h2-curve 1000 700 Relaxed Scan", "hold 2"]),
    # butadiene HOMO/LUMO (chapter density-views), candidate views
    "butadiene": (os.path.join(HERE, "stored", "butadiene-scis-optfreq"), "MOs",
                  W + [l for n, tag in ((15, "homo"), (16, "lumo")) for l in
                       ["moselect %d" % n, "mopanel compute"] +
                       [x for v, st in (("a", []), ("b", ["rotatex 25"]), ("c", ["rotatex -25"]),
                                        ("d", ["rotate 25"]), ("e", ["rotatex 90", "rotatex 25"]),
                                        ("f", ["rotatex 90", "rotatex -25"]), ("g", ["rotate 90", "rotatex 25"]))
                        for x in st + ["viewall", "saveimage {png}/bd-%s-%s.png 2 white" % (tag, v)] +
                        [("rotatex " if s.startswith("rotatex") else "rotate ") + str(-float(s.split()[1]))
                         for s in reversed(st)]]]),
}
