# Criação de Skills — Refatoração Arquitetural Automatizada

Skill `refactor-arch` que analisa um backend, gera um relatório de auditoria e refatora o projeto para MVC. A skill é agnóstica de stack: os três projetos do repositório (dois Flask e um Express) passam pelas mesmas três fases.

Ferramenta: Cursor com o agente Grok. A skill vive em `.cursor/skills/refactor-arch/` (convenção do Cursor). Uma cópia idêntica fica em `.claude/skills/refactor-arch/` para o caminho descrito no enunciado do curso. O nome da skill e o arquivo `SKILL.md` não mudam.

Fork de [devfullcycle/mba-ia-refactor-projects-skill](https://github.com/devfullcycle/mba-ia-refactor-projects-skill).

## Análise Manual

Leitura feita antes de escrever a skill, no código original. A amostra abaixo é o que orientou o catálogo. A auditoria da skill registra o conjunto completo em `reports/`.

### code-smells-project (Python/Flask, e-commerce)

Quatro arquivos de aplicação, sem pastas de camada. `models.py` concentra SQL, regra de pedido e formatação dos quatro domínios.

| Severidade | Onde | Problema | Por que importa |
| --- | --- | --- | --- |
| CRITICAL | `models.py:28`, `47-52`, `109-111`, `126-129`, `279-281`, `285-299` | SQL montado por concatenação (id, nome, e-mail, senha, busca) | Qualquer campo vindo do cliente altera a query. Login e busca são os vetores mais diretos. |
| CRITICAL | `app.py:7` e `controllers.py:289` | `SECRET_KEY` fixa e repetida no `GET /health` | O segredo sai no código e na resposta HTTP. |
| CRITICAL | `app.py:59-76` | `POST /admin/query` executa o SQL recebido, sem autenticação | Leitura e escrita irrestritas do SQLite. |
| HIGH | `database.py:4-10` e `75-83`; `models.py:75-88` | Conexão global mutável e senhas em texto puro devolvidas na listagem de usuários | A conexão vaza entre requests; a senha trafega na API. |
| HIGH | `models.py:1-315` | God module: produtos, usuários, pedidos e relatório no mesmo arquivo, com SQL e regra juntos | Não dá para testar um domínio sem carregar os outros. |
| MEDIUM | `models.py:174-198` e `206-230` | N+1: para cada pedido, uma query de itens e outra por produto | O custo cresce com o volume de pedidos. |
| MEDIUM | `controllers.py` (criar e atualizar produto, e o `try/except` repetido em cada função) | Validação e tratamento de erro copiados | Uma regra nova precisa ser alterada em dois lugares e o erro não tem formato único. |
| LOW | `models.py:257-262` | Limiares `10000`, `5000`, `1000` e taxas `0.1`, `0.05`, `0.02` | A regra de desconto não tem nome e se confunde com número solto. |
| LOW | `controllers.py:8`, `208-210` | `print` de listagem, e-mail, SMS e push | Efeito colateral no stdout no lugar de um ponto de extensão. |

### ecommerce-api-legacy (Node.js/Express, LMS com checkout)

Três arquivos. `AppManager` abre o SQLite em memória, cria o schema, registra as rotas e executa o checkout.

| Severidade | Onde | Problema | Por que importa |
| --- | --- | --- | --- |
| CRITICAL | `src/utils.js:2-4` | Usuário de banco, senha e chave `pk_live_` no fonte | Segredo de produção versionado. |
| CRITICAL | `src/AppManager.js:4-139` | God Class: schema, HTTP, pagamento e matrícula na mesma classe | Qualquer mudança no checkout mexe no relatório e no delete. |
| CRITICAL | `src/AppManager.js:45` | Log do número do cartão e da chave do gateway | PAN e credencial vazam no stdout. |
| HIGH | `src/utils.js:9-14` | `globalCache` e `totalRevenue` mutáveis de módulo | Estado compartilhado entre requests, sem dono. |
| HIGH | `src/utils.js:17-23` e `src/AppManager.js:28-77` | Hash caseiro de 10 caracteres e regra de pagamento dentro da rota | Senha previsível; a rota não é testável sem o Express. |
| MEDIUM | `src/AppManager.js:80-128` | Relatório financeiro em N+1 (curso, matrícula, usuário, pagamento) | Quatro níveis de callback e uma query por linha. |
| MEDIUM | `src/AppManager.js:131-136` | `DELETE /api/users/:id` apaga o usuário e deixa matrícula e pagamento | A mensagem admite o dado órfão. A validação do checkout só checa presença dos campos. |
| LOW | `src/AppManager.js:29-33` | Parâmetros `u`, `e`, `p`, `cid`, `cc` | O fluxo de checkout fica ilegível. |
| LOW | `src/utils.js:19` e `src/AppManager.js:1` | Laço mágico de `10000` iterações e `sqlite3.verbose()` | O laço não adiciona entropia; `verbose()` é a API de stack trace de debug do driver. |

### task-manager-api (Python/Flask, tasks)

Já existe `models/`, `routes/`, `services/` e `utils/`. A separação não chega em controller, e a borda HTTP concentra regra, acesso e serialização.

| Severidade | Onde | Problema | Por que importa |
| --- | --- | --- | --- |
| CRITICAL | `models/user.py:16-32` | MD5 sem salt e `password` dentro de `to_dict` | A senha (fraca) sai em criação, detalhe e login. |
| HIGH | `app.py:11-13` e `services/notification_service.py:6-10` | `SECRET_KEY` e senha SMTP no fonte; URI do banco no entry point | Configuração de segurança misturada com o bootstrap. |
| HIGH | `routes/user_routes.py:205-210` | Login devolve `fake-jwt-token-` + id | Qualquer cliente forja o token. Não há controller: a rota faz a política. |
| MEDIUM | `routes/task_routes.py:26-55` e `routes/report_routes.py:53-68`, `157-164` | N+1: usuário e categoria por task; tasks por usuário; contagem por categoria | A listagem dispara uma query por relacionamento. |
| MEDIUM | `routes/task_routes.py`, `routes/user_routes.py`, `routes/report_routes.py`, `models/task.py:50-60` | A mesma regra de tarefa atrasada copiada | O critério de atraso diverge se um ponto for corrigido e outro não. |
| MEDIUM | `datetime.utcnow` em models, rotas, services e seed; `Model.query.get` nas rotas | APIs obsoletas (Python 3.12 e SQLAlchemy 2) | `utcnow` emite warning e `Query.get` saiu do estilo 2.0. |
| LOW | `routes/task_routes.py:105-127` e `routes/user_routes.py:64` | Limites `3`, `200` e `4` repetidos, embora `utils/helpers.py:110-116` já defina constantes | A constante existe e não é usada. |
| LOW | `routes/task_routes.py:60` (`except:`) e `app.py:7` | `except` nu e imports `os`, `sys`, `json` sem uso | Engole erro de programação; o entry point mente sobre as dependências. |

## Construção da Skill

A skill fica em `code-smells-project/.cursor/skills/refactor-arch/` e é copiada para `.claude/skills/refactor-arch/` e para os outros dois projetos. O `SKILL.md` é o procedimento (três fases, pausa obrigatória, validação). O conhecimento de domínio está em cinco arquivos de referência, um nível abaixo do `SKILL.md`:

- `project-analysis.md` — heurísticas de linguagem, framework, banco, domínio, arquitetura e contagem de arquivos.
- `anti-patterns.md` — 14 anti-patterns com sinal de detecção e severidade, incluindo o mapa de APIs obsoletas.
- `audit-report-template.md` — formato da Fase 2, com arquivo e linhas, ordem de severidade e a pergunta de confirmação.
- `mvc-guidelines.md` — responsabilidades de config, model, controller, rota, erro e entry point, com layout Python e Node e a regra para projeto que já tem camadas.
- `refactor-playbook.md` — 10 transformações com antes/depois em Python e JavaScript.

O catálogo cobre o que a análise manual encontrou nos três projetos: God Class, segredo hardcoded, SQL injection, dado sensível, regra na rota, estado global, hash fraco, N+1, validação duplicada, API obsoleta, duplicação, efeito incompleto, magic number e nome opaco. A skill não lista os bugs deste repositório; lista sinais (`execute` com string concatenada, `datetime.utcnow`, `pk_live_`). Por isso o mesmo texto serve para Flask e Express.

A Fase 2 grava o relatório e para. Nesta entrega, a confirmação da Fase 3 foi a aprovação do plano de execução do desafio. O `SKILL.md` continua exigindo `y` em invocações futuras.

Decisões de adaptação:

- Projeto sem camadas ganha `config/`, `models/`, `controllers/`, `views/` ou `routes/` e `middlewares/`.
- Projeto com blueprints mantém os blueprints e ganha controllers. As rotas ficam finas.
- `python app.py` e `npm start` continuam sendo o entry point.
- O contrato de sucesso dos endpoints permanece. SQL arbitrário, senha na resposta e token falso não permanecem.

Dificuldade principal: o projeto 3 parece organizado e mesmo assim concentra regra nas rotas. A guideline de "não desmontar o que já funciona" evita reescrever models e blueprints do zero, e o catálogo ainda marca N+1, MD5 e API obsoleta.

## Resultados

A Fase 2 rodou sobre o código original. A Fase 3 foi confirmada na aprovação do plano de execução. Os relatórios completos estão em `reports/`.

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
| --- | --- | --- | --- | --- | --- |
| code-smells-project | 4 | 2 | 2 | 2 | 10 |
| ecommerce-api-legacy | 3 | 2 | 3 | 2 | 10 |
| task-manager-api | 1 | 2 | 3 | 2 | 8 |

Os três passaram do mínimo: stack correta, pelo menos 5 findings, pelo menos um CRITICAL ou HIGH, e a aplicação respondeu depois da refatoração. API obsoleta apareceu no Express (`sqlite3.verbose()`) e no task manager (`datetime.utcnow`, `Query.get`). O e-commerce Flask não usava essas APIs; o relatório registra a ausência.

### Antes e depois

code-smells-project, de 4 arquivos sem camada:

```text
app.py
config/settings.py
models/          database, produto, usuario, pedido, passwords
controllers/     produto, usuario, pedido, sistema
views/routes.py
middlewares/error_handler.py
```

ecommerce-api-legacy, de `AppManager` + `utils`:

```text
src/app.js
src/config/settings.js
src/models/      db, passwords
src/controllers/ checkout, report, user
src/routes/
src/middlewares/errorHandler.js
```

task-manager-api manteve models, routes e services, e ganhou:

```text
config/settings.py
controllers/     task, user, report, category
middlewares/error_handler.py
routes/category_routes.py
```

As rotas do task manager ficaram só com o encaminhamento. Senha saiu do JSON, o token falso saiu do login e o MD5 virou PBKDF2.

### Checklist de validação

Fase 1 — Análise

- [x] Linguagem detectada nos 3 projetos (Python, JavaScript, Python)
- [x] Framework detectado (Flask 3.1.1 no e-commerce; Express 4 no LMS; Flask no task manager, pin 3.0.0 no requirements e 3.1.1 no `.venv`)
- [x] Domínio descrito (e-commerce, LMS com checkout, task manager)
- [x] Arquivos analisados: 4, 3 e 15

Fase 2 — Auditoria

- [x] Relatórios seguem o template (`reports/audit-project-1.md`, `2`, `3`)
- [x] Cada finding tem arquivo e linhas do código original
- [x] Findings ordenados de CRITICAL a LOW
- [x] Mínimo de 5 findings em cada projeto (10, 10 e 8)
- [x] API obsoleta registrada onde existia; no projeto 1, nenhuma ocorrência
- [x] A skill pede confirmação antes da Fase 3; nesta entrega o `y` foi a aprovação do plano

Fase 3 — Refatoração

- [x] Diretórios no padrão MVC, com adaptação no projeto que já tinha blueprints
- [x] Config em módulo próprio, com `.env.example` e sem segredo no fonte
- [x] Models abstraem os dados e usam SQL parametrizado
- [x] Rotas só encaminham
- [x] Controllers concentram o fluxo
- [x] Error handler único em cada projeto
- [x] Entry point único (`python app.py` e `npm start`)
- [x] As três aplicações subiram sem traceback
- [x] Endpoints originais responderam

### Logs de boot

code-smells-project (`python app.py`):

```text
SERVIDOR INICIADO
Rodando em http://localhost:5000
 * Running on http://127.0.0.1:5000
GET /health -> {"status":"ok","database":"connected","counts":{"produtos":10,"usuarios":3,"pedidos":0},"versao":"1.0.0"}
GET /produtos -> 10 itens
POST /login admin@loja.com -> Login OK, tipo admin
```

ecommerce-api-legacy (`npm start`):

```text
Frankenstein LMS rodando na porta 3000...
POST /api/checkout (cartão 4...) -> 200 {"msg":"Sucesso","enrollment_id":2}
POST /api/checkout (cartão 5...) -> 400 Pagamento recusado
GET /api/admin/financial-report -> Clean Architecture revenue 997; Docker revenue 497
DELETE /api/users/1 -> 200 Usuário deletado e registros relacionados removidos.
```

task-manager-api (`python seed.py` e `python app.py`):

```text
Seed concluído com sucesso!
  3 usuários
  4 categorias
  10 tasks
 * Running on http://127.0.0.1:5000
GET /health -> status ok
GET /tasks -> 10
POST /login joao@email.com -> Login realizado com sucesso, role admin, sem campo password
```

### Stacks diferentes

A mesma skill serviu para os três porque o catálogo fala de sinais (`execute` com concatenação, `SECRET_KEY` literal, `datetime.utcnow`), não de um arquivo deste repositório. No monolito Flask a Fase 3 criou as pastas. No Express a Fase 3 trocou callback aninhado por `async/await` e um `JOIN`. No task manager a Fase 3 não apagou `models/` nem os blueprints: só esvaziou as rotas e corrigiu senha, N+1 e API obsoleta. O contrato HTTP de sucesso ficou; SQL arbitrário, senha na resposta e token falso não ficaram.

## Como Executar

Pré-requisitos: Python 3.11+ (testado com 3.13), Node.js 18+, Git e Cursor. O ambiente virtual fica na raiz do repositório. Os pins de Flask dos dois projetos divergem (`3.1.1` e `3.0.0`); o `.venv` único usa o conjunto compatível mais novo (Flask 3.1.1, flask-cors 5.0.1, flask-sqlalchemy 3.1.1, marshmallow, requests, python-dotenv). Os `requirements.txt` originais não foram alterados por causa disso.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install flask==3.1.1 flask-cors==5.0.1 flask-sqlalchemy==3.1.1 marshmallow==3.20.1 requests==2.31.0 python-dotenv==1.0.0
cd ecommerce-api-legacy
npm install
```

No Cursor, abra a pasta do projeto e peça a execução da skill `refactor-arch`. Equivale ao `claude "/refactor-arch"` do enunciado. A skill pede confirmação antes de editar arquivos.

Ordem sugerida:

```text
code-smells-project
ecommerce-api-legacy
task-manager-api
```

Os dois Flask usam a porta 5000. Encerre um antes de subir o outro. O Express usa a porta 3000.

Validar o e-commerce Flask:

```powershell
cd code-smells-project
..\.venv\Scripts\python.exe app.py
```

`GET http://localhost:5000/health`, `GET /produtos` e `POST /login` com `admin@loja.com` / `admin123`.

Validar o LMS:

```powershell
cd ecommerce-api-legacy
npm start
```

Repetir os quatro chamados de `api.http` (checkout aprovado, checkout recusado, relatório, delete).

Validar o task manager:

```powershell
cd task-manager-api
..\.venv\Scripts\python.exe seed.py
..\.venv\Scripts\python.exe app.py
```

`GET http://localhost:5000/health`, `GET /tasks` e `POST /login` com `joao@email.com` / `1234`.
