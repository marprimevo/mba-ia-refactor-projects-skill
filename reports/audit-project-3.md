# Architecture Audit Report

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.0.0 (requirements) — runtime do ambiente único: Flask 3.1.1
Dependencies:  flask-sqlalchemy, flask-cors, marshmallow, requests, python-dotenv
Domain:        Task Manager API (tasks, usuários, categorias, relatórios)
Architecture:  Camadas parciais — models, routes, services e utils; sem controllers; regra de negócio nas rotas
Source files:  15 files analyzed
DB tables:     users, tasks, categories
================================
```

```text
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask
Files:   15 analyzed | ~970 lines of code

## Summary
CRITICAL: 1 | HIGH: 2 | MEDIUM: 3 | LOW: 2

## Findings

### [CRITICAL] Criptografia fraca e exposição de senha
File: models/user.py:16-32
Description: `to_dict` inclui `password`. `set_password` grava `hashlib.md5` sem salt. Criação, detalhe e login devolvem esse valor.
Impact: A senha sai na API e o MD5 sem salt é reversível com tabela pré-calculada.
Recommendation: PBKDF2 com salt e DTO sem o campo `password` (playbook 8 e 10).

### [HIGH] Hardcoded credentials
File: app.py:11-13
Description: `SECRET_KEY` é `super-secret-key-123` e a URI do banco está no entry point. `services/notification_service.py:6-10` fixa usuário e senha SMTP (`senha123`).
Impact: Segredo de sessão e de e-mail no repositório, misturado com o bootstrap.
Recommendation: Módulo `config/settings.py` lendo ambiente (playbook 2).

### [HIGH] Regra de negócio na borda HTTP
File: routes/user_routes.py:186-211
Description: O login monta a política de autenticação na rota e devolve `token: fake-jwt-token-` + id. `routes/task_routes.py` e `routes/report_routes.py` calculam atraso, validam título e disparam queries.
Impact: O token é forjável. Não existe controller para testar o caso de uso sem o Flask.
Recommendation: Controller fino, rota só encaminha, token falso removido (playbook 3 e 10).

### [MEDIUM] Query N+1
File: routes/task_routes.py:26-55
Description: A listagem percorre tasks e chama `User.query.get` e `Category.query.get` por item. `routes/report_routes.py:53-68` busca as tasks de cada usuário. `routes/report_routes.py:157-164` conta tasks por categoria em loop.
Impact: A listagem e o relatório disparam uma query por relacionamento.
Recommendation: `joinedload` / `selectinload` e um `GROUP BY` (playbook 5).

### [MEDIUM] Duplicação de código
File: routes/task_routes.py:31-38
Description: A regra de tarefa atrasada está copiada em `routes/task_routes.py`, `routes/user_routes.py:172`, `routes/report_routes.py:35` e `models/task.py:50-60`. Os limites `3`, `200` e `4` também reaparecem nas rotas, embora `utils/helpers.py:110-116` já declare constantes.
Impact: Um ajuste no critério de atraso ou no tamanho do título precisa ser repetido em vários arquivos.
Recommendation: `Task.is_overdue()` e as constantes do helper (playbook 6 e 9).

### [MEDIUM] API obsoleta
File: models/user.py:14
Description: `datetime.utcnow` é o default das colunas e aparece em models, rotas, `services/notification_service.py:35`, `utils/helpers.py:38` e `seed.py`. As rotas usam `Model.query.get` (`routes/user_routes.py:29`, `routes/task_routes.py:42`, `routes/report_routes.py:105`).
Impact: `utcnow` está obsoleto no Python 3.12. `Query.get` é a API legada do SQLAlchemy 2.
Recommendation: `datetime.now(timezone.utc)` e `db.session.get` (playbook 7).

### [LOW] Magic number
File: routes/task_routes.py:105-127
Description: Título mínimo `3`, máximo `200` e senha mínima `4` em `routes/user_routes.py:64` repetem números que já têm nome em `utils/helpers.py`.
Impact: A regra de validação não aponta para a constante.
Recommendation: Usar `MIN_TITLE_LENGTH`, `MAX_TITLE_LENGTH` e `MIN_PASSWORD_LENGTH` (playbook 9).

### [LOW] Nome opaco ou debug barulhento
File: routes/task_routes.py:60
Description: `except:` sem tipo engole qualquer erro, inclusive de programação. `app.py:7` importa `os`, `sys` e `json` sem uso. Há `print` de criação e falha nas rotas.
Impact: Falha vira 500 genérico sem rastreio, e o entry point mente sobre as dependências.
Recommendation: Capturar `Exception` no handler central e tirar import morto.

================================
Total: 8 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
Confirmação concedida na aprovação do plano de execução do desafio.
```
