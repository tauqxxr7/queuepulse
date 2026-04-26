# Recruiter Pitch

## 30-Second Explanation

QueuePulse is a production-style distributed messaging simulator. It shows how real-time chat platforms handle WebSockets, queues, retries, dead-letter queues, idempotency, ordered delivery, metrics, and observability.

## 60-Second Explanation

QueuePulse looks like a chat app on the surface, but the real focus is backend reliability. Messages move through a FastAPI WebSocket/API gateway, a message service, idempotency checks, room-level ordering, a queue layer, worker processing, persistence, retries, and dead-letter handling. The dashboard shows throughput, latency, queue depth, failures, and system-health insights.

## Interview Explanation

I built QueuePulse to demonstrate backend infrastructure thinking beyond CRUD. A user message is treated as an event that needs durable processing, duplicate protection, ordered delivery within rooms, retry behavior, failure isolation, and operational visibility. The system has a no-Docker local simulation mode for demos and a Docker distributed mode with RabbitMQ, Redis, PostgreSQL, and a separate worker.

## What Problem It Solves

QueuePulse demonstrates how messaging platforms can keep message delivery reliable even when workers fail, duplicate requests arrive, or downstream delivery is delayed.

## Technical Concepts Demonstrated

- WebSockets
- Queue-based asynchronous processing
- At-least-once delivery
- Idempotency keys
- Room-level ordering
- Retry queues
- Dead-letter queues
- Persistence and audit trails
- Rate limiting and presence
- Metrics dashboards
- Operational insights

## Explaining Docker Limitation Honestly

Docker mode represents the full distributed architecture, but Docker/WSL can be unstable on some Windows laptops. To keep the project demo-ready, I added local mode with SQLite and in-memory services. The local mode proves the product flow and backend logic, while Docker mode preserves the intended RabbitMQ, Redis, PostgreSQL, and worker architecture.

## Local Mode Vs Distributed Mode

Local mode is for demos and screenshots. It runs with SQLite, in-memory queues, in-memory presence/rate limiting, and a FastAPI background worker.

Distributed Docker mode is the architecture mode. It uses RabbitMQ, Redis, PostgreSQL, and a separate worker process to model a more production-like deployment.
