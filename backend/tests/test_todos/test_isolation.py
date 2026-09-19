"""Tests for cross-user data isolation."""


def _signup_login(client, auth, username, password="pass123"):
    auth.signup(username, password)
    token = auth.login(username, password).json()["access_token"]
    return token


def _create_todo(client, token, auth, title="Task"):
    return client.post("/todos", json={"title": title}, headers=auth.header(token)).json()["id"]


def test_user_sees_only_own_todos(client, auth):
    alice = _signup_login(client, auth, "alice")
    bob = _signup_login(client, auth, "bob")

    _create_todo(client, alice, auth, "Alice task")

    bobs_todos = client.get("/todos", headers=auth.header(bob)).json()
    assert bobs_todos == []


def test_bob_cannot_see_alices_todo_in_list(client, auth):
    alice = _signup_login(client, auth, "alice")
    bob = _signup_login(client, auth, "bob")

    alice_id = _create_todo(client, alice, auth, "Alice task")
    bobs_todos = client.get("/todos", headers=auth.header(bob)).json()
    assert all(t["id"] != alice_id for t in bobs_todos)


def test_bob_cannot_delete_alices_todo(client, auth):
    alice = _signup_login(client, auth, "alice")
    bob = _signup_login(client, auth, "bob")

    alice_id = _create_todo(client, alice, auth)
    r = client.delete(f"/todos/{alice_id}", headers=auth.header(bob))
    assert r.status_code == 404


def test_bob_cannot_update_alices_todo(client, auth):
    alice = _signup_login(client, auth, "alice")
    bob = _signup_login(client, auth, "bob")

    alice_id = _create_todo(client, alice, auth)
    r = client.patch(f"/todos/{alice_id}", json={"completed": True}, headers=auth.header(bob))
    assert r.status_code == 404


def test_alices_todo_unaffected_after_bob_delete_attempt(client, auth):
    alice = _signup_login(client, auth, "alice")
    bob = _signup_login(client, auth, "bob")

    alice_id = _create_todo(client, alice, auth)
    client.delete(f"/todos/{alice_id}", headers=auth.header(bob))

    alices_todos = client.get("/todos", headers=auth.header(alice)).json()
    assert any(t["id"] == alice_id for t in alices_todos)


def test_multiple_users_independent_lists(client, auth):
    alice = _signup_login(client, auth, "alice")
    bob = _signup_login(client, auth, "bob")

    _create_todo(client, alice, auth, "Alice 1")
    _create_todo(client, alice, auth, "Alice 2")
    _create_todo(client, bob, auth, "Bob 1")

    assert len(client.get("/todos", headers=auth.header(alice)).json()) == 2
    assert len(client.get("/todos", headers=auth.header(bob)).json()) == 1
