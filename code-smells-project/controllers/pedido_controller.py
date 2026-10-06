from flask import jsonify, request

from config.settings import VALID_ORDER_STATUS
from middlewares.error_handler import AppError
from models import pedido_model


def criar_pedido():
    dados = request.get_json(silent=True)
    if not dados:
        raise AppError("Dados inválidos", 400)
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])
    if not usuario_id:
        raise AppError("Usuario ID é obrigatório", 400)
    if not itens:
        raise AppError("Pedido deve ter pelo menos 1 item", 400)
    resultado = pedido_model.criar(usuario_id, itens)
    if "erro" in resultado:
        return jsonify({"erro": resultado["erro"], "sucesso": False}), 400
    return jsonify({
        "dados": resultado,
        "sucesso": True,
        "mensagem": "Pedido criado com sucesso",
    }), 201


def listar_pedidos_usuario(usuario_id):
    return jsonify({"dados": pedido_model.listar_por_usuario(usuario_id), "sucesso": True}), 200


def listar_todos_pedidos():
    return jsonify({"dados": pedido_model.listar_todos(), "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    dados = request.get_json(silent=True) or {}
    novo_status = dados.get("status", "")
    if novo_status not in VALID_ORDER_STATUS:
        raise AppError("Status inválido", 400)
    pedido_model.atualizar_status(pedido_id, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200


def relatorio_vendas():
    return jsonify({"dados": pedido_model.relatorio_vendas(), "sucesso": True}), 200
