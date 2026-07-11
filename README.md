# 🐝 FootPass

**A local-first Foot Passport appliance.** FootPass helps a person complete a
focused five-minute foot-photo routine and build a *private, longitudinal*
foot-health record — on their own hardware, with no cloud, no subscription, and
no account required.

> FootPass helps you organize and compare images. **It does not diagnose medical
> conditions.** Contact your clinician if you notice a new or concerning change.

Your calm guide through the routine is **Freddy**.

---

## Core principles

- **Local-first** — runs entirely on your ZimaBoard / mini-PC / NAS.
- **No cloud, no subscription, no required account.**
- **You own everything.** Images live on your filesystem; only metadata is in the
  database. Original photographs are **immutable** and never overwritten.
- **Works offline.** Nothing breaks if the internet or NAS is unavailable.
- **Runs anywhere** — ZimaBoard, Jetson Orin Nano, mini-PCs, NAS-connected systems.
- **No analytics, no telemetry, no external tracking.**

## Architecture

Six Docker services behind a single reverse proxy:

| Service | Role |
|---|---|
| `footpass-proxy` | Caddy — the only host-facing service (port 80) |
| `footpass-ui` | React + TypeScript + Vite + Tailwind (built static, no CDN) |
| `footpass-api` | FastAPI + SQLAlchemy + Alembic |
| `footpass-camera` | OpenCV / V4L2 USB camera capture (streamed by the server) |
| `footpass-worker` | Background jobs (exports, NAS backup) |
| `footpass-db` | PostgreSQL (metadata only — never image binaries) |

Routes: `/` → UI · `/api` → API · `/camera` → camera · `/docs` → API docs.

See [`docs/architecture.md`](docs/architecture.md).

## Quick start

```bash
# 1. Configure
make setup            # creates .env from the template
$EDITOR .env          # set POSTGRES_PASSWORD and FOOTPASS_SECRET_KEY

# 2. Launch
make start            # docker compose up -d

# 3. Open
#    http://footpass.local   (after running scripts/configure-hostname.sh)
#    or  http://<zimaboard-ip>/
```

Full install (hostname + Avahi + Docker checks):

```bash
sudo bash scripts/install-zimaboard.sh
```

## Build phases

- **Phase 1 (this release)** — skeleton, Compose, PostgreSQL, FastAPI health,
  React dashboard, reverse proxy, `footpass.local` setup, system health page.
- **Phase 2** — USB camera detection, live preview, single capture, storage.
- **Phase 3** — six-photo guided workflow, quality checks, history, notes.
- **Phase 4** — comparison, ZIP/PDF export, NAS backup.
- **Phase 5** — security hardening, tests, docs, production installer.

## Documentation

[architecture](docs/architecture.md) ·
[install (ZimaBoard)](docs/installation-zimaboard.md) ·
[camera setup](docs/camera-setup.md) ·
[NAS backup](docs/nas-backup.md) ·
[GPU support](docs/gpu-support.md) ·
[security](docs/security.md) ·
[troubleshooting](docs/troubleshooting.md)

---

Part of the **OpenFootLab** ecosystem. Built by Swarm & Bee. 🐝
