# Task Manager API

A simple REST API for managing tasks, built with Flask and SQLAlchemy.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
make install
```

## Running

```bash
make run
# Server starts at http://127.0.0.1:5000
```

## Testing

```bash
make test        # run all tests with verbose output
make test-fast   # stop on first failure
```

## API Reference

### Users

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/users` | List all users |
| POST | `/api/users` | Create a user |
| GET | `/api/users/<id>` | Get a user |
| DELETE | `/api/users/<id>` | Delete a user |

**Create user payload**
```json
{ "username": "alice", "email": "alice@example.com" }
```

### Tasks

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/tasks` | List tasks (supports `?user_id=`, `?completed=`, `?page=`) |
| POST | `/api/tasks` | Create a task |
| GET | `/api/tasks/<id>` | Get a task |
| PUT | `/api/tasks/<id>` | Update a task |
| DELETE | `/api/tasks/<id>` | Delete a task |
| POST | `/api/tasks/<id>/complete` | Mark a task complete |

**Create task payload**
```json
{
  "title": "Write docs",
  "description": "Optional longer text",
  "priority": 2,
  "due_date": "2024-12-31",
  "user_id": 1,
  "tags": ["work", "writing"]
}
```

Priority values: `1` = low, `2` = medium, `3` = high.

### Tags

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/tags` | List all tags |

## Known Issues

There are two bugs intentionally left in the codebase for testing purposes:

1. **Wrong status code on task completion** (`app/routes.py`, `complete_task`): the
   `/api/tasks/<id>/complete` endpoint returns `201 Created` instead of `200 OK`.

2. **Missing input validation on user creation** (`app/routes.py`, `create_user`): the
   endpoint does not validate that `username` and `email` are present, causing a
   server error instead of a `400 Bad Request` when fields are missing.
