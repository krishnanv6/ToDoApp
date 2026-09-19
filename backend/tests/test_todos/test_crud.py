"""Tests for /todos CRUD endpoints."""


def _create(client, token, auth, title="Buy milk", priority="High", due_date=None):
    payload = {"title": title, "priority": priority}
    if due_date:
        payload["due_date"] = due_date
    return client.post("/todos", json=payload, headers=auth.header(token))


# ---------- auth guard ----------

def test_get_todos_without_token_returns_401(client):
    r = client.get("/todos")
    assert r.status_code in (401, 403)


def test_post_todo_without_token_returns_401(client):
    r = client.post("/todos", json={"title": "x"})
    assert r.status_code in (401, 403)


# ---------- list ----------

def test_get_todos_initially_empty(client, alice, auth):
    r = client.get("/todos", headers=auth.header(alice))
    assert r.status_code == 200
    assert r.json() == []


def test_get_todos_returns_own_todos(client, alice, auth):
    _create(client, alice, auth, "Task 1")
    _create(client, alice, auth, "Task 2")
    todos = client.get("/todos", headers=auth.header(alice)).json()
    assert len(todos) == 2


def test_get_todos_response_is_list(client, alice, auth):
    r = client.get("/todos", headers=auth.header(alice))
    assert isinstance(r.json(), list)


def test_get_todos_item_schema(client, alice, auth):
    _create(client, alice, auth, "Task")
    item = client.get("/todos", headers=auth.header(alice)).json()[0]
    for field in ("id", "title", "priority", "due_date", "completed", "created_at", "owner_id"):
        assert field in item


def test_get_todos_count_matches_creates_and_deletes(client, alice, auth):
    id1 = _create(client, alice, auth, "T1").json()["id"]
    _create(client, alice, auth, "T2")
    client.delete(f"/todos/{id1}", headers=auth.header(alice))
    todos = client.get("/todos", headers=auth.header(alice)).json()
    assert len(todos) == 1


def test_patch_without_token_returns_401(client):
    r = client.patch("/todos/1", json={"completed": True})
    assert r.status_code in (401, 403)


def test_delete_without_token_returns_401(client):
    r = client.delete("/todos/1")
    assert r.status_code in (401, 403)


# ---------- create ----------

def test_create_todo_returns_201(client, alice, auth):
    r = _create(client, alice, auth)
    assert r.status_code == 201


def test_create_todo_fields(client, alice, auth):
    r = _create(client, alice, auth, title="Buy milk", priority="High")
    data = r.json()
    assert data["title"] == "Buy milk"
    assert data["priority"] == "High"
    assert data["completed"] is False
    assert "id" in data
    assert "created_at" in data


def test_create_todo_default_priority_is_medium(client, alice, auth):
    r = client.post("/todos", json={"title": "Task"}, headers=auth.header(alice))
    assert r.json()["priority"] == "Medium"


def test_create_todo_with_due_date(client, alice, auth):
    r = _create(client, alice, auth, due_date="2026-12-31")
    assert r.json()["due_date"] == "2026-12-31"


def test_create_todo_invalid_priority_returns_422(client, alice, auth):
    r = client.post("/todos", json={"title": "Task", "priority": "Critical"}, headers=auth.header(alice))
    assert r.status_code == 422


def test_create_todo_empty_title_returns_422(client, alice, auth):
    r = client.post("/todos", json={"title": "   "}, headers=auth.header(alice))
    assert r.status_code == 422


def test_create_todo_missing_title_returns_422(client, alice, auth):
    r = client.post("/todos", json={}, headers=auth.header(alice))
    assert r.status_code == 422


def test_create_todo_priority_low(client, alice, auth):
    r = _create(client, alice, auth, priority="Low")
    assert r.status_code == 201
    assert r.json()["priority"] == "Low"


def test_create_todo_priority_medium_explicit(client, alice, auth):
    r = _create(client, alice, auth, priority="Medium")
    assert r.status_code == 201
    assert r.json()["priority"] == "Medium"


def test_create_todo_priority_high(client, alice, auth):
    r = _create(client, alice, auth, priority="High")
    assert r.status_code == 201
    assert r.json()["priority"] == "High"


