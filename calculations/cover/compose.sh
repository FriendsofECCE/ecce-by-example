#!/bin/sh
# compose.sh <maps dir> <out.png> <hero> <tile1> ...
# Cover art for A4 (DPI env, default 150): hero map on the top two-thirds, the
# accent band at its foot, a row of equal-height maps below. main.tex sets the text.
set -e
M=$1; OUT=$2; HERO=$3; shift 3
DPI=${DPI:-150}; W=$((DPI*827/100)); H=$((DPI*1169/100))
R="$(dirname "$0")/render_maps.py"
HH=$((H*2/3)); N=$#; GAP=$((W/60)); TW=$(( (W - (N+1)*GAP) / N ))
python3 "$R" "$M/$HERO.csv" "$M/_hero.png" $W $HH --zoom ${HZOOM:-1.0}
i=0; for t in "$@"; do python3 "$R" "$M/$t.csv" "$M/_t$i.png" $TW $TW --zoom ${TZOOM:-1.0} --lines 1.5; i=$((i+1)); done
TILES=""; i=0; for t in "$@"; do TILES="$TILES $M/_t$i.png"; i=$((i+1)); done
convert $TILES -bordercolor white -border $((GAP/2))x0 +append "$M/_row.png"
BAND=$((H/9)); OC='rgb(243,102,25)'
convert -size ${W}x${H} xc:white "$M/_hero.png" -geometry +0+0 -composite \
  \( -size ${W}x${BAND} xc:"$OC" \) -geometry +0+$((HH - BAND)) -composite \
  "$M/_row.png" -gravity north -geometry +0+$((HH + GAP)) -composite \
  "$OUT"
