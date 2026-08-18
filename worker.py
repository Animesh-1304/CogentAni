from arq.connections import RedisSettings


async def say_hello(ctx, name):
    print(f"Hello, {name}!")


class WorkerSettings:
    functions = [say_hello]

    redis_settings = RedisSettings(
        host="redis",
        port=6379
    )