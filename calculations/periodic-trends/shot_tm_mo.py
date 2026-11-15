#!/usr/bin/env python3
"""Figure fig:pt-tm (chapter teaching-periodic-trends), headless: the MO Diagram
panel of the General Chemistry atoms Ca, Cr and Cu, energies to scale, as narrow
floating panels with enlarged fonts so that the energies stay readable in print.

    ECCE_SRC=<checkout> ECCE_TEST_HOME=<install>/ecce ECCE_TEST_WRAPPERS=<install>/bin \\
        ECCE_XVFB_SCREEN=1800x1024x24 ECCE_PLOTSHOT_POS=1200,40 python3 shot_tm_mo.py <png dir> [width height dpi-scale]

(the position keeps the floating panel clear of the 3-D viewer, which would be
copied over it)
"""
import glob, os, shutil, subprocess, sys, tempfile, time
REPO = os.environ.get("ECCE_SRC", "ECCE")
sys.path.insert(0, os.path.join(REPO, "tests", "apps"))
import apps, isolate, xdisplay  # noqa: E402
import md_compare_examples_test as mc  # noqa: E402

PNG = os.path.abspath(sys.argv[1])
W, H, DPI = (sys.argv[2:5] if len(sys.argv) >= 5 else ("520", "640", "1.6"))
os.makedirs(PNG, exist_ok=True)
ATOMS = tuple(os.environ.get("ATOMS", "Cr Cu").split())


def find(root, name):
    hits = [os.path.dirname(p) for p in glob.glob(os.path.join(root, "**", ".ecce-meta"), recursive=True)
            if ("/Atoms/" + name + "/") in p]
    return min(hits, key=len) if hits else None


def main():
    isolate.apply(apps.INSTALL)
    os.environ.update(ECCE_NO_REAP="1", GTK_THEME="Adwaita", GDK_DPI_SCALE=DPI,
                      ECCE_MODIAGRAM_AUFBAU_SCALE="1")
    work = tempfile.mkdtemp(prefix="tmmoshot-", dir=os.environ.get("ECCE_REALUSERHOME"))
    data = os.path.join(work, "data"); root = os.path.join(data, "users", "local")
    os.makedirs(root); os.environ["ECCE_LOCAL_DATA"] = data
    with xdisplay.Display() as display:
        subprocess.run([os.path.join(apps.INSTALL, "bin", "ecce-gateway-start")], env=display.env(), timeout=180)
        try:
            cmds = os.path.join(work, "commands"); open(cmds, "w").write("examples genchem\n")

            def imported(_d):
                end = time.time() + 900
                while time.time() < end:
                    if all(find(root, a) for a in ATOMS):
                        time.sleep(20); return
                    time.sleep(5)
            apps.run(display, "organizer", windowTimeout=60, settle=10,
                     env={"ECCE_TEST_ORGANIZER": cmds, "ECCE_NO_EXAMPLE_IMPORT": ""}, inspect=imported)
            for a in ATOMS:
                calc = find(root, a)
                assert calc, a
                scene = os.path.join(work, "scene-" + a)
                open(scene, "w").write("hold 15\nplotshot tm-mo-%s %s %s MO Diagram\nhold 2\n" % (a.lower(), W, H))
                os.environ["ECCE_VIEWER_SCENE"] = scene
                os.environ["ECCE_VIEWER_SCENE_OUT"] = PNG
                log = mc.builder(display, "file://" + calc + "/", ["wait 25000"], settle=40, panel="MO Diagram")
                print("\n".join(l for l in log.splitlines() if "PLOTSHOT:" in l or "FAIL" in l)[-1500:])
        finally:
            subprocess.run([os.path.join(apps.INSTALL, "bin", "ecce-gateway-stop")], env=display.env(), timeout=120)
    shutil.rmtree(work, ignore_errors=True)
    print("png:", sorted(os.listdir(PNG)))


if __name__ == "__main__":
    main()
