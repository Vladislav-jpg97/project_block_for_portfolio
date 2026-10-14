from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from backend.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=10,
    max_overflow=10,
)

SessionFactory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
