#!/usr/bin/env python3
"""Chapter reaction-rates (lab L1b, 5KE176 Exercise 1 steps 9-11): Diels-Alder
gauche butadiene + ethene -> cyclohexene in ORCA, B3LYP D3BJ def2-TZVP, the
same level as the separated reactants (scans/orca-butadiene-scis-optfreq,
density-views/orca-ethene-optfreq).

One atom numbering for every structure: butadiene C1-C4 (C1 and C4 the
termini), its H5-H10, ethene C11 C12, H13-H16; the new bonds are C1-C11 and
C4-C12.

Steps, each a calculation made and launched as in run_l1a.py (tests/launch
harness: isolated HOME, local data, machine localhost; theory, basis, run
type and details chosen in the real Calculation Editor through
ECCE_CALCED_SCRIPT, then Save and Launch):
  da-butadiene-gauche-optfreq, da-ethene-optfreq
                          GeoVib, the separated reactants again from the
                          stored minima (same level; for the Energy Calculator)
  da-reactant-complex     Geometry, ethene 3.6 A over the termini
  da-cyclohexene-optfreq  GeoVib, from ethene 1.95 A from the termini (downhill)
  da-ts-nebts             Transition State (NEB-TS) + Frequencies: a new
                          calculation without a structure; the editor's
                          Structure from other calculations picks the
                          reactant complex (reactant) and the cyclohexene
                          (product), as a user does
  da-ts-irc               IRC, both directions, from the TS geometry

The editor offers only calculations of the same project as end points, so
the reactant and product calculations are moved into the TS calculation's
project before it is set up (what the Organizer's move does; no ECCE app is
running at that point).

    ECCE_SRC=<checkout> python3 run_l1b.py <outdir> <start.json>
    ... --from-ts <earlier outdir>    IRC only, from a stored NEB-TS
"""
import glob, json, math, os, re, shutil, subprocess, sys, time

REPO = os.environ.get("ECCE_SRC", "ECCE")
BUILD = os.environ.get("ECCE_BUILD", os.path.join(REPO, "build-cmake"))
PARSERS = os.path.join(REPO, "scripts", "parsers")
OUT = os.path.abspath(sys.argv[1])
START = json.load(open(sys.argv[2]))
FROMTS = sys.argv[sys.argv.index("--from-ts") + 1] if "--from-ts" in sys.argv else ""
PROCS = int(os.environ.get("L1B_PROCS", "6"))
NEB = "Transition State (NEB-TS) + Frequencies"
os.makedirs(OUT, exist_ok=True)


def log(t):
    print("L1B: " + t, flush=True)
    open(os.path.join(OUT, "run.log"), "a").write(time.strftime("%H:%M:%S ") + t + "\n")


def vsub(a, b): return [a[i] - b[i] for i in range(3)]
def vadd(a, b): return [a[i] + b[i] for i in range(3)]
def vmul(a, s): return [x * s for x in a]
def vnorm(a): return vmul(a, 1.0 / math.sqrt(sum(x * x for x in a)))
def vcross(u, v): return [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]


def assemble(diene, h, pyramid):
    """Ethene parallel to C1...C4, h A along the normal of the diene's mean
    plane from the C1-C4 midpoint; pyramid pushes its H away (sp3-like)."""
    p = [a[1:] for a in diene]
    u = vnorm(vsub(p[3], p[0]))
    mid14 = vmul(vadd(p[0], p[3]), 0.5)
    v = vnorm(vsub(mid14, vmul(vadd(p[1], p[2]), 0.5)))
    n = vnorm(vcross(u, v))
    c = vadd(vadd(mid14, vmul(n, h)), vmul(v, 0.4))  # off the central C2-C3
    c11, c12 = vadd(c, vmul(u, -0.667)), vadd(c, vmul(u, 0.667))
    eth = [("C", c11), ("C", c12)]
    for cc, s in ((c11, -1), (c12, 1)):
        for t in (1, -1):
            eth.append(("H", vadd(vadd(cc, vmul(u, 0.568 * s)), vadd(vmul(v, 0.921 * t), vmul(n, pyramid)))))
    # termini H (atoms 5, 6, 9, 10) pushed the other way, as in the ring
    out = [(a[0], *vadd(a[1:], vmul(n, -pyramid))) if k in (4, 5, 8, 9) else tuple(a)
           for k, a in enumerate(diene)]
    return out + [(e, *x) for e, x in eth]


