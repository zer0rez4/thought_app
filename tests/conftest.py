import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import get_db
from app.database.models import Base
from app.core.settings import settings

from tests.helpers.requests import (
    register_user,
    get_access_token,
    get_refresh_token
)


engine = create_engine(settings.TEST_SQLALCHENY_DATABASE_URL)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture(scope='function')
def db():
    Base.metadata.create_all(bind=engine)

    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db):
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def registered_user(client):
    response = register_user(client)

    return {
        "access_token": get_access_token(response),
        "refresh_token": get_refresh_token(response)
    }