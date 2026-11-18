"""Retakes of batch A from other directions (shapes, CH4 bond, F2 pi, O2 pi*)."""
import os, runpy
A = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "spec_a.py"))
G, DIA, VS, W, mos = A["G"], A["DIA"], A["VS"], A["W"], A["mos"]

V = (("e", ["rotate 20", "rotatex 30"]), ("f", ["rotatex 30", "rotate 20"]),
     ("g", ["rotate 60", "rotatex 25"]), ("h", ["rotate 45", "rotatex 35"]))


def views(name, vs=V):
    lines = list(W)
    for tag, steps in vs:
        undo = [("rotatex " if s.startswith("rotatex") else "rotate ") + str(-float(s.split()[1]))
                for s in reversed(steps)]
        lines += steps + ["viewall", "saveimage {png}/%s-%s.png 2 white" % (name, tag)] + undo
    return lines


def mo_views(name, n, field, vs):
    lines = list(W) + (["mofield " + field] if field else []) + ["moselect %d" % n, "mopanel compute"]
    return lines + views(name, vs)[len(W):]


JOBS = {
    **{"s-" + m.lower(): (VS + "ecceqm-" + m, None, views("shape-" + m.lower()))
       for m in ("PF5", "SF4", "SF6", "BrF5", "NH3", "CH4")},
    "ch4-bond": (VS + "ecceqm-CH4", "MOs", mo_views("ch4-bond", 2, "Localised MO",
                 (("a", ["rotatex 90"]), ("b", ["rotatex 90", "rotate 90"]), ("c", ["rotate 60"]),
                  ("d", ["rotate 90", "rotatex 90"]), ("e", ["rotate 30"]), ("f", ["rotatex 45"])))),
    "f2-pi": (DIA + "ecceqm-F2", "MOs", mo_views("f2-pi7", 7, None, (("a", ["rotate 90"]), ("b", ["rotate 90", "rotatex 90"])))),
    "o2-pistar": (DIA + "ecceqm-O2", "MOs", mo_views("o2-pistar9", 9, None,
                  (("a", ["rotate 90"]), ("b", ["rotate 90", "rotatex 90"]), ("c", ["rotate 90", "rotatex 45"])))),
}
