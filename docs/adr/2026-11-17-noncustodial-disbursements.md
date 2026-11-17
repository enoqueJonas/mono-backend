# ADR 2026-11-17 — Desembolsos do Xitique sem custódia de fundos

**Decisão arquitectural:** o Mono não mantém fundos do Xitique, não detém PIN/credenciais de carteira móvel, não ordena a transferência a partir da carteira do tesoureiro e não se apresenta como prestador financeiro. O grupo escolhe um titular responsável por uma carteira externa; no protótipo, a **nomeação é registada pelo gestor**. A transferência é executada fora do Mono pelo titular, que depois declara a referência da operação.

**Âmbito do experimento:** a RN06 autoriza a decisão; a blockchain ancora hashes das declarações. Isto comprova integridade do **registo na aplicação**, não liquidação real num prestador financeiro nem impossibilidade de furto na carteira externa.

## Actores
- **Gestor**: propõe o desembolso, nomeia responsável externo, pede a ancoragem de autorização e, depois da confirmação do beneficiário, a ancoragem final.
- **Membros elegíveis**: emitem votos na aplicação, cada voto associado à sua conta; o proponente e o beneficiário não votam; maioria estrita dos elegíveis e pelo menos duas aprovações.
- **Responsável pela carteira externa**: pessoa designada pertencente ao grupo; recebe a instrução, transfere independentemente do Mono, declara a referência da operação. A função não altera automaticamente o seu perfil de membro.
- **Beneficiário**: consulta a declaração e responde se recebeu ou não o montante; em caso negativo justifica a contestação.
- **Blockchain**: guarda o hash da autorização e separadamente o hash da declaração de recepção do beneficiário, sem identificar este segundo evento como liquidação comprovada.

## Sequência
1. **Antes da proposta**, o gestor designa o responsável por uma carteira externa; o sistema exige que seja um membro activo diferente do beneficiário. Não existe votação colectiva específica sobre essa designação.
2. Criar a proposta conforme a rotação e contribuições (`AWAITING_CONSENSUS`), com o responsável já definido e visível aos membros.
3. Votos RN06 até `APPROVED`.
4. O gestor pede ancoragem da autorização. O hash contém proposta, participantes da votação e identificação/atributos do mandato de custódia. Confirmada a transacção EVM, o estado passa a `AWAITING_PAYMENT`.
5. O titular realiza, **fora da aplicação**, a transferência a partir da sua carteira externa; o Mono não chama APIs M-Pesa/e-Mola.
6. O titular declara a referência; o Mono regista o valor e moeda imutavelmente a partir da proposta, e passa a `AWAITING_CONFIRMATION`.
7. O beneficiário confirma a recepção (`EVIDENCE_PENDING`) ou contesta com justificação (`DISPUTED`).
8. Em caso positivo, o gestor ancora um hash etiquetado `SELF_REPORTED_EXTERNAL_PAYMENT` ligado à referência e às identidades das contas de declaração/recepção.
9. Após confirmação da ancoragem, o processo é `COMPLETED` e a rotação avança. O sistema **não pode afirmar confirmação por PSP**.

## API, modelo e flags
- `POST/GET /api/v1/groups/{group_id}/treasury-mandate/` — nomeação e consulta da carteira externa (identificador abreviado, sem PIN).
- `POST .../disbursements/{id}/open-external/` — requer gestor, RN06 e ancoragem autorizativa.
- `POST .../disbursements/{id}/report-external/` — requer titular designado; regista referência, não movimenta fundos.
- `POST .../disbursements/{id}/acknowledge-external/` — requer beneficiário; `received=true/false` e `dispute_reason` na negativa.
- `POST .../disbursements/{id}/finalize-external/` — requer gestor e confirmação positiva; ancora prova e avança rotação.
- `NON_CUSTODIAL_DISBURSEMENTS_ENABLED=true` habilita as novas operações.
- `SANDBOX_PAYMENTS_ENABLED=false` impede o antigo pagamento automático de laboratório.
- `ALLOW_LEGACY_ADMINISTRATIVE_COMPLETION=false` impede concluir pela rota administrativa histórica. O modo de teste antigo apenas é permitido no `config.settings_test` para preservar cenários unitários legados.
- UI: `NEXT_PUBLIC_NON_CUSTODIAL_DISBURSEMENTS_ENABLED=true`, desactiva botões antigos, apresenta o titular designado antes dos votos e oferece as novas acções.
- É obrigatório implantar uma versão **nova** do `DisbursementRegistry` com `recordBeneficiaryAcknowledgment`; um contrato já implantado não ganha esse método automaticamente.

## Evidência da implementação experimental
- Testes de serviço/API: `disbursements/test_noncustodial_workflow.py`.
- Contrato e operador: `smart_contracts/tests/test_disbursement_registry.py`.
- PostgreSQL + Ganache reais: `integration_tests/test_noncustodial_disbursement_ganache.py`, que inclui duas operações de ancoragem, ausência de débito pelo Mono e recuperação após resposta EVM perdida **depois de mineração**.
- PR backend: https://github.com/enoqueJonas/mono-backend/pull/38
- PR frontend: https://github.com/enoqueJonas/mono-frontend/pull/6
- Os PRs são *draft* e empilhados sobre os fluxos RN06 anteriores. Diagramas e monografia NÃO foram alterados.

## Limitações críticas, **não ocultar**
1. **Dinheiro fora do controlo do Mono**: a RN06 não pode bloquear transferências que o titular faça directamente no M-Pesa/e-Mola; isto é controlo de decisão, não custódia nem garantia de fundos.
2. A referência declarada **não é validada com o prestador**. A confirmação do beneficiário é uma declaração de utilizador, não uma confirmação financeira independente. O conluio continua possível.
3. O gestor nomeia o titular **sem voto colectivo específico sobre o mandato de custódia**; não afirmar que houve aprovação RN06 deste mandato. Um protocolo de nomeação/substituição é evolução futura.
4. Quando titular e beneficiário são a **mesma pessoa**, este fluxo bloqueia a **criação da proposta**: falta uma política de testemunha/retensão independente. Não existe ainda uma forma de substituir o titular depois da nomeação.
5. Contestação `DISPUTED` fica bloqueada para resolução externa; ainda não existe um processo formal de arbitragem, correcção ou segunda confirmação.
6. A assinatura dos votos/declarações é a autenticação da aplicação (JWT). Não são assinaturas criptográficas individuais guardadas pelo membro.
7. A prova EVM resiste à alteração do histórico da cadeia, mas não garante que uma declaração falsa nunca foi apresentada nem que o operador da aplicação é honesto.
8. A recuperação de **timeout após transacção minerada** foi testada. Falta um outbox durável específico para tentativas ambíguas **ainda não mineradas**, com política de bloqueio de rebroadcast e reconciliação explícita.
9. O caminho de contribuição manual conserva as limitações do registo contabilístico existente; não prova dinheiro depositado numa carteira externa.

## Regras para documentação científica
- Empregar «desembolso declarado», «recebimento confirmado pelo beneficiário», «evidência ancorada» e «execução externa».
- NÃO afirmar «pagamento efectuado pelo Mono», «transferência automática M-Pesa», «liquidação validada pelo operador» ou «prevenção de fraude externa garantida».
- A Figura A.4 deve mostrar a transferência iniciada pelo titular fora do Mono e os dois registos blockchain separados.
- A Figura A.8 deve mostrar claramente as mensagens dos membros RN06, titular e beneficiário; sem mensagem de API da carteira móvel iniciada pelo Mono.
- O utilizador fará manualmente os diagramas. Nenhuma alteração à monografia está autorizada nesta etapa.
