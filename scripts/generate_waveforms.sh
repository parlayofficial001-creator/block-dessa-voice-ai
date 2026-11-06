#!/usr/bin/env bash
# Render a two-lane waveform (left channel = person in blue, right channel =
# AI in red) for each stereo recording you pass in. Outputs go to
# assets/waveforms/<name>.png and assets/waveforms/<name>.mp4.
#
# Only use recordings you have the right to process. Outputs are gitignored
# so third-party audio is never committed to this repository.
#
# Usage: scripts/generate_waveforms.sh recording.wav [more.wav ...]
set -euo pipefail

if [[ $# -eq 0 ]]; then
  echo "usage: $0 <stereo-audio> [more ...]" >&2
  exit 2
fi
command -v ffmpeg >/dev/null || { echo "ffmpeg is required" >&2; exit 1; }

out_dir="$(cd "$(dirname "$0")/.." && pwd)/assets/waveforms"
mkdir -p "$out_dir"
colors="0x3B82F6|0xEF4444"

for input in "$@"; do
  channels="$(ffprobe -v error -select_streams a:0 -show_entries stream=channels -of csv=p=0 "$input")"
  if [[ "$channels" -lt 2 ]]; then
    echo "skip: $input is not stereo (one speaker per channel required)" >&2
    continue
  fi
  name="$(basename "${input%.*}")"

  ffmpeg -v error -y -i "$input" \
    -filter_complex "[0:a]showwavespic=s=1600x400:split_channels=1:colors=${colors}" \
    -frames:v 1 "$out_dir/$name.png"

  ffmpeg -v error -y -i "$input" \
    -filter_complex "[0:a]showwaves=s=1280x360:mode=cline:rate=30:split_channels=1:colors=${colors},format=yuv420p[v]" \
    -map "[v]" -map 0:a -c:v libx264 -c:a aac -shortest "$out_dir/$name.mp4"

  echo "$out_dir/$name.png"
  echo "$out_dir/$name.mp4"
done
