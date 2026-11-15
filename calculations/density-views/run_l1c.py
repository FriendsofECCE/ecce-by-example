#!/usr/bin/env python3
"""Lab L1c (5KE176 Exercises 2 and 3) through ECCE, ORCA, B3LYP-D3BJ.

    hbond:  phenol-water complex, phenol, water: GeoVib (Opt+Freq) at
            def2-TZVP with Hirshfeld and NBO charges; the monomers start from
            the optimised complex, split in two (as the lab does it).
    raman:  benzocaine GeoVib + Raman activities at def2-SVP (cost check);
            B3LYP needs Numerical frequencies for Raman in ORCA.

Same route as calculations/scans/run_l1a.py: ECCE's ORCA generator writes
the deck, the real Calculation Editor (ECCE_CALCED_SCRIPT, Xvfb) sets theory,
basis, run type and details and saves, and the calculation is launched
through ECCE's Launch / job monitor / parsers in an isolated ECCE.

    ECCE_SRC=<checkout> ECCE_BUILD=<build> python3 run_l1c.py <outdir> hbond|raman
"""
import glob, math, os, shutil, subprocess, sys, time

REPO = os.environ.get("ECCE_SRC", "ECCE")
BUILD = os.environ.get("ECCE_BUILD", os.path.join(REPO, "build-cmake"))
PARSERS = os.path.join(REPO, "scripts", "parsers")
OUT = os.path.abspath(sys.argv[1])
MODE = sys.argv[2]
PROCS = int(os.environ.get("L1C_PROCS", "4"))
HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)


def log(t):
    print("L1C: " + t, flush=True)
    open(os.path.join(OUT, "run.log"), "a").write(time.strftime("%H:%M:%S ") + t + "\n")


def phenolWater():
    """Phenol (atoms 1-13, O7-H8 the donor) and water (O14 H15 H16, the
    acceptor) in a rough start: O-H...O linear, H...O 1.9 A."""
    atoms = []
    for k in range(6):
        a = math.radians(60 * k)
        atoms.append(("C", 1.39 * math.cos(a), 1.39 * math.sin(a), 0.0))
    o = (2.75, 0.0, 0.0)
    u = (math.cos(math.radians(71)), math.sin(math.radians(71)), 0.0)
    h = (o[0] + 0.96 * u[0], o[1] + 0.96 * u[1], 0.0)
    atoms += [("O",) + o, ("H",) + h]
    for k in range(1, 6):
        a = math.radians(60 * k)
        atoms.append(("H", 2.47 * math.cos(a), 2.47 * math.sin(a), 0.0))
    ow = (h[0] + 1.9 * u[0], h[1] + 1.9 * u[1], 0.0)
    c, s_ = 0.96 * math.cos(math.radians(52)), 0.96 * math.sin(math.radians(52))
    atoms += [("O",) + ow,
              ("H", ow[0] + c * u[0], ow[1] + c * u[1], s_),
              ("H", ow[0] + c * u[0], ow[1] + c * u[1], -s_)]
    return atoms


def nboexe():
    p = os.environ.get("NBOEXE", "")
    return p if p and os.access(p, os.X_OK) else ""


def param(runtype, charges, raman):
    p = ("Category: DFT\nTheory: RDFT\nRunType: %s\nCharge: 0\nChemSys.Multiplicity: 1\n"
         "ES.Theory.DFT.XCFunctionals: B3LYP\nES.Theory.SCF.Dispersion: D3BJ\n"
         "ES.Theory.UseSymmetry: 0\n" % runtype)
    if charges:
        p += "ES.Runtype.ORCA.UseHirshfeld: 1\n"
        if nboexe():
            p += "ES.Runtype.ORCA.UseNBO: 1\n"
    if raman:
        p += "ES.Runtype.Vibration.Method: Numerical\nES.Runtype.Vibration.UseRaman: 1\n"
    return p


def frag(title, atoms):
    return ("# frag\nnum_atoms: %d\ntitle: %s\natom_info: symbol\natom_list:\n%s" %
            (len(atoms), title, "".join("%s %.6f %.6f %.6f\n" % a for a in atoms)))


