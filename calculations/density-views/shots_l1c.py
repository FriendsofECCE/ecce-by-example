#!/usr/bin/env python3
"""Screenshots for chapter density-views (lab L1c, the hydrogen bond), headless.

    ECCE_SRC=<checkout> ECCE_BUILD=<build> python3 shots_l1a.py <calcs dir> <png dir>

<calcs dir> holds the stored calculations made by run_l1c.py hbond.  Each one is
copied into an isolated ECCE's local data (tests/launch harness, Xvfb) and
opened in the real Builder / Calculation Editor driven by their script hooks
(ECCE_BUILDER_SCRIPT, ECCE_VIEWER_SCENE, ECCE_CALCED_SCRIPT); the 3-D view
gets a white background.
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


s = harness.Session(BUILD, "bookl1cshots", {}, local=True, keep=True)
for exe in bo.GUI + ("calced",):
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
    project = os.path.join(s.localData(), "users", "local", "density-views")
    os.makedirs(project, exist_ok=True)
    shutil.copy(bo.PROJECT_META, os.path.join(project, ".ecce-meta"))
    calc = {}
    for name in os.listdir(CALCS):
        src = os.path.join(CALCS, name)
        if os.path.isdir(os.path.join(src, "Props")):
            calc[name] = os.path.join(project, name)
            shutil.rmtree(calc[name], ignore_errors=True)
            shutil.copytree(src, calc[name], symlinks=True,
                            ignore=shutil.ignore_patterns("rundir"))
    # Phenol O7-H8 donates to water O14 (run_l1c.py's atom order).
    pw = calc.get("phenol-water-optfreq")
    if pw and "--esp-only" not in sys.argv:
        app(s, display, env, wrappers, "ecce-builder", "ECCE_BUILDER_SCRIPT", pw,
            WHITE + ["measure dist 8 14", "measure angle 7 8 14", "wait 2000",
                     "shot hbond-measure", "quit"], "measure")
    for name, tag in (("phenol-water-optfreq", "complex"), ("phenol-optfreq", "phenol"),
                      ("water-optfreq", "water")):
        if name in calc:
            app(s, display, env, wrappers, "ecce-builder", "ECCE_BUILDER_SCRIPT", calc[name],
                WHITE + ["wait 240000", "quit"], "esp-" + tag, {"ECCE_OPEN_PANEL": "Surfaces",
                 "ECCE_VIEWER_SCENE_HOLD": "1"},  # draw in the Builder canvas, not a capture frame
                scene=["mofield ESP on Density", "moiso -2.7", "mopanel compute",
                       "mobar espbar-%s" % tag, "shot esp-%s" % tag])
finally:
    if display:
        display.__exit__(None, None, None)
    s.stop()
