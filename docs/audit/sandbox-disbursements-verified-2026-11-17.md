# Laboratório de pagamentos fictícios do Xitique — 17/11/2026

## Âmbito e regras de segurança
Esta integração **NÃO movimenta dinheiro real** e não chama M-Pesa, e-Mola ou outro PSP. O simulador em `wallets` é um livro-razão SQL isolado logicamente, dentro do backend do protótipo. Um crédito gerado pelo webhook representa apenas um **pagamento simulado**. `ISSUER` é a conta criadora de saldos fictícios, podendo ter saldo negativo por desenho, mas grupos e membros não podem gastar além do saldo.

O modelo imita *comportamentos* de um prestador (saldo, débito, crédito, idempotência e falhas), mas não é uma sandbox certificada por operador financeiro. A própria aplicação controla o simulador, logo a prova não é independente.

## Percurso implementado

1. Criar um grupo, membros e ciclo. Configurar contribuição fixa e moeda no Django.
2. Iniciar uma rede Ganache descartável; implantar `ContributionRegistry`, `DisbursementRegistry` e restantes contratos, usando a conta operadora definida no backend.
3. Activar **explicitamente** num ambiente de testes:
   - `SANDBOX_PAYMENTS_ENABLED=true`;
   - `MOBILE_WALLET_WEBHOOK_ENABLED=true`;
   - `MOBILE_WALLET_WEBHOOK_SECRET=<segredo apenas de testes>`;
   - `DISBURSEMENT_REGISTRY_ADDRESS=<endereço no Ganache>`;
   - `CONTRIBUTION_REGISTRY_ADDRESS=<endereço no Ganache>`.
   Nunca publicar segredos, nem activar esta modalidade em produção.
4. Reproduzir os callbacks simulados de contribuição em `POST /api/v1/wallets/contributions/confirmation/`, assinados com o protocolo HMAC e cabeçalho temporal já presente em `wallets/views.py`.
5. Após persistência e ancoragem das contribuições, cada callback válido credita uma única vez o grupo na sandbox. **Contribuições manuais não criam saldo fictício no prestador.**
6. Gestor propõe desembolso; cada membro elegível aprova com JWT e quórum RN06 independente. Beneficiário e proponente não votam.
7. Gestor autenticado faz `POST /api/v1/groups/{groupId}/disbursements/{disbursementId}/sandbox-execute/`. O servidor:
   - valida RN06 e a correspondência das contribuições;
   - ancora hash determinístico da autorização no contrato `DisbursementRegistry`;
   - confere a prova no Ganache;
   - debita a conta fictícia do grupo e credita o membro numa transacção SQL com dois lançamentos;
   - ancora o hash do comprovativo virtual;
   - só então marca o desembolso concluído e avança a rotação.
8. Se a RPC falhar após o débito, o desembolso fica `PROCESSING`. Repetir o endpoint reconcilia pela prova on-chain e pela mesma referência idempotente, **sem novo débito**.

A rota administrativa anterior `/complete/` é bloqueada em modo sandbox para impedir passar directamente de `APPROVED` a `COMPLETED`.

## Evidência automática e limites da validação
- Django/SQLite: `wallets/test_sandbox_payments.py` testa dinheiro virtual, contabilidade equilibrada, replay, RN06, saldo insuficiente, divergência de hash e simulação de falha; a API com HMAC está também testada.
- Brownie/Ganache: `smart_contracts/tests/test_disbursement_registry.py` verifica autorização prévia, operador, imutabilidade dos dois registos e rejeições.
- PostgreSQL + Ganache reais: `integration_tests/test_sandbox_disbursement_ganache.py` ensaia o caminho completo e um timeout artificial **após a transacção EVM ter sido minerada**, verificando recuperação sem novo pagamento fictício.
- CI de integração confirmada verde: https://github.com/enoqueJonas/mono-backend/actions/runs/44057430809 (17/11/2026). Confirma testes de ambiente descartável, não pagamentos reais.
- UI: https://github.com/enoqueJonas/mono-frontend/pull/4 , com aviso visual «pagamentos fictícios», botão de execução e reconciliação, dependente da flag `NEXT_PUBLIC_SANDBOX_PAYMENTS_ENABLED=true`.

## Lacunas e controlos a não ocultar
- O simulador não comprova a existência de fundos fora da base de dados, a identidade civil, nem pagamentos ao mundo real.
- A RN06 é governança validada na API por contas JWT; os votos não têm assinaturas pessoais autónomas e o contrato não implementa governança multiparticipante.
- O simulador está dentro do backend; não fornece confiança independente contra um operador do servidor desonesto.
- Não há PSP externo, webhook **assíncrono de desembolso** ou reconciliação com conta bancária/operador real.
- O contrato conserva **hashes**, não os fundos. O mesmo operador controla as transacções EVM de teste.
- A eventual alteração da monografia deve usar evidência e termos exactos: *«execução de desembolso fictício num simulador próprio, com provas ancoradas numa rede Ganache local»*; não dizer *«liquidação financeira real»* nem *«redução de fraudes comprovada»*.
- As Figuras A.4 e A.8 históricas necessitam de harmonização: uma única ordem observada é **aprovação RN06 → ancoragem de autorização → débito/crédito fictício → ancoragem do resultado → conclusão/avanço da rotação**. Preservar originais para comparação, actualizar diagramas finais apenas de acordo com o fluxo testado.
- PRs de backend #26 e #35 e UI #4 permanecem em *draft* até revisão. A `master` não contém automaticamente esta integração.
