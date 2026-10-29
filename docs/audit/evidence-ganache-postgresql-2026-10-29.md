# Relatório de evidências — PostgreSQL + Ganache, 29/10/2026

## Identificação

- Repositório: `enoqueJonas/mono-backend`.
- Branch: `fix/authorize-vc-revocation-and-wallet-simulation` (PR #13, dependente do PR #11).
- Commit observado: `0c2b7d38f30f19fbadb0bb2bec88690058580836`.
- Execução integrada: [GitHub Actions 40876239023](https://github.com/enoqueJonas/mono-backend/actions/runs/40876239023), **aprovada**.
- Suite Django: [GitHub Actions 40876238901](https://github.com/enoqueJonas/mono-backend/actions/runs/40876238901), **aprovada**.
- Ambiente: runner Ubuntu, Python 3.12, PostgreSQL 16 (serviço isolado), Ganache 7.9.2 (rede local, chain ID 1337), Web3.py e Django REST Framework.
- Testes: `python -m pytest integration_tests/test_vc_ganache.py -q -s --ds=config.settings_integration` e `python -m pytest -q` (suite Django SQLite).
- Dados: utilizadores, grupo e contribuição **sintéticos**. O saldo de blockchain é fictício.

## Resultados observados

| ID | Verificação | Resultado |
|---|---|---|
| INT-01 | Implantação de `CredentialRegistry` no Ganache e consulta do recibo | Aprovado |
| INT-02 | Emissão de VC assinada via API com persistência PostgreSQL | Aprovado |
| INT-03 | Hash SHA-256 idêntico ao documento assinado e presente on-chain | Aprovado |
| INT-04 | Verificação de VC válida pelo endpoint público | Aprovado |
| INT-05 | Alteração do montante de contribuição detectada pelo verificador | Aprovado |
| INT-06 | Tentativa de revogação por membro não gestor negada (HTTP 403) | Aprovado |
| INT-07 | Estado on-chain permanece não revogado após tentativa não autorizada | Aprovado |
| INT-08 | Revogação por gestor activo e confirmação do estado no contrato | Aprovado |
| INT-09 | Verificação posterior à revogação devolve `valid=false` | Aprovado |

- Total da integração: **1 cenário completo aprovado**, 2 avisos de dependências.
- Total da suite Django: **119 testes aprovados** (em SQLite), sem falhas.
- Execução evidencial: contrato `0xF2E246BB76DF876Cef8b38ae84130F4F55De395b`, tx de implantação `90c57b145bbcb13be2d42213a5bae00795456693c219cddd028215e62384b377`.
- Hash de VC sintética dessa execução: `107e464ac1c8fe59b8335fb6ebbd541bf4bbd0bb9620a6b00c4de56f4c68d041`.

## Limites metodológicos

1. A contribuição foi introduzida na base de dados para preparar o cenário. **Não houve validação de pagamento real, contacto com M-Pesa/e-Mola nem reconciliação financeira.**
2. Ganache é uma blockchain local controlada, não rede pública nem operação distribuída real.
3. A suite de contratos Brownie separada ainda não foi executada como parte deste relatório.
4. O documento de VC usa uma assinatura Ed25519 da aplicação; não foi avaliada interoperabilidade externa com verificadores W3C de terceiros.
5. Não foi medida taxa de fraude, confiança dos membros ou adopção por cooperativas reais.
6. Não foi provocado cenário de falha entre confirmação on-chain e persistência SQL; falta testar reconciliação e atomicidade entre sistemas.
7. O webhook de carteira móvel está protegido por HMAC para **simulação controlada** e desactivado por defeito, sem representar contrato de operador financeiro.

## Consequências científicas

Há evidência técnica positiva para emissão, integridade, consulta, controlo de acesso e revogação de credenciais no ambiente experimental. As hipóteses de impacto social/financeiro mantêm-se sem demonstração empírica de impacto. A avaliação final das hipóteses HG e HE1–HE5 deve manter estas distinções.

## Reprodutibilidade

O workflow e os testes encontram-se em:
- `.github/workflows/ganache-vc-integration.yml`
- `integration_tests/test_vc_ganache.py`
- `config/settings_integration.py`
- `.github/workflows/backend-tests.yml`

A configuração de teste usa credenciais descartáveis, exclusivas do runner CI.
