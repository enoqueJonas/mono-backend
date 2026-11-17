# Decisão de arquitectura — desembolso sem custódia pela plataforma
Data: 17/11/2026
Estado: proposta implementada em branch de trabalho; não integrada na master

## Regra fundamental
Mono é um sistema de **governança, registo e auditoria** do Xitique. Não detém
fundos nem tem autorização para debitar a carteira móvel pessoal do gestor/tesoureiro.

O dinheiro dos participantes é depositado numa **carteira móvel externa
designada pelo grupo**. O titular da carteira opera fora do Mono, através da
sua aplicação/USSD habitual. `M-Pesa` ou `e-Mola` são canais de pagamento,
não recursos automaticamente controlados pela plataforma.

## Quem movimenta o dinheiro?
1. Um gestor designa explicitamente como responsável um **membro activo**
   com papel `MANAGER` ou `TREASURER`, identificando prestador e número.
2. A aplicação regista essa designação como **declaração**, não como
   verificação de titularidade bancária; não valida o saldo externo.
3. Ao criar a proposta de desembolso, congela-se o responsável, prestador e
   número de origem; os votos RN06 (maioria estrita e mínimo 2) aprovam o
   **desembolso proposto**, não libertam dinheiro na carteira externa.
4. Após aprovação, o responsável faz manualmente a transferência para o
   beneficiário **fora da plataforma**.
5. Esse responsável declara o valor fixo da proposta, a referência do
   pagamento e o número destinatário, sem modificar o montante autorizado.
6. Beneficiário valida pessoalmente e confirma a recepção; uma contestação
   bloqueia a rotação e aguarda tratamento de conflito.
7. A rotação avança apenas depois dessa confirmação. O estado
   `COMPLETED` representa **recepção declarada pelo beneficiário**,
   e não confirmação independente de liquidação pelo prestador.

## Estados
`AWAITING_CONSENSUS` → `APPROVED` →
`PAYMENT_REPORTED` → `COMPLETED`

Ramo de divergência: `PAYMENT_REPORTED` → `DISPUTED` (sem avanço automático).

Todos os APIs e serviços novos estão sob
`NONCUSTODIAL_WALLET_FLOW_ENABLED` (desligado por defeito).
A rota administrativa antiga `complete/` é BLOQUEADA quando activada.

## Confronto com sandbox do PR #35
A sandbox de pagamentos do PR #35 permite que o sistema debite uma carteira
virtual `GROUP` e credite `MEMBER`. Trata-se de **um outro modelo de
execução**, útil para testar integração com um possível prestador, mas que
NÃO corresponde automaticamente à arquitectura sem custódia adoptada aqui.

Não é correcto considerar uma transferência na sandbox como prova de
transferência M-Pesa/e-Mola na realidade. Nem como prova de que Mono pode
debitar a conta pessoal de alguém.

## Limites antifraude
- O responsável pode transferir fundos da sua própria carteira fora da
  autorização RN06; a aplicação não consegue tecnicamente bloquear isso.
- Uma referência introduzida pelo responsável pode ser falsa ou atribuída
  a outra transacção; o número destinatário é declarado e só sujeito à
  revisão humana do beneficiário.
- Uma confirmação por JWT é uma **declaração de conta de utilizador**,
  não assinatura electrónica verificada de prestador financeiro.
- Nem a blockchain, nem os hashes de eventos, provam que fundos externos
  tenham sido realmente transferidos.
- Beneficiário e responsável podem conluiar-se; a detecção exige reconciliação
  ou evidência independente do prestador.
- O processo de contestação entra em `DISPUTED`; o procedimento
  administrativo de resolução não está implementado nesta etapa.

## Blockchain — distinção de prova
O código desta etapa implementa relatórios/confirmação humana em SQL
**sem novas ancoragens blockchain do desembolso**. Não chamar a esses
registos `settlement` ou `pagamento verificado`.
A etapa blockchain posterior deve ancorar **(a)** autorização RN06 e
**(b)** conteúdo assinado/autenticado da declaração do responsável e da
confirmação do beneficiário, com semântica inequívoca de *declarações*.
Nunca usar nomes/eventos como `PaymentSettled` sem validação do PSP.

## Diagramas de actividade e sequência
Conservar os originais que o autor escolheu. **Não foram alterados**.
Na actividade, adicionar raias «Membros Elegíveis» e «Responsável pela
Carteira Móvel» e transições declaração/confirmação. A «Carteira Móvel»
é o canal externo, NÃO uma API invocada pelo Sistema.
Na sequência, NÃO desenhar `Sistema -> API da Carteira Móvel:
processarPagamento()` para este modelo; desenhar o responsável a
efectuar manualmente a transferência, a comunicar referência ao Sistema,
e o beneficiário a confirmar ou contestar. A ancoragem precisa de seguir
os eventos que forem efectivamente integrados e demonstrados em testes.

## Evidência de testes
`disbursements/test_noncustodial_wallet.py`: restrições de custódia,
quórum, idempotência da referência, actores autorizados, confirmação,
bloqueio de conclusão administrativa e contestação. CI a verificar.
