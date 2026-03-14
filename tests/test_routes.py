"""
Route tests.

NOTE: Two tests in this file are *intentionally failing* to give an AI agent
something concrete to fix:

  - test_complete_task_returns_200  — fails because the /complete endpoint
    returns 201 instead of 200.

  - test_create_user_missing_fields — fails because the create-user endpoint
    lacks input validation and crashes (500) instead of returning 400.
"""

import json
import pytest
from app import create_app, db
from app.models import User, Task


@pytest.fixture
def app():
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )
    with application.app_context():
        db.create_all()
        yield application
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_user(app):
    with app.app_context():
        user = User(username="bob", email="bob@example.com")
        db.session.add(user)
        db.session.commit()
        return user.id  # return id only — objects detach after context exit


@pytest.fixture
def sample_task(app, sample_user):
    with app.app_context():
        task = Task(title="Sample task", user_id=sample_user)
        db.session.add(task)
        db.session.commit()
        return task.id


# ---------------------------------------------------------------------------
# User routes
# ---------------------------------------------------------------------------

def test_list_users_empty(client):
    resp = client.get("/api/users")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_user(client):
    resp = client.post(
        "/api/users",
        data=json.dumps({"username": "carol", "email": "carol@example.com"}),
        content_type="application/json",
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["username"] == "carol"
    assert data["email"] == "carol@example.com"


def test_create_user_duplicate_username(client):
    payload = {"username": "dave", "email": "dave@example.com"}
    client.post("/api/users", data=json.dumps(payload), content_type="application/json")
    resp = client.post(
        "/api/users",
        data=json.dumps({"username": "dave", "email": "dave2@example.com"}),
        content_type="application/json",
    )
    assert resp.status_code == 409


def test_get_user(client, sample_user):
    resp = client.get(f"/api/users/{sample_user}")
    assert resp.status_code == 200
    assert resp.get_json()["username"] == "bob"


def test_get_user_not_found(client):
    resp = client.get("/api/users/9999")
    assert resp.status_code == 404


# INTENTIONALLY FAILING TEST #1
# Bug: the create_user endpoint has no validation for missing fields.
# When username or email is absent the app raises an IntegrityError (500).
# Fix: add the missing-field guard in app/routes.py create_user().
def test_create_user_missing_fields(client):
    resp = client.post(
        "/api/users",
        data=json.dumps({"username": "nomail"}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_delete_user(client, sample_user):
    resp = client.delete(f"/api/users/{sample_user}")
    assert resp.status_code == 200
    assert client.get(f"/api/users/{sample_user}").status_code == 404


# ---------------------------------------------------------------------------
# Task routes
# ---------------------------------------------------------------------------

def test_list_tasks_empty(client):
    resp = client.get("/api/tasks")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["items"] == []
    assert body["total"] == 0


def test_create_task(client, sample_user):
    resp = client.post(
        "/api/tasks",
        data=json.dumps({"title": "New task", "user_id": sample_user}),
        content_type="application/json",
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["title"] == "New task"
    assert data["completed"] is False


def test_create_task_missing_title(client, sample_user):
    resp = client.post(
        "/api/tasks",
        data=json.dumps({"user_id": sample_user}),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_create_task_unknown_user(client):
    resp = client.post(
        "/api/tasks",
        data=json.dumps({"title": "Orphan task", "user_id": 9999}),
        content_type="application/json",
    )
    assert resp.status_code == 404


def test_get_task(client, sample_task):
    resp = client.get(f"/api/tasks/{sample_task}")
    assert resp.status_code == 200
    assert resp.get_json()["title"] == "Sample task"


def test_update_task(client, sample_task):
    resp = client.put(
        f"/api/tasks/{sample_task}",
        data=json.dumps({"title": "Updated title", "priority": 3}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["title"] == "Updated title"
    assert data["priority"] == 3


def test_delete_task(client, sample_task):
    resp = client.delete(f"/api/tasks/{sample_task}")
    assert resp.status_code == 200
    assert client.get(f"/api/tasks/{sample_task}").status_code == 404


# INTENTIONALLY FAILING TEST #2
# Bug: POST /api/tasks/<id>/complete returns 201 instead of 200.
# Fix: change the return status code in app/routes.py complete_task() to 200.
def test_complete_task_returns_200(client, sample_task):
    resp = client.post(f"/api/tasks/{sample_task}/complete")
    assert resp.status_code == 200, (
        f"Expected 200 but got {resp.status_code}. "
        "The /complete endpoint returns 201 — fix it in app/routes.py."
    )
    assert resp.get_json()["completed"] is True


def test_list_tasks_filter_by_completed(client, sample_user):
    # Create two tasks, complete one
    def post_task(title):
        return client.post(
            "/api/tasks",
            data=json.dumps({"title": title, "user_id": sample_user}),
            content_type="application/json",
        ).get_json()["id"]

    t1 = post_task("task one")
    post_task("task two")
    client.post(f"/api/tasks/{t1}/complete")

    resp = client.get("/api/tasks?completed=true")
    assert resp.status_code == 200
    # Only one task should appear (regardless of the /complete status-code bug)
    assert resp.get_json()["total"] == 1


def test_list_tasks_with_tags(client, sample_user):
    resp = client.post(
        "/api/tasks",
        data=json.dumps(
            {"title": "Tagged task", "user_id": sample_user, "tags": ["work", "urgent"]}
        ),
        content_type="application/json",
    )
    assert resp.status_code == 201
    tag_names = {t["name"] for t in resp.get_json()["tags"]}
    assert tag_names == {"work", "urgent"}
