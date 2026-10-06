# Template do relatório de auditoria

A Fase 2 produz um markdown com o resumo da Fase 1 e os findings. Não altere a ordem das seções. Findings ordenados por severidade e, na mesma severidade, pelo caminho do arquivo.

```markdown
# Architecture Audit Report

================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework>
Dependencies:  <deps>
Domain:        <domínio>
Architecture:  <arquitetura atual>
Source files:  <N> files analyzed
DB tables:     <tabelas>
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome da pasta>
Stack:   <linguagem> + <framework>
Files:   <N> analyzed | ~<linhas> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [<SEVERIDADE>] <título curto do catálogo>
File: <caminho relativo>:<linha inicial>-<linha final>
Description: <o que o código faz>
Impact: <por que importa>
Recommendation: <qual padrão do playbook aplicar>

================================
Total: <n> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> <y ou n, e quem confirmou>
```

Regras:

- `File:` usa caminho relativo à raiz do projeto auditado, com linhas inclusivas (`app.py:7` se for uma linha só, `models.py:1-315` se for um bloco).
- A descrição cita o sinal do catálogo, não um julgamento vago ("código ruim").
- Se não houver API obsoleta, acrescente uma linha em Summary: `Deprecated APIs: nenhuma ocorrência no código`.
- Se houver, cada ocorrência é um finding MEDIUM "API obsoleta", a menos que o catálogo já a classifique de outro jeito.
- O relatório descreve o código **antes** da Fase 3. Não atualize as linhas depois da refatoração.
- Confirmação: sem `y` explícito, a skill não segue para a Fase 3.
