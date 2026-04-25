import asyncio

from app.db import SessionLocal, init_db
from app.services.messages import process_message
from app.services.queue import MAIN_QUEUE, RETRY_QUEUE, queue_service


async def handle(payload: dict) -> None:
    with SessionLocal() as db:
        await process_message(db, payload["message_id"])


async def main() -> None:
    init_db()
    await asyncio.gather(
        queue_service.consume_forever(handle, MAIN_QUEUE),
        queue_service.consume_forever(handle, RETRY_QUEUE),
    )


if __name__ == "__main__":
    asyncio.run(main())
