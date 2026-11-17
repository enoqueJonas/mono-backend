# Desembolsos — implementação fiel aos diagramas A.4 e A.8
Data: 17/11/2026. Ramo base: feat/rn06-independent-disbursement-approval, PR #26 (DRAFT, não em master).

## Divergência real entre diagramas
- A.4: gestor confirma → PSP transfere → PSP confirma → ancoragem blockchain → rotação concluída.
- A.8: blockchain confirma hash antes de iniciar pagamento → PSP confirma → desembolso/registo e rotação.
- Ambos apresentam PSP, mas nenhum contrato ou serviço de desembolso actual executa pagamentos reais.
- Não é cientificamente válido afirmar que ambos os diagramas são a implementação efectiva.

## Decisão de modelação
RN06 proposta → votos elegíveis (dois distintos e maioria estrita) → **autorizar** → ancorar hash da autorização → solicitar payout à entidade de pagamentos → receber/verificar recibo do prestador → ancorar hash do recibo → marcar pagamento liquidado → concluir ciclo/rotação.

Estados necessários: AWAITING_CONSENSUS, APPROVED, AUTHORIZATION_ANCHOR_PENDING, AUTHORIZATION_ANCHORED, PAYOUT_REQUESTED, PAYOUT_PROCESSING, PAYOUT_FAILED, PAID_PENDING_ANCHOR, COMPLETED. Não marcar COMPLETED em resposta à simples aprovação. Requer migrações e compatibilidade com os estados actuais.

## Entrega desta primeira etapa (código)
- `smart_contracts/contracts/DisbursementRegistry.sol`: `recordAuthorization`, `recordSettlement`, leitura dos dois hashes e datas, guardião de operador, impossibilidade de liquidação sem autorização ancorada ou duplicação.
- `smart_contracts/tests/test_disbursement_registry.py`: cenários positivos e negativos Brownie, ainda não executados neste commit.
- Este contrato **não transfere fundos** e a ancoragem do hash não prova, por si, que houve pagamento. A confirmação depende de integração efectiva com prestador verificado.
- O contrato está integrado no script de deploy, dispõe de ABI no backend, configuração `DISBURSEMENT_REGISTRY_ADDRESS` e cliente Web3.py com guardião de operador, mas **ainda não está ligado aos serviços de desembolso Django nem ao frontend**. É uma base para o sistema de provas, **não implementação completa de A.4/A.8**. As suites Brownie/Django ainda não foram executadas nesta intervenção.

## Gates para considerar a funcionalidade implementada
1. **Feito no código:** contrato, deploy, ABI, settings e cliente Web3. **Pendente:** ligar ao fluxo Django com migrações e intents/outbox, testes integrados e recuperação após erro entre SQL e Ganache.
2. Implementar adaptador PSP real com credenciais válidas, autorização explícita, idempotency key e consulta de estado final, ou manter modo *simulação* rotulado que **não marca pagamento liquidado**.
3. Não confirmar transferência apenas com resposta HTTP 200; validar referência do PSP, montante, moeda, beneficiário, assinatura de webhook, estado definitivo e reconciliação.
4. Testar payout falhado, repetição do webhook, timeout após envio incerto, confirmação tardia, payload adulterado, mudança de beneficiário, dinheiro debitado sem confirmação SQL, falha após confirmação de PSP antes de ancorar, e falha na ancoragem depois da liquidação.
5. Actualizar simultaneamente A.4 e A.8 para uma ordem única; manter os originais históricos intactos como fontes.
6. Só actualizar os resultados/hipóteses da monografia depois de teste executado com evidência reprodutível. Não atribuir prova de integração PSP real a Ganache ou mocks.
