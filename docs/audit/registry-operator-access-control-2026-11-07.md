# Auditoria de autorização on-chain — 07/11/2026

## Base e escopo
Continuação técnica de PR #14 (`audit/chain-db-consistency-recovery`). Esta alteração incide exclusivamente sobre os três contratos de ancoragem do protótipo em rede Ethereum/Ganache: `GroupRegistry`, `ContributionRegistry` e `CredentialRegistry`.

## Modelo de ameaça e limite
O contrato original aceitava escritas de qualquer endereço capaz de submeter transacções ao nó. Isto permitia ancoragens de terceiros e revogações não autorizadas no contrato de credenciais; o controlo Django existente no PR #14 não é uma defesa on-chain.

O novo `operator` de cada contrato é a conta que o implanta. As funções que alteram estado exigem `msg.sender == operator`; as consultas permanecem abertas. Testes de negação de acesso por outra conta foram adicionados, mantendo os testes funcionais para a conta operadora.

**Importante:** esta é uma restrição técnica à escrita no registo. Não é consenso entre membros de Xitique, multi-assinatura, separação efectiva entre operador e gestor, custódia de fundos, nem confirmação da ocorrência de pagamentos externos. O servidor continua a guardar a chave de assinatura EVM e a centralizar a submissão das operações.

## Integração e migração obrigatórias
- Contratos Solidity já implantados não recebem esta correcção automaticamente. É necessário compilar e implantar **novos contratos** no Ganache de teste, sincronizar ABIs/endereços e executar testes E2E.
- A conta `BLOCKCHAIN_ACCOUNT_ADDRESS`/chave respectiva deve corresponder à conta que implantou os contratos. O script `smart_contracts/scripts/deploy.py` utiliza `accounts[0]` em `development`. Se a conta do servidor for diferente, as escritas serão correctamente rejeitadas.
- Não reutilizar dados/endereços antigos sem procedimento explícito de migração; a alteração não copia históricos ancorados em contratos anteriores.
- Validar novo endpoint de revogação como gestor/membro no ramo PR #14 e o cenário integrado PostgreSQL/Ganache.
- Verificar que os três contratos rejeitam `accounts[1]` e permitem `accounts[0]`; confirmar ABI/bytecode e endereço de implantação.

## Evidência
Revisão estática do código e novos testes Brownie. Testes de runtime **não foram executados nesta sessão** (Brownie/Ganache/PostgreSQL indisponíveis no ambiente da auditoria). A revisão deve permanecer draft até execução CI e validação de implantação.

## Pendências fora do escopo
1. RN06 exige política de quórum independente por operação, identidade das pessoas aprovadoras, rastreabilidade de votos, bloqueio de alteração unilateral de política e rejeição de `complete()` sem limiar.
2. Documentar política de custódia das chaves Ed25519 e EVM, rotação, perda e comprometimento; gerar chaves DID no servidor e cifrá-las numa BD não equivale a SSI autocustodiada.
3. Impedir confirmação unilateral de pagamentos manuais sem evidência financeira independente e sem processo de contestação pelos membros; a ancoragem de hash não comprova que houve pagamento.
4. Reconciliar PRs #11 → #13 → #14 e #12 antes de considerar o `master` pronto.

## Critérios de fecho
- CI Brownie, Django e E2E Ganache aprovados no mesmo commit.
- Novo deploy em ambiente isolado, e demonstração de rejeição de escrita on-chain por conta não autorizada.
- Documentação académica classifica este mecanismo como controlo técnico de registo; nunca como consenso financeiro nem implantação de produção.
