"""Tests for GET / (root endpoint)."""


def test_root_returns_200(client):
    r = client.get("/")
    assert r.status_code == 200


def test_root_returns_json(client):
    r = client.get("/")
    assert r.headers["content-type"].startswith("application/json")


def test_root_contains_message_key(client):
    r = client.get("/")
    assert "message" in r.json()


def test_root_message_is_string(client):
    data = client.get("/").json()
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0


def test_root_no_auth_required(client):
    r = client.get("/")
    assert r.status_code != 401
    assert r.status_code != 403
