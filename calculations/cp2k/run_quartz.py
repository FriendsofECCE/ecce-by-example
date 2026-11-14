#!/usr/bin/env python3
"""Chapter cp2k: alpha-quartz 2x2x2 supercell, CP2K energy and geometry
optimisation through ECCE's real generator (ai.cp2k) and Launch, local data."""
import math, os, shutil, sys, time, importlib.util
REPO = os.environ.get("ECCE_SRC", "ECCE")  # an ECCE checkout with a build in build-cmake
sys.path.insert(0, os.path.join(REPO, "tests", "launch"))
sys.path.insert(0, os.path.join(REPO, "tests", "apps"))
import harness
from harness import say
spec = importlib.util.spec_from_file_location("cp2k_features", os.path.join(REPO, "tests", "cp2k_features", "run_tests.py"))
feat = importlib.util.module_from_spec(spec); spec.loader.exec_module(feat)
OUT = sys.argv[1]
GUI = ["ES.Theory.GPW.MaxScf: 30"]  # the editor's default for a new calculation (OT on)
A, C = 4.9134, 5.4052   # alpha-quartz, P3_121 (tests/fixtures/cif/quartz.cif)
FRAC = [("O",0.14660,0.73310,0.45227),("O",0.26690,0.41350,0.78560),("O",0.41350,0.26690,0.21440),
        ("O",0.58650,0.85340,0.11893),("O",0.73310,0.14660,0.54773),("O",0.85340,0.58650,0.88107),
        ("Si",0.0,0.46970,2/3),("Si",0.46970,0.0,1/3),("Si",0.53030,0.53030,0.0)]
av = (A, 0.0, 0.0); bv = (-A/2, A*math.sqrt(3)/2, 0.0); cv = (0.0, 0.0, C)
atoms = []
for i in range(2):
    for j in range(2):
        for k in range(2):
            for el, x, y, z in FRAC:
                f = (x+i, y+j, z+k)
                atoms.append((el,)+tuple(f[0]*av[n]+f[1]*bv[n]+f[2]*cv[n] for n in range(3)))
lat = ["%.6f %.6f %.6f" % tuple(2*v for v in vec) for vec in (av, bv, cv)]
QZ = dict(title="quartz", lattice=lat, atoms=atoms)
MVM = ("title: quartz\ntype: crystal\nnum_atoms: %d\natom_info: symbol cart\nlattice_vectors:\n%s\natom_list:\n%s"
       "attr_list:\n%satom_type_list:\n%snum_bonds: 0\nbond_list:\n") % (
    len(atoms), "\n".join(lat), "".join("%s %.6f %.6f %.6f\n" % a for a in atoms),
    " 0.000000   1   0   0   0\n"*len(atoms),
    "".join("       %d   %d\n" % ((14, 4) if a[0]=="Si" else (8, 2)) for a in atoms))
s = harness.Session(os.path.join(REPO, "build-cmake"), "bookcp2k", {"CP2K": shutil.which("cp2k.psmp")}, local=True, keep=True)
work = os.path.join(s.state, "decks"); rundir = os.path.join(s.state, "run")
shutil.rmtree(work, ignore_errors=True); os.makedirs(work); os.makedirs(rundir, exist_ok=True)
xyz = os.path.join(work, "quartz.xyz")
open(xyz, "w").write("%d\nalpha-quartz 2x2x2\n%s" % (len(atoms), "".join("%s %.6f %.6f %.6f\n" % a for a in atoms)))
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "quartz-start.mvm"), "w").write(MVM)
try:
    assert s.services(True)
    for name, rt, params in (("quartz-energy", "Energy", GUI), ("quartz-opt", "Geometry", GUI)):
        text, err, rc = feat.deck(QZ, rt, params)
        say("deck %s rc=%d %s" % (name, rc, err[-300:]))
        deck = os.path.join(work, name + ".cp2kin"); open(deck, "w").write(text)
        url, out = s.create(name, "cp2k_es", deck, "cp2k.cp2kin", rundir,
                            extra=("procs=4", "code=CP2K", "xyz=" + xyz, "theory=QS:GPW", "runtype=" + rt))
        say("created %s" % url)
        calc = url[len("file://"):].rstrip("/")
        open(os.path.join(calc, "Parameters", "chemsys.mvm"), "w").write(MVM)
        t0 = time.time(); rc, out = s.launch(url); say(out[-500:])
        st = s.waitState(url, seconds=5400)
        say("%s: %s in %.0f s" % (name, st, time.time()-t0))
        dest = os.path.join(OUT, name); shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(calc, dest, symlinks=True)
        open(os.path.join(OUT, name + ".url"), "w").write(url + "\n%s %.0f s\n" % (st, time.time()-t0))
finally:
    s.stop()
