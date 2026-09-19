"""HTTP-level behaviour: method-not-allowed, content-type, unsupported routes."""


# ---------- method not allowed ----------

def test_put_todos_returns_405(client):
    r = client.put("/todos", json={"title": "x"})
    assert r.status_code == 405


def test_get_single_todo_route_not_defined_returns_405(client, alice, auth):
    # GET /todos/{id} is not a defined route (only PATCH/DELETE are)
    r = client.get("/todos/1", headers=auth.header(alice))
    assert r.status_code == 405


def test_post_todo_by_id_returns_405(client, alice, auth):
    r = client.post("/todos/1", json={"title": "x"}, headers=auth.header(alice))
    assert r.status_code == 405


def test_put_todo_by_id_returns_405(client, alice, auth):
    r = client.put("/todos/1", json={"title": "x"}, headers=auth.header(alice))
    assert r.status_code == 405


def test_delete_auth_signup_returns_405(client):
    r = client.delete("/auth/signup")
    assert r.status_code == 405


def test_get_auth_login_returns_405(client):
    r = client.get("/auth/login")
    assert r.status_code == 405


# ---------- undefined routes ----------

def test_unknown_route_returns_404(client):
    r = client.get("/nonexistent")
    assert r.status_code == 404


def test_get_todo_by_id_not_allowed(client, alice, auth):
    # /todos/{id} exists for PATCH/DELETE only; GET on it returns 405
    r = client.get("/todos/stats", headers=auth.header(alice))
    assert r.status_code == 405


# ---------- content-type ----------

def test_non_json_body_signup_returns_422(client):
    r = client.post(
        "/auth/signup",
        content="username=alice&password=pass",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 422


def test_non_json_body_login_returns_422(client):
    r = client.post(
        "/auth/login",
        content="username=alice&password=pass",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 422


def test_non_json_body_create_todo_returns_422(client, alice, auth):
    r = client.post(
        "/todos",
        content="title=task",
        headers={**auth.header(alice), "Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 422