def frag(title, atoms):
    return ("# frag\nnum_atoms: %d\ntitle: %s\natom_info: symbol\natom_list:\n%s" %
            (len(atoms), title, "".join("%s %.6f %.6f %.6f\n" % tuple(a) for a in atoms)))


def mvm(title, atoms):
    bonds = []
    for i in range(len(atoms)):
        for j in range(i + 1, len(atoms)):
            d = math.dist(atoms[i][1:], atoms[j][1:])
            if d < (1.25 if "H" in (atoms[i][0], atoms[j][0]) else 1.75):
                bonds.append((i + 1, j + 1))
    return ("title: %s\ntype: molecule\nnum_atoms: %d\natom_info: symbol cart\natom_list: \n%s"
            "attr_list:\n%satom_type_list:\n%snum_bonds: %d\nbond_list: \n%s") % (
        title, len(atoms), "".join("%s %.6f %.6f %.6f\n" % tuple(a) for a in atoms),
        " 0.000000   1   0   0   0\n" * len(atoms), "        0   1\n" * len(atoms),
        len(bonds), "".join("%d %d 1.00000 1\n" % b for b in bonds))


def deck(name, atoms, runtype):
    """A first deck for the create call; the editor's Save replaces it."""
    work = os.path.join(OUT, "decks", name)
    shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    shutil.copy(os.path.join(PARSERS, "orca.tpl"), os.path.join(work, "t.tpl"))
    open(os.path.join(work, "w.frag"), "w").write(frag(name, atoms))
    open(os.path.join(work, "chemsys.mvm"), "w").write(mvm(name, atoms))
    open(os.path.join(work, "w.basis"), "w").write("useRouteCard def2-TZVP\n")
    open(os.path.join(work, "w.param"), "w").write(
        "Category: DFT\nTheory: RDFT\nRunType: %s\nCharge: 0\nChemSys.Multiplicity: 1\n"
        "ES.Theory.DFT.XCFunctionals: B3LYP\nES.Theory.SCF.Dispersion: D3BJ\n"
        "ES.Theory.UseSymmetry: 0\n" % runtype)
    p = subprocess.run(["perl", os.path.join(PARSERS, "ai.orca"), "-p", "-f", "-b", "-n", "w",
                        "-t", "t.tpl"], cwd=work, env=dict(os.environ, ECCE_HOME=REPO),
                       capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr)
    shutil.copy(os.path.join(work, "t.tpl"), os.path.join(work, "orca.orcain"))
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


sys.path.insert(0, os.path.join(REPO, "tests", "launch"))
sys.path.insert(0, os.path.join(REPO, "tests", "apps"))
import harness, xdisplay
import builder_overlay_test as bo
orca = os.environ.get("ORCA") or (sorted(glob.glob("/opt/orca/orca_6*/orca")) or [shutil.which("orca")])[-1]
log("ORCA %s, procs %d" % (orca, PROCS))
s = harness.Session(BUILD, "bookl1b", {"ORCA": orca}, local=True, keep=True)
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


def editor(url, runtype, pre=(), mid=(), post=()):
    """pre: before theory (structure source); mid: after the run type (the
    NEB product); post: Runtype Details settings."""
    work = os.path.join(s.state, "calced"); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    lines = ["wait 9000", "info"] + list(pre) + [
        "theory RDFT", "wait 3000", "basis def2-TZVP", "wait 2000",
        "runtype " + runtype, "wait 3000"] + list(mid) + [
        "details theory", "wait 8000",
        "gui ES.Theory.DFT.XCFunctionals B3LYP", "gui ES.Theory.SCF.Dispersion D3BJ",
        "close-details", "wait 2000"]
    if post:
        lines += ["details runtype", "wait 8000"] + list(post) + ["close-details", "wait 2000"]
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
            time.sleep(0.5)
    finally:
        bo.stop(proc)
    text = open(log_, errors="replace").read()
    log("editor:\n" + "\n".join(l for l in text.splitlines() if "CALCED" in l or "FAIL" in l))


