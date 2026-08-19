import asyncio

import redis.asyncio as redis
from arq import Retry
from arq.connections import RedisSettings


async def say_hello(ctx, name):
    message = f"Hello, {name}!"
    print(message)
    return message


async def failing_job(ctx):
    print("failing_job started")

    raise Retry(defer=1)


async def process_product(ctx, task_id, product_id):
    redis_client = redis.from_url(
        "redis://redis:6379/0",
        decode_responses=True
    )

    try:
        await redis_client.set(
            f"product_task:{task_id}",
            "pending"
        )

        print(f"Processing product {product_id}...")

        await asyncio.sleep(3)

        await redis_client.set(
            f"product_task:{task_id}",
            "done"
        )

        print(f"Product {product_id} processing completed.")

    except Exception:
        await redis_client.set(
            f"product_task:{task_id}",
            "failed"
        )

        raise

    finally:
        await redis_client.aclose()


class WorkerSettings:
    functions = [
        say_hello,
        failing_job,
        process_product
    ]

    redis_settings = RedisSettings(
        host="redis",
        port=6379
    )

    max_tries = 3