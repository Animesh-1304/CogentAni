import json

import aio_pika


RABBITMQ_URL = "amqp://guest:guest@rabbitmq:5672/"


async def publish_product_created(product_id: int):
    connection = await aio_pika.connect_robust(RABBITMQ_URL)

    async with connection:
        channel = await connection.channel()

        queue = await channel.declare_queue(
            "product_events",
            durable=True
        )

        event = {
            "event": "product_created",
            "id": str(product_id)
        }

        message = aio_pika.Message(
            body=json.dumps(event).encode(),
            content_type="application/json"
        )

        await channel.default_exchange.publish(
            message,
            routing_key=queue.name
        )

        print(f"Published: {event}")


async def main():
    await publish_product_created(1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())