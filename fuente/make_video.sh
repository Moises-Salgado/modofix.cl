#!/usr/bin/env bash
# Builds the hero background loop from the MotionSites clip.
# - hue=-72 turns the violet globe into the brand teal (luma is kept).
# - curves only removes the clip's near-black base (~5 %) so it vanishes
#   under mix-blend-mode: screen; the glow, arrows and stars keep their
#   original brightness.
# - the last second is cross-faded into the first one for a seamless loop.
set -euo pipefail
SRC=${1:?usage: make_video.sh source.mp4 outdir}
OUT=${2:?usage: make_video.sh source.mp4 outdir}
mkdir -p "$OUT"
HUE=${HUE:--72}
LOOK="hue=h=${HUE},curves=all='0/0 0.058/0 0.1/0.045 0.2/0.165 1/1'"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SRC")
X=1
OFF=$(python3 -c "print(round($D - 2*$X, 4))")

loop() {  # $1 = extra scale filter, $2 = crf, $3 = output
  ffmpeg -v error -y -i "$SRC" -filter_complex \
    "[0:v]${1}${LOOK},split[a][b];[a]trim=start=${X},setpts=PTS-STARTPTS[m];[b]trim=end=${X},setpts=PTS-STARTPTS[h];[m][h]xfade=transition=fade:duration=${X}:offset=${OFF},format=yuv420p[v]" \
    -map "[v]" -an -c:v libx264 -preset veryfast -crf "$2" -profile:v high -movflags +faststart "$3"
}

loop "" 23 "$OUT/hero-globo-1080.mp4"
loop "scale=1280:720:flags=lanczos," 25 "$OUT/hero-globo-720.mp4"
ffmpeg -v error -y -i "$OUT/hero-globo-1080.mp4" -frames:v 1 -q:v 4 "$OUT/hero-globo-poster.jpg"
ls -la "$OUT"
