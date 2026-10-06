# Architecture Audit Report

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript
Framework:     Express ^4.18.2
Dependencies:  sqlite3
Domain:        LMS API com fluxo de checkout (usuários, cursos, matrículas, pagamentos)
Architecture:  Monolítica — God Class AppManager registra rotas, schema e pagamento
Source files:  3 files analyzed
DB tables:     users, courses, enrollments, payments, audit_logs
================================
```

```text
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript + Express
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 3 | LOW: 2

## Findings

### [CRITICAL] God Class / God Method
File: src/AppManager.js:4-139
Description: A classe abre o SQLite, cria as cinco tabelas, registra checkout, relatório e delete, e decide se o pagamento foi aprovado.
Impact: Não há model nem controller. O relatório e o delete mudam junto com o checkout.
Recommendation: Separar models, controllers e routes (playbook 3).

### [CRITICAL] Hardcoded credentials
File: src/utils.js:1-6
Description: `dbUser`, `dbPass` (`senha_super_secreta_prod_123`) e `paymentGatewayKey` (`pk_live_1234567890abcdef`) estão no fonte, junto com o usuário SMTP.
Impact: Segredo de produção versionado. A chave é usada no log do checkout.
Recommendation: Ler do ambiente e não registrar a chave (playbook 2).

### [CRITICAL] Exposição de dado sensível
File: src/AppManager.js:45
Description: `console.log` imprime o número do cartão (`cc`) e `config.paymentGatewayKey`.
Impact: PAN e credencial do gateway vazam no stdout do processo.
Recommendation: Não logar PAN nem chave (playbook 10).

### [HIGH] Estado global mutável
File: src/utils.js:9-14
Description: `globalCache` e `totalRevenue` são variáveis de módulo. `logAndCache` grava o último checkout nesse objeto e o exporta.
Impact: Requests compartilham cache sem dono e sem limite.
Recommendation: Não exportar estado mutável de módulo (playbook 4). O checkout não precisa desse cache para responder.

### [HIGH] Criptografia fraca e regra na rota
File: src/utils.js:17-23
Description: `badCrypto` concatena dois caracteres de base64 dez mil vezes e devolve 10 caracteres. `src/AppManager.js:28-77` aplica essa função e a regra do cartão (`startsWith("4")`) dentro do handler HTTP.
Impact: A senha é previsível. A rota não é testável sem o Express e o driver.
Recommendation: `scrypt` com salt (playbook 8) e caso de uso no controller (playbook 3).

### [MEDIUM] Query N+1
File: src/AppManager.js:80-128
Description: O relatório percorre cursos, depois matrículas de cada curso, depois usuário e pagamento de cada matrícula, com callbacks aninhados.
Impact: Quatro níveis de I/O e uma query por linha. Um curso sem matrícula ainda entra no fluxo de contagem manual.
Recommendation: Um `LEFT JOIN` e agrupamento em memória (playbook 5).

### [MEDIUM] Efeito colateral incompleto
File: src/AppManager.js:131-136
Description: `DELETE /api/users/:id` apaga só `users`. A resposta admite que matrículas e pagamentos ficam no banco. O checkout (`src/AppManager.js:35`) só verifica presença dos campos.
Impact: Relatório financeiro continua somando pagamento de usuário removido. Entrada sem formato de e-mail ou cartão segue adiante.
Recommendation: Apagar pagamentos e matrículas na mesma operação (playbook 6).

### [MEDIUM] API obsoleta
File: src/AppManager.js:1
Description: `require('sqlite3').verbose()` liga stack trace de debug do driver no entry point da aplicação.
Impact: Caminho de biblioteca pensado para diagnóstico fica ativo o tempo todo.
Recommendation: `require('sqlite3')` (playbook 7).

### [LOW] Nome opaco
File: src/AppManager.js:29-33
Description: O body do checkout é lido em `u`, `e`, `p`, `cid` e `cc`.
Impact: Nome, e-mail, senha, curso e cartão não se distinguem na leitura da função.
Recommendation: Nomes de domínio no controller (`name`, `email`, `courseId`, `card`).

### [LOW] Magic number
File: src/utils.js:19
Description: O laço de hash usa `10000` iterações e `substring(0, 10)` sem nomear a política.
Impact: O número parece custo computacional e não adiciona entropia.
Recommendation: Trocar o algoritmo (playbook 8 e 9), em vez de nomear o laço.

================================
Total: 10 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
Confirmação concedida na aprovação do plano de execução do desafio.
```
