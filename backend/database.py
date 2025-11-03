from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from config import settings
import logging

logger = logging.getLogger(__name__)

# Async Engine ???????? ??? ?????????
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Sync Engine ??????? ????????? ?????????
sync_engine = create_engine(
    settings.DATABASE_SYNC_URL,
    echo=True,
    pool_size=10,
    max_overflow=20
)

# Session Maker
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    """
    Dependency ?????? ??? ???? ????? ????????
    Database Session Dependency
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

async def init_db():
    """
    ????? ????? ????????
    Initialize Database
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully")

async def close_db():
    """
    ????? ??????? ????? ????????
    Close Database Connections
    """
    await async_engine.dispose()
    logger.info("Database connections closed")
