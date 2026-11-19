#!/usr/bin/env python3
"""Append MANIFEST.tsv rows for the Teaching-part figures made with this folder's
scripts (replaces rows of the same file): python3 manifest_rows.py <MANIFEST.tsv>"""
import sys

V, C, D = "9.5.3-dev", "59577d64b", "2026-11-18"
SHOT = ("headless Builder (tests/apps harness, isolated HOME, local data, Xvfb) on beryllium, "
        "calculations/teaching-figures/shots_teaching.py with %s; ECCE_VIEWER_SCENE: background 1 1 1, %s, "
        "saveimage 2 white; white margin trimmed with ImageMagick -trim -border 30")
DIAG = ("headless Builder (tests/apps harness, isolated HOME, local data, Xvfb) on beryllium, "
        "calculations/teaching-figures/shots_teaching.py with %s; scene modioptions 0, plotshot <name> 1000 700 "
        "MO Diagram; cropped above the hint line by calculations/teaching-figures/crop_diagram.py")
GC = "stored example genchem/"
DIA = GC + "molecular-orbitals-of-diatomics/ecceqm-"
POL = GC + "polar-bonds-and-dipole-moments/ecceqm-"
VS = GC + "vsepr/ecceqm-"
REDO = " (wip/teaching-redo 8e3703bed, pre-parsed)"
rows = []


def shot(path, spec, src, how, kind="saveimage factor 2"):
    rows.append((path, kind, SHOT % (spec + ", " + src, how)))


def diag(path, spec, src):
    rows.append((path, "screenshot", DIAG % (spec + ", " + src)))


for m, orbs in (("hf", {3: "sigma", 4: "pi", 6: "sigmastar"}), ("lih", {2: "sigma", 3: "lumo"}),
                ("co", {4: "sigma", 5: "pi", 7: "homo", 8: "pistar"})):
    src = DIA + {"hf": "HF", "lih": "LiH", "co": "CO"}[m]
    for n, t in orbs.items():
        shot("polarised-bonds/%s-%s.ecce-%s.png" % (m, t, V), "spec_a.py", src,
             "ECCE_OPEN_PANEL=MOs, rotate 90, moselect %d, mopanel compute, viewall" % n)
    diag("polarised-bonds/%s-diagram.ecce-%s.png" % (m, V), "spec_a.py", src)
for t, n in (("sigma", 1), ("sigmastar", 2)):
    shot("bond-order/h2-%s.ecce-%s.png" % (t, V), "spec_a.py", DIA + "H2",
         "ECCE_OPEN_PANEL=MOs, rotate 90, moselect %d, mopanel compute, viewall" % n)
diag("bond-order/h2-diagram.ecce-%s.png" % V, "spec_a.py", DIA + "H2")
for f, src, n, view in (("n2-sigma", "N2", 7, "rotate 90"), ("n2-pi", "N2", 5, "rotate 90"),
                        ("f2-sigma", "F2", 5, "rotate 90"), ("f2-pi", "F2", 7, "rotate 90 (spec_b.py)"),
                        ("o2-pistar", "O2", 9, "rotate 90 (spec_b.py)")):
    shot("diatomics/%s.ecce-%s.png" % (f, V), "spec_a.py/spec_b.py", DIA + src,
         "ECCE_OPEN_PANEL=MOs, moselect %d, mopanel compute, %s, viewall" % (n, view))
for m in ("n2", "f2", "o2"):
    diag("diatomics/%s-diagram.ecce-%s.png" % (m, V), "spec_a.py", DIA + m.upper())
diag("diatomics/b2-diagram.ecce-%s.png" % V, "spec_c.py", DIA + "B2" + REDO)
VIEW = {"a": "no turn", "b": "rotate 90", "c": "rotatex 90", "d": "rotate 35, rotatex 20",
        "e": "rotate 20, rotatex 30", "f": "rotatex 30, rotate 20", "g": "rotate 60, rotatex 25",
        "h": "rotate 45, rotatex 35"}
