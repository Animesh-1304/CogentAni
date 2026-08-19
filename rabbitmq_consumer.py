import asyncio
import json

import aio_pika
from sqlalchemy import insert

from database import session
from database_models import Event


RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672/"
QUEUE_NAME = "product_events"


async def save_event(event_data: dict):
    async with session() as db:
        event = Event(
            event=event_data["event"],
            event_id=event_data["id"]
        )

        db.add(event)

        await db.commit()

        print(f"Event saved to PostgreSQL: {event_data}")


async def consume():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)

    channel = await connection.channel()

    queue = await channel.declare_queue(
        QUEUE_NAME,
        durable=True
    )

    print("RabbitMQ consumer started...")
    print(f"Waiting for messages in '{QUEUE_NAME}'...")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():

                event = json.loads(
                    message.body.decode()
                )

                print("Received event:")
                print(event)

                await save_event(event)


async def main():
    await consume()


if __name__ == "__main__":
    asyncio.run(main())