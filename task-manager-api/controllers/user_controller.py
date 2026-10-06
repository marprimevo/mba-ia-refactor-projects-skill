from flask import jsonify, request
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import db
from middlewares.error_handler import AppError
from models.task import Task
from models.user import User
from utils.helpers import MIN_PASSWORD_LENGTH, VALID_ROLES, validate_email


def _require_json():
    data = request.get_json(silent=True)
    if not data:
        raise AppError("Dados inválidos", 400)
    return data


def _public_task(task):
    data = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "created_at": str(task.created_at),
        "due_date": str(task.due_date) if task.due_date else None,
        "overdue": task.is_overdue(),
    }
    return data


def list_users():
    stmt = select(User).options(selectinload(User.tasks)).order_by(User.id)
    users = db.session.scalars(stmt).unique().all()
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "active": user.active,
            "created_at": str(user.created_at),
            "task_count": len(user.tasks),
        })
    return jsonify(result), 200


def get_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"error": "Usuário não encontrado"}), 404
    data = user.to_dict()
    tasks = db.session.scalars(select(Task).where(Task.user_id == user_id).order_by(Task.id)).all()
    data["tasks"] = [task.to_dict() for task in tasks]
    return jsonify(data), 200


def create_user():
    data = _require_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if not name:
        raise AppError("Nome é obrigatório", 400)
    if not email:
        raise AppError("Email é obrigatório", 400)
    if not password:
        raise AppError("Senha é obrigatória", 400)
    if not validate_email(email):
        raise AppError("Email inválido", 400)
    if len(password) < MIN_PASSWORD_LENGTH:
        raise AppError("Senha deve ter no mínimo 4 caracteres", 400)
    if role not in VALID_ROLES:
        raise AppError("Role inválido", 400)
    existing = db.session.scalar(select(User).where(User.email == email))
    if existing:
        return jsonify({"error": "Email já cadastrado"}), 409

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    try:
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        raise AppError("Erro ao criar usuário", 500) from error
    return jsonify(user.to_dict()), 201


def update_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"error": "Usuário não encontrado"}), 404
    data = _require_json()

    if "name" in data:
        user.name = data["name"]
    if "email" in data:
        if not validate_email(data["email"]):
            raise AppError("Email inválido", 400)
        existing = db.session.scalar(select(User).where(User.email == data["email"]))
        if existing and existing.id != user_id:
            return jsonify({"error": "Email já cadastrado"}), 409
        user.email = data["email"]
    if "password" in data:
        if len(data["password"]) < MIN_PASSWORD_LENGTH:
            raise AppError("Senha muito curta", 400)
        user.set_password(data["password"])
    if "role" in data:
        if data["role"] not in VALID_ROLES:
            raise AppError("Role inválido", 400)
        user.role = data["role"]
    if "active" in data:
        user.active = data["active"]

    try:
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        raise AppError("Erro ao atualizar", 500) from error
    return jsonify(user.to_dict()), 200


def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"error": "Usuário não encontrado"}), 404
    tasks = db.session.scalars(select(Task).where(Task.user_id == user_id)).all()
    for task in tasks:
        db.session.delete(task)
    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        raise AppError("Erro ao deletar", 500) from error
    return jsonify({"message": "Usuário deletado com sucesso"}), 200


def get_user_tasks(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"error": "Usuário não encontrado"}), 404
    tasks = db.session.scalars(select(Task).where(Task.user_id == user_id).order_by(Task.id)).all()
    return jsonify([_public_task(task) for task in tasks]), 200


def login():
    data = _require_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        raise AppError("Email e senha são obrigatórios", 400)

    user = db.session.scalar(select(User).where(User.email == email))
    if user is None or not user.check_password(password):
        return jsonify({"error": "Credenciais inválidas"}), 401
    if not user.active:
        return jsonify({"error": "Usuário inativo"}), 403
    return jsonify({
        "message": "Login realizado com sucesso",
        "user": user.to_dict(),
    }), 200