for m, v in (("becl2", "b"), ("bf3", "a"), ("h2o", "b"), ("clf3", "b"), ("ch4", "e"), ("nh3", "e"),
             ("pf5", "f"), ("sf4", "e"), ("sf6", "h"), ("brf5", "e")):
    name = {"becl2": "BeCl2", "bf3": "BF3", "h2o": "H2O", "clf3": "ClF3", "ch4": "CH4", "nh3": "NH3",
            "pf5": "PF5", "sf4": "SF4", "sf6": "SF6", "brf5": "BrF5"}[m]
    shot("shapes/%s.ecce-%s.png" % (m, V), "spec_a.py/spec_b.py", VS + name, "%s, viewall (structure only)" % VIEW[v])
for m, n, v in (("ch4", 2, "rotatex 45 (spec_b.py)"), ("bf3", 5, "no turn"), ("becl2", 12, "rotate 90")):
    shot("hybridisation/%s-bond.ecce-%s.png" % (m, V), "spec_a.py/spec_b.py",
         VS + {"ch4": "CH4", "bf3": "BF3", "becl2": "BeCl2"}[m],
         "ECCE_OPEN_PANEL=MOs, mofield Localised MO, moselect %d, mopanel compute, %s, viewall" % (n, v))
rows.append(("h2-bond/h2-curve.ecce-%s.png" % V, "plot from ECCE data",
             "python3 calculations/teaching-figures/plot_h2_curve.py <stored Props of genchem/bond-formation/"
             "orca-h2_bond_curve> <png>; SCANCOORD/SCANENERGY relative to the 5.0 A point"))
rows.append(("density-views/homo-lumo-scis.ecce-%s.png" % V, "saveimage factor 2",
             SHOT % ("spec_a.py, stored butadiene-scis-optfreq (calculations/scans run_l1a.py, l1a-redo)",
                     "ECCE_OPEN_PANEL=MOs, moselect 15 (HOMO) / 16 (LUMO), mopanel compute, rotatex 65 (view f), viewall") +
             "; the two placed side by side, each on 900x620"))
rows.append(("dipoles/bond-dipoles.ecce-%s.png" % V, "plot from ECCE data",
             "python3 calculations/teaching-figures/plot_bond_dipoles.py <png> NAME=<qmout> for CO2 SO2 H2O_dipole "
             "BF3_dipole NH3_dipole CH3F of " + POL + "*" + REDO + ": CHELPG charges, geometry, dipole_debye"))
rows.append(("polar-ionic/charge-scale.ecce-%s.png" % V, "plot from ECCE data",
             "python3 calculations/teaching-figures/plot_charge_scale.py <png> for HBr HCl HF_dipole LiH_dipole "
             "LiF_dipole NaCl_dipole of " + POL + "*" + REDO + "; measured q/e from the chapter table"))
E = "mofield ESP on Density, mopanel esp (ESP range Auto)"
for f, spec, src, how in (("polar-ionic/nacl-nci", "spec_d.py", "NaCl_dipole", "mofield NCI, mopanel nci, rotate 60"),
                          ("polar-ionic/hf-nci", "spec_c.py", "HF_dipole", "rotate 90, mofield NCI, mopanel nci (no surface drawn)"),
                          ("polar-ionic/nacl-esp", "spec_c.py", "NaCl_dipole", "rotate 90, " + E),
                          ("polar-ionic/hf-esp", "spec_c.py", "HF_dipole", "rotate 90, " + E),
                          ("dipoles/co2-esp", "spec_c.py", "CO2", E + ", rotate 90"),
                          ("dipoles/so2-esp", "spec_c.py", "SO2", E + ", rotate 90"),
                          ("dipoles/h2o-esp", "spec_d.py", "H2O_dipole", E + ", rotate 90, rotatex 90")):
    shot("%s.ecce-%s.png" % (f, V), spec, POL + src + REDO, "ECCE_OPEN_PANEL=MOs, " + how + ", viewall")

# Second round (2026-11-19): one scale per figure, ECCE-drawn pictures only.
ONE = ("; then calculations/teaching-figures/scale_group.py: each picture shrunk by R/R_max "
       "(R the padded atom-box radius) and all cut to one box, so the figure has one scale")
