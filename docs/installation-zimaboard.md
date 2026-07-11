# Installation — ZimaBoard 2 (and other Debian/Ubuntu boxes)

## Prerequisites

- Debian/Ubuntu-based Linux (tested on Ubuntu 25.10, ZimaBoard 2 / Intel N150).
- Docker Engine + Docker Compose plugin.
- A USB camera (for Phase 2+). Not required to bring up Phase 1.

## One-command install

```bash
git clone git@github.com:SudoSuOps/footpass.git
cd footpass
sudo bash scripts/install-zimaboard.sh
```

This will:
1. Verify Docker + Compose.
2. Create `.env` and auto-generate a secure DB password + secret key.
3. Create the data directory tree at `${FOOTPASS_DATA_DIR}` (default `/srv/footpass`).
4. Print a hardware report and write `hardware.json` for the System Health page.
5. Build and start the stack.
6. Print the access URL.

## Manual steps

```bash
make setup     # copy .env.example -> .env (edit secrets)
make start     # docker compose up -d
make status    # container health
make logs      # follow logs
```

## Access

- By IP immediately: `http://<zimaboard-ip>/` (find it with `hostname -I`).
- By name after enabling mDNS:

  ```bash
  sudo bash scripts/configure-hostname.sh
  # -> http://footpass.local
  ```

  > ⚠️ `configure-hostname.sh` renames the **whole machine** to `footpass`. If
  > this box runs other services, decide deliberately.

## Data location

Set `FOOTPASS_DATA_DIR` in `.env`. Production default `/srv/footpass`. For a
no-sudo local test, point it at a home path (e.g.
`/home/you/footpass/data`) and run `make start`.

## Persistence

PostgreSQL data lives in the `footpass-db-data` Docker volume and survives
`make restart` / `make stop && make start`. Images live under
`${FOOTPASS_DATA_DIR}`.
