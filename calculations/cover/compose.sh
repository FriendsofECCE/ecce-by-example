#!/bin/sh
# compose.sh <maps dir> <out.png> <hero> <tile1> ...
# Cover art for A4 (DPI env, default 150): hero map on the top two-thirds, the
# accent band at its foot, a row of equal-height maps below. main.tex sets the text.
# A map name ending in ":s" is an orbital (signed amplitude); otherwise a density.
set -e
M=$1; OUT=$2; HERO=$3; shift 3
DPI=${DPI:-150}; W=$((DPI*827/100)); H=$((DPI*1169/100))
R="$(dirname "$0")/render_maps.py"
HH=$((H*2/3)); N=$#; GAP=$((W/60)); TW=$(( (W - (N+1)*GAP) / N )); TH=$((TW*${TILE_ASPECT:-3}/4))
draw() { n=${1%:s}; if [ "$n" != "$1" ]; then python3 "$R" "$M/$n.csv.gz" "$2" $3 $4 --signed $5; \
         else python3 "$R" "$M/$n.csv.gz" "$2" $3 $4 $5; fi; }
draw "$HERO" "$M/_hero.png" $W $HH "--zoom ${HZOOM:-1.0}"
i=0; TILES=""; for t in "$@"; do draw "$t" "$M/_t$i.png" $TW $TH "--lines 1.5"; TILES="$TILES $M/_t$i.png"; i=$((i+1)); done
convert $TILES -bordercolor white -border $((GAP/2))x0 +append "$M/_row.png"
BAND=$((H/9)); OC='rgb(243,102,25)'
convert -size ${W}x${H} xc:white "$M/_hero.png" -geometry +0+0 -composite \
  \( -size ${W}x${BAND} xc:"$OC" \) -geometry +0+$((HH - BAND)) -composite \
  "$M/_row.png" -gravity north -geometry +0+$((HH + GAP)) -composite \
  "$OUT"
rm -f "$M"/_*.png
