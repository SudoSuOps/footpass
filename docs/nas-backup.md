# NAS backup (Phase 4)

FootPass can copy your passport to a NAS **without knowing any NAS credentials**
— you mount the share in Linux, and FootPass copies into the mounted path.

## Configure

```bash
# in .env
FOOTPASS_BACKUP_DIR=/mnt/nas/Foot-Passport
```

Supported: SMB-mounted, NFS-mounted, or any locally mounted filesystem; rsync;
scheduled runs.

## Behavior (by design)

1. Detects whether the mount is available before running.
2. Copies **new** files without blocking capture.
3. Verifies copied files by SHA-256 checksum.
4. Records backup status (shown on the dashboard).
5. Retries failed backups.
6. **Never deletes** NAS files automatically.
7. If the NAS is offline, FootPass keeps working locally — backups just wait.

## Run

```bash
make backup      # or: bash scripts/backup-now.sh
```

## Example mounts

```bash
# SMB
sudo mount -t cifs //nas/Foot-Passport /mnt/nas/Foot-Passport -o guest,uid=$(id -u)
# NFS
sudo mount -t nfs nas:/volume1/Foot-Passport /mnt/nas/Foot-Passport
```

> Phase 1 ships the status stub; the copy/verify/retry engine lands in Phase 4.
