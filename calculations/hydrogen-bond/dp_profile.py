#!/usr/bin/env python3
"""Density Profile (total density, line between two atoms) of a stored
General Chemistry example, headless, exported as CSV by the panel.

    ECCE_SRC=<checkout> ECCE_TEST_HOME=<install> ECCE_TEST_WRAPPERS=<install-bin> \\
        python3 dp_profile.py <out dir> <example> <calc> <atom I> <atom J> <name>

e.g. dp_profile.py out ecceqm-nacl_ion_pair nacl_ion_pair 1 2 dp-Na1-Cl2
writes <out>/<name>.csv (and the panel's own <name>.png).
"""
import os, shutil, subprocess, sys, tempfile
REPO = os.environ.get("ECCE_SRC", "ECCE")
sys.path.insert(0, os.path.join(REPO, "tests", "apps"))
import apps, isolate, xdisplay  # noqa: E402
import md_compare_examples_test as mc  # noqa: E402
import ecceqm_builder_test as eb  # noqa: E402

OUT, STUDY, CALC, I, J, NAME = sys.argv[1:7]
OUT = os.path.abspath(OUT)
os.makedirs(OUT, exist_ok=True)


def main():
    isolate.apply(apps.INSTALL)
    os.environ.update(ECCE_NO_REAP="1", GTK_THEME="Adwaita", GDK_DPI_SCALE="1.5")
    work = tempfile.mkdtemp(prefix="dpshot-", dir=os.environ.get("ECCE_REALUSERHOME"))
    data = os.path.join(work, "data")
    os.environ["ECCE_LOCAL_DATA"] = data
    with xdisplay.Display() as display:
        subprocess.run([os.path.join(apps.INSTALL, "bin", "ecce-gateway-start")], env=display.env(), timeout=180)
        try:
            src = os.path.join(REPO, "data", "client", "examples", "genchem",
                               "intermolecular-interactions", STUDY, "stored", CALC)
            url = eb.installLocal(data, {CALC: src})[CALC]
            os.environ["ECCE_VIEWER_SCENE_OUT"] = OUT
            lines = ["background 1 1 1", "hold 10", "dpopen", "dpmode line", "dpatoms %s %s" % (I, J),
                     "dpquantity density", "dpshow total", "dpyaxis log", "dpcsv " + NAME,
                     "dppng %s 1000 650" % NAME, "hold 2"]
            scene = os.path.join(work, "scene-dp")
            open(scene, "w").write("\n".join(lines) + "\n")
            os.environ["ECCE_VIEWER_SCENE"] = scene
            log = mc.builder(display, url, ["wait 40000"], settle=60, panel="Density Profile")
            print("\n".join(l for l in log.splitlines() if any(k in l for k in ("DENSITYPROFILE", "FAIL", "unknown")))[-1500:])
        finally:
            subprocess.run([os.path.join(apps.INSTALL, "bin", "ecce-gateway-stop")], env=display.env(), timeout=120)
    shutil.rmtree(work, ignore_errors=True)
    print("out:", sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main()
