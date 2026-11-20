#!/usr/bin/env python3
"""Chapter clays: a Na-montmorillonite model with MINFF in GROMACS, made the
way a person makes it in ECCE (Organizer New > GROMACS MD study with Prepare,
Optimize, Equilibrate and Dynamics; the Prepare editor's Mineral (MINFF)
source), driven through the editors' test hooks and run through the real
Launch, local data, private Xvfb.

    ECCE_SRC=<ECCE checkout with build-cmake> python3 run_clay.py <outdir>

Needs gmx, Xvfb, atomipy (ECCE_ATOMIPY_PYTHON or importable) and the pinned
min.ff download (scripts/minff_topology.py fetch_pinned). Each finished task
is copied to <outdir>/<NN-task>; the editors' window shots go to <outdir>/png.
"""
import os, re, shutil, subprocess, sys, time
REPO = os.environ.get("ECCE_SRC", "ECCE")
sys.path.insert(0, os.path.join(REPO, "tests", "launch"))
sys.path.insert(0, os.path.join(REPO, "tests", "apps"))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import harness
from harness import say
from gromacs_test import Editor
import minff_topology as mt
import xdisplay

OUT = os.path.abspath(sys.argv[1])
PNG = os.path.join(OUT, "png")
build = os.path.join(os.environ["BLD"], "b") if "BLD" in os.environ else os.path.join(REPO, "build-cmake")
CELL = os.path.join(REPO, "third_party", "minff", "unit_cells",
                    "Pyrophyllite_Lee_Guggenheim_1981_GII_0.071.pdb")
# The model: 6 x 4 x 1 pyrophyllite cells (one layer per periodic cell, so
# the water layer on top is the interlayer), 18 octahedral Al -> Mg
# (0.75 per Al4Si8O20(OH)4 cell), 18 Na+ in 0.6 nm of water.
REPEAT, SUBS, SEED, WATER_NM, ION = "6 4 1", "Al,Mgo,18", "1", "0.6", "Na"
STEPS = {"optimize": "5000", "equilibrate": "50000", "dynamics": "500000"}
NPT = ("pcoupl = C-rescale\\npcoupltype = semiisotropic\\ntau-p = 5.0\\n"
       "ref-p = 1.0 1.0\\ncompressibility = 4.5e-5 4.5e-5")


def where(u):
    return u[len("file://"):].rstrip("/")


def subdirs(d):
    return sorted(x for x in os.listdir(d) if not x.startswith(".")
                  and os.path.isdir(os.path.join(d, x)))


gmx = shutil.which("gmx")
py = mt.find_atomipy_python()
ffdir = mt.fetch_pinned()
if not (gmx and py and ffdir):
    harness.skip("needs gmx (%s), atomipy (%s) and min.ff (%s)" % (gmx, py, ffdir))
exes = ("mdoptimize", "mddynamics", "gmxprepare", "builder", "organizer")
s = harness.Session(build, "bookclay", {"GROMACS": gmx}, local=True, keep=True)
os.makedirs(PNG, exist_ok=True)
for exe in exes:
    harness.link(os.path.join(build, exe), os.path.join(s.home, "bin", exe))
gw = os.path.join(REPO, "packaging", "gateway")
for name in os.listdir(gw):
    if name.startswith("ecce-"):
        harness.link(os.path.join(gw, name), os.path.join(s.home, "bin", name))
wrappers = os.path.join(s.state, "wrappers")
shutil.rmtree(wrappers, ignore_errors=True)
shutil.copytree(os.path.join(build, "wrappers"), wrappers)
for entry in os.listdir(wrappers):
    os.chmod(os.path.join(wrappers, entry), 0o755)
