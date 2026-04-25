# GitHub Polish Checklist

## Repository Description

Distributed real-time messaging simulator with FastAPI WebSockets, RabbitMQ queues, Redis rate limiting, PostgreSQL persistence, retries, DLQ, and a Next.js observability dashboard.

## GitHub Topics

- distributed-systems
- fastapi
- websocket
- rabbitmq
- redis
- postgresql
- nextjs
- observability
- message-queue
- system-design
- full-stack
- docker-compose

## Pinned Repo Strategy

Pin QueuePulse alongside two complementary projects:

- one production-style backend/API project
- one polished frontend/product project
- QueuePulse as the distributed systems flagship

Use the README opening, architecture diagram, dashboard screenshot, and resume bullets as the first reviewer path.

## Screenshot Names

Store final screenshots under `screenshots/`:

- `landing.png`
- `chat-two-clients.png`
- `dashboard-healthy.png`
- `dashboard-failures-dlq.png`
- `architecture.png`
- `rabbitmq-queues.png`

## Demo Video Shots

Capture a 60-90 second video with:

1. dashboard baseline
2. two chat windows sending messages
3. failure rate increase
4. retry/DLQ metrics rising
5. load test terminal output
6. architecture page

## LinkedIn Post Caption

I built QueuePulse, a distributed real-time messaging infrastructure simulator that goes beyond a normal chat app.

It uses FastAPI WebSockets, RabbitMQ, Redis, PostgreSQL, and Next.js to demonstrate at-least-once delivery, idempotency keys, room-level ordering, retries, dead-letter queues, rate limiting, failure simulation, and a live observability dashboard.

The goal was to make the invisible backend mechanics behind Slack/WhatsApp-style systems visible, demoable, and easy to reason about.

## README Checklist

- Architecture diagram is visible near the top.
- Run commands are copy-pasteable.
- Demo flow is explicit.
- Screenshots checklist is present.
- Resume bullets are included.
- Verification limitations are honest.
- No secrets are committed.
