from flask import jsonify, request

from config.settings import MAX_PRODUCT_NAME, MIN_PRODUCT_NAME, VALID_CATEGORIES
from middlewares.error_handler import AppError
from models import produto_model


def _validar(dados):
    if not dados:
        raise AppError("Dados inválidos", 400)
    if "nome" not in dados:
        raise AppError("Nome é obrigatório", 400)
    if "preco" not in dados:
        raise AppError("Preço é obrigatório", 400)
    if "estoque" not in dados:
        raise AppError("Estoque é obrigatório", 400)

    nome = dados["nome"]
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    if preco < 0:
        raise AppError("Preço não pode ser negativo", 400)
    if estoque < 0:
        raise AppError("Estoque não pode ser negativo", 400)
    if len(nome) < MIN_PRODUCT_NAME:
        raise AppError("Nome muito curto", 400)
    if len(nome) > MAX_PRODUCT_NAME:
        raise AppError("Nome muito longo", 400)
    if categoria not in VALID_CATEGORIES:
        raise AppError("Categoria inválida. Válidas: " + str(list(VALID_CATEGORIES)), 400)
    return nome, dados.get("descricao", ""), preco, estoque, categoria


def listar_produtos():
    produtos = produto_model.listar()
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produto(id):
    produto = produto_model.buscar_por_id(id)
    if produto is None:
        return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404
    return jsonify({"dados": produto, "sucesso": True}), 200


def criar_produto():
    nome, descricao, preco, estoque, categoria = _validar(request.get_json(silent=True))
    produto_id = produto_model.criar(nome, descricao, preco, estoque, categoria)
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(id):
    if produto_model.buscar_por_id(id) is None:
        return jsonify({"erro": "Produto não encontrado"}), 404
    nome, descricao, preco, estoque, categoria = _validar(request.get_json(silent=True))
    produto_model.atualizar(id, nome, descricao, preco, estoque, categoria)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(id):
    if not produto_model.deletar(id):
        return jsonify({"erro": "Produto não encontrado"}), 404
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria")
    preco_min = request.args.get("preco_min")
    preco_max = request.args.get("preco_max")
    try:
        if preco_min is not None:
            preco_min = float(preco_min)
        if preco_max is not None:
            preco_max = float(preco_max)
    except ValueError as error:
        raise AppError("Dados inválidos", 400) from error
    resultados = produto_model.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
