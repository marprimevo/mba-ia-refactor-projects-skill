# Architecture Audit Report

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```text
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~784 lines of code

## Summary
CRITICAL: 4 | HIGH: 2 | MEDIUM: 2 | LOW: 2
Deprecated APIs: nenhuma ocorrência no código

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-315
Description: Um único módulo executa SQL, regra de estoque, desconto e formatação de produtos, usuários, pedidos e relatório.
Impact: Impossível testar um domínio sem carregar os outros quatro. Qualquer alteração no SQL de produto passa pelo mesmo arquivo do checkout.
Recommendation: Separar models e controllers por domínio (playbook 3).

### [CRITICAL] SQL injection
File: models.py:28-299
Description: Queries de produto, usuário, login, pedido, status e busca concatenam id, nome, e-mail, senha e termo de busca na string SQL (`"WHERE id = " + str(id)`, `"email = '" + email + "'"`).
Impact: O cliente controla a query. Login e `/produtos/busca` são os vetores mais diretos de leitura e escrita.
Recommendation: Placeholders `?` com parâmetros ligados (playbook 1).

### [CRITICAL] Hardcoded credentials
File: app.py:7
Description: `SECRET_KEY` está fixa como `minha-chave-super-secreta-123`.
Impact: O segredo fica no repositório e não muda entre ambientes.
Recommendation: Ler `SECRET_KEY` do ambiente (playbook 2).

### [CRITICAL] Exposição de dado sensível
File: controllers.py:276-290
Description: `GET /health` devolve `secret_key`, `debug` e `db_path`. `models.py:75-88` inclui `senha` na listagem de usuários, e `database.py:75-83` grava senha em texto puro no seed.
Impact: Quem chama `/health` ou `/usuarios` recebe segredo e senha. O hash não existe.
Recommendation: Hash com salt (playbook 8), DTO público sem senha (playbook 10) e health sem segredo.

### [HIGH] Estado global mutável
File: database.py:4-10
Description: `db_connection` é um singleton de módulo, aberto com `check_same_thread=False`.
Impact: Requests compartilham a mesma conexão SQLite. O estado de transação de um request vaza para o outro.
Recommendation: Conexão em `flask.g`, fechada no teardown (playbook 4).

### [HIGH] Efeito destrutivo sem autenticação
File: app.py:47-78
Description: `POST /admin/reset-db` apaga as quatro tabelas e `POST /admin/query` executa o SQL enviado no body, ambos sem credencial.
Impact: Qualquer cliente zera a loja ou lê a tabela de senhas.
Recommendation: Reset permanece como operação explícita de desenvolvimento. A query arbitrária deixa de executar e responde 403 (playbook 1 e 2).

### [MEDIUM] Query N+1
File: models.py:174-230
Description: `get_pedidos_usuario` e `get_todos_pedidos` buscam itens por pedido e, para cada item, o nome do produto.
Impact: O número de queries cresce com pedidos e itens. O relatório de vendas repete cinco `COUNT` separados no mesmo arquivo (`models.py:239-254`).
Recommendation: Um `JOIN` (ou um agregado) e agrupamento em memória (playbook 5).

### [MEDIUM] Validação e erro duplicados
File: controllers.py:31-92
Description: Criar e atualizar produto repetem as mesmas checagens de nome, preço, estoque e categoria. Cada função copia o mesmo `try/except` que devolve `str(e)`.
Impact: A regra diverge entre POST e PUT, e o erro interno vaza detalhe do banco.
Recommendation: Uma função de validação e um error handler único (playbook 6).

### [LOW] Magic number
File: models.py:257-262
Description: O desconto usa os limiares `10000`, `5000`, `1000` e as taxas `0.1`, `0.05`, `0.02` sem nome.
Impact: A política comercial não é distinguível de um número solto.
Recommendation: Constantes `DISCOUNT_TIERS` (playbook 9).

### [LOW] Nome opaco ou debug barulhento
File: controllers.py:208-210
Description: Criar pedido faz `print` de e-mail, SMS e push. Outros `print` de fluxo estão em `controllers.py:8` e `controllers.py:179-182`.
Impact: Efeito colateral no stdout no lugar de um ponto de extensão, e dado de usuário no log.
Recommendation: Remover o debug. Notificação, se existir, fica atrás de um serviço chamado pelo controller.

================================
Total: 10 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
Confirmação concedida na aprovação do plano de execução do desafio.
```
