# Screenshot Checklist

Capture these images before publishing or pinning the repository. Use them in the GitHub README, LinkedIn post, portfolio page, and live demo walkthrough.

- `landing.png` - Use as the primary GitHub/portfolio hero screenshot. Show the QueuePulse name and product positioning.
- `chat-two-tabs.png` - Use to prove real-time behavior. Capture two browser tabs connected to the same room with delivered messages.
- `dashboard.png` - Use as the strongest recruiter screenshot. Show throughput, queue depth, latency, failures, and insights.
- `architecture.png` - Use in interviews and LinkedIn comments to explain the pipeline visually.
- `health-endpoint.png` - Use to show the backend running locally at `http://localhost:8000/health`.
- `load-test.png` - Use to show terminal output from `python scripts/load_test.py --users 50 --messages 500 --room demo`.

## Capture Order

1. Start backend in local mode.
2. Start frontend.
3. Capture `health-endpoint.png`.
4. Capture `landing.png`.
5. Open two chat tabs, send messages, capture `chat-two-tabs.png`.
6. Open dashboard after traffic, capture `dashboard.png`.
7. Open architecture page, capture `architecture.png`.
8. Run load test and capture `load-test.png`.

Recommended video clip:

1. Start on dashboard baseline.
2. Show two chat tabs sending messages.
3. Increase failure rate and worker delay.
4. Show retries, DLQ, metrics, and insights changing.
