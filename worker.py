import asyncio
from scraper import crawl
import redis.asyncio as redis
from arq import Retry
from arq.connections import RedisSettings
from database import session
from database_models import ScrapeResult


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

async def scrape_job(ctx, url, max_pages):
    redis = ctx["redis"]

    job_id = ctx["job_id"]

    progress_key = f"scrape:{job_id}"

    await redis.hset(
        progress_key,
        mapping={
            "status": "running",
            "progress": 0,
        }
    )

    async def update_progress(progress):
        await redis.hset(
            progress_key,
            "progress",
            progress
        )


    pages = await crawl(
    url,
    max_pages=max_pages,
    progress_callback=update_progress
)

    async with session() as db:

        for page in pages:
            result = ScrapeResult(
                job_id=job_id,
                url=page["url"],
                title=page["title"],
                text=page["text"]
            )

            db.add(result)

        await db.commit()

    await redis.hset(
        progress_key,
        mapping={
            "status": "done",
            "progress": 100,
        }
    )

    return pages

class WorkerSettings:
    functions = [
        say_hello,
        failing_job,
        process_product,
        scrape_job
    ]

    redis_settings = RedisSettings(
        host="redis",
        port=6379
    )

    max_tries = 3