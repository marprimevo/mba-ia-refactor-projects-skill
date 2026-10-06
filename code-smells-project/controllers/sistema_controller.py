from flask import jsonify, request

from middlewares.error_handler import AppError
from models.database import get_db, limpar_dados
from models.pedido_model import contagens


def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": "1.0.0",
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


def health_check():
    get_db().cursor().execute("SELECT 1")
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": contagens(),
        "versao": "1.0.0",
    }), 200


def reset_database():
    limpar_dados()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200


def executar_query():
    dados = request.get_json(silent=True) or {}
    if not dados.get("sql"):
        raise AppError("Query não informada", 400)
    raise AppError("Execução de SQL arbitrário desabilitada", 403)
