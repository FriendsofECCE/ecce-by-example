#!/usr/bin/env python3
"""Chapter scans (lab L1a): butadiene s-trans opt+freq, relaxed C1-C2-C3-C4
scan (ORCA %geom Scan), frequencies at the ~100 deg maximum, s-cis opt+freq,
ethene opt+freq; B3LYP D3BJ def2-TZVP throughout.

Decks are written by ECCE's own ORCA generator (ai.orca, what the Calculation
Editor runs on Save) from the .param/.frag/.basis/.gcst an ECCE calculation
holds; the scan is the GeomConstraintModel the Builder's Geometry
Constraints > Scan... dialog stores.  Each calculation is created in an
isolated ECCE (tests/launch harness: own HOME, ECCE_LOCAL_DATA, machine
localhost) and run through the real Launch / job monitor / parsers.  The next
step's start geometry is the previous calculation's last geometry, as
New from This > Continue from Last Geometry takes it.

    ECCE_SRC=<ECCE checkout with build-cmake> python3 run_l1a.py <outdir> [--decks]
"""
import glob, math, os, re, shutil, subprocess, sys, tempfile, time

REPO = os.environ.get("ECCE_SRC", "ECCE")
BUILD = os.environ.get("ECCE_BUILD", os.path.join(REPO, "build-cmake"))
PARSERS = os.path.join(REPO, "scripts", "parsers")
OUT = os.path.abspath(sys.argv[1])
DECKS_ONLY = "--decks" in sys.argv
# --resume <dir>: steps 3-5 only, from a stored scan (<dir>/butadiene-dihedral-scan).
RESUME = sys.argv[sys.argv.index("--resume") + 1] if "--resume" in sys.argv else ""
PROCS = int(os.environ.get("L1A_PROCS", "4"))
os.makedirs(OUT, exist_ok=True)


def log(t):
    print("L1A: " + t, flush=True)
    open(os.path.join(OUT, "run.log"), "a").write(time.strftime("%H:%M:%S ") + t + "\n")


def rot(x, y, a, r):
    return (x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a)))


def butadiene():
    # Planar s-trans start: C=C 1.34, C-C 1.46, C-H 1.09 A, 120-124 deg.
    c2, c3 = (-0.73, 0.0), (0.73, 0.0)
    c1 = rot(*c2, 123.5, 1.34)
    c4 = rot(*c3, -56.5, 1.34)
    h2 = rot(*c2, 242.0, 1.09); h3 = rot(*c3, 62.0, 1.09)
    h1a = rot(*c1, 63.5, 1.09); h1b = rot(*c1, 183.5, 1.09)
    h4a = rot(*c4, 243.5, 1.09); h4b = rot(*c4, 3.5, 1.09)
    pts = [("C", c1), ("C", c2), ("C", c3), ("C", c4), ("H", h1a), ("H", h1b),
           ("H", h2), ("H", h3), ("H", h4a), ("H", h4b)]
    return [(e, p[0], p[1], 0.0) for e, p in pts]


ETHENE = [("C", -0.667, 0.0, 0.0), ("C", 0.667, 0.0, 0.0),
          ("H", -1.235, 0.921, 0.0), ("H", -1.235, -0.921, 0.0),
          ("H", 1.235, 0.921, 0.0), ("H", 1.235, -0.921, 0.0)]


def nboexe():
    for p in [os.environ.get("NBOEXE", "")] + [os.path.join(os.environ.get("REALHOME", "/nonexistent"), "nbo7/nbo7/bin/nbo7.i8.exe")]:
        if p and os.access(p, os.X_OK):
            return p
    return ""


def param(runtype, charges):
    p = ("Category: DFT\nTheory: RDFT\nRunType: %s\nCharge: 0\nChemSys.Multiplicity: 1\n"
         "ES.Theory.DFT.XCFunctionals: B3LYP\nES.Theory.SCF.Dispersion: D3BJ\n"
         "ES.Theory.UseSymmetry: 0\n" % runtype)
    if charges:
        p += "ES.Runtype.ORCA.UseHirshfeld: 1\n"
        if nboexe():
            p += "ES.Runtype.ORCA.UseNBO: 1\n"
    return p


