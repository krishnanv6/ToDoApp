import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import Base, get_db
from main import app

_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def _override_get_db():
    db = _Session()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Clear the in-memory rate limiter between tests so tests don't interfere."""
    from limiter import limiter
    storage = getattr(limiter, "_storage", None)
    if storage is not None:
        storage.reset()
    yield
    if storage is not None:
        storage.reset()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth(client):
    """Returns helpers: signup(u,p), login(u,p), header(token)."""

    def signup(username="alice", password="password123"):
        return client.post("/auth/signup", json={"username": username, "password": password})

    def login(username="alice", password="password123"):
        return client.post("/auth/login", json={"username": username, "password": password})

    def header(token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    return type("Auth", (), {"signup": staticmethod(signup), "login": staticmethod(login), "header": staticmethod(header)})()


@pytest.fixture
def alice(client, auth):
    """Creates user alice and returns her auth token."""
    auth.signup("alice", "password123")
    token = auth.login("alice", "password123").json()["access_token"]
    return token
