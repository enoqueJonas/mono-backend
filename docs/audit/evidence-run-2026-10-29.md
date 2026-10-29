# Registo experimental — suite Django de 29/10/2026

## Identificação e rastreabilidade
- Sistema: Mono Backend (protótipo de Xitique e credenciais verificáveis).
- Branch: `fix/vc-issuance-verification-audit` (PR #11).
- Commit sob teste: `b2a174f0ea5747654fa8155590fc6b5a1b009582`.
- Execução: [GitHub Actions run 40874203127](https://github.com/enoqueJonas/mono-backend/actions/runs/40874203127).
- Workflow: `Backend QA (unit and integration-style tests)`.
- Runner: Ubuntu (GitHub Actions), Python 3.12.15; Django 6.0.6; SQLite em memória.
- Hora: 29/10/2026 (UTC, conforme logs do workflow).

## Comandos reproduzíveis
1. `python -m pip install -r requirements-dev.txt`
2. `python -m compileall -q accounts blockchain contributions core credentials disbursements groups identity penalties wallets config`
3. `python -m pytest --collect-only -q`
4. `python -m pytest -q`

## Resultados observados nos logs
- Compilação Python: **aprovada**.
- Recolha: **111 testes** (1,11 s).
- Execução: **111 aprovados, 0 falhas, 2 avisos** (2,11 s).
- Avisos não bloqueantes: dependência `websockets.legacy` obsoleta e `min_value` de serializer DRF.

## Interpretação académica
Este resultado demonstra a aprovação da **suite automatizada nesta configuração de teste**.
Abrange hashing, políticas, emissão, assinatura Ed25519 de teste, persistência da VC,
verificação de estados simulados, regras de grupos e contribuições e respostas de API
com integrações externas substituídas por mocks nos cenários apropriados.

**Não demonstra:**
- Interacção ponta-a-ponta Django + PostgreSQL + Ganache em execução;
- Execução da suite Brownie no mesmo runner;
- Segurança do webhook com operador de carteira móvel real;
- Redução real/quantificada de fraudes, mudança de confiança comunitária ou viabilidade
  jurídica/cultural da adopção.

## Próximas evidências a recolher
- [ ] Brownie: ancoragem, consulta, revogação e consulta do estado revogado.
- [ ] Django + Ganache: emissão, recibo on-chain, verificação positiva, revogação, verificação negativa.
- [ ] Provas de autorização na API e autenticidade dos webhooks (#9).
- [ ] Consolidação da matriz de hipóteses HG/HE1–HE5 (#6).

**Regra:** nunca confundir a aprovação de testes com mocks com a validação integral da blockchain real.
