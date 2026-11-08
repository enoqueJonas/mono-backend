# PR #12 vs. PR #11 — reconciliação por conteúdo

**Data:** 8 de Novembro de 2026  
**Repositório:** `enoqueJonas/mono-backend`  
**PRs:** #11 `fix/vc-issuance-verification-audit` e #12 `chore/reproducible-test-discovery`

## Resultado reproduzível

Todos os seis ficheiros no diff do PR #12 têm **exactamente o mesmo SHA de blob Git** no PR #11:

| Caminho | SHA Git comum nos dois ramos |
|---|---|
| `.github/workflows/backend-tests.yml` | `3e4e8ee0b9c9e8ce173a33dd86c47f2aa7fe3073` |
| `config/settings_test.py` | `cddfacb4487cced532a610ab928795ced35c466b` |
| `docs/audit/test-execution.md` | `46eed3a02ba677786f51031850050b431d6b12de` |
| `pytest.ini` | `90b6b4419b0ab65f881fdc83e13d1c7979fc5a76` |
| `requirements-dev.txt` | `b8fa017805ec15750d07ba809fb01ed2b1534ece` |
| `wallets/tests.py` | `d4a28b5065cf0b8b4e8eeff49c46beadea245159` |

Comparação ao PR #26: os cinco primeiros blobs continuam iguais; `wallets/tests.py` avançou por medidas posteriores relacionadas com o simulador de carteira. O facto de #12 ter o mesmo conteúdo de ficheiros que #11 não demonstra identidade de histórico de commits nem garante que todos os PRs são isentos de conflitos quando os ramos-base forem actualizados.

**Consequência:** o PR #12 não transporta alterações exclusivas necessárias ao ramo activo. Não fazer cherry-pick nem merge adicional. Pode ser administrativamente marcado como supersedido após confirmação final, sem perder o histórico de discussão e evidências.

## Integração dependente

1. Rever e integrar PR #11 sobre `master`, preservando os seis blobs.
2. Rever PR #13 sobre #11; PR #14 sobre #13; PR #22 sobre #14; PR #26 sobre #22.
3. Recalcular cada diff, migrações e CI depois de alterar a base de cada PR. Não confundir sucesso de testes de um ramo experimental com testes sobre o merge commit exacto.
4. Ligar frontend PR #1 somente a uma API backend com RN06 incorporada; manter checkout backend fixado em SHA para a CI, revendo a dependência após cada mudança.
5. Não juntar alterações sem decisões sobre política financeira do ciclo (#28), custódia de chaves (#29) e restrições de implantação.

## Critérios de qualidade pós-reconciliação

- CI Django deve executar `makemigrations --check --dry-run`, para detectar alterações de modelos sem migração antes de testes.
- Manter Django/SQLite unitário, Brownie/Ganache e Playwright/PostgreSQL em workflows distintos: cada um mede uma dimensão diferente.
- Não declarar completude de uma tese nem adequação para dinheiro real a partir de testes de um protótipo.
