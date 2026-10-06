# Análise de projeto

Use estes sinais para a Fase 1. Confirme com o conteúdo dos arquivos, não só com o nome da pasta.

## Linguagem

| Sinal | Linguagem |
| --- | --- |
| `requirements.txt`, `pyproject.toml` ou arquivos `.py` | Python |
| `package.json` e arquivos `.js` sem `tsconfig.json` | JavaScript (Node) |
| `package.json` e arquivos `.ts` | TypeScript |
| `go.mod` | Go |
| `pom.xml` ou `build.gradle` | Java |

Se houver mais de uma linguagem, a da aplicação (entry point) prevalece. Scripts soltos não mudam a stack.

## Framework

| Sinal | Framework |
| --- | --- |
| `flask` em `requirements.txt` ou `from flask import` | Flask. Versão: pin em `requirements.txt` (`flask==x.y.z`) |
| `express` em `dependencies` de `package.json` ou `require('express')` | Express. Versão: range do `package.json` |
| `fastapi` importado | FastAPI |
| `django` em requirements | Django |

Dependências de runtime relevantes: liste as que não são o próprio framework (por exemplo `flask-cors`, `sqlite3`, `flask-sqlalchemy`). Ignore dependências transitivas de lockfile, salvo se o código as importar.

## Banco de dados

| Sinal | Banco |
| --- | --- |
| `sqlite3`, `sqlite:///`, arquivo `.db`, `new sqlite3.Database` | SQLite |
| `psycopg`, `pg`, `postgres://` | PostgreSQL |
| `pymysql`, `mysql2` | MySQL |
| nenhum acesso a dados | nenhum |

Tabelas: extraia nomes de `CREATE TABLE`, `__tablename__` ou `db.Model`. Liste os nomes, não invente tabelas.

## Domínio

Leia, nesta ordem: README do projeto, caminhos das rotas, nomes de tabelas e funções públicas. Descreva o domínio em uma linha com os substantivos de negócio (`E-commerce API (produtos, pedidos, usuários)`, `LMS API com checkout`, `Task Manager API`).

## Arquitetura atual

Classifique o que o código faz hoje:

- **Monolito sem camadas:** rotas, SQL e regra de negócio no mesmo arquivo ou em poucos arquivos sem pasta de responsabilidade.
- **Camadas parciais:** existem `models/`, `routes/` ou `services/`, mas controllers estão ausentes, rotas contêm regra de negócio, ou config está hardcoded no entry point.
- **MVC:** `models/`, rotas/views e `controllers/` com responsabilidades separadas.

Anote também estado global (`global`, variável de módulo mutável exportada, singleton de conexão) e se existe middleware de erro.

## Contagem de arquivos

Conte arquivos-fonte da aplicação (`.py`, `.js`, `.ts`) excluindo:

- `.cursor/`, `.claude/`, `node_modules/`, `.venv/`, `venv/`, `__pycache__/`
- testes gerados, `reports/`, `instance/`, `*.db`
- `package-lock.json`

Não conte `requirements.txt` nem `package.json` como arquivo de código. Informe o número inteiro no resumo.
