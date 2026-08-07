from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

DATABASE_URL = "postgresql+asyncpg://postgres:Radha%4013@localhost:5432/animesh"

engine = create_async_engine(
    DATABASE_URL,
    echo=True
)

session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)