Built something beyond a “chat app.”

I engineered QueuePulse, a distributed messaging system that simulates how platforms like WhatsApp or Slack handle real-time communication at scale.

Key things I focused on:
- Queue-based message pipeline
- Retry mechanisms and Dead Letter Queue
- Idempotency and ordered delivery
- Real-time WebSocket communication
- Observability dashboard with metrics and insights

I also added a local no-Docker mode to make the system demo-friendly while preserving the real distributed architecture using RabbitMQ, Redis, and PostgreSQL.

This project helped me deeply understand how backend systems are designed in production.

GitHub: https://github.com/tauqxxr7/queuepulse

Would love feedback from backend and system design engineers.
