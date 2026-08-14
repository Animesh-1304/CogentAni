import os

from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")


engine = create_async_engine(
    DATABASE_URL,
    echo=DEBUG
)


session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)