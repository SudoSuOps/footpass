#!/usr/bin/env bash
# Trigger a NAS/local backup. Full implementation lands in Phase 4; this stub
# reports whether the backup target is available. FootPass always keeps working
# locally whether or not the NAS is online.
set -euo pipefail

BACKUP_DIR="${FOOTPASS_BACKUP_DIR:-/mnt/nas/Foot-Passport}"

echo "== FootPass backup =="
echo "Target (when enabled): ${BACKUP_DIR}"

if [ -d "${BACKUP_DIR}" ]; then
  echo "Backup path is present and writable-checkable."
else
  echo "Backup path not mounted — that's OK. FootPass continues working locally."
fi

echo "Scheduled, checksum-verified NAS backup arrives in Phase 4 (see docs/nas-backup.md)."
