# Interview Talking Points

## Why did you build this?

I wanted to build something stronger than a normal chat app. QueuePulse lets me discuss backend reliability, queueing, retries, idempotency, ordering, and observability using a demo that is easy to understand.

## Why use queues?

Queues decouple message ingestion from delivery processing. The API can accept messages quickly while workers process delivery asynchronously. This improves resilience when downstream work is slow or temporarily failing.

## What is at-least-once delivery?

At-least-once delivery means the system prefers retrying over losing messages. A message may be processed more than once, so consumers must be idempotent to avoid duplicate side effects.

## What is idempotency?

Idempotency means repeated requests produce the same result. QueuePulse uses `client_message_id` scoped to a room so duplicate submissions return the original message instead of creating duplicates.

## Why use Redis?

Redis is useful for low-latency ephemeral state. QueuePulse uses it in Docker mode for online presence, rate limiting, and shared runtime simulation controls.

## Why use RabbitMQ?

RabbitMQ is a practical queue for local distributed demos. It provides a clear producer/consumer model and makes retry and dead-letter queue concepts easy to demonstrate.

## What is a dead-letter queue?

A dead-letter queue stores messages that failed too many times. It prevents poison messages from blocking normal processing and gives operators a place to inspect or replay failures.

## How would you scale this?

I would partition rooms across worker pools, run multiple WebSocket gateway instances behind a load balancer, use Redis pub/sub or a message bus for cross-instance fanout, add OpenTelemetry tracing, and move metrics into Prometheus/Grafana.

## What would you improve next?

I would add authentication, per-device read receipts, DLQ replay tooling, OpenTelemetry traces, Prometheus metrics, and a production-grade migration setup with Alembic.

## How is this different from a basic chat app?

A basic chat app mainly sends and displays messages. QueuePulse models the reliability layer behind messaging: queueing, retries, DLQ, idempotency, ordering, metrics, and operational insights.
