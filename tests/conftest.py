import pytest_asyncio

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)

from app.main import app
from app.database.database import get_db
from app.database.models import Base
from app.core.settings import settings
from app.services.auth import generate_tokens

from tests.factories.user import create_user_in_db
from tests.factories.thought import create_thought_in_db


engine = create_async_engine(
    settings.TEST_SQLALCHENY_DATABASE_URL
)

TestSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest_asyncio.fixture(scope="session")
async def database():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope='function')
async def db(database):
    async with engine.connect() as connection:
        transaction = await connection.begin()

        async with TestSessionLocal(
            bind=connection,
            join_transaction_mode='create_savepoint'
        ) as session:
            yield session

        await transaction.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db):
    async def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
def authenticated_user(db):
    async def factory(**kwargs):
        user = await create_user_in_db(db, **kwargs)
        tokens = generate_tokens(user.id, db)

        await db.commit()

        return {
            'user': user,
            'access_token': tokens.access_token,
            'refresh_token': tokens.refresh_token
        }
    return factory


@pytest_asyncio.fixture
def thought_factory(db):
    async def factory(author_id, **kwargs):
        return await create_thought_in_db(db, author_id, **kwargs)
    return factory