def gcst(scan):
    if not scan:
        return ""
    group, value, steps, step = scan
    return ('<GeomConstraintModel>\n<Constraint type="torsion">\n  <Group>%s</Group>\n'
            '  <Value>%s</Value>\n  <Scan steps="%d" step="%s"/>\n</Constraint>\n'
            '</GeomConstraintModel>\n' % (group, value, steps, step))


def frag(title, atoms):
    return ("# frag\nnum_atoms: %d\ntitle: %s\natom_info: symbol\natom_list:\n%s" %
            (len(atoms), title, "".join("%s %.6f %.6f %.6f\n" % a for a in atoms)))


def mvm(title, atoms):
    """The chemical system a calculation made in the Builder holds; without it
    the job store writes no results.h5 and the Builder shows no panels."""
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


def deck(name, atoms, runtype, scan=None, charges=False):
    work = os.path.join(OUT, "decks", name)
    shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    shutil.copy(os.path.join(PARSERS, "orca.tpl"), os.path.join(work, "t.tpl"))
    open(os.path.join(work, "w.frag"), "w").write(frag(name, atoms))
    open(os.path.join(work, "chemsys.mvm"), "w").write(mvm(name, atoms))
    open(os.path.join(work, "w.basis"), "w").write("useRouteCard def2-TZVP\n")
    open(os.path.join(work, "w.param"), "w").write(param(runtype, charges))
    argv = ["perl", os.path.join(PARSERS, "ai.orca"), "-p", "-f", "-b", "-n", "w", "-t", "t.tpl"]
    if scan:
        open(os.path.join(work, "w.con"), "w").write(gcst(scan))
        argv.insert(-4, "-c")
    p = subprocess.run(argv, cwd=work, env=dict(os.environ, ECCE_HOME=REPO),
                       capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr)
    text = open(os.path.join(work, "t.tpl")).read()
    open(os.path.join(work, "orca.orcain"), "w").write(text)
    log("deck %s:\n%s" % (name, text))
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


