#!/usr/bin/env bash
# One-time setup in a fresh cloud session: copies the kit to /home/claude and installs voices.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p /home/claude
cp -rn "$HERE/tree/." /home/claude/
cp "$HERE/tools/"*.py /home/claude/
pip install --break-system-packages -q sherpa-onnx soundfile numpy pillow >/dev/null
cd /home/claude/tts
for v in priyamvada rohan pratham; do
  d="vits-piper-hi_IN-$v-medium"
  if [ ! -d "$d" ]; then
    curl -sSL -o "$d.tar.bz2" "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/$d.tar.bz2"
    tar xjf "$d.tar.bz2" && rm "$d.tar.bz2"
  fi
done
command -v ffmpeg >/dev/null || (apt-get update -qq && apt-get install -y -qq ffmpeg >/dev/null)
python3 -c "import sherpa_onnx, PIL; print('setup ok')"
