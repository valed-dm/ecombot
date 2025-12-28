"""
SQLAlchemy database session and engine management.

This module sets up the asynchronous engine and session factory for the application,
following the standard SQLAlchemy 2.0 async pattern.
"""

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import declarative_base

from ecombot.config import settings


DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.PGUSER,
    password=settings.PGPASSWORD,
    host=settings.PGHOST,
    port=settings.PGPORT,
    database=settings.PGDATABASE,
)

async_engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()
