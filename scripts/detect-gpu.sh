#!/usr/bin/env bash
# Report NVIDIA GPU status and write an enrichment file the API reads
# (<FOOTPASS_DATA_DIR>/hardware.json) so the System Health page can show it.
# A GPU is NOT required by FootPass.
set -euo pipefail

DATA_DIR="${FOOTPASS_DATA_DIR:-/srv/footpass}"

if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "No NVIDIA GPU / driver detected. FootPass runs fine without one."
  exit 0
fi

echo "== NVIDIA GPU =="
nvidia-smi --query-gpu=name,driver_version,memory.total,memory.free,temperature.gpu,power.draw \
  --format=csv,noheader || true

# Write JSON enrichment for the System Health page (best-effort).
if mkdir -p "${DATA_DIR}" 2>/dev/null && command -v python3 >/dev/null 2>&1; then
  python3 - "${DATA_DIR}" <<'PY'
import json, os, subprocess, sys
q = ["nvidia-smi",
     "--query-gpu=name,driver_version,memory.total,memory.free,temperature.gpu",
     "--format=csv,noheader,nounits"]
out = subprocess.run(q, capture_output=True, text=True).stdout.strip()
gpus = []
for line in out.splitlines():
    p = [x.strip() for x in line.split(",")]
    if len(p) >= 5:
        gpus.append({
            "name": p[0], "driver_version": p[1],
            "memory_total_mb": int(float(p[2])), "memory_free_mb": int(float(p[3])),
            "temperature_c": int(float(p[4])),
        })
path = os.path.join(sys.argv[1], "hardware.json")
with open(path, "w") as f:
    json.dump({"gpus": gpus}, f)
print("Wrote", path)
PY
fi