def mvm(title, atoms):
    """The chemical system a Builder-made calculation holds (results.h5 and
    the Builder's panels need it)."""
    bonds = []
    for i in range(len(atoms)):
        for j in range(i + 1, len(atoms)):
            d = math.dist(atoms[i][1:], atoms[j][1:])
            if d < (1.25 if "H" in (atoms[i][0], atoms[j][0]) else 1.75):
                bonds.append((i + 1, j + 1))
    return ("title: %s\ntype: molecule\nnum_atoms: %d\natom_info: symbol cart\natom_list: \n%s"
            "attr_list:\n%satom_type_list:\n%snum_bonds: %d\nbond_list: \n%s") % (
        title, len(atoms), "".join("%s %.6f %.6f %.6f\n" % a for a in atoms),
        " 0.000000   1   0   0   0\n" * len(atoms), "        0   1\n" * len(atoms),
        len(bonds), "".join("%d %d 1.00000 1\n" % b for b in bonds))


def deck(name, atoms, runtype, basis, charges=False, raman=False):
    work = os.path.join(OUT, "decks", name)
    shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    shutil.copy(os.path.join(PARSERS, "orca.tpl"), os.path.join(work, "t.tpl"))
    open(os.path.join(work, "w.frag"), "w").write(frag(name, atoms))
    open(os.path.join(work, "chemsys.mvm"), "w").write(mvm(name, atoms))
    open(os.path.join(work, "w.basis"), "w").write("useRouteCard %s\n" % basis)
    open(os.path.join(work, "w.param"), "w").write(param(runtype, charges, raman))
    argv = ["perl", os.path.join(PARSERS, "ai.orca"), "-p", "-f", "-b", "-n", "w", "-t", "t.tpl"]
    p = subprocess.run(argv, cwd=work, env=dict(os.environ, ECCE_HOME=REPO),
                       capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr)
    text = open(os.path.join(work, "t.tpl")).read()
    open(os.path.join(work, "orca.orcain"), "w").write(text)
    return os.path.join(work, "orca.orcain")


def lastGeom(outtext):
    i = outtext.rfind("CARTESIAN COORDINATES (ANGSTROEM)")
    atoms = []
    for line in outtext[i:].splitlines()[2:]:
        w = line.split()
        if len(w) != 4:
            break
        atoms.append((w[0], float(w[1]), float(w[2]), float(w[3])))
    return atoms


def readXyz(path):
    lines = open(path).read().splitlines()
    return [(w[0], float(w[1]), float(w[2]), float(w[3]))
            for w in (l.split() for l in lines[2:2 + int(lines[0])])]


sys.path.insert(0, os.path.join(REPO, "tests", "launch"))
sys.path.insert(0, os.path.join(REPO, "tests", "apps"))
import harness, xdisplay
import builder_overlay_test as bo
orca = os.environ.get("ORCA") or sorted(glob.glob("/opt/orca/orca_6*/orca"))[-1]
log("ORCA %s, NBO %s, procs %d, mode %s" % (orca, nboexe() or "none", PROCS, MODE))
s = harness.Session(BUILD, "bookl1c" + MODE, {"ORCA": orca}, local=True, keep=True)
rundir = os.path.join(s.state, "run"); os.makedirs(rundir, exist_ok=True)
harness.link(os.path.join(BUILD, "calced"), os.path.join(s.home, "bin", "calced"))
wrappers = os.path.join(s.state, "wrappers"); shutil.rmtree(wrappers, ignore_errors=True)
shutil.copytree(os.path.join(BUILD, "wrappers"), wrappers)
for f in os.listdir(wrappers):
    os.chmod(os.path.join(wrappers, f), 0o755)
xdisplay.SCREEN = "1500x950x24"
display = xdisplay.Display().__enter__()
xenv = s.env({"DISPLAY": display.name, "GTK_THEME": "Adwaita",
              "PATH": wrappers + os.pathsep + s.env()["PATH"]})