def dihedral(a, b, c, d):
    def sub(p, q): return [p[i] - q[i] for i in range(3)]
    def cross(u, v): return [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
    def dot(u, v): return sum(u[i]*v[i] for i in range(3))
    b1, b2, b3 = sub(b, a), sub(c, b), sub(d, c)
    n1, n2 = cross(b1, b2), cross(b2, b3)
    m = cross(n1, [x / math.sqrt(dot(b2, b2)) for x in b2])
    return math.degrees(math.atan2(dot(m, n2), dot(n1, n2)))


def readXyz(path):
    lines = open(path).read().splitlines()
    n = int(lines[0])
    return [(w[0], float(w[1]), float(w[2]), float(w[3]))
            for w in (l.split() for l in lines[2:2 + n])]


if DECKS_ONLY:
    deck("strans", butadiene(), "GeoVib")
    deck("scan", butadiene(), "Geometry", scan=("0 1 2 3", "180.0", 35, "-10.0"))
    deck("ethene", ETHENE, "GeoVib", charges=True)
    sys.exit(0)

sys.path.insert(0, os.path.join(REPO, "tests", "launch"))
import harness
orca = os.environ.get("ORCA") or (sorted(glob.glob("/opt/orca/orca_6*/orca")) or [shutil.which("orca")])[-1]
log("ORCA %s, NBO %s, procs %d" % (orca, nboexe() or "none", PROCS))
if nboexe():
    os.environ["NBOEXE"] = nboexe()  # ORCA runs NBO through this
s = harness.Session(BUILD, "bookl1a", {"ORCA": orca}, local=True, keep=True)
rundir = os.path.join(s.state, "run"); os.makedirs(rundir, exist_ok=True)


def run(name, path):
    url, out = s.create(name, "orca_es", path, "orca.orcain", rundir,
                        extra=("procs=%d" % PROCS, "code=ORCA"))
    if not url:
        raise RuntimeError("create %s: %s" % (name, out[-500:]))
    calc = url[len("file://"):].rstrip("/")
    os.makedirs(os.path.join(calc, "Parameters"), exist_ok=True)
    shutil.copy(os.path.join(os.path.dirname(path), "chemsys.mvm"),
                os.path.join(calc, "Parameters", "chemsys.mvm"))
    con = os.path.join(os.path.dirname(path), "w.con")
    if os.path.exists(con):  # what the Builder's Scan... dialog stores
        os.makedirs(os.path.join(calc, "Parameters"), exist_ok=True)
        shutil.copy(con, os.path.join(calc, "Parameters", "GeomConstraintModel.gcst"))
    t0 = time.time(); rc, lo = s.launch(url)
    st = s.waitState(url, seconds=4 * 3600)
    log("%s: %s in %.0f s (%s)" % (name, st, time.time() - t0, url))
    dest = os.path.join(OUT, name); shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(calc, dest, symlinks=True)
    jobdir = sorted(glob.glob(os.path.join(rundir, "*" + name + "*")) + glob.glob(os.path.join(rundir, name)))
    for j in jobdir:
        shutil.copytree(j, os.path.join(dest, "rundir"), dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("*.gbw", "*.tmp*", "*.densities*", "*.hess"))
    outs = glob.glob(os.path.join(dest, "**", "*.orcaout"), recursive=True) + \
        glob.glob(os.path.join(dest, "**", "*.out"), recursive=True)
    text = open(outs[0], errors="replace").read() if outs else ""
    return dest, text, jobdir


try:
    assert s.services(True)
    if RESUME:
        jd = glob.glob(os.path.join(os.path.abspath(RESUME), "butadiene-dihedral-scan", "rundir", "*"))
        jd = [j for j in jd if os.path.isdir(j)] or [os.path.join(os.path.abspath(RESUME), "butadiene-dihedral-scan", "rundir")]
        t2 = open(glob.glob(os.path.join(jd[0], "*.orcaout"))[0], errors="replace").read()
    else:
        _, t1, _ = run("butadiene-strans-optfreq", deck("strans", butadiene(), "GeoVib", charges=True))
        g1 = lastGeom(t1)
        _, t2, jd = run("butadiene-dihedral-scan",
                        deck("scan", g1, "Geometry",
                             scan=("0 1 2 3", "%.4f" % dihedral(*[a[1:] for a in g1[:4]]), 35, "-10.0")))
    # Scan points: ORCA's own table, and the point geometries it wrote.
    i = t2.rfind("RELAXED SURFACE SCAN RESULTS")
    pts = [(float(a), float(b)) for a, b in re.findall(r"^\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)\s*$", t2[i:t2.find("using the SCF energy", i)], re.M)]
    log("scan points %d: %s" % (len(pts), pts))
    xyzs = sorted(glob.glob(os.path.join(jd[0], "*.[0-9][0-9][0-9].xyz"))) if jd else []
    geoms = [readXyz(p) for p in xyzs]
    dih = [dihedral(*[a[1:] for a in g[:4]]) for g in geoms]
    log("point dihedrals: %s" % ["%.1f" % d for d in dih])

    def nearest(target, lo, hi):
        best = None
        for k, g in enumerate(geoms):
            d = abs(dih[k])
            if lo <= d <= hi and (best is None or abs(d - target) < abs(abs(dih[best]) - target)):
                best = k
        return best
    kmax = max((k for k in range(min(len(geoms), len(pts))) if 60 <= abs(dih[k]) <= 140),
               key=lambda k: pts[k][1])
    log("maximum: point %d, dihedral %.1f" % (kmax + 1, dih[kmax]))
    run("butadiene-scanmax-freq", deck("scanmax", geoms[kmax], "Vibration"))
    kcis = min((k for k in range(min(len(geoms), len(pts))) if abs(dih[k]) <= 60),
               key=lambda k: pts[k][1])
    log("s-cis side minimum: point %d, dihedral %.1f" % (kcis + 1, dih[kcis]))
    run("butadiene-scis-optfreq", deck("scis", geoms[kcis], "GeoVib", charges=True))
    run("ethene-optfreq", deck("ethene", ETHENE, "GeoVib", charges=True))
    log("DONE")
finally:
    s.stop()
