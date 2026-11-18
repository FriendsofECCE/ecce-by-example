"""Teaching figures from the calculations rerun or added on wip/teaching-redo
(their stored copies under $EX_ROOT = data/client/examples/genchem of that branch)."""
import os, runpy
A = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "spec_a.py"))
W, mos, diagram = A["W"], A["mos"], A["diagram"]
EX = os.environ.get("EX_ROOT", "/nonexistent")
DIA = os.path.join(EX, "molecular-orbitals-of-diatomics")
POL = os.path.join(EX, "polar-bonds-and-dipole-moments")


def stored(topic, name):
    return os.path.join(topic, "ecceqm-" + name, "stored", name)


def field(name, f, panel_cmd, pre=("rotate 90",), extra=()):
    return list(W) + list(pre) + ["mofield " + f, "mopanel " + panel_cmd, "hold 20"] + list(extra) + \
        ["viewall", "saveimage {png}/%s-a.png 2 white" % name,
         "rotate 90", "viewall", "saveimage {png}/%s-b.png 2 white" % name, "rotate -90",
         "rotatex 90", "viewall", "saveimage {png}/%s-c.png 2 white" % name]


JOBS = {
    "b2": (stored(DIA, "B2"), "MOs", mos("b2", {5: "pi", 7: "sigma"}) + diagram("b2")[2:]),
    "c2": (stored(DIA, "C2"), "MOs", diagram("c2")),
    "nacl-nci": (stored(POL, "NaCl_dipole"), "MOs", field("nacl-nci", "NCI", "nci", extra=("mosurf nacl-ncisurf",))),
    "nacl-esp": (stored(POL, "NaCl_dipole"), "MOs", field("nacl-esp", "ESP on Density", "esp", extra=("mobar nacl-espbar",))),
    "hf-nci": (stored(POL, "HF_dipole"), "MOs", field("hf-nci", "NCI", "nci", extra=("mosurf hf-ncisurf",))),
    "hf-esp": (stored(POL, "HF_dipole"), "MOs", field("hf-esp", "ESP on Density", "esp", extra=("mobar hf-espbar",))),
    "hf-dens": (stored(POL, "HF_dipole"), "MOs", field("hf-dens", "Density", "dens")),
    "co2-esp": (stored(POL, "CO2"), "MOs", field("co2-esp", "ESP on Density", "esp", pre=(), extra=("mobar co2-espbar",))),
    "so2-esp": (stored(POL, "SO2"), "MOs", field("so2-esp", "ESP on Density", "esp", pre=(), extra=("mobar so2-espbar",))),
    "h2o-esp": (stored(POL, "H2O_dipole"), "MOs", field("h2o-esp", "ESP on Density", "esp", pre=(), extra=("mobar h2o-espbar",))),
}
