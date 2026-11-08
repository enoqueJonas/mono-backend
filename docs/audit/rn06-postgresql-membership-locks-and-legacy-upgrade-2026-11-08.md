# RN06 — Concorrência de filiação e migração de dados antigos

**Data:** 8 de Novembro de 2026  
**Objectivo:** verificar a sincronização de entradas/saídas de membros com a decisão de desembolso sem inventar uma política de contribuições ou redistribuição de fundos.

## 1. Defeito reproduzido antes do patch

Teste PostgreSQL com duas conexões/transacções reais: a transacção A detém `SELECT FOR UPDATE` do registo `Group` durante uma verificação RN06; a transacção B chama `GroupService.remove_member()`.

No commit `eb787db2ea883e7cb92f9cf64a9862a6d8f2c662`, a suite PostgreSQL/Ganache falhou exactamente com:

`RN06MembershipLockingTests.test_leave_cannot_change_membership_during_group_ledger_snapshot` → `AssertionError: Membership operation completed while RN06 group lock was held`.

**Resultado inicial:** **1 failed, 6 passed**. Não foi apenas uma hipótese por leitura de código: o fluxo de saída foi efectivamente executado enquanto a transacção de verificação mantinha o bloqueio do grupo.

## 2. Correcção técnica

`groups/services/group_service.py`:
- `add_member` passou a usar `@transaction.atomic` e `Group.objects.select_for_update().get(...)`, antes de calcular vagas/decidir reactivar um membro `LEFT`.
- `remove_member`, já transaccional, passou a bloquear **o mesmo registo do grupo** antes de alterar `GroupMember.status`.
- A validação financeira RN06 em `DisbursementService.create()` já bloqueava a linha de `Group`; no método `complete()`, a consulta `select_for_update().select_related("group", ...)` participa no mesmo domínio de bloqueios.

Regra de implementação: operações de filiação têm de passar pelos serviços que adquirem o lock do grupo; os novos testes detectam regressões se essa barreira for removida.

## 3. Testes de concorrência verificados

`integration_tests/test_rn06_membership_concurrency.py` utiliza `TransactionTestCase`, duas conexões reais e `ThreadPoolExecutor` para testar:

1. A entrada de um novo membro não termina enquanto a validação RN06 mantém o lock.
2. A saída de um membro não altera o estado enquanto a mesma linha do grupo está bloqueada.
3. A readmissão `LEFT → ACTIVE` respeita o lock.

**Evidência de CI após correcção:** commit `64c6d85c1ba21e6e9582edbb36c98af6d7bf144c`, teste PostgreSQL/Ganache **8/8 aprovados** (incluindo três testes de concorrência, além dos cinco testes anteriores), no workflow `VC Ganache integration`. A suite Brownie e a suite Django são workflows separados.

### Limites

- Esta verificação prova **serialização das operações de filiação testadas através de `GroupService`**, não isolamento global serializável de todo o PostgreSQL.
- SQL directo, `QuerySet.update()`, scripts manuais, futuros serviços de suspensão, ou escritores não coordenados podem contornar o lock do grupo.
- A existência de contribuição de ex-membro continua a bloquear o desembolso; nenhuma política financeira foi definida para esse dinheiro.
- Ainda falta um snapshot imutável dos contribuintes obrigados no início do ciclo e regras de entrada/saída adoptadas pelo grupo.

## 4. Migração real de registo histórico

`integration_tests/probe_rn06_legacy_migration.py` opera **somente** no PostgreSQL CI descartável. Sequência:

1. Aplicar migrações completas; reverter apenas `disbursements` a `0001_initial`.
2. Criar utilizadores, grupo, beneficiário e um desembolso histórico `APPROVED`, **sem os campos RN06**.
3. Aplicar `0002_independent_approvals`.
4. Comprovar que a linha anterior mantém montante e estado histórico, mas recebe `proposed_by = NULL` e `eligible_approver_ids = []`.
5. Tentar concluir via `DisbursementService.complete()`: rejeição obrigatória por quórum insuficiente. A rotação não avança.

**Evidência de CI:** `RN06_LEGACY_UPGRADE_OK PostgreSQL schema=0001->0002 old_approved_record_untrusted=True rotation_not_advanced=True` no commit `64c6d85c1ba21e6e9582edbb36c98af6d7bf144c`.

Não se convertem aprovações antigas sem prova em votos efectivos.

## 5. Bloqueios remanescentes

- Definir política de participantes obrigados no início de cada ciclo e destino de fundos de ex-membros (issue #28).
- Criar trilho transaccional/auditável de alteração de filiação e cobrir escritores que não usem `GroupService`, incluindo suspensão.
- Ensaiar concorrência real de `complete()` versus alteração de contribuições em PostgreSQL, não apenas filiação; confirmar ordem de locks e evitar deadlocks.
- Confirmar que a CI do frontend PR #1 corre contra o **head exacto** deste ramo, conforme gate de SHA.
- Não apresentar `COMPLETED` como comprovativo de transferência bancária/e-Mola/M-Pesa.

**Conclusão:** regressão de concorrência reproduzida e corrigida; migração do esquema antigo demonstrada como fail-closed. A política financeira de saída ainda não está resolvida e a issue #28 não deve ser fechada.
