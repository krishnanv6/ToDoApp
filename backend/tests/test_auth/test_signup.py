"""Tests for POST /auth/signup."""


def test_signup_creates_user(client, auth):
    r = auth.signup()
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "alice"
    assert "id" in data
    assert "created_at" in data


def test_signup_duplicate_username_returns_409(client, auth):
    auth.signup()
    r = auth.signup()
    assert r.status_code == 409


def test_signup_different_users_succeed(client, auth):
    assert auth.signup("alice").status_code == 201
    assert auth.signup("bob", "bobpass").status_code == 201


def test_signup_missing_username_returns_422(client):
    r = client.post("/auth/signup", json={"password": "secret"})
    assert r.status_code == 422


def test_signup_missing_password_returns_422(client):
    r = client.post("/auth/signup", json={"username": "alice"})
    assert r.status_code == 422


def test_signup_empty_body_returns_422(client):
    r = client.post("/auth/signup", json={})
    assert r.status_code == 422


def test_signup_returns_no_password_field(client, auth):
    data = auth.signup().json()
    assert "password" not in data
    assert "hashed_password" not in data


def test_signup_id_is_integer(client, auth):
    data = auth.signup().json()
    assert isinstance(data["id"], int)


def test_signup_username_is_case_sensitive(client, auth):
    # "alice" and "Alice" should be treated as two different users
    assert auth.signup("alice").status_code == 201
    assert auth.signup("Alice").status_code == 201


def test_signup_two_users_get_different_ids(client, auth):
    id_alice = auth.signup("alice").json()["id"]
    id_bob = auth.signup("bob", "bobpass").json()["id"]
    assert id_alice != id_bob


def test_signup_response_schema_complete(client, auth):
    data = auth.signup().json()
    assert set(data.keys()) == {"id", "username", "created_at"}


def test_signup_created_at_is_iso_string(client, auth):
    from datetime import datetime
    created_at = auth.signup().json()["created_at"]
    # should parse without error
    datetime.fromisoformat(created_at)


def test_signup_with_special_characters_in_password(client, auth):
    r = auth.signup("alice", "p@$$w0rd!#%")
    assert r.status_code == 201
