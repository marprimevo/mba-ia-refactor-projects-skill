# Guidelines de arquitetura MVC

O alvo é o mesmo nas linguagens: HTTP na borda, regra na aplicação, dados no model, configuração fora do código, erro num lugar só.

## Responsabilidades

| Camada | Faz | Não faz |
| --- | --- | --- |
| Config | Lê ambiente, expõe constantes de domínio nomeadas, paths e porta | Abrir banco, decidir HTTP, guardar segredo no repositório |
| Model | Schema, queries parametrizadas, mapeamento de linha para estrutura simples | `request`, `req`/`res`, status HTTP |
| Controller | Orquestra um caso de uso: valida entrada já parseada, chama models, devolve resultado | Montar SQL, conhecer driver |
| View / Route | Amarra método e path ao controller, lê JSON/query | Regra de desconto, hash de senha, laço de SQL |
| Middleware de erro | Converte falha em resposta única | Regra de negócio |
| Entry point | Compõe config, rotas, erro e sobe o processo | Domínio |

Serviço existente (envio de e-mail, gateway) permanece, chamado pelo controller. Não duplique o serviço dentro da rota. Não crie camada nova se ela só repassa uma chamada.

## Layout

Python (entry point continua `python app.py` na raiz do projeto):

```text
app.py
config/settings.py
models/
controllers/
views/routes.py
middlewares/error_handler.py
.env.example
```

Node (entry point continua `npm start` → `src/app.js`):

```text
src/app.js
src/config/settings.js
src/models/
src/controllers/
src/routes/
src/middlewares/errorHandler.js
.env.example
```

Projeto que já tem `models/`, `routes/` e `services/`:

- Mantenha `models/` e os blueprints.
- Deixe as rotas finas e mova o corpo para `controllers/`.
- Config sai do `app.py` para `config/settings.py`.
- `middlewares/error_handler.py` registra os handlers.
- Não mova tudo para um único `routes.py` se os blueprints já separam o domínio.

## Regras de dependência

- Rota importa controller. Controller importa model. Model não importa rota nem controller.
- Model recebe conexão ou usa o escopo do request (`flask.g`, sessão do ORM), não um singleton global mutável.
- Segredo só via ambiente. `.env.example` lista as chaves com valor vazio ou placeholder óbvio (`change-me`), nunca chave de produção.
- A aplicação sobe sem `.env` se o default de desenvolvimento for seguro (porta, SQLite local, segredo aleatório de processo quando a API não usa sessão).

## Contrato HTTP

- Preserve path, método e o formato de sucesso já consumido pelo cliente (`api.http`, README, campos `dados`/`sucesso`).
- Pode deixar de devolver `password`, `senha`, `secret_key` e PAN de cartão.
- Endpoint perigoso continua existindo e responde: execução de SQL arbitrário passa a responder erro de autorização, sem rodar a query.
- Status de validação (400, 404, 409, 401) permanece com as mesmas condições de negócio.

## Erro

Uma classe de erro de aplicação (mensagem + status) e um handler genérico para o inesperado. O handler genérico não devolve stack nem segredo. Rotas não copiam `try/except` idêntico em toda função.

## Entry point

Um módulo sobe o servidor. Python: factory `create_app()` chamada por `app.py`. Node: `src/app.js` espera o schema existir antes de `listen`, para o primeiro request não correr com o banco vazio.
