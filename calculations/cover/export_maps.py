#!/usr/bin/env python3
"""Density-map grids for the cover, exported by ECCE's Density Map (headless).

    ECCE_SRC=<checkout> ECCE_BUILD=<build> python3 export_maps.py <out dir> name=<calc dir>[:plane[:a,b,c]] ...

Each calculation is copied into an isolated ECCE (tests/launch harness, Xvfb),
opened in the Builder, and the scene hook writes the total electron density
in the chosen plane (0 = molecular plane) with 'dmcsv'.
"""
import os, shutil, subprocess, sys, time
REPO = os.environ.get("ECCE_SRC", "ECCE")
BUILD = os.environ.get("ECCE_BUILD", os.path.join(REPO, "build-cmake"))
sys.path.insert(0, os.path.join(REPO, "tests", "launch"))
sys.path.insert(0, os.path.join(REPO, "tests", "apps"))
import harness, xdisplay
import builder_overlay_test as bo
OUT = os.path.abspath(sys.argv[1]); os.makedirs(OUT, exist_ok=True)
JOBS = []
for arg in sys.argv[2:]:
    name, spec = arg.split("=", 1)
    parts = spec.split(":")
    JOBS.append((name, os.path.abspath(parts[0]), parts[1] if len(parts) > 1 else "0",
                 parts[2].replace(",", " ") if len(parts) > 2 else ""))

s = harness.Session(BUILD, "bookcover", {}, local=True, keep=True)
for exe in bo.GUI:
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
    project = os.path.join(s.localData(), "users", "local", "cover")
    os.makedirs(project, exist_ok=True)
    shutil.copy(bo.PROJECT_META, os.path.join(project, ".ecce-meta"))
    for name, src, plane, atoms in JOBS:
        calc = os.path.join(project, name)
        shutil.rmtree(calc, ignore_errors=True)
        shutil.copytree(src, calc, symlinks=True, ignore=shutil.ignore_patterns("rundir"))
        work = os.path.join(s.state, name); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
        script = os.path.join(work, "script"); open(script, "w").write("wait 4000\nwait 120000\nquit\n")
        scene = os.path.join(work, "scene")
        open(scene, "w").write("densitymap %s 900 700 0 alpha %s %s\ndmcsv %s\n" % (name, plane, atoms, name))
        e = dict(env, ECCE_BUILDER_SCRIPT=script, ECCE_VIEWER_SCENE=scene, ECCE_VIEWER_SCENE_OUT=work,
                 ECCE_VIEWER_SCENE_HOLD="1")
        log = os.path.join(work, "app.log")
        proc = subprocess.Popen([os.path.join(wrappers, "ecce-builder"), "-context", "file://" + calc + "/"],
                                env=e, cwd=os.path.join(s.home, "bin"), stdout=open(log, "w"),
                                stderr=subprocess.STDOUT, start_new_session=True)
        csv = os.path.join(work, name + ".csv")
        deadline = time.time() + 300
        while time.time() < deadline and proc.poll() is None and not os.path.exists(csv):
            time.sleep(1)
        time.sleep(2)
        bo.stop(proc)
        if os.path.exists(csv):
            shutil.copy(csv, OUT); shutil.copy(os.path.join(work, name + ".png"), OUT)
            print("ok", name, flush=True)
        else:
            print("FAIL", name, "\n".join(l for l in open(log, errors="replace").read().splitlines()
                                          if "SCRIPT" in l or "SCENE" in l or "FAIL" in l)[-2000:], flush=True)
finally:
    if display:
        display.__exit__(None, None, None)
    s.stop()
