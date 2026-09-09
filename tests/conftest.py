import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import get_db
from app.database.models import Base, UserBase
from app.core.settings import settings
from app.services.auth import generate_tokens

from tests.helpers.data import DEFAULT_USER
from tests.helpers.requests import (
    register_user,
    get_access_token,
    get_refresh_token,
    create_thought
)
from tests.factories.user import create_user_in_db
from tests.factories.thought import create_thought_in_db


engine = create_engine(settings.TEST_SQLALCHENY_DATABASE_URL)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture(scope="session")
def database():
    Base.metadata.create_all(engine)

    yield

    Base.metadata.drop_all(engine)


@pytest.fixture(scope='function')
def db(database):
    connection = engine.connect()
    transaction = connection.begin()

    db = TestSessionLocal(bind=connection)

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_user(db):
    def factory(**kwargs):
        user = create_user_in_db(db, **kwargs)
        tokens = generate_tokens(user.id, db)

        db.commit()

        return {
            'user': user,
            'access_token': tokens.access_token,
            'refresh_token': tokens.refresh_token
        }
    return factory


@pytest.fixture
def thought_factory(db):
    def factory(author_id, **kwargs):
        return create_thought_in_db(db, author_id, **kwargs)
    return factory