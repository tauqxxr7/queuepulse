# QueuePulse Lessons and Assumptions

## Assumptions
- RabbitMQ is the primary queue for the production-like local stack because it is easier to run reliably with Docker Compose than Kafka.
- The backend uses SQLAlchemy synchronous sessions for clarity and recruiter readability. FastAPI delegates blocking database work in short request paths, which is acceptable for this simulator.
- Redis is used when available for presence, metrics counters, and rate limiting; deterministic in-memory fallbacks are included so tests and demos still work without external services.
- The queue layer supports RabbitMQ and a durable local in-process fallback. Docker runs RabbitMQ; tests use the fallback.
- Delivery is simulated at the infrastructure layer: messages are persisted, marked delivered or failed, retried with exponential backoff, and moved to DLQ after max retries.

## Fixes and Decisions
- Idempotency is enforced with a unique `(room_id, client_message_id)` database constraint and service-level lookup.
- Room ordering is enforced with a per-room sequence row lock when the database supports it, plus safe fallback behavior for SQLite tests.
- Retry attempts are persisted in `delivery_attempts`; status transitions are persisted in `message_status_events`.
- Rate limiting returns HTTP 429 with a useful error payload.
- Operational insights are rule-based by default and require no paid API.
- Dashboard simulation controls are backed by Redis when available so API requests affect the separate worker process under Docker; local tests still use the in-memory fallback.
- Local verification can be limited by host resources; this review recorded the disk/page-file blocker explicitly in README and tasks rather than claiming tests passed.

## Lessons Learned
- A strong systems project is more impressive when the chat UI is only the entry point and the real story is the delivery pipeline.
- Recruiter impact comes from showing operational mechanics directly: queue depth, retries, DLQ, failure rate, and delivery latency.
- Local-first systems should degrade gracefully during tests while still using real infrastructure under Docker.
