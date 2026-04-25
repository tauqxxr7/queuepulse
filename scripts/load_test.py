import argparse
import asyncio
import statistics
import time
from uuid import uuid4

import httpx


async def ensure_room(client: httpx.AsyncClient, name: str) -> str:
    rooms = (await client.get("/api/rooms")).json()
    for room in rooms:
        if room["name"] == name:
            return room["id"]
    return (await client.post("/api/rooms", json={"name": name})).json()["id"]


async def send_one(client: httpx.AsyncClient, room_id: str, user: str, index: int) -> tuple[bool, float]:
    start = time.perf_counter()
    response = await client.post(
        "/api/messages",
        json={
            "room_id": room_id,
            "username": user,
            "content": f"load-test message {index}",
            "client_message_id": f"lt-{uuid4()}",
        },
    )
    latency = (time.perf_counter() - start) * 1000
    return response.status_code < 400, latency


async def run(args: argparse.Namespace) -> None:
    async with httpx.AsyncClient(base_url=args.api_url, timeout=20) as client:
        room_id = await ensure_room(client, args.room)
        tasks = [
            send_one(client, room_id, f"user-{idx % args.users}", idx)
            for idx in range(args.messages)
        ]
        results = await asyncio.gather(*tasks)

    latencies = [latency for ok, latency in results if ok]
    successful = sum(1 for ok, _ in results if ok)
    failed = len(results) - successful
    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else (max(latencies) if latencies else 0)

    print(f"total sent: {len(results)}")
    print(f"successful: {successful}")
    print(f"failed: {failed}")
    print(f"avg latency ms: {statistics.mean(latencies) if latencies else 0:.2f}")
    print(f"p95 latency ms: {p95:.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="QueuePulse HTTP load test")
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--users", type=int, default=50)
    parser.add_argument("--messages", type=int, default=500)
    parser.add_argument("--room", default="load-test")
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
