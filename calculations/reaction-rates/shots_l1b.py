#!/usr/bin/env python3
"""Screenshots for chapter reaction-rates (lab L1b), headless.

    ECCE_SRC=<checkout> ECCE_BUILD=<build> python3 shots_l1b.py <calcs dir> <png dir>

<calcs dir> holds the calculations made by run_l1b.py; they are copied into
one project of an isolated ECCE's local data (tests/launch harness, Xvfb)
and opened in the real Builder and Organizer through their script hooks
(ECCE_BUILDER_SCRIPT, ECCE_TEST_ORGANIZER); the 3-D view gets a white
background.
"""
import os, shutil, subprocess, sys, time
REPO = os.environ.get("ECCE_SRC", "ECCE")
BUILD = os.environ.get("ECCE_BUILD", os.path.join(REPO, "build-cmake"))
sys.path.insert(0, os.path.join(REPO, "tests", "launch"))
sys.path.insert(0, os.path.join(REPO, "tests", "apps"))
import harness, xdisplay
import builder_overlay_test as bo
CALCS, PNG = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.makedirs(PNG, exist_ok=True)
WHITE = ["wait 6000", "background 1 1 1", "viewall"]


def app(s, display, env, wrappers, wrapper, hook, calc, lines, prefix, extra=None, scene=None):
    """Runs one app with its script hook and answers each "shot" handshake
    (<script dir>/<name>.ready -> photograph -> <name>.go)."""
    work = os.path.join(s.state, prefix); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    script = os.path.join(work, "script"); open(script, "w").write("\n".join(lines) + "\n")
    e = dict(env, **{hook: script}, **(extra or {}))
    names = [l.split()[1] for l in lines if l.startswith("shot ")]
    if scene:
        sc = os.path.join(work, "scene"); open(sc, "w").write("\n".join(scene) + "\n")
        e.update(ECCE_VIEWER_SCENE=sc, ECCE_VIEWER_SCENE_OUT=work, ECCE_TRANSPARENCY_FALLBACK_MS="0")
        names += [l.split()[1] for l in scene if l.startswith("shot ")]
    log = os.path.join(work, "app.log")
    proc = subprocess.Popen([os.path.join(wrappers, wrapper), "-context", "file://" + calc + "/"],
                            env=e, cwd=os.path.join(s.home, "bin"), stdout=open(log, "w"),
                            stderr=subprocess.STDOUT, start_new_session=True)
    deadline = time.time() + 400
    try:
        while names and time.time() < deadline and proc.poll() is None:
            for n in list(names):
                if os.path.exists(os.path.join(work, n + ".ready")):
                    time.sleep(1.5)
                    path = os.path.join(PNG, n + ".png")
                    print("shot %s %s" % (n, bo.snap(display, env, path)), flush=True)
                    os.unlink(os.path.join(work, n + ".ready"))
                    open(os.path.join(work, n + ".go"), "w").close()
                    names.remove(n)
            time.sleep(0.3)
        time.sleep(3)
    finally:
        bo.stop(proc)
    text = open(log, errors="replace").read()
    print("---- %s: missing %s\n%s" % (prefix, names, "\n".join(
        l for l in text.splitlines() if "SCRIPT" in l or "BUILDER:" in l or "CALCED:" in l
        or "FAIL" in l)[-3000:]), flush=True)
    return text




def organizer(s, display, env, wrappers, cmds, pngs):
    """The Organizer with ECCE_TEST_ORGANIZER; waits for each PNG."""
    work = os.path.join(s.state, "org"); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    cf = os.path.join(work, "cmds"); open(cf, "w").write("")
    log = os.path.join(work, "app.log")
    proc = subprocess.Popen([os.path.join(wrappers, "ecce-organizer")], env=dict(env, ECCE_TEST_ORGANIZER=cf),
                            cwd=os.path.join(s.home, "bin"), stdout=open(log, "w"),
                            stderr=subprocess.STDOUT, start_new_session=True)
    try:
        time.sleep(20)
        open(cf, "a").write("\n".join(cmds) + "\n")
        deadline = time.time() + 240
        while time.time() < deadline and not all(os.path.exists(p) for p in pngs):
            time.sleep(1)
        time.sleep(3)
    finally:
        bo.stop(proc)
    print("---- organizer\n" + "\n".join(l for l in open(log, errors="replace").read().splitlines()
                                       if "ECCE_TEST_ORGANIZER" in l)[-4000:], flush=True)


