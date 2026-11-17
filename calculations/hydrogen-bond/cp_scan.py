#!/usr/bin/env python3
"""Counterpoise single points on the stored relaxed scans of oo_scan.py, run through ECCE.

    ECCE_SRC=<checkout> ECCE_TEST_HOME=<install>/ecce ECCE_TEST_WRAPPERS=<install>/bin \\
        python3 cp_scan.py <out dir> <data root> [pair ...]

<data root>/<pair> is an oo_scan.py --data folder holding the scans inward and
outward. For each scan the Builder assigns the two fragments (fragment hooks,
then save), the Relaxed Scan panel makes the counterpoise calculation
(scan cpsingle), the Launcher runs it on localhost, and when it is complete the
panel's CP column (scan cpcolumn) and CSV export go to <out>, with the
calculation's SCANCP, SCANRAW and SCANBSSE vectors.
"""
import glob, os, re, shutil, subprocess, sys, time
REPO = os.environ.get("ECCE_SRC", "ECCE")
sys.path.insert(0, os.path.join(REPO, "tests", "apps"))
import apps, isolate, xdisplay  # noqa: E402
import md_compare_examples_test as mc  # noqa: E402

# atoms of fragment 1 and 2 (1-based), and (charge, multiplicity) of each
FRAG = {"ar_dimer": ("1", "2", (0, 1), (0, 1)),
        "h2o_dimer": ("1-3", "4-6", (0, 1), (0, 1)),
        "na_h2o": ("1", "2-4", (1, 1), (0, 1)),
        "nacl_ion_pair": ("1", "2", (1, 1), (-1, 1))}
SCANS = ("inward", "outward")
TERMINAL = ("Complete", "Completed", "Failed", "Killed", "Unsuccessful", "Loaded")
OUT = os.path.abspath(sys.argv[1])
ROOT = os.path.abspath(sys.argv[2])
PAIRS = sys.argv[3:] or list(FRAG)


def meta_get(path, key):
    m = re.search(r"ecce:%s\t\t([^\n]*)" % key, open(path, errors="surrogateescape").read())
    return m.group(1) if m else ""


def app(display, data, name, var, lines, url, tag, settle=60, panel=None):
    script = os.path.join(data, "%s-%s.script" % (name, tag))
    open(script, "w").write("\n".join(lines) + "\n")
    env = {var: script, "ECCE_FEEDBACK_STDERR": "1"}
    if panel:
        env.update(ECCE_PANEL_MODE="detail", ECCE_OPEN_PANEL=panel)
    r = apps.run(display, name, args=["-context", url], windowTimeout=90, settle=settle, env=env)
    log = r.log or ""
    open(os.path.join(OUT, "%s-%s.log" % (tag, name)), "w").write(log)
    return log


def pair(display, p):
    data = os.path.join(ROOT, p)
    root = os.path.join(data, "users", "local", "qm")
    os.environ["ECCE_LOCAL_DATA"] = data
    a1, a2, s1, s2 = FRAG[p]
    subprocess.run([os.path.join(apps.INSTALL, "bin", "ecce-gateway-start")], env=display.env(), timeout=180)
    children = {}
    try:
        for n in SCANS:
            url = "file://" + os.path.join(root, n) + "/"
            tag = "%s-%s" % (p, n)
            mvm = os.path.join(root, n, "Parameters", "chemsys.mvm")
            # A Builder save of the fragments sets a completed scan back to Created, and
            # scan cpsingle then refuses it; the fragment block the Builder writes is
            # appended to the stored structure instead, as tests/launch/counterpoise_scan_test.py does.
            if "fragment_states" not in open(mvm, errors="replace").read():
                natoms = {"ar_dimer": 2, "h2o_dimer": 6, "na_h2o": 4, "nacl_ion_pair": 2}[p]
                first = {"ar_dimer": 1, "h2o_dimer": 3, "na_h2o": 1, "nacl_ion_pair": 1}[p]
                with open(mvm, "a") as f:
                    f.write("\nfragment_states: 2\n1 %d %d\n2 %d %d\natom_fragment_list:\n" % (s1 + s2)
                            + "".join("%d\n" % (1 if k < first else 2) for k in range(natoms)))
            log = app(display, data, "builder", "ECCE_BUILDER_SCRIPT",
                      ["wait 6000", "scan cpsingle", "wait 6000", "quit"], url, tag + "-cpsingle",
                      panel="Relaxed Scan")
            m = re.search(r"scan cpsingle url=(\S+)", log) or \
                re.search(r"already has a counterpoise calculation\D*?(file://\S+)", log)
            print(tag, "\n".join(l for l in log.splitlines() if "cpsingle" in l or "FAIL" in l)[-600:], flush=True)
            if not m:
                sys.exit(tag + ": no counterpoise calculation made")
            cu = m.group(1)
            child = cu.replace("file://", "").rstrip("/")
            children[n] = (url, cu, child)
            if meta_get(os.path.join(child, ".ecce-meta"), "state") in TERMINAL:
                continue
            run = os.path.join(data, "run-cp-" + n)
            os.makedirs(run, exist_ok=True)
            log = app(display, data, "launcher", "ECCE_LAUNCHER_SCRIPT",
                      ["wait 3000", "machine localhost", "rundir " + run, "wait 1500", "launch",
                       "wait 8000", "quit"], cu, tag + "-launch", settle=30)
            print(tag, "\n".join(l for l in log.splitlines() if "LAUNCHER" in l or "FAIL" in l)[-600:], flush=True)
        end = time.time() + 12 * 3600
        while time.time() < end:
            st = {n: meta_get(os.path.join(c[2], ".ecce-meta"), "state") for n, c in children.items()}
            print(time.strftime("%H:%M:%S"), p, st, flush=True)
            if all(v in TERMINAL for v in st.values()):
                break
            time.sleep(120)
        for n, (url, cu, child) in children.items():
            tag = "%s-%s" % (p, n)
            for k in ("SCANCP", "SCANRAW", "SCANBSSE", "SCANCOORD", "SCANENERGY"):
                for d in (child, os.path.join(root, n)):
                    f = os.path.join(d, "Props", k)
                    if os.path.exists(f):
                        shutil.copy(f, os.path.join(OUT, "%s.%s" % (tag, k)))
                        break
            for f in glob.glob(os.path.join(child, "Outputs", "*.qmout")):
                shutil.copy(f, os.path.join(OUT, tag + "-cp.qmout"))
            log = mc.builder(display, url, ["wait 12000", "scan cpcolumn",
                                            "scancsv %s/%s-cp.csv" % (OUT, tag), "wait 8000"],
                             settle=60, panel="Relaxed Scan")
            open(os.path.join(OUT, tag + "-cpcolumn.log"), "w").write(log or "")
            print(tag, "state", meta_get(os.path.join(child, ".ecce-meta"), "state"), flush=True)
    finally:
        subprocess.run([os.path.join(apps.INSTALL, "bin", "ecce-gateway-stop")], env=display.env(), timeout=120)


def main():
    os.makedirs(OUT, exist_ok=True)
    isolate.apply(apps.INSTALL)
    os.environ.update(ECCE_NO_REAP="1", GTK_THEME="Adwaita", OMP_NUM_THREADS=os.environ.get("OMP_NUM_THREADS", "5"))
    xdisplay.SCREEN = "1500x950x24"
    with xdisplay.Display() as display:
        for p in PAIRS:
            print("===", p, time.strftime("%H:%M:%S"), flush=True)
            pair(display, p)
    print("out:", sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main()
