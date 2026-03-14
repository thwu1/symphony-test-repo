from flask import Blueprint, jsonify, request
from . import db
from .models import Task, User, Tag
from .utils import validate_email, parse_due_date, paginate_query, sanitize_string

bp = Blueprint("api", __name__, url_prefix="/api")


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@bp.route("/users", methods=["GET"])
def list_users():
    users = User.query.all()
    return jsonify([u.to_dict() for u in users]), 200


@bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    username = sanitize_string(data.get("username"), max_length=80)
    email = sanitize_string(data.get("email"), max_length=120)

    # BUG: missing validation — the endpoint never checks whether *username*
    # or *email* are present.  A request with an empty body (or missing fields)
    # will crash with an IntegrityError rather than returning a 400.
    # Fix: add the block below before creating the User object:
    #
    #   if not username or not email:
    #       return jsonify({"error": "username and email are required"}), 400
    #   if not validate_email(email):
    #       return jsonify({"error": "Invalid email address"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

@bp.route("/tasks", methods=["GET"])
def list_tasks():
    page = request.args.get("page", 1, type=int)
    user_id = request.args.get("user_id", type=int)
    completed = request.args.get("completed", type=lambda v: v.lower() == "true")

    query = Task.query
    if user_id is not None:
        query = query.filter_by(user_id=user_id)
    if completed is not None:
        query = query.filter_by(completed=completed)

    result = paginate_query(query, page)
    result["items"] = [t.to_dict() for t in result["items"]]
    return jsonify(result), 200


@bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict()), 200


@bp.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    title = sanitize_string(data.get("title"), max_length=200)
    if not title:
        return jsonify({"error": "title is required"}), 400

    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    task = Task(
        title=title,
        description=sanitize_string(data.get("description")),
        priority=data.get("priority", 1),
        due_date=parse_due_date(data.get("due_date")),
        user_id=user_id,
    )

    tag_names = data.get("tags", [])
    for name in tag_names:
        name = sanitize_string(name, max_length=50)
        if name:
            tag = Tag.query.filter_by(name=name).first() or Tag(name=name)
            task.tags.append(tag)

    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    if "title" in data:
        title = sanitize_string(data["title"], max_length=200)
        if not title:
            return jsonify({"error": "title cannot be empty"}), 400
        task.title = title
    if "description" in data:
        task.description = sanitize_string(data["description"])
    if "priority" in data:
        task.priority = data["priority"]
    if "due_date" in data:
        task.due_date = parse_due_date(data["due_date"])
    if "completed" in data:
        task.completed = bool(data["completed"])

    db.session.commit()
    return jsonify(task.to_dict()), 200


@bp.route("/tasks/<int:task_id>/complete", methods=["POST"])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    db.session.commit()
    # Fixed: return 200 (OK) instead of 201 (Created) since the task was updated, not created.
    return jsonify(task.to_dict()), 200


@bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------

@bp.route("/tags", methods=["GET"])
def list_tags():
    tags = Tag.query.order_by(Tag.name).all()
    return jsonify([t.to_dict() for t in tags]), 200
