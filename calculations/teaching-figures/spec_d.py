"""Retakes of batch C from other directions: the NaCl NCI disc seen at an angle, water's ESP in its plane."""
import os, runpy
C = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "spec_c.py"))
W, stored, POL = C["W"], C["stored"], C["POL"]


def turned(name, f, cmd, views):
    lines = list(W) + ["mofield " + f, "mopanel " + cmd, "hold 20"]
    for tag, steps in views:
        undo = [("rotatex " if s.startswith("rotatex") else "rotate ") + str(-float(s.split()[1]))
                for s in reversed(steps)]
        lines += steps + ["viewall", "saveimage {png}/%s-%s.png 2 white" % (name, tag)] + undo
    return lines


JOBS = {
    "nacl-nci2": (stored(POL, "NaCl_dipole"), "MOs", turned("nacl-nci2", "NCI", "nci",
                  (("a", ["rotate 60"]), ("b", ["rotate 50", "rotatex 20"]), ("c", ["rotate 120"])))),
    "h2o-esp2": (stored(POL, "H2O_dipole"), "MOs", turned("h2o-esp2", "ESP on Density", "esp",
                 (("d", ["rotatex 90", "rotate 90"]), ("e", ["rotate 90", "rotatex 90"]),
                  ("f", ["rotate 90", "rotatex -90"]), ("g", ["rotatex -90"])))),
}
