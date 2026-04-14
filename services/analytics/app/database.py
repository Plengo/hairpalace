from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


def _make_engine():
    settings = get_settings()
    return create_async_engine(settings.analytics_database_url, echo=False)


# Engine and session factory are created lazily so tests can patch the URL
engine = None
SessionLocal: async_sessionmaker | None = None


def _ensure_engine() -> None:
    global engine, SessionLocal
    if engine is None:
        engine = _make_engine()
        SessionLocal = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )


class Base(DeclarativeBase):
    pass


async def get_db():
    _ensure_engine()
    async with SessionLocal() as session:
        yield session
