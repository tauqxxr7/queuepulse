# QueuePulse Implementation Tasks

## Status Legend
- [ ] Pending
- [~] In progress
- [x] Verified

## Build Plan
- [x] Inspect repository structure and confirm starting state.
- [x] Create project scaffold and task tracker.
- [x] Add backend configuration, database models, schemas, and startup schema initialization.
- [x] Implement FastAPI routes for health, rooms, messages, metrics, insights, and simulations.
- [x] Implement WebSocket gateway with room subscriptions and live status broadcasts.
- [x] Implement queue abstraction with RabbitMQ support and durable local fallback for tests/dev.
- [x] Implement message pipeline: idempotency, room ordering, retries, DLQ, status events, delivery attempts.
- [x] Add Redis-backed presence, counters, rate limiting, and shared runtime simulation state with in-memory fallback.
- [x] Add worker entrypoint for consuming queued messages.
- [x] Add backend tests for health, idempotency, rate limiting, persistence, and retry/DLQ behavior.
- [x] Add Next.js frontend with landing, chat, dashboard, and architecture pages.
- [x] Add dashboard controls for failure rate, worker delay, load spike, and consumer pause/resume.
- [x] Add Docker Compose, Dockerfiles, .env.example, Makefile, and load-test script.
- [x] Add README and docs for architecture, API, system design, and resume bullets.
- [x] Add detailed demo script and GitHub polish checklist.
- [~] Run local syntax and backend test verification where possible.

## Verification Log
- Repository inspection: workspace was empty and not initialized as git.
- Backend syntax: `python -m compileall queuepulse/backend/app queuepulse/scripts`.
- Backend syntax re-run after hardening: passed via Node child process wrapper because PowerShell startup was blocked by page-file pressure.
- Backend tests: attempted `pytest app/tests` and `python -m pytest app/tests`; local Python did not have pytest installed. Attempted dependency install into a project `.venv`, but pip failed with `OSError: [Errno 28] No space left on device`. Cleaned up the partial `.venv`.
- Docker verification: `docker compose config` passed.
- Hardening note: simulation/runtime controls were moved to Redis-backed shared state so dashboard failure and pause/resume controls affect the separate worker container.
- Hardening fix: corrected simulation route helper shadowing so `/api/simulate/failure-rate` calls the shared-state setter instead of recursing.
- Verification blocked by disk/page-file pressure after syntax and Compose validation; rerun dependency-based tests/builds on a machine with more free space.
- Secret scan: no API key or secret assignments found in committed text files.
