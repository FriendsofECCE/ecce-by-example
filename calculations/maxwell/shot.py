#!/usr/bin/env python3
"""Figure for chapter teaching-maxwell, headless: the Speed Distribution panel of
he-gas with ar-gas-300K compared over it (General Chemistry example set).

    ECCE_SRC=<checkout> ECCE_TEST_HOME=<install>/ecce ECCE_TEST_WRAPPERS=<install>/bin \\
        python3 shot.py <png dir> [<own run> <compared run> <shot name>]

Default: he-gas with ar-gas-300K compared, shot speed-he-ar.

Uses the import and Builder helpers of tests/apps/md_compare_examples_test.py
(isolated HOME, local data, Xvfb); the panel is photographed by the Builder's
plotshot scene command.
"""
import os, shutil, subprocess, sys, tempfile, time
REPO = os.environ.get("ECCE_SRC", "ECCE")
sys.path.insert(0, os.path.join(REPO, "tests", "apps"))
import apps, isolate, xdisplay  # noqa: E402
import md_compare_examples_test as mc  # noqa: E402

PNG = os.path.abspath(sys.argv[1])
OWN, OTHER, NAME = (sys.argv[2:5] if len(sys.argv) >= 5
                     else ("he-gas", "ar-gas-300K", "speed-he-ar"))
os.makedirs(PNG, exist_ok=True)


def main():
    isolate.apply(apps.INSTALL)
    os.environ["ECCE_NO_REAP"] = "1"
    os.environ["GTK_THEME"] = "Adwaita"
    work = tempfile.mkdtemp(prefix="maxwellshot-", dir=os.environ.get("ECCE_REALUSERHOME"))
    data = os.path.join(work, "data")
    root = os.path.join(data, "users", "local")
    os.makedirs(root)
    os.environ["ECCE_LOCAL_DATA"] = data
    with xdisplay.Display() as display:
        subprocess.run([os.path.join(apps.INSTALL, "bin", "ecce-gateway-start")],
                       env=display.env(), timeout=180)
        try:
            cmds = os.path.join(work, "commands")
            open(cmds, "w").write("examples genchem\n")

            def imported(_d):
                end = time.time() + 900
                while time.time() < end:
                    done = [mc.task(root, st) for st in (OWN, OTHER)]
                    if all(done) and all(os.path.exists(os.path.join(d, "Props", "GEOMTRACE"))
                                         for d in done):
                        time.sleep(20)
                        return
                    time.sleep(5)
            apps.run(display, "organizer", windowTimeout=60, settle=10,
                     env={"ECCE_TEST_ORGANIZER": cmds, "ECCE_NO_EXAMPLE_IMPORT": ""},
                     inspect=imported)
            he, ar = mc.task(root, OWN), mc.task(root, OTHER)
            assert he and ar, (he, ar)
            scene = os.path.join(work, "scene")
            open(scene, "w").write("hold 25\nplotshot " + NAME + " 900 620 Speed Distribution\nhold 2\n")
            os.environ["ECCE_VIEWER_SCENE"] = scene
            os.environ["ECCE_VIEWER_SCENE_OUT"] = PNG
            log = mc.builder(display, "file://" + he + "/",
                             ["wait 6000", "comparewith " + OTHER + "/" + os.path.basename(ar),
                              "wait 30000"], settle=60)
            print("\n".join(l for l in log.splitlines()
                            if "PLOTSHOT" in l or "mdcompare" in l or "FAIL" in l)[-3000:])
        finally:
            subprocess.run([os.path.join(apps.INSTALL, "bin", "ecce-gateway-stop")],
                           env=display.env(), timeout=120)
    shutil.rmtree(work, ignore_errors=True)
    print("png:", os.listdir(PNG))


if __name__ == "__main__":
    main()
