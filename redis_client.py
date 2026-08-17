import redis.asyncio as redis
import os

REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise RuntimeError("REDIS_URL environment variable is not set.")
redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True
)
async def clear_product_cache():
    async for key in redis_client.scan_iter(match="products:*"):
        await redis_client.delete(key)