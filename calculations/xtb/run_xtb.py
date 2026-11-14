#!/usr/bin/env python3
"""Chapter xtb: caffeine with GFN2-xTB (optimisation + frequencies, gas and
ALPB water), GFN-FF (optimisation) and GFN2-xTB molecular dynamics, through
ECCE's real generator (ai.xtb) and Launch, local data.

    ECCE_SRC=<ECCE checkout with build-cmake> python3 run_xtb.py <outdir>
"""
import os, shutil, sys, time
REPO = os.environ.get("ECCE_SRC", "ECCE")
sys.path.insert(0, os.path.join(REPO, "tests", "launch"))
sys.path.insert(0, os.path.join(REPO, "tests", "apps"))
import harness
from harness import say
import xtb_test as xt
OUT = os.path.abspath(sys.argv[1])
HERE = os.path.dirname(os.path.abspath(__file__))
build = os.path.join(os.environ["BLD"], "b") if "BLD" in os.environ else os.path.join(REPO, "build-cmake")


def readxyz(path):
    lines = open(path).read().splitlines()
    n = int(lines[0])
    return [(l.split()[0],) + tuple(float(v) for v in l.split()[1:4]) for l in lines[2:2 + n]]


START = readxyz(os.path.join(HERE, "00-start-caffeine", "caffeine-obabel.xyz"))
WATER = "ES.Theory.Solvent.Model:\tALPB\nES.Theory.Solvent.Name:\twater\n"
MD = ("ES.Runtype.MD.Temperature:\t300\nES.Runtype.MD.Time:\t20\n"
      "ES.Runtype.MD.Step:\t2\nES.Runtype.MD.Dump:\t50\nES.Runtype.MD.Shake:\tX-H bonds\n")
# name, theory, run type (ECCE's internal name), extra .param lines, start
JOBS = [
    ("01-xtb-gfn2-optfreq-gas", "GFN2-xTB", "GeoVib", "", "start"),
    ("02-xtb-gfn2-optfreq-water", "GFN2-xTB", "GeoVib", WATER, "start"),
    ("03-xtb-gfnff-opt", "GFN-FF", "Geometry", "", "start"),
    ("04-xtb-gfn2-md-300K", "GFN2-xTB", "Molecular Dynamics", MD, "01"),
]


def optimised(calc):
    """The final structure of a finished optimisation (xtbopt.xyz if stored)."""
    for root, _, files in os.walk(calc):
        for f in files:
            if f.endswith(".xyz") and "opt" in f:
                return readxyz(os.path.join(root, f))
    return None


s = harness.Session(build, "bookxtb", {"xTB": shutil.which("xtb")}, local=True, keep=True)
work = os.path.join(s.state, "decks")
rundir = os.path.join(s.state, "run")
shutil.rmtree(work, ignore_errors=True)
os.makedirs(work)
os.makedirs(rundir, exist_ok=True)
os.makedirs(OUT, exist_ok=True)
done = {}
try:
    assert s.services(True)
    for name, theory, rt, extra, start in JOBS:
        atoms = START
        if start != "start":
            atoms = optimised(done.get(start, "")) or START
            say("%s starts from %s" % (name, "the optimised structure of " + start
                                        if atoms is not START else "the start structure"))
        level = "normal"
        text, rc = xt.deck(atoms, rt, level=level, theory=theory, extra=extra)
        say("deck %s rc=%d" % (name, rc))
        deck = os.path.join(work, name + ".xtbin")
        open(deck, "w").write(text)
        xyz = os.path.join(work, name + ".xyz")
        open(xyz, "w").write("%d\ncaffeine\n%s" % (len(atoms), "".join(
            "%s %.6f %.6f %.6f\n" % a for a in atoms)))
        url, out = s.create(name, "xtb_es", deck, "xtb.xtbin", rundir,
                            extra=("procs=4", "code=xTB", "xyz=" + xyz,
                                   "theory=SE:" + theory, "runtype=" + rt))
        say("created %s" % url)
        t0 = time.time()
        rc, out = s.launch(url)
        say(out[-400:])
        st = s.waitState(url, seconds=3600)
        say("%s: %s in %.0f s" % (name, st, time.time() - t0))
        calc = url[len("file://"):].rstrip("/")
        dest = os.path.join(OUT, name)
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(calc, dest, symlinks=True)
        done[name[:2]] = dest
        open(os.path.join(OUT, name + ".url"), "w").write("%s\n%s %.0f s\n" % (url, st, time.time() - t0))
finally:
    s.stop()
