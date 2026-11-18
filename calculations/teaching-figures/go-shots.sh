#!/bin/bash
# Run shots_teaching.py on an offload host against an installed build of ECCE.
#   go-shots.sh <build ref under ~/ecce-offload/build> <ECCE checkout> <png dir> <spec.py> [JOB ...]
R=$1; SRC=$2; shift 2
B=$HOME/ecce-offload/build/$R
T=$(cd "$(dirname "$0")" && pwd)
export HOME=$T/home XDG_CACHE_HOME=$T/home/.cache TMPDIR=$T/home/tmp DISPLAY=:987
mkdir -p "$TMPDIR"
export ECCE_TEST_HOME=$B/install ECCE_TEST_WRAPPERS=$B/install-bin ECCE_TEST_ANY_VERSION=1
export GTK_THEME=Adwaita GDK_DPI_SCALE=${DPI:-1.5}
cd "$SRC" && exec nice python3 "$T/shots_teaching.py" "$SRC" "$@"
