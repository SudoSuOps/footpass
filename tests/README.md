# Tests

- **Backend unit/API tests** live in `backend/tests/` (run inside the API
  container so they need no local Python): `make test`.
- **Integration smoke test** here (`smoke_test.sh`) hits a *running* stack over
  HTTP to verify the proxy, API, and UI are wired together.

Frontend interaction tests (keyboard/spacebar capture, mobile layout) arrive
with the Vitest harness in a later phase.
