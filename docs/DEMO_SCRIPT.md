# QueuePulse Demo Script

Use this flow for a 5-8 minute recruiter or engineering review demo.

## 1. Start The Stack

### No-Docker Local Demo

Use this path when WSL or Docker is unavailable.

Terminal 1:

```bash
cd queuepulse/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Terminal 2:

```bash
cd queuepulse/frontend
npm install
npm run dev
```

Verify:

```bash
curl http://localhost:8000/health
```

Local demo mode uses SQLite plus in-memory queue, presence, rate limiting, and runtime controls. The real distributed architecture uses RabbitMQ, Redis, and PostgreSQL in Docker mode.

### Docker Demo

```bash
cd queuepulse
cp .env.example .env
docker compose up --build
```

Wait for:

- backend on `http://localhost:8000`
- frontend on `http://localhost:3000`
- RabbitMQ UI on `http://localhost:15672`

Verify:

```bash
curl http://localhost:8000/health
```

## 2. Open Chat In Two Browser Windows

Open:

- `http://localhost:3000/chat` in window A
- `http://localhost:3000/chat` in window B

Use different usernames, for example `ada` and `grace`, and select the same room.

## 3. Send Messages

Send a few messages from both windows. Point out:

- messages are created by the API
- persisted with idempotency keys
- queued through RabbitMQ
- delivered by the worker
- broadcast back over WebSocket
- ordered by room sequence number

## 4. Show The Dashboard

Open `http://localhost:3000/dashboard`.

Call out:

- total messages
- messages per second
- queue depth
- retry queue count
- dead-letter count
- success rate
- average delivery latency
- recent failed messages
- rule-based operational insights

## 5. Simulate Failures

In the dashboard:

1. Set failure rate to `40%`.
2. Set worker delay to `750ms`.
3. Send several messages from chat.
4. Watch failed messages, retry pressure, and latency rise.

Explain that simulation settings are stored in Redis-backed shared runtime state, so the API container and worker container see the same controls.

## 6. Show Retries And DLQ

Set failure rate to `100%`, send messages, and wait for max retries.

Point out:

- retry count increases
- failed status events are persisted
- poison messages move to dead-letter state
- DLQ count appears on the dashboard

Then set failure rate back to `0%`.

## 7. Run A Load Test

In a separate terminal:

```bash
python scripts/load_test.py --users 50 --messages 500 --room demo
```

Show the printed:

- total sent
- successful
- failed
- average latency
- p95 latency

Refresh the dashboard and show throughput movement.

## 8. Close With System Design

Open `http://localhost:3000/architecture`.

Close on the design points:

- at-least-once delivery
- idempotent producers
- room-level ordering
- retry isolation
- DLQ handling
- observable operations
