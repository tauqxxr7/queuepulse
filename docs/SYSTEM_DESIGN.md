# QueuePulse System Design

## Problem Statement

Build a real-time messaging substrate that can accept user messages, preserve room ordering, tolerate worker failures, retry delivery, isolate poison messages, and expose operational health.

## Functional Requirements

- Users join rooms and send messages.
- Connected clients receive live status updates.
- Messages transition through `queued`, `failed`, `delivered`, `read`, and `dead_lettered`.
- Operators can simulate failure and load.

## Non-Functional Requirements

- At-least-once delivery.
- Idempotent producer semantics.
- Per-room ordering.
- Durable persistence.
- Observable retry and DLQ behavior.
- Local-first developer experience.

## Data Model

`messages` is the system of record. `message_status_events` provides an audit log. `delivery_attempts` captures retry history and latency. `room_sequences` assigns monotonically increasing sequence numbers per room.

## Queueing Model

RabbitMQ carries message IDs instead of full payloads. This keeps events small and makes PostgreSQL the durable state source. Workers can safely re-fetch message state before processing.

## Retry Strategy

Failures are retried with exponential backoff. After `MAX_RETRIES`, the message is marked `dead_lettered` and published to the DLQ. This prevents poison messages from blocking normal flow.

## Idempotency

Clients generate `client_message_id`. The API enforces a unique `(room_id, client_message_id)` constraint. Replayed submissions return the original message.

## Scaling Plan

- Partition rooms across worker pools.
- Add Redis streams or Kafka for high-cardinality event fanout.
- Use OpenTelemetry for cross-service tracing.
- Separate WebSocket gateway instances behind a load balancer with Redis pub/sub fanout.
- Add replay tooling for DLQ recovery.
