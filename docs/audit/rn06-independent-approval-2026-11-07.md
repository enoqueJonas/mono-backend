# RN06 — aprovação multiparticipante de desembolsos (proposta experimental)

## Fundamento

A RN06 antiga chamava "consenso" à aprovação de um único gestor. A alteração neste ramo introduz **aprovação multiutilizador na camada Django**: são votos de contas autenticadas, **não assinaturas digitais autónomas** de chaves controladas pelos membros e **não consenso da rede Ethereum**.

## Política aplicada
1. Só gestor activo pode propor desembolso. A proposta usa a rotação e as contribuições confirmadas do período.
2. O estado inicial é sempre `AWAITING_CONSENSUS`, mesmo para configurações históricas com `requires_consensus=False`. Novas configurações e actualizações com `False` são rejeitadas.
3. São elegíveis apenas membros activos do grupo, **excluindo proponente e beneficiário**. A lista de IDs de utilizadores elegíveis é capturada na proposta. Membros adicionados depois não recebem autorização para votar nesta proposta.
4. O limiar é maioria estrita dos elegíveis, nunca menos de duas pessoas: `max(2, floor(N/2)+1)`. Grupo com menos de dois elegíveis não pode propor a operação automaticamente, evitando simular quórum.
5. Cada utilizador pode votar uma única vez; uma restrição de unicidade na base de dados impede duplicados. O registo é uma aprovação da aplicação associada à conta autenticada.
6. `APPROVED` só é alcançado após atingir o limiar, e `complete` volta a contar os votos válidos de membros ainda activos. Registos legados `APPROVED` sem evidência de votos ficam bloqueados.
7. Apenas um gestor activo pode marcar a operação como `COMPLETED`; este estado **não** transfere dinheiro nem valida uma liquidação financeira externa.

## Exemplo
Grupo com gestor proponente, beneficiário e duas outras pessoas activas: o gestor e o beneficiário são excluídos; as duas outras pessoas têm de aprovar. Uma só aprovação mantém `AWAITING_CONSENSUS`.

## Riscos residuais e limitações
- A aplicação centraliza autenticação e armazenamento de aprovações; um operador privilegiado com acesso à base de dados continua a ser um actor de confiança. Os votos não são assinados com chaves detidas exclusivamente pelos membros nem ancorados on-chain.
- Não existe carteira de fundos, liquidação automática, nem integração real com M-Pesa/e-Mola. Uma transferência externa por tesoureiro desonesto não é bloqueada pelo software.
- Membros fictícios previamente admitidos podem contornar a independência pretendida; exige verificação de identidade e regras comunitárias de admissão.
- O direito de impugnar/rejeitar, cancelamento do pedido, política de emergência, recuperação de acesso, alterações na rotação, votação de alterações de regras e limiares alternativos para grupos pequenos ainda não foram implementados.
- Alterações no PostgreSQL por um administrador da infra-estrutura não são detectadas por ancoragem do hash de desembolso, que ainda não existe.
- Uma alteração de estado de um membro após a aprovação pode fazer perder o quórum e bloquear a conclusão. A política de substituição de aprovações necessita de especificação posterior.

## Testes e gates
`disbursements/test_independent_quorum.py` cobre situações de bypass, votação repetida, fraude por inclusão tardia de membros, falta de quórum, elegibilidade, suspensão e impedimento de concluir um registo legado sem votos. Os testes preexistentes de desembolso/penalização foram adaptados.

**A implementação não deve ser descrita como demonstrada na monografia até a CI, as migrações e o fluxo de API serem verificados num único commit.**

Antes de aprovar o PR:
- [ ] `python manage.py makemigrations --check --dry-run` e `python manage.py migrate` sobre uma base de dados de teste.
- [ ] `python -m pytest -q`, testes específicos e o cenário Ganache/PostgreSQL.
- [ ] Confirmar que a autorização real permanece coerente com os PRs #11, #13, #14 e #22.
- [ ] Ensaio de API com quatro membros e dois logins independentes.
- [ ] Rever a interface: ela ainda permite escolher `requires_consensus`; a opção "desactivar" deve ser eliminada ou explicitamente bloqueada.
- [ ] Planeamento para dados históricos em `APPROVED` com votos ausentes: nunca converter silenciosamente esses registos em aprovados com quórum.
- [ ] Avaliar se 2–3 membros e diferentes papéis precisam de assinatura de terceiro independente, sob pena de bloqueio explícito.
