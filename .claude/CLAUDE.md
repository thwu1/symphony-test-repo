# Task Manager API — Agent Guide

## Project overview

This is a Flask + SQLAlchemy REST API for managing tasks and users.  The
codebase is intentionally small so that an AI agent can navigate it quickly.

## Directory layout

```
app/
  __init__.py   Flask app factory; sets up SQLAlchemy and registers the blueprint
  models.py     SQLAlchemy ORM models: User, Task, Tag (and task_tags join table)
  routes.py     All API endpoints, grouped by resource
  utils.py      Pure helper functions (validation, pagination, sanitisation)
tests/
  test_models.py  Unit tests for ORM models
  test_routes.py  Integration tests for HTTP routes — two tests intentionally fail
run.py          Entry point for `flask run`
requirements.txt
Makefile
```

## Running tests

```bash
make test        # pytest -v
make test-fast   # pytest -x -q  (stop on first failure)
```

## Known bugs (good starting tasks for an agent)

### Bug 1 — Wrong HTTP status code in task completion endpoint

**File:** `app/routes.py`, function `complete_task`
**Symptom:** `POST /api/tasks/<id>/complete` returns `201 Created`.
**Expected:** `200 OK` — the task was updated, not created.
**Failing test:** `tests/test_routes.py::test_complete_task_returns_200`
**Fix:** Change the final `return` statement from `201` to `200`.

### Bug 2 — Missing validation in user creation endpoint

**File:** `app/routes.py`, function `create_user`
**Symptom:** Sending a POST to `/api/users` without `username` or `email`
causes an unhandled `IntegrityError` (HTTP 500) instead of a proper
`400 Bad Request`.
**Failing test:** `tests/test_routes.py::test_create_user_missing_fields`
**Fix:** Add the following guard after extracting `username` and `email`:

```python
if not username or not email:
    return jsonify({"error": "username and email are required"}), 400
if not validate_email(email):
    return jsonify({"error": "Invalid email address"}), 400
```

## Coding conventions

- All responses are JSON.
- HTTP status codes follow REST conventions: 200 OK, 201 Created, 400 Bad
  Request, 404 Not Found, 409 Conflict.
- Helper functions live in `utils.py`; keep `routes.py` thin.
- Use `sanitize_string()` on all user-supplied string fields before persisting.
- `paginate_query()` handles list endpoints; always return the paginated
  envelope `{items, total, page, per_page, pages}` for collections.
