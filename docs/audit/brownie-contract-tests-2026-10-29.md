# Auditoria de testes Solidity/Brownie — 29/10/2026

## Ambiente reproduzível

- Repositório: `enoqueJonas/mono-backend`.
- Branch de auditoria: `audit/chain-db-consistency-recovery`, PR #14.
- Linguagem/compilação: Solidity 0.8.20, EVM Istanbul.
- Ferramentas: Python 3.10, Brownie 1.21.0, Ganache 7.9.2.
- Workflow: `.github/workflows/brownie-contracts.yml`.
- Execução comprovada: [GitHub Actions run 40878468432](https://github.com/enoqueJonas/mono-backend/actions/runs/40878468432).

## Comando

```bash
cd smart_contracts
brownie test -s --network development tests/
```

## Resultados

**14 testes aprovados, zero falhas**, execução de 2,28 segundos (tempo reportado para a suite após inicialização).

| Contrato | Casos abrangidos |
|---|---|
| `ContributionRegistry` | Registo/consulta de hash de contribuição; rejeição de duplicação |
| `CredentialRegistry` | Registo/consulta de hash; rejeição de hash duplicado; revogação e rejeição de segunda revogação |
| `GroupRegistry` | Ancoragem e versionamento de parâmetros; duplicação proibida; diferentes grupos; versões e hashes inválidos |

## Histórico de aprendizagem da execução

- O primeiro CI falhou a inicialização porque o compilador Solidity fixado
  não estava disponível no runner. Instalou-se o binário nativo de 0.8.20.
- A execução seguinte com `ganache-cli` 6.12.2 teve **7 falhas e 7 aprovações**
  porque a resposta RPC de revert incluía simultaneamente `error` e
  `result`, incompatível com Web3/Brownie instalado. Esta é evidência de
  incompatibilidade do ambiente de testes, não de uma vulnerabilidade
  demonstrada no contrato.
- Após usar Ganache 7.9.2, o mesmo conjunto passou **14/14**.

## O que estes resultados sustentam

Os três contratos implementam as regras testadas em **blockchain local
controlada**, incluindo integridade de parâmetros e de hashes ancorados,
unicidade de identificadores e registo de revogação.

## O que não sustentam

- Redução medida da taxa de fraude nos grupos de xitique.
- Identificação real de quem originou contribuições móveis.
- Escalabilidade, custos em rede pública, governação distribuída
  ou auditoria formal externa de contratos.
- Protecção contra abuso de chaves administrativas e/ou do emissor
  fora dos casos concretos incluídos na suite.

A monografia deve apresentar os testes como **evidência experimental técnica
em ambiente de laboratório**, distinguindo-os de efeitos socioeconómicos.
