#!/usr/bin/env bash
# Genera la versión acelerada (timelapse) de una grabación, sin audio.
# Uso: ./acelerar.sh "~/Movies/code-with-me/code-with-me 2026-10-17 15-00-00.mov" [factor=8]
set -euo pipefail
entrada="$1"
factor="${2:-8}"
salida="${entrada%.*}_x${factor}.mp4"
ffmpeg -hide_banner -i "$entrada" -vf "setpts=PTS/${factor},fps=30" -an \
  -c:v h264_videotoolbox -b:v 8M "$salida"
echo "Listo: $salida"
