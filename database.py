from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

DATABASE_URL = "postgresql+asyncpg://postgres:Radha%4013@localhost:5432/animesh"

engine = create_async_engine( # Create an async engine
    DATABASE_URL,
    echo=True
)

session = async_sessionmaker( # Create an async session factory
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)