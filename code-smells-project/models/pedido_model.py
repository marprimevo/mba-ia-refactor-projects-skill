from config.settings import DISCOUNT_TIERS
from models.database import get_db

_PEDIDOS_SQL = """
    SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
           i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
"""


def _agrupar(rows):
    pedidos = {}
    ordem = []
    for row in rows:
        pedido_id = row["id"]
        if pedido_id not in pedidos:
            pedidos[pedido_id] = {
                "id": pedido_id,
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
            ordem.append(pedido_id)
        if row["produto_id"] is None:
            continue
        nome = row["produto_nome"] if row["produto_nome"] else "Desconhecido"
        pedidos[pedido_id]["itens"].append({
            "produto_id": row["produto_id"],
            "produto_nome": nome,
            "quantidade": row["quantidade"],
            "preco_unitario": row["preco_unitario"],
        })
    return [pedidos[pedido_id] for pedido_id in ordem]


def criar(usuario_id, itens):
    connection = get_db()
    cursor = connection.cursor()
    total = 0
    reservados = []

    for item in itens:
        cursor.execute(
            "SELECT id, nome, preco, estoque FROM produtos WHERE id = ?",
            (item["produto_id"],),
        )
        produto = cursor.fetchone()
        if produto is None:
            connection.rollback()
            return {"erro": "Produto " + str(item["produto_id"]) + " não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            connection.rollback()
            return {"erro": "Estoque insuficiente para " + produto["nome"]}
        total = total + (produto["preco"] * item["quantidade"])
        reservados.append((produto, item["quantidade"]))

    cursor.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total),
    )
    pedido_id = cursor.lastrowid
    for produto, quantidade in reservados:
        cursor.execute(
            """
            INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
            VALUES (?, ?, ?, ?)
            """,
            (pedido_id, produto["id"], quantidade, produto["preco"]),
        )
        cursor.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (quantidade, produto["id"]),
        )
    connection.commit()
    return {"pedido_id": pedido_id, "total": total}


def listar_por_usuario(usuario_id):
    cursor = get_db().cursor()
    cursor.execute(_PEDIDOS_SQL + " WHERE p.usuario_id = ? ORDER BY p.id", (usuario_id,))
    return _agrupar(cursor.fetchall())


def listar_todos():
    cursor = get_db().cursor()
    cursor.execute(_PEDIDOS_SQL + " ORDER BY p.id")
    return _agrupar(cursor.fetchall())


def atualizar_status(pedido_id, novo_status):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT status FROM pedidos WHERE id = ?", (pedido_id,))
    atual = cursor.fetchone()
    cursor.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?",
        (novo_status, pedido_id),
    )
    if atual is not None and novo_status == "cancelado" and atual["status"] != "cancelado":
        cursor.execute(
            "SELECT produto_id, quantidade FROM itens_pedido WHERE pedido_id = ?",
            (pedido_id,),
        )
        for item in cursor.fetchall():
            cursor.execute(
                "UPDATE produtos SET estoque = estoque + ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )
    connection.commit()
    return True


def relatorio_vendas():
    cursor = get_db().cursor()
    cursor.execute(
        """
        SELECT
            COUNT(*) AS total_pedidos,
            COALESCE(SUM(total), 0) AS faturamento,
            SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END) AS pendentes,
            SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END) AS aprovados,
            SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END) AS cancelados
        FROM pedidos
        """
    )
    row = cursor.fetchone()
    total_pedidos = row["total_pedidos"]
    faturamento = row["faturamento"] or 0
    desconto = 0
    for limite, taxa in DISCOUNT_TIERS:
        if faturamento > limite:
            desconto = faturamento * taxa
            break
    ticket = round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0
    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": row["pendentes"] or 0,
        "pedidos_aprovados": row["aprovados"] or 0,
        "pedidos_cancelados": row["cancelados"] or 0,
        "ticket_medio": ticket,
    }


def contagens():
    cursor = get_db().cursor()
    cursor.execute(
        """
        SELECT
            (SELECT COUNT(*) FROM produtos) AS produtos,
            (SELECT COUNT(*) FROM usuarios) AS usuarios,
            (SELECT COUNT(*) FROM pedidos) AS pedidos
        """
    )
    row = cursor.fetchone()
    return {"produtos": row["produtos"], "usuarios": row["usuarios"], "pedidos": row["pedidos"]}
