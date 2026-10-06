# Catálogo de anti-patterns

Escala:

- **CRITICAL:** segurança, perda de dados ou mistura total de responsabilidades (God Class, SQL injection, segredo hardcoded, senha exposta).
- **HIGH:** MVC ou SOLID quebrados a ponto de impedir teste e mudança (regra de negócio na rota, estado global mutável, criptografia fraca, acoplamento sem injeção).
- **MEDIUM:** duplicação, N+1, validação ausente, API obsoleta, efeito colateral incompleto.
- **LOW:** nomes, magic numbers, `print`/`console.log` de debug, imports mortos.

Cada finding precisa de arquivo e intervalo de linhas. Um arquivo pode gerar vários findings. Não marque estilo pessoal como CRITICAL.

## 1. God Class / God Method — CRITICAL

Sinais: o mesmo arquivo abre banco, declara rotas e decide regra de negócio; ou um módulo "model" cobre vários domínios com SQL, validação e formatação. Heurística: arquivo com mais de uma responsabilidade entre {HTTP, SQL, regra de negócio} e acima de ~200 linhas, ou classe cujo nome é `Manager`/`Utils` e concentra o sistema.

## 2. Credenciais hardcoded — CRITICAL

Sinais: string literal atribuída a `SECRET_KEY`, `password`, `passwd`, `dbPass`, `apiKey`, `api_key`, `token`, `smtp` password, chave `pk_live_` ou `sk_live_`. Também conta segredo devolvido em JSON (`secret_key` no health).

## 3. SQL injection — CRITICAL

Sinais: SQL montado com concatenação, f-string ou template string e enviado a `execute`, `executemany` ou equivalente. Exemplo de sinal: `"... " + variavel` ou `` `... ${id}` `` dentro da query. Placeholder `?` ou `:nome` com tupla de parâmetros não é injection.

## 4. Exposição de dado sensível — CRITICAL

Sinais: campo `senha`, `password`, `pass` ou número de cartão em resposta JSON, log ou `print`/`console.log`. Health que ecoa segredo. Listagem de usuários que devolve hash ou senha.

## 5. Regra de negócio na borda HTTP — HIGH

Sinais: função de rota ou controller que calcula preço, estoque, desconto, status de pagamento ou política de autorização além de ler o request e chamar um serviço. Vários `if` de domínio dentro de `app.get`/`@bp.route`.

## 6. Estado global mutável — HIGH

Sinais: `global conexao`, `let globalCache = {}`, `let totalRevenue = 0`, conexão única de módulo reutilizada entre requests (`check_same_thread=False` para contornar isso). Constante imutável de configuração não entra aqui.

## 7. Criptografia fraca ou senha em texto puro — HIGH

Sinais: `hashlib.md5`, senha gravada sem hash, hash caseiro em loop (`badCrypto`), comparação de senha em claro no SQL. `pbkdf2`, `scrypt` ou `bcrypt` com salt não entram.

## 8. Query N+1 — MEDIUM

Sinais: `for` (ou `forEach`) que executa `execute`, `query.get` ou `db.get` por item. Laço de pais que, para cada filho, busca o neto.

## 9. Validação ausente ou copiada — MEDIUM

Sinais: body usado sem checar campo obrigatório; a mesma lista de regras (`len < 3`, status válidos) repetida em criar e atualizar; rota sem tratamento de JSON ausente.

## 10. API obsoleta — MEDIUM

Sinais e substituto:

| Sinal | Substituto |
| --- | --- |
| `datetime.utcnow` | `datetime.now(timezone.utc)` (naive apenas se o banco já grava datetime sem fuso: `.replace(tzinfo=None)`) |
| `Model.query.get(id)` | `db.session.get(Model, id)` |
| `@app.before_first_request` | inicialização no factory / `with app.app_context()` |
| `new Buffer(` | `Buffer.from(` |
| `req.param(` | `req.params` ou `req.body` / `req.query` |
| `sqlite3.verbose()` | `require('sqlite3')` |

Só reporte se o símbolo aparecer no código.

## 11. Duplicação de código — MEDIUM

Sinais: o mesmo bloco de montagem de dicionário, a mesma regra de "atrasado" ou o mesmo `try/except` copiado em três ou mais pontos.

## 12. Efeito colateral incompleto — MEDIUM

Sinais: comentário ou mensagem que promete uma ação que o código não faz (apagar usuário e deixar matrícula; cancelar pedido e não devolver estoque; `except:` vazio).

## 13. Magic number — LOW

Sinais: limiar de negócio numérico sem nome (`10000`, `0.1`, `10000` iterações de hash, prioridade `3` solta) quando já existe constante no projeto ou o número codifica regra.

## 14. Nome opaco ou debug barulhento — LOW

Sinais: variáveis de uma letra para conceito de negócio (`u`, `e`, `cid`, `cc`); `print`/`console.log` de fluxo normal com dado de usuário; imports não usados (`os, sys, json` no entry point sem uso).

Não reporte formatação, aspas ou ordem de imports.
