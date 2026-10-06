from flask import jsonify, request
from sqlalchemy import func, select

from database import db
from middlewares.error_handler import AppError
from models.category import Category
from models.task import Task
from utils.helpers import DEFAULT_COLOR


def list_categories():
    categories = db.session.scalars(select(Category).order_by(Category.id)).all()
    counts = dict(
        db.session.execute(select(Task.category_id, func.count()).group_by(Task.category_id)).all()
    )
    result = []
    for category in categories:
        data = category.to_dict()
        data["task_count"] = counts.get(category.id, 0)
        result.append(data)
    return jsonify(result), 200


def create_category():
    data = request.get_json(silent=True)
    if not data:
        raise AppError("Dados inválidos", 400)
    name = data.get("name")
    if not name:
        raise AppError("Nome é obrigatório", 400)
    category = Category(
        name=name,
        description=data.get("description", ""),
        color=data.get("color", DEFAULT_COLOR),
    )
    db.session.add(category)
    try:
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        raise AppError("Erro ao criar categoria", 500) from error
    return jsonify(category.to_dict()), 201


def update_category(cat_id):
    category = db.session.get(Category, cat_id)
    if category is None:
        return jsonify({"error": "Categoria não encontrada"}), 404
    data = request.get_json(silent=True)
    if not data:
        raise AppError("Dados inválidos", 400)
    if "name" in data:
        category.name = data["name"]
    if "description" in data:
        category.description = data["description"]
    if "color" in data:
        category.color = data["color"]
    try:
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        raise AppError("Erro ao atualizar", 500) from error
    return jsonify(category.to_dict()), 200


def delete_category(cat_id):
    category = db.session.get(Category, cat_id)
    if category is None:
        return jsonify({"error": "Categoria não encontrada"}), 404
    try:
        db.session.delete(category)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        raise AppError("Erro ao deletar", 500) from error
    return jsonify({"message": "Categoria deletada"}), 200