s = harness.Session(BUILD, "bookl1bshots", {}, local=True, keep=True)
for exe in bo.GUI + ("calced",):
    if os.path.exists(os.path.join(BUILD, exe)):
        harness.link(os.path.join(BUILD, exe), os.path.join(s.home, "bin", exe))
for exe in ("ecce-thermo", "autosym"):
    if os.path.exists(os.path.join(BUILD, exe)):
        harness.link(os.path.join(BUILD, exe), os.path.join(s.home, "bin", exe))
wrappers = os.path.join(s.state, "wrappers"); shutil.rmtree(wrappers, ignore_errors=True)
shutil.copytree(os.path.join(BUILD, "wrappers"), wrappers)
for f in os.listdir(wrappers):
    os.chmod(os.path.join(wrappers, f), 0o755)
display = None
try:
    assert s.services(True)
    xdisplay.SCREEN = "1500x950x24"
    display = xdisplay.Display().__enter__()
    env = s.env({"DISPLAY": display.name, "GTK_THEME": "Adwaita",
                 "PATH": wrappers + os.pathsep + s.env()["PATH"]})
    project = os.path.join(s.localData(), "users", "local", "diels-alder")
    os.makedirs(project, exist_ok=True)
    shutil.copy(bo.PROJECT_META, os.path.join(project, ".ecce-meta"))
    calc = {}
    for name in os.listdir(CALCS):
        src = os.path.join(CALCS, name)
        if os.path.isdir(os.path.join(src, "Props")):
            calc[name] = os.path.join(project, name)
            shutil.rmtree(calc[name], ignore_errors=True)
            shutil.copytree(src, calc[name], symlinks=True, ignore=shutil.ignore_patterns("rundir"))
    detail = {"ECCE_PANEL_MODE": "detail"}
    ts = calc.get("da-ts-nebts")
    if ts:
        app(s, display, env, wrappers, "ecce-builder", "ECCE_BUILDER_SCRIPT", ts,
            WHITE + ["specclick 1", "wait 3000", "shot ts-imaginary-mode", "quit"],
            "vib", dict(detail, ECCE_OPEN_PANEL="Vibrational Frequencies"))
        app(s, display, env, wrappers, "ecce-builder", "ECCE_BUILDER_SCRIPT", ts,
            WHITE + ["thermo RRHO", "wait 3000", "shot ts-thermo-panel", "quit"],
            "thermo", dict(detail, ECCE_OPEN_PANEL="Thermochemistry"))
    irc = calc.get("da-ts-irc")
    if irc:
        app(s, display, env, wrappers, "ecce-builder", "ECCE_BUILDER_SCRIPT", irc,
            WHITE + ["ircview graph", "ircpath %s/irc-kjmol.csv" % PNG, "ircpath %s/irc-kcal.csv kcal" % PNG,
                     "wait 2000", "shot irc-path", "quit"],
            "irc", dict(detail, ECCE_OPEN_PANEL="IRC Path"))
    u = lambda n: "file://" + calc[n] + "/"
    reac = "%s,%s" % (u("da-butadiene-gauche-optfreq"), u("da-ethene-optfreq"))
    cmds, pngs = [], []
    for side, tag in (("da-ts-nebts", "activation"), ("da-cyclohexene-optfreq", "reaction")):
        if side in calc and "da-ethene-optfreq" in calc:
            p = os.path.join(PNG, "energy-calculator-%s.png" % tag)
            cmds += ["compareenergies %s %s" % (reac, u(side)),
                     "comparedialog %s %s %s" % (reac, u(side), p)]
            pngs.append(p)
    if cmds:
        organizer(s, display, env, wrappers, cmds, pngs)
finally:
    if display:
        display.__exit__(None, None, None)
    s.stop()
