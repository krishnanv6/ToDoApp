"""Edge-case input validation for /todos endpoints."""
import pytest


def _make(client, token, auth, **kwargs):
    payload = {"title": "Task", **kwargs}
    return client.post("/todos", json=payload, headers=auth.header(token))


# ---------- title edge cases ----------

@pytest.mark.parametrize("bad_title", [
    "",          # empty string
    " ",         # single space
    "   ",       # multiple spaces
    "\t",        # tab only
    "\n",        # newline only
    "\t \n",     # mixed whitespace
])
def test_create_todo_whitespace_only_title_rejected(client, alice, auth, bad_title):
    r = _make(client, alice, auth, title=bad_title)
    assert r.status_code == 422


@pytest.mark.parametrize("bad_title", [
    " ",
    "\t",
    "\n",
])
def test_patch_whitespace_only_title_rejected(client, alice, auth, bad_title):
    todo_id = _make(client, alice, auth).json()["id"]
    r = client.patch(f"/todos/{todo_id}", json={"title": bad_title}, headers=auth.header(alice))
    assert r.status_code == 422


# ---------- priority case sensitivity ----------

@pytest.mark.parametrize("bad_priority", ["high", "low", "medium", "HIGH", "LOW", "MEDIUM"])
def test_create_todo_priority_wrong_case_rejected(client, alice, auth, bad_priority):
    r = _make(client, alice, auth, priority=bad_priority)
    assert r.status_code == 422


@pytest.mark.parametrize("bad_priority", ["high", "low", "medium", "Urgent", "Critical"])
def test_patch_invalid_priority_rejected(client, alice, auth, bad_priority):
    todo_id = _make(client, alice, auth).json()["id"]
    r = client.patch(f"/todos/{todo_id}", json={"priority": bad_priority}, headers=auth.header(alice))
    assert r.status_code == 422


# ---------- due_date edge cases ----------

def test_create_todo_past_due_date_accepted(client, alice, auth):
    # no restriction on past dates
    r = _make(client, alice, auth, due_date="2000-01-01")
    assert r.status_code == 201
    assert r.json()["due_date"] == "2000-01-01"


def test_create_todo_nonexistent_calendar_date_rejected(client, alice, auth):
    # Feb 30 does not exist
    r = _make(client, alice, auth, due_date="2027-02-30")
    assert r.status_code == 422


def test_create_todo_due_date_wrong_format_rejected(client, alice, auth):
    # DD-MM-YYYY is not ISO
    r = _make(client, alice, auth, due_date="31-12-2027")
    assert r.status_code == 422


def test_patch_invalid_due_date_rejected(client, alice, auth):
    todo_id = _make(client, alice, auth).json()["id"]
    r = client.patch(f"/todos/{todo_id}", json={"due_date": "not-a-date"}, headers=auth.header(alice))
    assert r.status_code == 422


def test_patch_nonexistent_calendar_date_rejected(client, alice, auth):
    todo_id = _make(client, alice, auth).json()["id"]
    r = client.patch(f"/todos/{todo_id}", json={"due_date": "2027-13-01"}, headers=auth.header(alice))
    assert r.status_code == 422


# ---------- non-integer todo_id in URL ----------

def test_patch_non_integer_id_returns_422(client, alice, auth):
    r = client.patch("/todos/abc", json={"completed": True}, headers=auth.header(alice))
    assert r.status_code == 422


def test_delete_non_integer_id_returns_422(client, alice, auth):
    r = client.delete("/todos/abc", headers=auth.header(alice))
    assert r.status_code == 422


def test_patch_float_id_returns_422(client, alice, auth):
    r = client.patch("/todos/1.5", json={"completed": True}, headers=auth.header(alice))
    assert r.status_code == 422
