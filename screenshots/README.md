# Screenshot Checklist

Capture these images before publishing or pinning the repository:

- `landing.png` - QueuePulse landing page with architecture signal.
- `chat-two-tabs.png` - Two browser tabs connected to the same room with delivered messages.
- `dashboard.png` - Metrics dashboard showing throughput, queue depth, latency, failures, and insights.
- `architecture.png` - Architecture page showing the message pipeline.
- `health-endpoint.png` - Browser or terminal output for `http://localhost:8000/health`.
- `load-test.png` - Terminal output from `python scripts/load_test.py --users 50 --messages 500 --room demo`.

Recommended video clip:

1. Start on dashboard baseline.
2. Show two chat tabs sending messages.
3. Increase failure rate and worker delay.
4. Show retries, DLQ, metrics, and insights changing.