def test_create_todo_all_fields(client, alice, auth):
    r = _create(client, alice, auth, title="Full todo", priority="Low", due_date="2027-06-15")
    data = r.json()
    assert data["title"] == "Full todo"
    assert data["priority"] == "Low"
    assert data["due_date"] == "2027-06-15"
    assert data["completed"] is False


def test_create_todo_without_due_date_returns_null(client, alice, auth):
    r = client.post("/todos", json={"title": "No date"}, headers=auth.header(alice))
    assert r.json()["due_date"] is None


def test_create_todo_invalid_date_format_returns_422(client, alice, auth):
    r = client.post("/todos", json={"title": "Task", "due_date": "not-a-date"}, headers=auth.header(alice))
    assert r.status_code == 422


def test_create_todo_ids_are_unique(client, alice, auth):
    id1 = _create(client, alice, auth, "T1").json()["id"]
    id2 = _create(client, alice, auth, "T2").json()["id"]
    assert id1 != id2


def test_create_todo_completed_defaults_to_false(client, alice, auth):
    data = _create(client, alice, auth, "Task").json()
    assert data["completed"] is False


# ---------- update ----------

def test_toggle_complete(client, alice, auth):
    todo_id = _create(client, alice, auth, "Task").json()["id"]
    r = client.patch(f"/todos/{todo_id}", json={"completed": True}, headers=auth.header(alice))
    assert r.status_code == 200
    assert r.json()["completed"] is True


def test_update_title(client, alice, auth):
    todo_id = _create(client, alice, auth, "Old").json()["id"]
    r = client.patch(f"/todos/{todo_id}", json={"title": "New"}, headers=auth.header(alice))
    assert r.json()["title"] == "New"


def test_update_priority(client, alice, auth):
    todo_id = _create(client, alice, auth, "Task", priority="Low").json()["id"]
    r = client.patch(f"/todos/{todo_id}", json={"priority": "High"}, headers=auth.header(alice))
    assert r.json()["priority"] == "High"


def test_update_due_date(client, alice, auth):
    todo_id = _create(client, alice, auth, "Task").json()["id"]
    r = client.patch(f"/todos/{todo_id}", json={"due_date": "2027-01-01"}, headers=auth.header(alice))
    assert r.json()["due_date"] == "2027-01-01"


def test_update_title_to_whitespace_returns_422(client, alice, auth):
    todo_id = _create(client, alice, auth, "Task").json()["id"]
    r = client.patch(f"/todos/{todo_id}", json={"title": "   "}, headers=auth.header(alice))
    assert r.status_code == 422


def test_update_nonexistent_todo_returns_404(client, alice, auth):
    r = client.patch("/todos/99999", json={"completed": True}, headers=auth.header(alice))
    assert r.status_code == 404


def test_patch_empty_payload_leaves_todo_unchanged(client, alice, auth):
    original = _create(client, alice, auth, "Task", priority="Low").json()
    r = client.patch(f"/todos/{original['id']}", json={}, headers=auth.header(alice))
    assert r.status_code == 200
    updated = r.json()
    assert updated["title"] == original["title"]
    assert updated["priority"] == original["priority"]
    assert updated["completed"] == original["completed"]


def test_patch_multiple_fields_at_once(client, alice, auth):
    todo_id = _create(client, alice, auth, "Old", priority="Low").json()["id"]
    r = client.patch(
        f"/todos/{todo_id}",
        json={"title": "New", "priority": "High", "completed": True},
        headers=auth.header(alice),
    )
    data = r.json()
    assert data["title"] == "New"
    assert data["priority"] == "High"
    assert data["completed"] is True


def test_patch_toggle_complete_back_to_false(client, alice, auth):
    todo_id = _create(client, alice, auth, "Task").json()["id"]
    client.patch(f"/todos/{todo_id}", json={"completed": True}, headers=auth.header(alice))
    r = client.patch(f"/todos/{todo_id}", json={"completed": False}, headers=auth.header(alice))
    assert r.json()["completed"] is False


def test_patch_clear_due_date(client, alice, auth):
    todo_id = _create(client, alice, auth, "Task", due_date="2027-01-01").json()["id"]
    r = client.patch(f"/todos/{todo_id}", json={"due_date": None}, headers=auth.header(alice))
    assert r.json()["due_date"] is None


