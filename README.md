# QueuePulse

> Distributed real-time messaging system with WebSockets, queues, retries, DLQ, and observability.

[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-Frontend-black?style=for-the-badge)](https://nextjs.org/)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-Queue-ff6600?style=for-the-badge)](https://www.rabbitmq.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Persistence-336791?style=for-the-badge)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-Observability%20%26%20Runtime-dc382d?style=for-the-badge)](https://redis.io/)

[![Source Code](https://img.shields.io/badge/Source_Code-111827?style=for-the-badge&logo=github&logoColor=white)](https://github.com/tauqxxr7/queuepulse)

QueuePulse demonstrates backend reliability patterns used in real-world messaging systems: queues, retries, DLQ, health checks, and observability.

QueuePulse is a distributed real-time messaging system with WebSockets, queues, retries, DLQ, and observability — designed to demonstrate backend reliability and system-design thinking.

## Why This Project Matters

Basic chat demos prove UI interaction. QueuePulse is built to show the harder engineering side: real-time communication, async backend processing, failure handling, message lifecycle control, and system visibility under load.

This is the strongest backend/system-design signal in the portfolio.

## Problem

Real-time systems need more than instant message rendering. They need reliability, retries, delivery visibility, failure recovery, and operational insight when the happy path breaks.

## Solution

QueuePulse models a production-style messaging pipeline with a WebSocket gateway, queue-backed processing, retry logic, dead-letter handling, and an observability dashboard that surfaces health and throughput signals.

## System Architecture

```text
Client → WebSocket Gateway → Message Queue → Worker → Retry Handler → DLQ → Observability Dashboard
```

## 🎥 System Walkthrough / Architecture Demo

- Expected file: `docs/architecture/queuepulse-architecture.gif`
- Walkthrough notes: [docs/architecture/queuepulse-flow.md](docs/architecture/queuepulse-flow.md)

This walkthrough focuses on how QueuePulse models reliability and observability rather than only showing chat UI behavior.

## 🧠 System Design Focus

QueuePulse demonstrates:

- real-time messaging via WebSockets
- asynchronous processing
- retry mechanisms
- dead-letter queue (DLQ)
- observability patterns

```text
Client → WebSocket → Queue → Worker → Retry → DLQ → Monitoring
```

## Features

- Real-time communication over WebSockets
- Queue-based message processing
- Retry handling for transient failures
- Dead-letter queue for failed messages
- Operational health endpoint
- Dashboard for throughput, latency, queue depth, and failures
- Local mode for laptop demos and distributed mode for deeper architecture demos

## Reliability Mechanisms

- Queue-backed processing instead of direct fire-and-forget delivery
- Retry logic with backoff for transient errors
- Dead-letter queue flow when max retries are exceeded
- Idempotency-aware message handling
- Room-level sequencing for ordered delivery

## Observability

- Health monitoring endpoint
- Metrics API for dashboard consumption
- Visibility into retries, failed deliveries, queue depth, and throughput
- Dashboard-oriented view of system behavior during load and failure simulation

## ⚙️ Engineering Notes

- Built with clear frontend/backend/API separation
- Designed for deployable architecture (Vercel + Render style)
- Uses modular structure for scalability and maintainability
- Focused on real-world use cases, not isolated demos

## Tech Stack

- Frontend: Next.js
- Backend: FastAPI, Python
- Real-time layer: WebSockets
- Queue layer: RabbitMQ in distributed mode
- Runtime/data services: Redis, PostgreSQL
- Local demo mode: SQLite and in-memory queue simulation

## How To Run

### Local mode

Use this path for recruiter demos or laptop development without Docker.

Backend:

```powershell
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open:

- `http://localhost:3000/chat`
- `http://localhost:3000/dashboard`
- `http://localhost:8000/health`

### Distributed Docker mode

```bash
docker compose up --build
```

This mode uses RabbitMQ, Redis, PostgreSQL, FastAPI, Next.js, and a separate worker to demonstrate a more realistic distributed architecture.

## API / WebSocket Usage

Core HTTP endpoints:

- `GET /health`
- `GET /api/metrics`
- `GET /api/insights`
- `POST /api/rooms`
- `GET /api/rooms`
- `POST /api/messages`
- `GET /api/messages/{room_id}`

Core recruiter-facing signals:

- Real-time communication
- Async backend processing
- Failure handling
- Dead-letter queue
- Health monitoring
- Observability dashboard

## Screenshots

### Landing Page

![Landing Page](screenshots/landing.png)

### Real-Time Chat

![Real-time chat](screenshots/chat-two-tabs.png)

### Observability Dashboard

![Observability dashboard](screenshots/dashboard.png)

### System Architecture

![System architecture](screenshots/architecture.png)

### Health Endpoint

![Health endpoint](screenshots/health-endpoint.png)

### Load Testing

![Load testing](screenshots/load-test.png)

## 🚀 Deployment

Deployment in progress (planned: Vercel / Render)

## Testing

Backend:

```bash
cd backend
python -m compileall app
python -m pytest app/tests
```

Frontend:

```bash
cd frontend
npm run build
```

## Future Improvements

- OpenTelemetry traces across gateway, worker, and delivery flow
- Message replay from DLQ
- Multi-worker consumer groups
- Prometheus/Grafana integration
- Authentication and room-level access control

## Author / Contact

Built by **Tauqeer Bharde** as a backend systems project focused on reliability, message durability, and operational visibility.

- GitHub: `https://github.com/tauqxxr7`
- LinkedIn: `https://www.linkedin.com/in/tauqeer-sameer-85b868235`

## Suggested GitHub Topics

`fastapi, websocket, messaging-system, distributed-systems, backend, python, async, dlq, observability, system-design`
