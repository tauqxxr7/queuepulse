# QueuePulse API

Base URL: `http://localhost:8000`

## Health

`GET /health`

Returns service health.

## Rooms

`POST /api/rooms`

```json
{ "name": "general" }
```

`GET /api/rooms`

Returns all rooms.

## Messages

`POST /api/messages`

```json
{
  "room_id": "uuid",
  "username": "ada",
  "content": "hello",
  "client_message_id": "client-generated-id"
}
```

`GET /api/messages/{room_id}`

Returns room messages ordered by `sequence_number`.

## Metrics

`GET /api/metrics`

Returns total messages, throughput, queue depth, retry count, DLQ count, active users, active rooms, success rate, latency, failure rate, and chart series.

## Insights

`GET /api/insights`

Returns rule-based operational insights and the metrics snapshot.

## Simulation

`POST /api/simulate/failure-rate`

```json
{ "failure_rate": 35 }
```

`POST /api/simulate/load-spike`

```json
{ "room_id": "uuid", "username_prefix": "load-user", "messages": 100 }
```

`POST /api/simulate/consumer-pause`

`POST /api/simulate/consumer-resume`

`POST /api/simulate/worker-delay`

```json
{ "worker_delay_ms": 750 }
```

## WebSocket

`ws://localhost:8000/ws/{room_id}/{username}`

Server events include:

- `presence.joined`
- `message.status`
- `message.delivered`
- `message.read`
