"""JWT authentication integration tests.

Covers the four scenarios specified in the task:
- POST /auth/register succeeds
- POST /auth/login returns a token
- GET /todos with valid token returns 200
- GET /todos without token returns 401
"""


def test_register_succeeds(client):
    r = client.post("/auth/register", json={"username": "testuser", "password": "securepass"})
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "testuser"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_login_returns_access_token(client, auth):
    auth.signup("testuser", "securepass")
    r = client.post("/auth/login", json={"username": "testuser", "password": "securepass"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


def test_get_todos_with_valid_token_returns_200(client, auth):
    auth.signup("testuser", "securepass")
    token = client.post("/auth/login", json={"username": "testuser", "password": "securepass"}).json()["access_token"]
    r = client.get("/todos", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200


def test_get_todos_without_token_returns_401(client):
    r = client.get("/todos")
    assert r.status_code == 401