def test_patch_returns_full_todo_schema(client, alice, auth):
    todo_id = _create(client, alice, auth, "Task").json()["id"]
    r = client.patch(f"/todos/{todo_id}", json={"completed": True}, headers=auth.header(alice))
    data = r.json()
    for field in ("id", "title", "priority", "due_date", "completed", "created_at", "owner_id"):
        assert field in data


# ---------- delete ----------

def test_delete_todo(client, alice, auth):
    todo_id = _create(client, alice, auth, "Task").json()["id"]
    r = client.delete(f"/todos/{todo_id}", headers=auth.header(alice))
    assert r.status_code == 204


def test_deleted_todo_not_in_list(client, alice, auth):
    todo_id = _create(client, alice, auth, "Task").json()["id"]
    client.delete(f"/todos/{todo_id}", headers=auth.header(alice))
    todos = client.get("/todos", headers=auth.header(alice)).json()
    assert all(t["id"] != todo_id for t in todos)


def test_delete_nonexistent_todo_returns_404(client, alice, auth):
    r = client.delete("/todos/99999", headers=auth.header(alice))
    assert r.status_code == 404


def test_delete_returns_no_body(client, alice, auth):
    todo_id = _create(client, alice, auth, "Task").json()["id"]
    r = client.delete(f"/todos/{todo_id}", headers=auth.header(alice))
    assert r.status_code == 204
    assert r.content == b""


def test_delete_twice_returns_404_second_time(client, alice, auth):
    todo_id = _create(client, alice, auth, "Task").json()["id"]
    client.delete(f"/todos/{todo_id}", headers=auth.header(alice))
    r = client.delete(f"/todos/{todo_id}", headers=auth.header(alice))
    assert r.status_code == 404


# ---------- response correctness ----------

def test_create_todo_owner_id_matches_user(client, alice, auth):
    signup_id = client.post("/auth/signup", json={"username": "alice2", "password": "p"}).json()["id"]
    token = client.post("/auth/login", json={"username": "alice2", "password": "p"}).json()["access_token"]
    todo = client.post("/todos", json={"title": "Task"}, headers=auth.header(token)).json()
    assert todo["owner_id"] == signup_id


def test_get_todos_all_items_belong_to_current_user(client, alice, auth):
    for t in ("T1", "T2", "T3"):
        client.post("/todos", json={"title": t}, headers=auth.header(alice))
    todos = client.get("/todos", headers=auth.header(alice)).json()
    assert len(todos) == 3
    # all todos must share a single owner_id value
    owner_ids = {item["owner_id"] for item in todos}
    assert len(owner_ids) == 1


def test_create_todo_created_at_is_iso_string(client, alice, auth):
    from datetime import datetime
    data = _create(client, alice, auth, "Task").json()
    datetime.fromisoformat(data["created_at"])


def test_get_todos_content_type_is_json(client, alice, auth):
    r = client.get("/todos", headers=auth.header(alice))
    assert r.headers["content-type"].startswith("application/json")


def test_patch_preserves_untouched_fields(client, alice, auth):
    original = _create(client, alice, auth, "Task", priority="Low", due_date="2027-05-01").json()
    # only patch completed
    updated = client.patch(
        f"/todos/{original['id']}", json={"completed": True}, headers=auth.header(alice)
    ).json()
    assert updated["title"] == original["title"]
    assert updated["priority"] == original["priority"]
    assert updated["due_date"] == original["due_date"]
    assert updated["completed"] is True


# ---------- stateful flows ----------

def test_get_todos_reflects_updates(client, alice, auth):
    todo_id = _create(client, alice, auth, "Task", priority="Low").json()["id"]
    client.patch(f"/todos/{todo_id}", json={"title": "Updated", "priority": "High", "completed": True},
                 headers=auth.header(alice))
    item = next(t for t in client.get("/todos", headers=auth.header(alice)).json() if t["id"] == todo_id)
    assert item["title"] == "Updated"
    assert item["priority"] == "High"
    assert item["completed"] is True