H = "headless Builder (tests/apps harness, isolated HOME, local data, Xvfb) on beryllium, origin/main 59577d64b, "
over = {}
for m in ("becl2", "bf3", "ch4", "nh3", "h2o", "pf5", "sf4", "clf3", "sf6", "brf5"):
    over["shapes/%s.ecce-%s.png" % (m, V)] = ("saveimage factor 2", H + "shots_teaching.py spec_g.py (WITH_SHAPES, "
        "from spec_f.py) on " + VS + "*: background 1 1 1, view turn, viewall, zoom 1.15, saveimage 2 white" + ONE)
for m in ("becl2", "bf3", "ch4"):
    over["hybridisation/%s-bond.ecce-%s.png" % (m, V)] = ("saveimage factor 2", H + "shots_teaching.py spec_h.py "
        "group hy: view turn, viewall, mofield Localised MO, moselect, mopanel compute, saveimage 2 white" + ONE)
for m in ("co2", "so2", "h2o", "bf3", "nh3", "ch3f"):
    over["dipoles/dip-%s.ecce-%s.png" % (m, V)] = ("saveimage factor 2", H + "shots_teaching.py spec_g.py, "
        "ECCE_OPEN_PANEL=Dipole Moment, ECCE_BUILDER_SCRIPT: background 1 1 1, view turn, viewall, zoom 1.3, "
        "bonddipoles on ESPFIT, vector DIPOLE, saveimage 2 white; " + POL + "*" + REDO + ONE)
for f in ("hf-sigma", "hf-pi", "hf-sigmastar", "lih-sigma", "co-sigma", "co-pi", "co-homo", "co-pistar"):
    over["polarised-bonds/%s.ecce-%s.png" % (f, V)] = ("saveimage factor 2", H + "shots_teaching.py spec_h.py "
        "group pb: rotate 90, viewall on the atoms, zoom 1/2.4, mofield MO, moselect, mopanel compute, saveimage 2 white" + ONE)
for f in ("n2-sigma", "n2-pi", "f2-sigma", "f2-pi"):
    over["diatomics/%s.ecce-%s.png" % (f, V)] = ("saveimage factor 2", H + "shots_teaching.py spec_h.py "
        "group da: rotate 90, viewall on the atoms, zoom 1/1.5, mofield MO, moselect, mopanel compute, saveimage 2 white" + ONE)
for f in ("co2-esp", "so2-esp", "h2o-esp"):
    over["dipoles/%s.ecce-%s.png" % (f, V)] = ("saveimage factor 2", H + "shots_teaching.py spec_h.py group dp: "
        "view turn, viewall on the atoms, zoom 1/2.2, mofield ESP on Density, mopanel esp (Auto range)" + REDO + ONE)
for f in ("nacl-nci", "nacl-esp", "hf-nci", "hf-esp"):
    over["polar-ionic/%s.ecce-%s.png" % (f, V)] = ("saveimage factor 2", H + "shots_teaching.py spec_h.py group pi: "
        "view turn, viewall on the atoms, zoom 1/2.4, mofield NCI / ESP on Density, mopanel nci / esp" + REDO + ONE)
over["diatomics/o2-spin.ecce-%s.png" % V] = ("saveimage factor 2", H + "shots_teaching.py spec_e.py, " + DIA +
    "O2: rotate 90, mofield Spin Density, mopanel compute, viewall, saveimage 2 white; trimmed -border 30")
over["h2-bond/h2-curve.ecce-%s.png" % V] = ("screenshot", H + "shots_teaching.py spec_g.py, ECCE_OPEN_PANEL=Relaxed "
    "Scan, plotshot h2-curve 1000 700 Relaxed Scan (kJ/mol, Zero: Lowest point) of genchem/bond-formation/"
    "orca-h2_bond_curve; plot area cropped (1000x418+0+150)")
rows = [r for r in rows if r[0] not in over and not r[0].startswith(("dipoles/bond-dipoles", "polarised-bonds/lih-lumo"))]
rows += [(p, k, how) for p, (k, how) in over.items()]

path = sys.argv[1]
lines = open(path).read().splitlines()
mine = {r[0] for r in rows}
keep = [l for l in lines if l.split("\t", 1)[0] not in mine]
keep += ["\t".join((p, V, C, k, how, D)) for p, k, how in rows]
open(path, "w").write("\n".join(keep) + "\n")
print(len(rows), "rows")
