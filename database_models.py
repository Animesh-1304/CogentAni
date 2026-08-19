from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(200)
    )

    description: Mapped[str] = mapped_column(
        String(500)
    )

    price: Mapped[float] = mapped_column(
        Float
    )

    quantity: Mapped[int] = mapped_column(
        Integer
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    username: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True
    )

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255)
    )

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event = Column(String, nullable=False)
    event_id = Column(String, nullable=False)