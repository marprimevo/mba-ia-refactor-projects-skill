# Playbook de refatoração

Aplique o padrão da stack detectada na Fase 1. Os pares antes/depois são o formato da transformação, não código para colar sem ler o projeto.

## 1. SQL concatenado para placeholder

Python:

```python
# antes
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "'")

# depois
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
```

JavaScript:

```javascript
// antes
db.get("SELECT * FROM courses WHERE id = " + cid, cb);

// depois
db.get("SELECT * FROM courses WHERE id = ?", [cid], cb);
```

Filtro opcional: monte a lista de condições e o array de parâmetros juntos. `LIKE` usa o valor ligado (`%` + termo), não concatenação dentro da string SQL.

## 2. Segredo hardcoded para ambiente

Python:

```python
# antes
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"

# depois
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or os.urandom(24).hex()
```

JavaScript:

```javascript
// antes
const config = { dbPass: "senha_super_secreta_prod_123", port: 3000 };

// depois
const config = {
  dbPass: process.env.DB_PASS || "",
  port: Number(process.env.PORT || 3000),
};
```

Crie `.env.example` com as chaves. Apague o segredo do health e dos logs.

## 3. God Class para MVC

Antes: um arquivo registra rotas, abre o banco e calcula o pedido.

Depois:

- schema e SQL no model do domínio;
- caso de uso no controller;
- `app.get/post` ou `add_url_rule` só aponta para o controller;
- o arquivo antigo é removido.

Não deixe o God Class reexportando a estrutura nova.

## 4. Estado global para escopo do request

Python:

```python
# antes
db_connection = None
def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(path, check_same_thread=False)
    return db_connection

# depois
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(path)
        g.db.row_factory = sqlite3.Row
    return g.db
```

Feche a conexão em `teardown_appcontext`. JavaScript: não exporte objeto de cache mutável. Se precisar de cache, injete um `Map` criado no composition root e documente o ciclo de vida. Prefira não cachear dado de request em variável de módulo.

## 5. N+1 para uma consulta

Python:

```python
# antes
for pedido in pedidos:
    itens = query_itens(pedido["id"])
    for item in itens:
        nome = query_produto(item["produto_id"])

# depois
rows = cursor.execute("""
    SELECT p.id, i.produto_id, i.quantidade, pr.nome AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
""").fetchall()
```

Agrupe as linhas em memória por id do pai. No ORM, use `joinedload` (ou um `GROUP BY`) em vez de `session.get` dentro do `for`.

## 6. Validação na borda, uma vez

Python:

```python
# antes
if "nome" not in dados: ...
if len(nome) < 2: ...
# o mesmo bloco copiado no PUT

# depois
def validar_produto(dados):
    if not dados or "nome" not in dados:
        raise AppError("Nome é obrigatório", 400)
    if len(dados["nome"]) < 2:
        raise AppError("Nome muito curto", 400)
    return dados
```

JavaScript: função `assertCheckout(body)` checa campos obrigatórios e devolve 400 antes de tocar no banco. Criar e atualizar chamam a mesma função.

## 7. API obsoleta para API atual

Python:

```python
# antes
User.query.get(user_id)
datetime.utcnow()

# depois
db.session.get(User, user_id)
datetime.now(timezone.utc).replace(tzinfo=None)
```

`replace(tzinfo=None)` só quando as colunas já são datetime naive. Caso novo, grave datetime com fuso.

JavaScript:

```javascript
// antes
const sqlite3 = require("sqlite3").verbose();
const buf = new Buffer(pwd);

// depois
const sqlite3 = require("sqlite3");
const buf = Buffer.from(pwd);
```

`req.param("id")` vira `req.params.id`. `@app.before_first_request` vira inicialização dentro de `create_app()`.

## 8. Senha em claro ou MD5 para hash com salt

Python:

```python
# antes
self.password = hashlib.md5(pwd.encode()).hexdigest()

# depois
salt = os.urandom(16)
digest = hashlib.pbkdf2_hmac("sha256", pwd.encode(), salt, 100_000)
self.password = salt.hex() + "$" + digest.hex()
```

A verificação recalcula o digest e compara com `hmac.compare_digest`. JavaScript: `crypto.scryptSync(password, salt, 32)` no mesmo formato `salt$hash`. Não logue a senha. Não devolva o campo na serialização (`to_dict` / objeto de resposta).

## 9. Magic number para constante

```python
# antes
if faturamento > 10000:
    desconto = faturamento * 0.1

# depois
for limite, taxa in settings.DISCOUNT_TIERS:
    if faturamento > limite:
        desconto = faturamento * taxa
        break
```

JavaScript: `const HASH_ROUNDS = 10000` não substitui um algoritmo fraco; se o número existe só para parecer trabalho, troque o algoritmo (padrão 8) e apague o laço.

## 10. Resposta pública

```python
# antes
return {"id": row["id"], "email": row["email"], "senha": row["senha"]}

# depois
return {"id": row["id"], "email": row["email"], "tipo": row["tipo"]}
```

Log de pagamento registra id do pedido, não PAN nem chave do gateway. Token de autenticação falso (`fake-jwt-token-` + id) é removido; o login responde sucesso e o usuário público.

## Ordem sugerida

1. Config e segredos.
2. Models com SQL parametrizado e schema.
3. Controllers e rotas finas.
4. Erro central e entry point.
5. Apagar arquivos substituídos.
6. Subir a aplicação e chamar os endpoints.
