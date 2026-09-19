import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import Base, get_db
from main import app

TEST_DB_URL = "sqlite://"  # in-memory, shared via StaticPool

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def signup(username="alice", password="password123"):
    return client.post("/auth/signup", json={"username": username, "password": password})


def login(username="alice", password="password123"):
    return client.post("/auth/login", json={"username": username, "password": password})


def auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


# 1. Signup creates user
def test_signup_creates_user():
    r = signup()
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "alice"
    assert "id" in data


# 2. Duplicate signup returns 409
def test_duplicate_signup():
    signup()
    r = signup()
    assert r.status_code == 409


# 3. Login with valid creds returns token
def test_login_success():
    signup()
    r = login()
    assert r.status_code == 200
    assert "access_token" in r.json()


# 4. Login with wrong password returns 401
def test_login_wrong_password():
    signup()
    r = login(password="wrongpassword")
    assert r.status_code == 401


# 5. GET /todos without token returns 401/403
def test_todos_requires_auth():
    r = client.get("/todos")
    assert r.status_code in (401, 403)


# 6. Authenticated user can create todo
def test_create_todo():
    signup()
    token = login().json()["access_token"]
    r = client.post("/todos", json={"title": "Buy milk", "priority": "High"}, headers=auth_header(token))
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Buy milk"
    assert data["priority"] == "High"
    assert data["completed"] is False


# 7. Empty title returns 422
def test_empty_title_rejected():
    signup()
    token = login().json()["access_token"]
    r = client.post("/todos", json={"title": "   "}, headers=auth_header(token))
    assert r.status_code == 422


# 8. Toggle complete (PATCH)
def test_toggle_complete():
    signup()
    token = login().json()["access_token"]
    todo_id = client.post("/todos", json={"title": "Task"}, headers=auth_header(token)).json()["id"]
    r = client.patch(f"/todos/{todo_id}", json={"completed": True}, headers=auth_header(token))
    assert r.status_code == 200
    assert r.json()["completed"] is True


# 9. Delete todo
def test_delete_todo():
    signup()
    token = login().json()["access_token"]
    todo_id = client.post("/todos", json={"title": "Task"}, headers=auth_header(token)).json()["id"]
    r = client.delete(f"/todos/{todo_id}", headers=auth_header(token))
    assert r.status_code == 204
    todos = client.get("/todos", headers=auth_header(token)).json()
    assert all(t["id"] != todo_id for t in todos)


# 10. Cross-user isolation
def test_cross_user_isolation():
    signup("alice")
    signup("bob", "bobpass")
    alice_token = login("alice").json()["access_token"]
    bob_token = login("bob", "bobpass").json()["access_token"]

    # Alice creates a todo
    todo_id = client.post(
        "/todos", json={"title": "Alice task"}, headers=auth_header(alice_token)
    ).json()["id"]

    # Bob cannot see Alice's todo in his list
    bobs_todos = client.get("/todos", headers=auth_header(bob_token)).json()
    assert all(t["id"] != todo_id for t in bobs_todos)

    # Bob cannot delete Alice's todo
    r = client.delete(f"/todos/{todo_id}", headers=auth_header(bob_token))
    assert r.status_code == 404
