from models.database import get_db
from models.passwords import hash_password, verify_password


def _publico(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def listar():
    cursor = get_db().cursor()
    cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios")
    return [_publico(row) for row in cursor.fetchall()]


def buscar_por_id(usuario_id):
    cursor = get_db().cursor()
    cursor.execute(
        "SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?",
        (usuario_id,),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    return _publico(row)


def criar(nome, email, senha, tipo="cliente"):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, hash_password(senha), tipo),
    )
    connection.commit()
    return cursor.lastrowid


def login(email, senha):
    cursor = get_db().cursor()
    cursor.execute(
        "SELECT id, nome, email, senha, tipo FROM usuarios WHERE email = ?",
        (email,),
    )
    row = cursor.fetchone()
    if row is None or not verify_password(senha, row["senha"]):
        return None
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
    }
