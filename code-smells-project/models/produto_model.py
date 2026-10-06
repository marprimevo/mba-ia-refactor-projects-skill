from models.database import get_db

def produto_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def listar():
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM produtos")
    return [produto_dict(row) for row in cursor.fetchall()]


def buscar_por_id(produto_id):
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    row = cursor.fetchone()
    if row is None:
        return None
    return produto_dict(row)


def criar(nome, descricao, preco, estoque, categoria):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    connection.commit()
    return cursor.lastrowid


def atualizar(produto_id, nome, descricao, preco, estoque, categoria):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE produtos
        SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ?
        WHERE id = ?
        """,
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    connection.commit()
    return cursor.rowcount > 0


def deletar(produto_id):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    connection.commit()
    return cursor.rowcount > 0


def buscar(termo, categoria=None, preco_min=None, preco_max=None):
    query = "SELECT * FROM produtos WHERE 1=1"
    params = []
    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        like = f"%{termo}%"
        params.extend((like, like))
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        query += " AND preco <= ?"
        params.append(preco_max)

    cursor = get_db().cursor()
    cursor.execute(query, params)
    return [produto_dict(row) for row in cursor.fetchall()]
