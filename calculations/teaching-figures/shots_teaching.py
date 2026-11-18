#!/usr/bin/env python3
"""Figures for the Teaching chapters, headless, from stored ECCE examples.

    ECCE_TEST_HOME=<install> ECCE_TEST_WRAPPERS=<wrappers> \\
        python3 shots_teaching.py <ECCE checkout> <png dir> <spec.py> [JOB ...]

<spec.py> defines JOBS = {job: (example folder under data/client/examples,
panel to open, [scene lines])}; "{png}" in a scene line is the png dir.
Each job opens the stored calculation in the Builder (tests/apps harness:
isolated HOME, local data, Xvfb) with ECCE_OPEN_PANEL=<panel> and runs the
scene (ECCE_VIEWER_SCENE): mofield, moselect, mopanel compute, rotate,
viewall, saveimage <png> 2 white, plotshot ... for panels.
"""
import glob, os, runpy, sys
REPO, PNG, SPEC = (os.path.abspath(a) for a in sys.argv[1:4])
ONLY = sys.argv[4:]
sys.path.insert(0, os.path.join(REPO, "tests", "apps"))
import apps, fixture, run_tests, xdisplay          # noqa: E402
from ecceqm_builder_test import installLocal        # noqa: E402

JOBS = runpy.run_path(SPEC)["JOBS"]
EX = os.path.join(REPO, "data", "client", "examples")


def stored(example):
    if os.path.isabs(example):
        return example
    return [d for d in glob.glob(os.path.join(EX, example, "stored", "*")) if os.path.isdir(d)][0]


def key(example):
    b = os.path.basename(example)
    return b.split("-", 1)[1] if b.startswith(("ecceqm-", "orca-")) else b


def main():
    xdisplay.SCREEN = "1600x1000x24"
    os.makedirs(PNG, exist_ok=True)

    def checkApp(display, name, results, verbose=False):
        folder = os.path.join(fixture.stateDir(), "teachshots-localdata")
        jobs = {j: v for j, v in JOBS.items() if not ONLY or j in ONLY}
        calcs = {}
        for j, (example, panel, lines) in jobs.items():
            calcs[key(example)] = stored(example)
        urls = installLocal(folder, calcs)
        os.environ["ECCE_LOCAL_DATA"] = folder
        restore = fixture.settleUpgradeNotices()
        out = os.path.join(folder, "shots"); os.makedirs(out, exist_ok=True)
        scene = os.path.join(folder, "scene")
        try:
            for j, (example, panel, lines) in jobs.items():
                url = urls[key(example)]
                open(scene, "w").write("\n".join(l.format(png=PNG) for l in lines) + "\nhold 1\n")
                env = {"ECCE_VIEWER_SCENE": scene, "ECCE_VIEWER_SCENE_OUT": PNG,
                       "ECCE_TRANSPARENCY_FALLBACK_MS": "0"}
                if panel:
                    env.update(ECCE_OPEN_PANEL=panel, ECCE_PANEL_MODE="detail")
                r = apps.run(display, "builder", args=("-context", url), windowTimeout=120, settle=600, env=env)
                print("==== job", j)
                print("\n".join(l for l in (r.log or "").splitlines()
                                if any(k in l for k in ("SCENE", "FAIL", "MOPANEL", "SAVEIMAGE", "PLOTSHOT",
                                                         "unknown", "Error")))[-3000:], flush=True)
        finally:
            restore()
            os.environ.pop("ECCE_LOCAL_DATA", None)
    run_tests.checkApp = checkApp
    sys.argv = [sys.argv[0], "--app", "builder"]
    return run_tests.main()


if __name__ == "__main__":
    sys.exit(main())
