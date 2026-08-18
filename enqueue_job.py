import asyncio

from arq import create_pool
from arq.connections import RedisSettings


async def main():
    redis = await create_pool(
        RedisSettings(
            host="redis",
            port=6379
        )
    )

    job = await redis.enqueue_job(
        "say_hello",
        "Ani"
    )

    print("Job ID:", job.job_id)

    await redis.close()


if __name__ == "__main__":
    asyncio.run(main())