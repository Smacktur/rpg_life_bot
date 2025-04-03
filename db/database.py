from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
import logging
import os
from typing import AsyncGenerator

from config import get_database_url
from db.models import Base

# Определяем, какую базу использовать
# В Docker контейнере будет использоваться PostgreSQL, локально - SQLite
USE_SQLITE = os.environ.get("USE_SQLITE", "false").lower() in ("true", "1", "yes")
logging.info(f"Database setting - Using SQLite: {USE_SQLITE}")

# Create async engine
engine = create_async_engine(
    get_database_url(use_sqlite=USE_SQLITE),
    echo=False,  # Set to True for SQL debugging
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions.
    Provides automatic rollback on exceptions.
    
    Usage:
        async with get_session() as session:
            # Use session
    """
    session = async_session()
    try:
        yield session
    except Exception as e:
        logging.error(f"Database error: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()

async def init_db() -> None:
    """Initialize database by creating all tables"""
    try:
        async with engine.begin() as conn:
            logging.info(f"Creating database tables (Using SQLite: {USE_SQLITE})")
            await conn.run_sync(Base.metadata.create_all)
        logging.info("Database tables created")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise 