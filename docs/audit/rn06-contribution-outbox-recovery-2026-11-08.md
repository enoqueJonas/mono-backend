# RN06 — Intenções duráveis para ancoragem de contribuições

**Data:** 08/11/2026  
**Âmbito:** protótipo Django 6, PostgreSQL e Ganache 7.9.2. Não envolve pagamentos reais nem rede blockchain pública.  
**Issue:** [#31](https://github.com/enoqueJonas/mono-backend/issues/31).

## 1. Falha original e alteração

Anteriormente `ContributionService.register_manual_contribution()` e
`register_mobile_wallet_contribution()` guardavam a contribuição, chamavam
`ContributionAnchorService().anchor()` e esperavam a transacção EVM **dentro**
de `@transaction.atomic`, já com `Group.select_for_update()`. Uma RPC lenta
mantinha o bloqueio de grupo; uma transacção minerada antes de falha do commit
PostgreSQL deixava ancoragem sem registo local recuperável nesse caminho.

O fluxo revisto é:

```text
Recepção de contribuição manual / callback sintético autenticado
    |
    +-- Transacção SQL curta: bloqueia Group, valida, persiste
    |   Contribution(CONFIRMED) + ContributionAnchorIntent(PENDING, hash)
    +-- COMMIT SQL; liberta bloqueio de Group
    |
    +-- on_commit tenta ancorar/reconciliar (RPC fora da transacção SQL)
    |   +-- lê getContribution do contrato
    |   +-- ainda não ancorada -> submete registerContribution
    |   +-- já ancorada -> compara hash e recupera ContributionAnchored/evento
    |
    +-- transacção SQL curta: BlockchainAnchor + intent CONFIRMED
         |
         +-- falha transitória -> mantém intent PENDING para retry
         +-- hash divergente -> REVIEW_REQUIRED, sem reenvio cego
```

**Atenção:** o callback `on_commit` ocorre na mesma requisição/processo
Django; liberta o bloqueio SQL antes da RPC, mas **não garante baixa latência
HTTP**. Se o processo morrer depois do commit e antes do callback, a intenção
SQL continua recuperável por comando explícito. Não existe ainda worker de
fundo/scheduler operacional nem outbox de mensagens assíncrono.

## 2. Modelo de dados e idempotência

- `ContributionAnchorIntent` tem uma relação `OneToOne` com a contribuição
  e o SHA-256 congelado do documento inicial. Estados: `PENDING`,
  `PROCESSING`, `CONFIRMED`, `REVIEW_REQUIRED`.
- O serviço toma um lease temporário em SQL e liberta-o antes da chamada RPC.
  Erros transitórios voltam a `PENDING` com **nome de classe do erro**,
  sem guardar mensagens RPC potencialmente sensíveis.
- Ao reprocessar, consulta primeiro o estado do contrato. Se a contribuição
  estiver ancorada com o mesmo hash, recupera o recibo do evento
  `ContributionAnchored` sem enviar outra transacção.
- O vínculo `BlockchainAnchor` e `ContributionAnchorIntent` não são
  transacção única; se falhar a última confirmação, outra tentativa reconcilia.
- Divergência de hash local/intenção ou on-chain/intenção implica
  `REVIEW_REQUIRED` e bloqueio automático, não substituição dos dados on-chain.
- A resposta REST expõe `status` (registo financeiro **simulado**/manual)
  e `anchoring_status` separadamente. Para linhas antigas sem intenção usa
  `UNTRACKED_LEGACY`; não é prova retroactiva.
- A RN06 rejeita novos desembolsos ou conclusão de votos quando uma
  contribuição desse ciclo possui intenção que não esteja `CONFIRMED`.
  Linhas históricas sem intenção não recebem provas inventadas; a sua
  política de importação e auditoria ainda precisa ser estabelecida.

## 3. Recuperação explícita

Para ambiente de **teste** com chaves e contratos de teste:

```bash
python manage.py reconcile_contribution_anchors --limit 100
```

O comando tenta `PENDING` e leases `PROCESSING` expirados, e reporta o
número confirmado, pendente e em revisão. Não deve ser executado contra
produção sem gestão de chave e nós apropriada. A reexecução não interpreta
`PENDING` como falha financeira nem converte automaticamente pagamentos
em `CONFIRMED`.

## 4. Provas executadas

### Django — 166 testes aprovados

GitHub Actions de backend inclui testes para intenção criada antes de RPC,
quorum RN06 bloqueado por intenção pendente, retry idempotente, falha RPC,
hash incompatível e dados inválidos. `makemigrations --check --dry-run`
também passa com a nova migração `contributions/0006`.

### PostgreSQL/Ganache — 15 testes aprovados

Quinze testes numa workflow: **sete com Ganache real** (cinco cenários de credenciais/registos e dois de recuperação de contribuição) e **oito testes PostgreSQL de concorrência e operação com RPC simulada** (bloqueios de filiação e contribuições, operador EVM e execução controlada do worker). A migração histórica `disbursements/0001 → 0002` é uma
verificação separada dentro da mesma workflow.

O ensaio de recuperação de contribuição confirma:
- `registerContribution` é executado fora de `transaction.atomic`.
- Ganache minera a ancoragem da contribuição sintética.
- Falha artificial ao inserir o recibo no PostgreSQL deixa o intent
  `PENDING`, sem apagar a contribuição.
- Nova tentativa consulta `getContribution`, obtém o evento e escreve
  o recibo original; **não** cria um segundo bloco nem retransmite.
- Novo retry de intent `CONFIRMED` é um no-op.

O ensaio de latência com RPC simulada confirma que uma nova adesão pode
adquirir lock de `Group` enquanto o outro pedido espera pelo RPC
pós-commit, sem o bloquear.

### Brownie — 18 testes aprovados

Os contratos GroupRegistry, ContributionRegistry e CredentialRegistry
continuam com a suite independente em verde. Brownie não testa as
interfaces financeiras externas.

## 5. Limitações / critérios ainda abertos da issue #31

1. **Operação do retry:** o comando é manual; falta orquestração/scheduler,
   monitorização e alertas para `PENDING`, `PROCESSING` expirados e
   `REVIEW_REQUIRED`.
2. **Leases e nonces EVM:** tarefas longas podem exceder o lease de dez
   minutos e causar tentativas concorrentes. O contrato rejeita duplicação
   mas isso pode custar gas; não há gestor centralizado de nonces nem fila de
   signatário provada sob carga.
3. **Reorganização da rede:** uma leitura do contrato/eventos no Ganache
   não prova finalização em rede pública nem resistência a reorgs.
   O protótipo procura eventos a partir do bloco zero, inviável em escala.
4. **Pagamento externo:** `Contribution.status=CONFIRMED` em lançamento
   manual ou callback **simulado** não significa liquidação verificada por
   M-Pesa, e-Mola ou banco; o hash comprova integridade do registo original,
   não veracidade da origem.
5. **Política dos ex-membros (#28):** o snapshot do início do ciclo e
   destino de contribuições de membros que saem estão indefinidos.
6. **Escritas não coordenadas:** alterações directas no PostgreSQL e
   futuros endpoints que não adoptem os serviços testados não são
   automaticamente serializadas com RN06.
7. **Outras ancoragens:** `GroupAnchorService` continua síncrono no
   fluxo de criação/alteração de grupo e deve receber auditoria própria;
   esta implementação altera apenas contribuições.
8. **Backend centralizado (#29):** as chaves DID/EVM e os votos continuam
   controlados pela aplicação, não por carteiras autocustodiadas de membros.

**Conclusão:** os resultados sustentam uma melhoria de disponibilidade
durante RPC e de recuperabilidade após falhas de persistência, em ambiente
experimental. Não validam prevenção de fraude financeira operacional.


## 6. Operação controlada e resultados de envio incertos — 8/11/2026

A segunda revisão evita o erro de transformar um timeout numa autorização para voltar a transmitir. Se `registerContribution` falhar **durante ou depois do envio**, o resultado pode ser desconhecido. O serviço converte-o em `ContributionAnchorSubmissionUncertain`, marca `REVIEW_REQUIRED` e **não** faz nova submissão automática. Se o worker terminar enquanto um intento se encontra `PROCESSING`, a retomada após expiração do lease consulta a blockchain em modo **apenas reconciliação** (`allow_submit=False`), não assume que a ausência temporária no estado confirmado significa inexistência no mempool.

O processamento de contribuições utiliza um `pg_try_advisory_lock` de sessão PostgreSQL, derivado do identificador de rede e endereço de conta operadora. Isto serializa **workers de ancoragem de contribuições que utilizem o mesmo PostgreSQL e esta implementação**, sem reter `Group.select_for_update` durante a operação RPC. O bloqueio é não bloqueante: quando outro processo o detém, a intenção não é modificada e pode ser retomada mais tarde. A regra não abrange automaticamente ancoragens de grupos ou credenciais, nem serviços ligados a outra base de dados.

As falhas com resultado certamente não confirmado são espaçadas com *backoff* exponencial a partir de 15 segundos até ao máximo de uma hora. Após **seis tentativas**, o intento fica em `REVIEW_REQUIRED`; não existe loop infinito de reenvios. O estado e a próxima tentativa elegível são persistidos em `ContributionAnchorIntent.next_attempt_at`, introduzido pela migração `contributions/0007_contribution_intent_retry_schedule.py`.

### Comandos disponíveis (ambiente experimental)

```bash
# Inspecção de saúde sem assinatura e sem qualquer transmissão Ethereum.
python manage.py reconcile_contribution_anchors --dry-run --fail-on-review

# Uma passagem limitada de intents elegíveis.
python manage.py reconcile_contribution_anchors --limit 25

# Processamento em ciclos finitos, explicitamente autorizado pelo operador.
CONTRIBUTION_ANCHOR_WORKER_ENABLED=1 \
python manage.py reconcile_contribution_anchors --cycles 12 --poll-seconds 30 --limit 25 --fail-on-review

# Apenas verificar se transacções QUARENTENADAS já foram mineradas;
# NÃO submete novas transacções.
python manage.py reconcile_contribution_anchors --review-only --limit 25
```

O comando emite contadores `outstanding_pending`, `outstanding_processing`, `outstanding_review`, `total_confirmed` e `oldest_pending_seconds` para integração futura com monitorização. A execução por vários ciclos exige explicitamente PostgreSQL e `CONTRIBUTION_ANCHOR_WORKER_ENABLED=1`, e termina depois do número finito de ciclos. **Não foi instalado nem activado um serviço de fundo**, um cron de produção, um scheduler em nuvem ou qualquer automação com chaves reais.

### Evidência suplementar

- **166/166 testes Django:** intenções, recuperação, limites de tentativas, diagnóstico `--dry-run`, revisão sem broadcast, leases expirados e isolamento dos estados de pagamento/ancoragem.
- **15/15 na workflow PostgreSQL/Ganache:** sete com Ganache real e oito de testes PostgreSQL de concorrência/execução controlada com RPC isolada. A migração histórica é ensaio adicional em etapa distinta do workflow.
- **18/18 Brownie:** contratos Solidity em testes independentes.
- **Nova prova de falha ambígua real em Ganache:** `CONTRIBUTION_UNCERTAIN_SEND_E2E mined_then_timeout=True quarantined=True review_only_recovered=True second_broadcast=False`. A transacção foi minerada, o cliente lançou um timeout artificial depois da mineração; o processo não retransmitiu até haver reconciliação explícita que recuperou o recibo original.
- **Prova do operador concorrente:** dois processos Django/PostgreSQL distintos não adquirem simultaneamente o mesmo advisory lock; o lock é libertado depois do processamento.

**Limitações:** não há supervisor operacional, alarmes entregues a responsáveis, gestão transversal de nonces com os fluxos de grupos e VCs, confirmação de finalidade de rede pública, integração M-Pesa/e-Mola, nem controlo de fundos. A aplicação mantém custódia centralizada das chaves (issue #29) e a política financeira de ex-membros permanece indefinida (issue #28). O PR continua em rascunho: estas melhorias laboratoriais não equivalem a aprovação de produção.