def test_multiple_consecutive_toggles(client, alice, auth):
    todo_id = _create(client, alice, auth, "Task").json()["id"]
    for expected in (True, False, True, False):
        r = client.patch(f"/todos/{todo_id}", json={"completed": expected}, headers=auth.header(alice))
        assert r.json()["completed"] is expected


def test_alice_token_valid_after_bob_creates_many_todos(client, alice, auth):
    auth.signup("bob", "bobpass")
    bob_token = auth.login("bob", "bobpass").json()["access_token"]
    for i in range(5):
        client.post("/todos", json={"title": f"Bob {i}"}, headers=auth.header(bob_token))
    # alice's token should still work independently
    r = client.get("/todos", headers=auth.header(alice))
    assert r.status_code == 200
    assert r.json() == []


def test_delete_one_leaves_siblings_intact(client, alice, auth):
    id1 = _create(client, alice, auth, "Keep 1").json()["id"]
    id2 = _create(client, alice, auth, "Delete me").json()["id"]
    id3 = _create(client, alice, auth, "Keep 2").json()["id"]
    client.delete(f"/todos/{id2}", headers=auth.header(alice))
    remaining_ids = {t["id"] for t in client.get("/todos", headers=auth.header(alice)).json()}
    assert id1 in remaining_ids
    assert id3 in remaining_ids
    assert id2 not in remaining_ids


# ---------- completed status (filter support) ----------
# The frontend status filter relies on the list endpoint returning ALL todos with
# accurate `completed` values so the client can filter All / Active / Completed.

def test_list_includes_completed_todos(client, alice, auth):
    todo_id = _create(client, alice, auth, "Done task").json()["id"]
    client.patch(f"/todos/{todo_id}", json={"completed": True}, headers=auth.header(alice))
    todos = client.get("/todos", headers=auth.header(alice)).json()
    assert any(t["id"] == todo_id and t["completed"] is True for t in todos)


def test_list_includes_both_active_and_completed(client, alice, auth):
    active_id = _create(client, alice, auth, "Active").json()["id"]
    done_id = _create(client, alice, auth, "Done").json()["id"]
    client.patch(f"/todos/{done_id}", json={"completed": True}, headers=auth.header(alice))
    todos = client.get("/todos", headers=auth.header(alice)).json()
    completed_flags = {t["id"]: t["completed"] for t in todos}
    assert completed_flags[active_id] is False
    assert completed_flags[done_id] is True


def test_list_active_count_decreases_after_completion(client, alice, auth):
    ids = [_create(client, alice, auth, f"T{i}").json()["id"] for i in range(3)]
    client.patch(f"/todos/{ids[0]}", json={"completed": True}, headers=auth.header(alice))
    todos = client.get("/todos", headers=auth.header(alice)).json()
    active = [t for t in todos if not t["completed"]]
    done = [t for t in todos if t["completed"]]
    assert len(active) == 2
    assert len(done) == 1


def test_list_completed_count_after_marking_all(client, alice, auth):
    ids = [_create(client, alice, auth, f"T{i}").json()["id"] for i in range(4)]
    for todo_id in ids:
        client.patch(f"/todos/{todo_id}", json={"completed": True}, headers=auth.header(alice))
    todos = client.get("/todos", headers=auth.header(alice)).json()
    assert all(t["completed"] is True for t in todos)
    assert len(todos) == 4


def test_list_completed_field_accurate_after_unmark(client, alice, auth):
    todo_id = _create(client, alice, auth, "Task").json()["id"]
    client.patch(f"/todos/{todo_id}", json={"completed": True}, headers=auth.header(alice))
    client.patch(f"/todos/{todo_id}", json={"completed": False}, headers=auth.header(alice))
    todo = next(t for t in client.get("/todos", headers=auth.header(alice)).json() if t["id"] == todo_id)
    assert todo["completed"] is False


def test_list_does_not_auto_filter_completed_todos(client, alice, auth):
    todo_id = _create(client, alice, auth, "Completed task").json()["id"]
    client.patch(f"/todos/{todo_id}", json={"completed": True}, headers=auth.header(alice))
    todos = client.get("/todos", headers=auth.header(alice)).json()
    assert len(todos) == 1
    assert todos[0]["completed"] is True