def create(name, atoms, runtype):
    extra = ["procs=%d" % PROCS, "code=ORCA", "theory=DFT:RDFT", "runtype=" + runtype]
    d = deck(name, atoms, "Geometry")
    if atoms is not None and runtype != NEB:
        extra.append("mvm=" + os.path.join(os.path.dirname(d), "chemsys.mvm"))
    url, out = s.create(name, "orca_es", d, "orca.orcain", rundir, extra=tuple(extra))
    if not url:
        raise RuntimeError("create %s: %s" % (name, out[-500:]))
    calc = url[len("file://"):].rstrip("/")
    if atoms is not None and runtype != NEB:
        os.makedirs(os.path.join(calc, "Parameters"), exist_ok=True)
        shutil.copy(os.path.join(os.path.dirname(d), "chemsys.mvm"),
                    os.path.join(calc, "Parameters", "chemsys.mvm"))
    return url, calc


def launch(name, url, calc, hours=10):
    deckNow = glob.glob(os.path.join(calc, "Inputs", "*.orcain"))
    log("%s: stored deck after Save:\n%s" % (name, open(deckNow[0]).read() if deckNow else "NONE"))
    log("%s: inputs %s" % (name, os.listdir(os.path.join(calc, "Inputs"))))
    t0 = time.time(); s.launch(url)
    st = s.waitState(url, seconds=hours * 3600)
    log("%s: %s in %.0f s (%s)" % (name, st, time.time() - t0, url))
    return save(name, calc)


def save(name, calc):
    dest = os.path.join(OUT, name); shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(calc, dest, symlinks=True)
    for j in glob.glob(os.path.join(rundir, "*", name)) + glob.glob(os.path.join(rundir, name)):
        shutil.copytree(j, os.path.join(dest, "rundir"), dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("*.gbw", "*.tmp*", "*.densities*"))
    outs = glob.glob(os.path.join(dest, "Outputs", "*.orcaout"))
    return open(outs[0], errors="replace").read() if outs else ""


try:
    assert s.services(True)
    if FROMTS:
        tsGeom = lastGeom(open(glob.glob(os.path.join(os.path.abspath(FROMTS), "da-ts-nebts", "Outputs", "*.orcaout"))[0], errors="replace").read())
    else:
        diene = [tuple(a) for a in START["butadiene"]]
        rc = assemble(diene, 3.6, 0.0)
        pr = assemble(diene, 1.70, 0.4)
        log("reactant complex start: %s" % rc)
        log("product start: %s" % pr)
        # the separated reactants again, same level, so that they sit in the
        # reaction's project for the Energy Calculator
        sep = []
        for nm, atoms in (("da-butadiene-gauche-optfreq", diene),
                          ("da-ethene-optfreq", [tuple(a) for a in START["ethene"]])):
            u, c = create(nm, atoms, "GeoVib")
            editor(u, "GeoVib")
            launch(nm, u, c)
            sep.append(c)
        u1, c1 = create("da-reactant-complex", rc, "Geometry")
        editor(u1, "Geometry")
        t1 = launch("da-reactant-complex", u1, c1)
        u2, c2 = create("da-cyclohexene-optfreq", pr, "GeoVib")
        editor(u2, "GeoVib")
        t2 = launch("da-cyclohexene-optfreq", u2, c2)
        u3, c3 = create("da-ts-nebts", rc, NEB)
        proj = os.path.dirname(c3)
        for c in [c1, c2] + sep:
            shutil.move(c, os.path.join(proj, os.path.basename(c)))
        log("moved reactant and product into %s: %s" % (proj, os.listdir(proj)))
        editor(u3, NEB,
               pre=["ts-source other", "wait 2000", "ts-pick reactant da-reactant-complex",
                    "wait 7000", "ts-state"],
               mid=["ts-pick product da-cyclohexene-optfreq", "wait 4000", "ts-state"])
        t3 = launch("da-ts-nebts", u3, c3, hours=12)
        tsGeom = lastGeom(t3)
    log("TS geometry: %s" % tsGeom)
    u4, c4 = create("da-ts-irc", tsGeom, "IRC")
    editor(u4, "IRC", post=["guiw ES.Runtype.IRC.MaximumStepsValue 60",
                            "guivalue ES.Runtype.IRC.Direction"])
    launch("da-ts-irc", u4, c4, hours=8)
    log("DONE")
finally:
    display.__exit__(None, None, None)
    s.stop()
