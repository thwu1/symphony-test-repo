import pytest
from app import create_app, db
from app.models import User, Task, Tag


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
def ctx(app):
    with app.app_context():
        yield


def make_user(username="alice", email="alice@example.com"):
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return user


# ---------------------------------------------------------------------------
# User model
# ---------------------------------------------------------------------------

def test_user_creation(ctx):
    user = make_user()
    assert user.id is not None
    assert user.username == "alice"
    assert user.email == "alice@example.com"
    assert user.created_at is not None


def test_user_to_dict(ctx):
    user = make_user()
    d = user.to_dict()
    assert d["username"] == "alice"
    assert d["email"] == "alice@example.com"
    assert d["task_count"] == 0
    assert "id" in d
    assert "created_at" in d


def test_user_unique_username(ctx):
    make_user()
    duplicate = User(username="alice", email="other@example.com")
    db.session.add(duplicate)
    with pytest.raises(Exception):
        db.session.commit()


# ---------------------------------------------------------------------------
# Task model
# ---------------------------------------------------------------------------

def test_task_creation(ctx):
    user = make_user()
    task = Task(title="Write tests", user_id=user.id)
    db.session.add(task)
    db.session.commit()

    assert task.id is not None
    assert task.title == "Write tests"
    assert task.completed is False
    assert task.priority == 1


def test_task_to_dict(ctx):
    user = make_user()
    task = Task(title="Buy milk", description="2% please", user_id=user.id, priority=2)
    db.session.add(task)
    db.session.commit()

    d = task.to_dict()
    assert d["title"] == "Buy milk"
    assert d["description"] == "2% please"
    assert d["priority"] == 2
    assert d["completed"] is False
    assert d["tags"] == []
    assert d["user_id"] == user.id


def test_task_default_priority(ctx):
    user = make_user()
    task = Task(title="Low priority thing", user_id=user.id)
    db.session.add(task)
    db.session.commit()
    assert task.priority == 1


# ---------------------------------------------------------------------------
# Tag model
# ---------------------------------------------------------------------------

def test_tag_creation(ctx):
    tag = Tag(name="urgent")
    db.session.add(tag)
    db.session.commit()
    assert tag.id is not None
    assert tag.name == "urgent"


def test_task_tag_association(ctx):
    user = make_user()
    tag = Tag(name="work")
    task = Task(title="Finish report", user_id=user.id)
    task.tags.append(tag)
    db.session.add(task)
    db.session.commit()

    fetched = Task.query.get(task.id)
    assert len(fetched.tags) == 1
    assert fetched.tags[0].name == "work"


def test_task_to_dict_includes_tags(ctx):
    user = make_user()
    tag = Tag(name="home")
    task = Task(title="Clean garage", user_id=user.id)
    task.tags.append(tag)
    db.session.add(task)
    db.session.commit()

    d = task.to_dict()
    assert len(d["tags"]) == 1
    assert d["tags"][0]["name"] == "home"
