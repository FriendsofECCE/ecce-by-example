"""Spin density of O2 (alpha minus beta), bond across the page as o2-pistar."""
import os, runpy
A = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "spec_a.py"))
W, DIA = A["W"], A["DIA"]

JOBS = {
    "o2-spin": (DIA + "ecceqm-O2", "MOs", list(W) + [
        "rotate 90", "mofield Spin Density", "mopanel compute", "hold 15", "mosurf o2-spinsurf",
        "viewall", "saveimage {png}/o2-spin-a.png 2 white",
        "rotatex 90", "viewall", "saveimage {png}/o2-spin-b.png 2 white", "rotatex -90",
        "rotatex 45", "viewall", "saveimage {png}/o2-spin-c.png 2 white"]),
}
