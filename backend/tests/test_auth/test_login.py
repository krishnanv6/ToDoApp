"""Tests for POST /auth/login."""


def test_login_returns_bearer_token(client, auth):
    auth.signup()
    r = auth.login()
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password_returns_401(client, auth):
    auth.signup()
    r = auth.login(password="wrongpassword")
    assert r.status_code == 401


def test_login_nonexistent_user_returns_401(client, auth):
    r = auth.login(username="ghost")
    assert r.status_code == 401


def test_login_missing_username_returns_422(client):
    r = client.post("/auth/login", json={"password": "secret"})
    assert r.status_code == 422


def test_login_missing_password_returns_422(client):
    r = client.post("/auth/login", json={"username": "alice"})
    assert r.status_code == 422


def test_login_token_allows_authenticated_request(client, auth):
    auth.signup()
    token = auth.login().json()["access_token"]
    r = client.get("/todos", headers=auth.header(token))
    assert r.status_code == 200


def test_invalid_token_rejected(client):
    r = client.get("/todos", headers={"Authorization": "Bearer notavalidtoken"})
    assert r.status_code in (401, 403)


def test_login_token_is_non_empty_string(client, auth):
    auth.signup()
    token = auth.login().json()["access_token"]
    assert isinstance(token, str)
    assert len(token) > 0


def test_login_username_case_sensitive(client, auth):
    # signed up as "alice" — logging in as "Alice" should fail
    auth.signup("alice")
    r = auth.login("Alice")
    assert r.status_code == 401


def test_two_users_receive_different_tokens(client, auth):
    auth.signup("alice", "pass1")
    auth.signup("bob", "pass2")
    token_alice = auth.login("alice", "pass1").json()["access_token"]
    token_bob = auth.login("bob", "pass2").json()["access_token"]
    assert token_alice != token_bob


def test_same_user_can_login_multiple_times(client, auth):
    auth.signup()
    r1 = auth.login()
    r2 = auth.login()
    assert r1.status_code == 200
    assert r2.status_code == 200


def test_missing_bearer_prefix_rejected(client, auth):
    auth.signup()
    token = auth.login().json()["access_token"]
    r = client.get("/todos", headers={"Authorization": token})
    assert r.status_code in (401, 403)


def test_no_auth_header_rejected(client):
    r = client.get("/todos")
    assert r.status_code in (401, 403)
