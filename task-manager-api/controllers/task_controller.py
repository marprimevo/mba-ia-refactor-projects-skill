from datetime import datetime

from flask import jsonify, request
from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload

from database import db
from middlewares.error_handler import AppError
from models.category import Category
from models.task import Task
from models.user import User
from utils.helpers import (
    DEFAULT_PRIORITY,
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    VALID_STATUSES,
    utc_now,
)


def _tags(value):
    if isinstance(value, list):
        return ",".join(value)
    return value


def _require_json():
    data = request.get_json(silent=True)
    if not data:
        raise AppError("Dados inválidos", 400)
    return data


def _validate_title(title, required=True):
    if title is None:
        if required:
            raise AppError("Título é obrigatório", 400)
        return None
    if len(title) < MIN_TITLE_LENGTH:
        raise AppError("Título muito curto", 400)
    if len(title) > MAX_TITLE_LENGTH:
        raise AppError("Título muito longo", 400)
    return title


def _validate_status(status):
    if status not in VALID_STATUSES:
        raise AppError("Status inválido", 400)
    return status


def _validate_priority(priority):
    if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
        raise AppError("Prioridade deve ser entre 1 e 5", 400)
    return priority


def _parse_due_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (TypeError, ValueError) as error:
        raise AppError("Formato de data inválido. Use YYYY-MM-DD", 400) from error


def _ensure_user(user_id):
    if not user_id:
        return
    if db.session.get(User, user_id) is None:
        raise AppError("Usuário não encontrado", 404)


def _ensure_category(category_id):
    if not category_id:
        return
    if db.session.get(Category, category_id) is None:
        raise AppError("Categoria não encontrada", 404)


def _list_payload(task):
    data = task.to_dict()
    data["overdue"] = task.is_overdue()
    data["user_name"] = task.user.name if task.user else None
    data["category_name"] = task.category.name if task.category else None
    return data


def list_tasks():
    stmt = (
        select(Task)
        .options(joinedload(Task.user), joinedload(Task.category))
        .order_by(Task.id)
    )
    tasks = db.session.scalars(stmt).unique().all()
    return jsonify([_list_payload(task) for task in tasks]), 200


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        return jsonify({"error": "Task não encontrada"}), 404
    data = task.to_dict()
    data["overdue"] = task.is_overdue()
    return jsonify(data), 200


def create_task():
    data = _require_json()
    title = _validate_title(data.get("title"))
    status = _validate_status(data.get("status", "pending"))
    priority = _validate_priority(data.get("priority", DEFAULT_PRIORITY))
    user_id = data.get("user_id")
    category_id = data.get("category_id")
    _ensure_user(user_id)
    _ensure_category(category_id)

    task = Task(
        title=title,
        description=data.get("description", ""),
        status=status,
        priority=priority,
        user_id=user_id,
        category_id=category_id,
    )
    if data.get("due_date"):
        task.due_date = _parse_due_date(data.get("due_date"))
    if data.get("tags"):
        task.tags = _tags(data.get("tags"))

    db.session.add(task)
    try:
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        raise AppError("Erro ao criar task", 500) from error
    return jsonify(task.to_dict()), 201


def update_task(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        return jsonify({"error": "Task não encontrada"}), 404
    data = _require_json()

    if "title" in data:
        task.title = _validate_title(data["title"])
    if "description" in data:
        task.description = data["description"]
    if "status" in data:
        task.status = _validate_status(data["status"])
    if "priority" in data:
        task.priority = _validate_priority(data["priority"])
    if "user_id" in data:
        _ensure_user(data["user_id"])
        task.user_id = data["user_id"]
    if "category_id" in data:
        _ensure_category(data["category_id"])
        task.category_id = data["category_id"]
    if "due_date" in data:
        task.due_date = _parse_due_date(data["due_date"]) if data["due_date"] else None
    if "tags" in data:
        task.tags = _tags(data["tags"])
    task.updated_at = utc_now()

    try:
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        raise AppError("Erro ao atualizar", 500) from error
    return jsonify(task.to_dict()), 200


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if task is None:
        return jsonify({"error": "Task não encontrada"}), 404
    try:
        db.session.delete(task)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        raise AppError("Erro ao deletar", 500) from error
    return jsonify({"message": "Task deletada com sucesso"}), 200


def search_tasks():
    query = request.args.get("q", "")
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    user_id = request.args.get("user_id", "")

    stmt = select(Task)
    if query:
        stmt = stmt.where(or_(Task.title.like(f"%{query}%"), Task.description.like(f"%{query}%")))
    if status:
        stmt = stmt.where(Task.status == status)
    if priority:
        try:
            stmt = stmt.where(Task.priority == int(priority))
        except ValueError as error:
            raise AppError("Prioridade inválida", 400) from error
    if user_id:
        try:
            stmt = stmt.where(Task.user_id == int(user_id))
        except ValueError as error:
            raise AppError("Usuário inválido", 400) from error

    results = db.session.scalars(stmt.order_by(Task.id)).all()
    return jsonify([task.to_dict() for task in results]), 200


def task_stats():
    tasks = db.session.scalars(select(Task)).all()
    total = len(tasks)
    pending = sum(1 for task in tasks if task.status == "pending")
    in_progress = sum(1 for task in tasks if task.status == "in_progress")
    done = sum(1 for task in tasks if task.status == "done")
    cancelled = sum(1 for task in tasks if task.status == "cancelled")
    overdue = sum(1 for task in tasks if task.is_overdue())
    completion = round((done / total) * 100, 2) if total else 0
    return jsonify({
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "done": done,
        "cancelled": cancelled,
        "overdue": overdue,
        "completion_rate": completion,
    }), 200