def editor(url, runtype, basis, charges, raman):
    """Theory, basis, run type and details as a user picks them, then Save."""
    work = os.path.join(s.state, "calced"); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    lines = ["wait 9000", "info", "theory RDFT", "wait 3000", "basis " + basis, "wait 2000",
             "runtype " + runtype, "wait 3000", "details theory", "wait 8000",
             "gui ES.Theory.DFT.XCFunctionals B3LYP", "gui ES.Theory.SCF.Dispersion D3BJ",
             "close-details", "wait 2000"]
    if charges or raman:
        lines += ["details runtype", "wait 8000"]
        if charges:
            lines += ["gui ES.Runtype.ORCA.UseHirshfeld 1"]
            lines += ["gui ES.Runtype.ORCA.UseNBO 1"] if nboexe() else []
        if raman:
            lines += ["gui ES.Runtype.Vibration.Method Numerical",
                      "gui ES.Runtype.Vibration.UseRaman 1"]
        lines += ["close-details", "wait 2000"]
    lines += ["guivalue ES.Theory.DFT.XCFunctionals", "guivalue ES.Theory.SCF.Dispersion",
              "button save", "wait 6000", "info", "quit"]
    script = os.path.join(work, "script"); open(script, "w").write("\n".join(lines) + "\n")
    log_ = os.path.join(work, "app.log")
    proc = subprocess.Popen([os.path.join(wrappers, "ecce-calced"), "-context", url],
                            env=dict(xenv, ECCE_CALCED_SCRIPT=script),
                            cwd=os.path.join(s.home, "bin"), stdout=open(log_, "w"),
                            stderr=subprocess.STDOUT, start_new_session=True)
    deadline = time.time() + 300
    try:
        while proc.poll() is None and time.time() < deadline:
            time.sleep(0.3)
    finally:
        bo.stop(proc)
    text = open(log_, errors="replace").read()
    log("editor:\n" + "\n".join(l for l in text.splitlines() if "CALCED" in l or "FAIL" in l))


def run(name, atoms, runtype, basis, charges=False, raman=False):
    path = deck(name, atoms, runtype, basis, charges, raman)
    url, out = s.create(name, "orca_es", path, "orca.orcain", rundir,
                        extra=("procs=%d" % PROCS, "code=ORCA", "theory=DFT:RDFT",
                               "mvm=" + os.path.join(os.path.dirname(path), "chemsys.mvm"),
                               "runtype=" + runtype))
    if not url:
        raise RuntimeError("create %s: %s" % (name, out[-500:]))
    calc = url[len("file://"):].rstrip("/")
    os.makedirs(os.path.join(calc, "Parameters"), exist_ok=True)
    shutil.copy(os.path.join(os.path.dirname(path), "chemsys.mvm"),
                os.path.join(calc, "Parameters", "chemsys.mvm"))
    editor(url, runtype, basis, charges, raman)
    deckNow = glob.glob(os.path.join(calc, "Inputs", "*.orcain"))
    if raman and deckNow:
        # ORCA 6.1.1 reads "Freq NumFreq" as analytic and stops (exit 55) for
        # B3LYP Raman; drop "Freq", as a Final Edit of the input would.
        d = open(deckNow[0]).read()
        open(deckNow[0], "w").write(d.replace(" Freq NumFreq", " NumFreq"))
    log("%s: stored deck after Save:\n%s" % (name, open(deckNow[0]).read() if deckNow else "NONE"))
    t0 = time.time(); s.launch(url)
    st = s.waitState(url, seconds=12 * 3600)
    log("%s: %s in %.0f s (%s)" % (name, st, time.time() - t0, url))
    dest = os.path.join(OUT, name); shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(calc, dest, symlinks=True)
    for j in glob.glob(os.path.join(rundir, "*" + name + "*")):
        shutil.copytree(j, os.path.join(dest, "rundir"), dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("*.tmp*", "*.densities*"))
    outs = glob.glob(os.path.join(dest, "Outputs", "*.orcaout"))
    return open(outs[0], errors="replace").read() if outs else ""


try:
    assert s.services(True)
    if MODE == "hbond":
        t = run("phenol-water-optfreq", phenolWater(), "GeoVib", "def2-TZVP", charges=True)
        g = lastGeom(t)
        run("phenol-optfreq", g[:13], "GeoVib", "def2-TZVP", charges=True)
        run("water-optfreq", g[13:], "GeoVib", "def2-TZVP", charges=True)
    elif MODE == "raman":
        run("benzocaine-svp-raman", readXyz(os.path.join(OUT, "benzocaine.xyz")),
            "GeoVib", "def2-SVP", raman=True)
    log("DONE")
finally:
    display.__exit__(None, None, None)
    s.stop()
