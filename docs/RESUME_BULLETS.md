# Resume Bullets

- Engineered a distributed real-time messaging pipeline using FastAPI WebSockets, RabbitMQ, Redis, and PostgreSQL with at-least-once delivery guarantees.
- Implemented idempotency keys, retry queues, dead-letter queues, and room-level message ordering to simulate production-grade chat infrastructure.
- Built an observability dashboard tracking throughput, queue depth, delivery latency, failure rate, retry behavior, active users, and dead-letter pressure in real time.
- Designed failure simulation controls for delivery failure percentage, consumer pause/resume, and load spikes to demonstrate operational resilience.
- Added persistent audit trails for message status transitions and delivery attempts, enabling debugging of failed and retried messages.
- Wrote backend tests covering health checks, idempotency, rate limiting, message persistence, and retry-to-DLQ behavior.
