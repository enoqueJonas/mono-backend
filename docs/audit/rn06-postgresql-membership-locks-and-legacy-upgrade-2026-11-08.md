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

## 4. Inserções concorrentes de contribuições — regressão adicional

Na suite PostgreSQL real, foram acrescentados dois testes contra a mesma linha bloqueada de `Group`:

- `test_manual_contribution_cannot_be_inserted_during_group_snapshot`;
- `test_simulated_wallet_contribution_cannot_be_inserted_during_group_snapshot`.

Os testes invocam `ContributionService.register_manual_contribution()` e `ContributionService.register_mobile_wallet_contribution()` com transacções distintas. A chamada externa de `ContributionAnchorService` é isolada com Mock **apenas nestes dois testes de concorrência SQL**, pois o objectivo é provar bloqueio de escritas, não comportamento de rede. Os outros testes da workflow exercitam Ganache real.

**Reprodução antes da correcção:** commit `117c2cf1dba4933b4aa6bcd8c1da996bcc543e6d`: **2 failed, 8 passed**. Ambos os registos conseguiam terminar apesar de a verificação RN06 manter o lock de grupo. Isso podia introduzir uma contribuição não presente no snapshot financeiro da proposta.

**Correcção:** o serviço de contribuições agora obtém `Group.objects.select_for_update()` no início de cada operação transaccional, antes de ler configurações, validar membro ou inserir contribuição. Alinha a ordem de acesso com os serviços RN06.

**Evidência pós-correcção:** commit `28bbcaef0f98739f4be78745afef4f5eed57833e`: **10/10 PostgreSQL/Ganache**, **148/148 Django**, workflow Brownie `success`. O teste de migração histórica também permaneceu verde.

**Risco operacional introduzido/acentuado:** as rotinas de contribuições ainda executam `ContributionAnchorService().anchor()` dentro de `transaction.atomic`. Por isso, uma chamada RPC demorada mantém a linha `Group` bloqueada e pode atrasar outras operações de filiação e desembolso. Além disso, a ancoragem Ethereum e o commit PostgreSQL não são uma única transacção distribuída. A solução de produção requer fluxo em duas fases ou intent/outbox durável com reconciliação idempotente e telemetria. **Isto não foi implementado nesta correcção.**

## 5. Migração real de registo histórico

`integration_tests/probe_rn06_legacy_migration.py` opera **somente** no PostgreSQL CI descartável. Sequência:

1. Aplicar migrações completas; reverter apenas `disbursements` a `0001_initial`.
2. Criar utilizadores, grupo, beneficiário e um desembolso histórico `APPROVED`, **sem os campos RN06**.
3. Aplicar `0002_independent_approvals`.
4. Comprovar que a linha anterior mantém montante e estado histórico, mas recebe `proposed_by = NULL` e `eligible_approver_ids = []`.
5. Tentar concluir via `DisbursementService.complete()`: rejeição obrigatória por quórum insuficiente. A rotação não avança.

**Evidência de CI:** `RN06_LEGACY_UPGRADE_OK PostgreSQL schema=0001->0002 old_approved_record_untrusted=True rotation_not_advanced=True` no commit `64c6d85c1ba21e6e9582edbb36c98af6d7bf144c`.

Não se convertem aprovações antigas sem prova em votos efectivos.

## 6. Bloqueios remanescentes

- Definir política de participantes obrigados no início de cada ciclo e destino de fundos de ex-membros (issue #28).
- Criar trilho transaccional/auditável de alteração de filiação e cobrir escritores que não usem `GroupService`, incluindo suspensão.
- Cobrir alterações de estado de contribuições (reversão/confirmar) por qualquer escritor e ensaiar `complete()` concorrente; confirmar a ordem de locks e ausência de deadlocks.
- Remover chamadas RPC blockchain de dentro de transacções SQL longas, usando intent/outbox e reconciliação; medir espera no bloqueio de grupo.
- Confirmar que a CI do frontend PR #1 corre contra o **head exacto** deste ramo, conforme gate de SHA.
- Não apresentar `COMPLETED` como comprovativo de transferência bancária/e-Mola/M-Pesa.

**Conclusão:** regressões de concorrência de filiação e inserção de contribuições reproduzidas e corrigidas nos serviços testados; migração do esquema antigo demonstrada como fail-closed. A política financeira de saída ainda não está resolvida e a issue #28 não deve ser fechada.
