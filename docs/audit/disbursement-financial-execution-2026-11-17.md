# RN06 — Desembolso financeiro, ancoragem e o alcance das Figuras A.4/A.8

**Estado:** implementação experimental isolada na branch `feat/disbursement-payout-anchoring`. NÃO integrada em master, NÃO activada em produção.

## Divergência detectada nos desenhos originais
- **A.4 (actividades):** pagamento pelo operador -> confirmação -> hash/ancoragem -> rotação
- **A.8 (sequência):** hash/ancoragem -> pedido ao operador -> confirmação -> rotação

É impossível afirmar que ambas representam exactamente a mesma sequência de eventos com uma única ancoragem. **Decisão de modelação:** duas provas distintas, imutáveis, com identificador idempotente comum:
1. **INTENT**: proposta RN06 aprovada, identidades elegíveis, valor, moeda, beneficiário e referência única. Ancorar antes de pedir transferência.
2. **SETTLEMENT**: confirmação consultada junto ao fornecedor, referência da transacção, valor e moeda. Ancorar após obter prova verificável de resultado financeiro.
3. Só após SETTLEMENT pode ocorrer **conclusão administrativa** e avanço de rotação.

## Invariantes
- RN06 permanece obrigatório; proponente e beneficiário não votam; quórum >= 2.
- Proposta aprovada ≠ dinheiro transferido. Resposta inicial HTTP ≠ liquidação confirmada.
- Nunca repetir um B2C perante timeout ou resposta ambígua sem consultar referência junto ao operador (evitar **pagamento duplo**).
- Se a transferência foi concluída mas a ancoragem falhou, não voltar a transferir; deixar `SETTLEMENT_PENDING_ANCHOR` e reconciliar depois.
- Só uma operação de pagamento por desembolso, com referência de negócio única.
- Hashes on-chain não contêm número de telefone, nome ou saldo em claro.
- Falha do operador não conclui o desembolso nem avança a rotação.
- A conta Ethereum é centralizada; a blockchain comprova integridade dos bytes, **não** veracidade de liquidação bancária.
- Comprovativos de pagamento só são considerados se obtidos por canal autenticado do operador e conferidos quanto a referência, beneficiário, montante e moeda.

## Integração operacional pendente
Vodacom Moçambique anuncia API M-Pesa B2C, mas activar exige acordo, credenciais e configuração próprias. A disponibilidade da API **não** constitui autorização para transferir fundos. E-Mola depende de contrato/documentação do fornecedor. Nunca criar pagamentos reais usando números fictícios ou credenciais de demonstração.

## Validação exigida
- Testar contrato Brownie: só operador, duas provas, rejeição de duplicados/settlement sem intent.
- Testar API com PostgreSQL/Ganache e provedor sandbox autorizado: proposta, dois votos, intent, transferência, confirmação, settlement, avanço de rotação.
- Testar atraso, falha, timeout, prova adulterada, dupla submissão, falha de ancoragem depois da transferência, comparação de referências e recuperação.
- Só depois alinhar as Figuras A.4/A.8 ao processo **efectivamente implementado**. Não adulterar automaticamente figuras históricas.

**Fontes externas:** https://www.vm.co.mz/m-pesa/artigo/api-aberta-do-m-pesa e https://developer.mpesa.vm.co.mz/documentation/