s.registerMachine("localhost", "Shell", {"GROMACS": gmx})
rundir = os.path.join(s.state, "run")
display = org = None
try:
    assert s.services(True)
    display = xdisplay.Display().__enter__()
    cmddir = os.path.join(s.state, "mded")
    os.makedirs(cmddir, exist_ok=True)
    genv = s.env({"DISPLAY": display.name, "ECCE_TEST_MDED": cmddir,
                  "ECCE_ATOMIPY_PYTHON": py, "ECCE_MINFF_DIR": ffdir,
                  "PATH": wrappers + os.pathsep + s.env()["PATH"]})
    rc, out = s.driver("gromacsstudy", s.userUrl(), "scratch")
    proj = [l for l in out.splitlines() if l.startswith("file://")][0].rsplit("/", 2)[0] + "/"
    pdir = where(proj)
    before = set(os.listdir(pdir))
    cmds = os.path.join(s.state, "organizer-commands")
    open(cmds, "w").close()
    olog = os.path.join(s.state, "organizer.log")
    org = subprocess.Popen([os.path.join(wrappers, "ecce-organizer")],
                           env=dict(genv, ECCE_TEST_ORGANIZER=cmds),
                           cwd=os.path.join(s.home, "bin"), stdout=open(olog, "w"),
                           stderr=subprocess.STDOUT, start_new_session=True)

    def send(line, timeout=120):
        with open(cmds, "a") as h:
            h.write(line + "\n")
        want = "ECCE_TEST_ORGANIZER: %s: " % line
        end = time.time() + timeout
        while time.time() < end:
            for t in open(olog, errors="replace").read().splitlines():
                if t.startswith(want):
                    return t[len(want):]
            time.sleep(0.5)
        return "no answer"

    say("New study: %s" % send("new %s gromacs_md_study" % proj))
    study = [x for x in subdirs(pdir) if x not in before and not subdirs(os.path.join(pdir, x))][0]
    study_url = proj.rstrip("/") + "/" + study
    tasks = {}
    for kind in ("prepare", "optimize", "equilibrate", "dynamics"):
        have = set(subdirs(where(study_url)))
        say("New %s: %s" % (kind, send("new %s gromacs_md_%s" % (study_url, kind))))
        tasks[kind] = study_url + "/" + sorted(set(subdirs(where(study_url))) - have)[0] + "/"
        s.driver("mdsetup", tasks[kind], "localhost", rundir, s.user(), "procs=4")

    ed = Editor(s, display, genv, wrappers, cmddir, "gmxprepare", "GMXPrepare")
    try:
        assert ed.up()
        for c in ("open " + tasks["prepare"], "set source minff", "set mcell " + CELL,
                  "set mrep " + REPEAT, "set msubs " + SUBS, "set mseed " + SEED,
                  "set mions HFE"):
            say("  %s -> %s" % (c, ed.cmd(c)))
        say("  build -> %s" % ed.cmd("set mbuild go", timeout=900))
        for c in ("set pname " + ION, "set dist " + WATER_NM, "set conc 0", "set rmin 0.3"):
            say("  %s -> %s" % (c, ed.cmd(c)))
        say("  fields: %s" % ed.cmd("fields"))
        say("  cellwarning: %s" % ed.cmd("cellwarning"))
        ed.cmd("save")
        say("  recipe: %s" % ed.cmd("recipe"))
        ed.cmd("snap " + os.path.join(PNG, "gmxprepare-minff.png"))
    finally:
        ed.close()

    for n, kind in enumerate(("prepare", "optimize", "equilibrate", "dynamics"), 1):
        if kind != "prepare":
            binary, app = (("mdoptimize", "MDOptimize") if kind == "optimize"
                           else ("mddynamics", "MDDynamics"))
            ed = Editor(s, display, genv, wrappers, cmddir, binary, app)
            try:
                assert ed.up()
                say("%s open -> %s; inputs: %s" % (kind, ed.cmd("open " + tasks[kind]), ed.cmd("inputs")))
                say("  steps -> %s" % ed.cmd("set-steps " + STEPS[kind]))
                if kind != "optimize":
                    say("  barostat C-rescale -> %s" % ed.cmd("run-set barostat 0"))
                    say("  semiisotropic -> %s" % ed.cmd("run-set pcoupltype 1"))
                ed.cmd("save")
                mdp = open(os.path.join(where(tasks[kind]), "Inputs", "gromacs.mdp")).read()
                if kind != "optimize" and not re.search(r"^pcoupl\s*=\s*(?!no)\S", mdp, re.M | re.I):
                    # the run is NVT by default: pressure coupling so the interlayer relaxes
                    say("  no pcoupl in the .mdp: extra -> %s" % ed.cmd("run-set extra " + NPT))
                    ed.cmd("save")
                    mdp = open(os.path.join(where(tasks[kind]), "Inputs", "gromacs.mdp")).read()
                say("  mdp: %s" % mdp.replace("\n", " | "))
                keys = dict(re.findall(r"^\s*([a-z_-]+)\s*=\s*([^;\n]*)", mdp, re.M))
                say("  check against the MINFF reference (dt 0.001, constraints none, rcoulomb/rvdw 1.2): "
                    + " ".join("%s=%s" % (k, keys.get(k, keys.get(k.replace("-", "_"), "?")).strip())
                               for k in ("dt", "constraints", "rcoulomb", "rvdw", "pcoupl", "pcoupltype", "periodic-molecules")))
                for tab in ed.cmd("tabs").split("|"):
                    if ed.cmd("tab " + tab) == "ok":
                        ed.cmd("snap " + os.path.join(PNG, "%s-%s.png" % (kind, tab.replace(" ", "_").lower())))
            finally:
                ed.close()
        t0 = time.time()
        rc, out = s.launch(tasks[kind])
        st = s.waitState(tasks[kind], 6 * 3600)
        say("%s: %s in %.0f s; props %s" % (kind, st, time.time() - t0, s.props(tasks[kind])))
        dest = os.path.join(OUT, "%02d-gromacs-%s" % (n, kind))
        shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(where(tasks[kind]), dest, symlinks=True)
        open(dest + ".url", "w").write("%s\n%s %.0f s\n" % (tasks[kind], st, time.time() - t0))
        if st not in ("completed", "loaded"):
            say("stopping: %s did not complete (%s)" % (kind, s.reason_of(tasks[kind])))
            break
    shutil.copy(olog, os.path.join(OUT, "organizer.log"))
finally:
    if org:
        org.terminate()
    if display:
        display.__exit__(None, None, None)
    s.stop()
