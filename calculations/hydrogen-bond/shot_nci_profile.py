#!/usr/bin/env python3
"""Figures for chapter teaching-hydrogen-bond, headless: the NCI surface and the
Density Profile (O1 to O4) of the General Chemistry example ecceqm-h2o_dimer.

    ECCE_SRC=<checkout> ECCE_TEST_HOME=<install>/ecce ECCE_TEST_WRAPPERS=<install>/bin \\
        python3 shot_nci_profile.py <out dir> [rotations, comma separated degrees about y]

NCI: saveimage at 2x on white, one picture per rotation (nci-rotN.png) so that the
orientation can be chosen. Profile: dp-profile.csv and dp-profile.png.
"""
import glob, os, shutil, subprocess, sys, tempfile, time
REPO = os.environ.get("ECCE_SRC", "ECCE")
sys.path.insert(0, os.path.join(REPO, "tests", "apps"))
import apps, isolate, xdisplay  # noqa: E402
import md_compare_examples_test as mc  # noqa: E402

PNG = os.path.abspath(sys.argv[1])
ROTS = [int(x) for x in (sys.argv[2] if len(sys.argv) > 2 else "0,30,30,30,30,30").split(",")]
os.makedirs(PNG, exist_ok=True)
STUDY = "ecceqm-h2o_dimer"


def find(root):
    f = glob.glob(os.path.join(root, "**", STUDY, "*", ".ecce-meta"), recursive=True)
    return os.path.dirname(f[0]) if f else None


def main():
    isolate.apply(apps.INSTALL)
    os.environ.update(ECCE_NO_REAP="1", GTK_THEME="Adwaita",
                      GDK_DPI_SCALE=os.environ.get("DPI", "1.5"))
    work = tempfile.mkdtemp(prefix="hbshot-", dir=os.environ.get("ECCE_REALUSERHOME"))
    data = os.path.join(work, "data"); root = os.path.join(data, "users", "local")
    os.environ["ECCE_LOCAL_DATA"] = data
    with xdisplay.Display() as display:
        subprocess.run([os.path.join(apps.INSTALL, "bin", "ecce-gateway-start")], env=display.env(), timeout=180)
        try:
            # The stored calculation copied straight into local data: importing
            # the whole General Chemistry set takes minutes.
            import ecceqm_builder_test as eb
            src = os.path.join(REPO, "data", "client", "examples", "genchem",
                               "intermolecular-interactions", "ecceqm-h2o_dimer", "stored", "h2o_dimer")
            url = eb.installLocal(data, {"h2o_dimer": src})["h2o_dimer"]
            calc = url[len("file://"):].rstrip("/")
            os.environ["ECCE_VIEWER_SCENE_OUT"] = PNG
            # NCI pictures
            # NCI_STEPS: "cmd;cmd;..." between the shots, e.g. "rotate 50;rotatex 20".
            lines = ["background 1 1 1", "hold 5", "mofield NCI", "mopanel nci", "hold 25", "viewall",
                     "zoom %s" % os.environ.get("NCI_ZOOM", "1.7"), "hold 3",
                     "saveimage %s/nci-a.png %s white" % (PNG, os.environ.get("NCI_FACTOR", "2"))]
            for i, step in enumerate(os.environ.get("NCI_STEPS", "rotate 50;rotatex 25").split(";")):
                lines += [step, "hold 3", "saveimage %s/nci-%s.png %s white" % (PNG, "bcdefg"[i], os.environ.get("NCI_FACTOR", "2"))]
            lines.append("hold 2")
            scene = os.path.join(work, "scene-nci"); open(scene, "w").write("\n".join(lines) + "\n")
            os.environ["ECCE_VIEWER_SCENE"] = scene
            log = mc.builder(display, "file://" + calc + "/", ["wait 70000"], settle=100, panel="MOs")
            open(os.path.join(PNG, "nci-builder.log"), "w").write(log)
            print("\n".join(l for l in log.splitlines() if any(k in l for k in ("MOPANEL", "FAIL", "SAVEIMAGE", "saveimage", "unknown")))[-2500:])
            # Density profile
            lines = ["hold 10", "dpopen", "dpmode line", "dpatoms 1 4", "dpquantity density", "dpshow total",
                     "dpyaxis log", "dpcsv dp-profile", "dppng dp-profile 1000 650", "hold 2",
                     "plotshot dp-docked 0 0 Density Profile:docked", "hold 2"]
            scene = os.path.join(work, "scene-dp"); open(scene, "w").write("\n".join(lines) + "\n")
            os.environ["ECCE_VIEWER_SCENE"] = scene
            log = mc.builder(display, "file://" + calc + "/", ["wait 40000"], settle=60, panel="Density Profile")
            print("\n".join(l for l in log.splitlines() if any(k in l for k in ("DENSITYPROFILE", "FAIL", "unknown", "PLOTSHOT")))[-2500:])
        finally:
            subprocess.run([os.path.join(apps.INSTALL, "bin", "ecce-gateway-stop")], env=display.env(), timeout=120)
    shutil.rmtree(work, ignore_errors=True)
    print("out:", sorted(os.listdir(PNG)))


if __name__ == "__main__":
    main()
