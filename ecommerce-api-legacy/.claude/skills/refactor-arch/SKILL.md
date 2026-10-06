---
name: refactor-arch
description: >-
  Analisa, audita e refatora um backend para o padrão MVC, independente da
  linguagem ou do framework. Use quando o usuário pedir refactor-arch,
  /refactor-arch, auditoria arquitetural, anti-patterns ou refatoração MVC.
disable-model-invocation: true
---

# refactor-arch

Skill agnóstica de tecnologia para analisar um backend, auditar anti-patterns e refatorar para MVC. Não assuma Python, Flask, Node ou Express: detecte a stack na Fase 1 e aplique só os exemplos da stack encontrada.

Execute as fases em ordem. Não edite código de aplicação antes da confirmação da Fase 2. Arquivos desta skill (`.cursor/`, `.claude/`) não são código de aplicação.

## Fase 1 — Análise

Leia [project-analysis.md](project-analysis.md) e siga as heurísticas.

Imprima o resumo neste formato, com valores reais do projeto:

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework e versão, se houver>
Dependencies:  <dependências de runtime relevantes>
Domain:        <domínio em uma linha>
Architecture:  <como as responsabilidades estão organizadas hoje>
Source files:  <N> files analyzed
DB tables:     <tabelas ou "nenhuma">
================================
```

Conte apenas arquivos de aplicação. Ignore `.cursor/`, `.claude/`, `node_modules/`, `.venv/`, `reports/` e bancos gerados.

## Fase 2 — Auditoria

Leia [anti-patterns.md](anti-patterns.md) e [audit-report-template.md](audit-report-template.md).

1. Percorra o código de aplicação e registre cada anti-pattern com arquivo e linhas exatas.
2. Classifique com a escala do catálogo. Inclua APIs obsoletas quando o código as usar.
3. Ordene CRITICAL, HIGH, MEDIUM, LOW.
4. Grave o relatório em markdown. Se o usuário indicar o caminho (por exemplo `reports/audit-project-1.md` na raiz do repositório do desafio), use esse caminho. Caso contrário, grave `reports/audit-<nome-do-projeto>.md` na raiz do repositório analisado.
5. Imprima o relatório.
6. Pare. Pergunte: `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`
7. Não crie, edite ou apague arquivos de aplicação até receber confirmação explícita (`y`, `sim` ou equivalente). Se a resposta for `n`, encerre.

## Fase 3 — Refatoração

Só depois da confirmação. Leia [mvc-guidelines.md](mvc-guidelines.md) e [refactor-playbook.md](refactor-playbook.md).

1. Escolha o layout MVC da stack detectada. Se o projeto já tem models, routes ou services, afine essas camadas e acrescente o que falta. Não jogue fora uma separação que já funciona.
2. Aplique um padrão do playbook para cada finding corrigível. Preserve rotas, métodos HTTP e o formato de sucesso das respostas. Correções de segurança mudam o comportamento perigoso: SQL arbitrário deixa de executar, segredos e senhas saem das respostas, senhas deixam de ficar em texto puro ou MD5.
3. Extraia configuração para módulo de config lendo variáveis de ambiente. Entregue `.env.example` sem segredos reais. A aplicação deve subir com os defaults de desenvolvimento documentados.
4. Centralize o tratamento de erro. Deixe um entry point único (`app.py` ou `src/app.js`).
5. Apague os arquivos legados que a nova estrutura substituiu, para não conviver God Class com MVC.

### Validação

A Fase 3 só termina quando os dois checks passarem:

- A aplicação inicia sem traceback e sem erro de import.
- Os endpoints originais respondem (health, listagem e o fluxo principal do domínio).

Python: suba `python app.py` e chame os endpoints. Node: suba `npm start` e chame os endpoints do `api.http`, se existir. Encerre o processo ao terminar. Se a validação falhar, corrija e rode de novo.

Imprima:

```text
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore MVC resultante>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

Se algum anti-pattern do catálogo permanecer de propósito, não marque o terceiro item. Corrija ou registre o que ficou e por quê.
