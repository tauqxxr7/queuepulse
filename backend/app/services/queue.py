import asyncio
import json
from collections import deque
from dataclasses import dataclass
from typing import Awaitable, Callable

import aio_pika

from app.config import get_settings

MAIN_QUEUE = "queuepulse.messages"
RETRY_QUEUE = "queuepulse.retry"
DLQ_QUEUE = "queuepulse.dead_letter"


@dataclass
class QueueEnvelope:
    message_id: str


class QueueService:
    def __init__(self) -> None:
        self._local: dict[str, deque[dict]] = {
            MAIN_QUEUE: deque(),
            RETRY_QUEUE: deque(),
            DLQ_QUEUE: deque(),
        }
        self._connection: aio_pika.RobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None

    async def connect(self) -> None:
        if self._connection or not get_settings().rabbitmq_url:
            return
        try:
            self._connection = await aio_pika.connect_robust(get_settings().rabbitmq_url)
            self._channel = await self._connection.channel()
            for queue in (MAIN_QUEUE, RETRY_QUEUE, DLQ_QUEUE):
                await self._channel.declare_queue(queue, durable=True)
        except Exception:
            self._connection = None
            self._channel = None

    async def close(self) -> None:
        if self._connection:
            await self._connection.close()
        self._connection = None
        self._channel = None

    async def publish(self, queue: str, payload: dict, delay_seconds: float = 0) -> None:
        if delay_seconds:
            await asyncio.sleep(delay_seconds)
        await self.connect()
        if self._channel:
            await self._channel.default_exchange.publish(
                aio_pika.Message(json.dumps(payload).encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                routing_key=queue,
            )
            return
        self._local[queue].append(payload)

    async def publish_message(self, message_id: str) -> None:
        await self.publish(MAIN_QUEUE, {"message_id": message_id})

    async def publish_retry(self, message_id: str, delay_seconds: float) -> None:
        await self.publish(RETRY_QUEUE, {"message_id": message_id}, delay_seconds=delay_seconds)

    async def publish_dead_letter(self, message_id: str) -> None:
        await self.publish(DLQ_QUEUE, {"message_id": message_id})

    def local_depth(self, queue: str) -> int:
        return len(self._local[queue])

    async def consume_local_once(self, handler: Callable[[dict], Awaitable[None]], queue: str = MAIN_QUEUE) -> bool:
        if not self._local[queue]:
            return False
        payload = self._local[queue].popleft()
        await handler(payload)
        return True

    async def consume_forever(self, handler: Callable[[dict], Awaitable[None]], queue: str = MAIN_QUEUE) -> None:
        await self.connect()
        if self._channel:
            q = await self._channel.declare_queue(queue, durable=True)
            async with q.iterator() as iterator:
                async for message in iterator:
                    async with message.process(requeue=False):
                        await handler(json.loads(message.body.decode()))
            return
        while True:
            consumed = await self.consume_local_once(handler, queue)
            if not consumed:
                await asyncio.sleep(0.2)


queue_service = QueueService()
