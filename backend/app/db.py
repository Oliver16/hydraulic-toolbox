from __future__ import annotations

import os
from contextlib import asynccontextmanager

from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from sqlmodel import SQLModel


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/hydraulic"
    sync_database_url: str = "postgresql://postgres:postgres@db:5432/hydraulic"
    redis_url: str = "redis://redis:6379/0"
    secret_key: str = "change-me"
    access_token_expiry_minutes: int = 30
    refresh_token_expiry_minutes: int = 60 * 24 * 14

    class Config:
        env_prefix = "APP_"
        env_file = os.getenv("ENV_FILE", ".env")
        case_sensitive = False


settings = Settings()

async_engine = create_async_engine(settings.database_url, echo=False, future=True)
async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)

sync_engine = create_engine(settings.sync_database_url, future=True)
session_factory = sessionmaker(bind=sync_engine, autoflush=False, expire_on_commit=False)


async def init_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def get_async_session() -> AsyncSession:
    session: AsyncSession = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


def get_session() -> Session:
    session: Session = session_factory()
    try:
        yield session
    finally:
        session.close()

