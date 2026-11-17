#!/usr/bin/env python3
"""Figures for the chapter "Localised bonds" (ethane, ethene, ethyne), headless.

    ECCE_TEST_HOME=<install> ECCE_TEST_WRAPPERS=<wrappers> \\
        python3 shots_locbonds.py <ECCE checkout> <png dir>

Uses the stored ECCE-QM examples in data/client/examples/organic/
bonding-in-hydrocarbons, the tests/apps harness (isolated HOME, Xvfb) and
the Builder's scene hooks: plotshot ... MOs:dockedloctable for the localised
table (its rows are printed), then mofield Localised MO, moselect, mopanel
compute and saveimage <png> 2 white for each orbital, in two views.
"""
import os, shutil, sys
REPO, PNG = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
sys.path.insert(0, os.path.join(REPO, "tests", "apps"))
import apps, fixture, run_tests, xdisplay          # noqa: E402
from ecceqm_builder_test import installLocal        # noqa: E402
from ecceqm_motable_test import parseState          # noqa: E402

SUF = ".ecce-9.5.3-dev"
EX = os.path.join(REPO, "data", "client", "examples", "organic", "bonding-in-hydrocarbons")
CALCS = {m: os.path.join(EX, "ecceqm-" + m, "stored", m) for m in ("ethane", "ethene", "ethyne")}
# localised orbital number -> picture name (order as stored in LOCMOLABEL)
ORBS = {"ethane": {3: "cc-sigma", 5: "ch-sigma"},
        "ethene": {3: "cc-sigma", 4: "cc-pi", 6: "ch-sigma"},
        "ethyne": {3: "cc-sigma", 4: "cc-pi1", 5: "cc-pi2", 6: "ch-sigma"}}
VIEWS = (("side", ["rotate 90", "viewall"], ["rotate -90"]),)
# C-H bonds of ethane and ethene: H3 points along the side view, so the C1-H4
# bond is drawn from views that put it across the page.
CH_VIEWS = (("a", ["rotatex 90", "viewall"], ["rotatex -90"]),
            ("b", ["rotatex 90", "rotate 90", "viewall"], ["rotate -90", "rotatex -90"]),
            ("c", ["rotate 60", "viewall"], ["rotate -60"]),
            ("d", ["rotate 90", "rotatex 90", "viewall"], ["rotatex -90", "rotate -90"]))
if os.environ.get("LOCB_CH"):
    ORBS = {"ethane": {5: "ch-sigma"}, "ethene": {6: "ch-sigma"}}
    VIEWS = CH_VIEWS
    CALCS = {m: CALCS[m] for m in ORBS}


def main():
    xdisplay.SCREEN = "1500x950x24"
    os.makedirs(PNG, exist_ok=True)

    def checkApp(display, name, results, verbose=False):
        folder = os.path.join(fixture.stateDir(), "locbonds-localdata")
        urls = installLocal(folder, CALCS)
        os.environ["ECCE_LOCAL_DATA"] = folder
        restore = fixture.settleUpgradeNotices()
        out = os.path.join(folder, "shots"); os.makedirs(out, exist_ok=True)
        scene = os.path.join(folder, "scene")
        try:
            for calc, url in urls.items():
                shot = "loctable-" + calc
                open(scene, "w").write("plotshot %s 0 0 MOs:dockedloctable\nhold 1\n" % shot)
                r = apps.run(display, "builder", args=("-context", url), windowTimeout=120, settle=300,
                             env={"ECCE_PANEL_FULLSCREEN": "1", "ECCE_VIEWER_SCENE": scene,
                                  "ECCE_VIEWER_SCENE_OUT": out})
                st = parseState(r.log or "", shot)
                print("---- %s header %s" % (shot, st.get("header")))
                for row in st["row"]:
                    print("ROW %s | %s" % (calc, " | ".join(row)))
                if os.path.exists(os.path.join(out, shot + ".png")):
                    shutil.copy(os.path.join(out, shot + ".png"), os.path.join(PNG, shot + SUF + ".png"))
                lines = ["mofield Localised MO", "background 1 1 1"]
                for n, tag in ORBS[calc].items():
                    lines += ["moselect %d" % n, "motable sel-%s-%d" % (calc, n), "mopanel compute"]
                    for view, pre, post in VIEWS:
                        lines += pre + ["saveimage %s/%s-%s-%s%s.png 2 white" % (PNG, calc, tag, view, SUF)] + post
                open(scene, "w").write("\n".join(lines) + "\n")
                r = apps.run(display, "builder", args=("-context", url), windowTimeout=120, settle=600,
                             env={"ECCE_OPEN_PANEL": "MOs", "ECCE_VIEWER_SCENE": scene,
                                  "ECCE_VIEWER_SCENE_OUT": out, "ECCE_TRANSPARENCY_FALLBACK_MS": "0"})
                print("\n".join(l for l in (r.log or "").splitlines()
                                if "SCENE" in l or "FAIL" in l or "MOPANEL" in l)[-2000:])
                for n in ORBS[calc]:
                    p = os.path.join(out, "sel-%s-%d.txt" % (calc, n))
                    print("SEL %s %d: %s" % (calc, n, open(p).read().replace("\n", " ; ")[:400]
                                             if os.path.exists(p) else "missing"))
                if os.path.exists(os.path.join(out, "FAILED")):
                    print("FAILED:", open(os.path.join(out, "FAILED")).read())
        finally:
            restore()
            os.environ.pop("ECCE_LOCAL_DATA", None)
    run_tests.checkApp = checkApp
    sys.argv = [sys.argv[0], "--app", "builder"]
    return run_tests.main()


if __name__ == "__main__":
    sys.exit(main())
