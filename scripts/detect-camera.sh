#!/usr/bin/env bash
# Detect USB cameras connected to this machine.
set -euo pipefail

echo "== USB camera detection =="
if ls /dev/video* >/dev/null 2>&1; then
  echo "Video devices found:"
  ls -l /dev/video*
  echo ""
  if command -v v4l2-ctl >/dev/null 2>&1; then
    v4l2-ctl --list-devices || true
  else
    echo "(For detailed info: sudo apt-get install -y v4l-utils)"
  fi
else
  echo "No /dev/video* devices found. Plug in the USB camera and try again."
  exit 0
fi
