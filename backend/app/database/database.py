from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from app.core.settings import settings

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URL
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with SessionLocal() as db:
        yield db
