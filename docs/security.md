# Security

FootPass is a **local health-record appliance**. Its security model is "stay on
the LAN, expose almost nothing, own your data."

## What is exposed

- Only the reverse proxy publishes a host port (**80**, optionally 443 later).
- PostgreSQL and all internal services are **never** published — they live on a
  private Docker network.

## Implemented in v1

- Local-network binding (proxy only).
- Security headers + Content-Security-Policy (no external JS, fonts, analytics).
- Input validation (Pydantic) and **path-traversal protection**
  (`app/core/security.safe_join` / `sanitize_segment`).
- Atomic, no-overwrite file writes; originals immutable.
- No analytics, no telemetry, no third-party fonts, no external JavaScript, no
  automatic cloud calls.
- Structured logs that **never** record image contents, PIN values, sensitive
  notes, or full local paths in user-facing errors.
- Secrets come from `.env` (git-ignored); the installer auto-generates a strong
  DB password + secret key.

## Coming in the security phase (Phase 5)

- Optional **local PIN**, stored only as a bcrypt hash on the device.
- Secure session cookies + CSRF protection for mutating requests.
- Rate limiting on capture/export endpoints.

## HTTPS (optional, later)

The first local version runs **HTTP** on `footpass.local`, which is acceptable
on a trusted home LAN. Notes for enabling HTTPS later:

- A locally trusted cert (e.g. Caddy internal CA or `mkcert`) must be installed
  on every client device, or browsers show warnings.
- `.local` mDNS names + self-signed certs interact awkwardly with some mobile
  browsers.
- **Because the camera is captured server-side**, FootPass does **not** need
  browser camera permission, so it does *not* need HTTPS for the camera to work
  — a key reason HTTP-on-LAN is fine for v1.

Enable by uncommenting the `443` port in `docker-compose.yml` and adding a TLS
block to `proxy/Caddyfile`.

## Not a medical device

FootPass organizes and compares images. It does not diagnose. All model/AI
inference (future) is local and opt-in.
