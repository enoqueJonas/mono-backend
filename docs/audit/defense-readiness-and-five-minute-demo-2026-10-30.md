# Preparação da defesa — estado integrado e roteiro de demonstração

**Data da auditoria:** 30 de Outubro de 2026.  
**Monografia canónica:** `Monografia_Canonica_Telas_Reorganizadas_30102026.docx` (156 páginas, `SHA-256 f1507fc0362226652affe1c709127a3faef0057a9442a11f27e831f94c7edea5`).  
**Branch técnica observada:** `audit/chain-db-consistency-recovery`, PR #14.

## 1. Constatação de integração de código

À data da consulta ao GitHub, os PRs #11, #12, #13 e #14 permaneciam **abertos e em rascunho**, não integrados em `master`:

| PR | Objectivo | Base declarada | Limite |
|---|---|---|---|
| #11 | Emissão/assinatura/verificação de VC | `master` | Rever credenciais anteriores e integração |
| #12 | Recolha de testes/CI | `master` | Tem alterações sobrepostas; reconciliar configuração |
| #13 | Autorização de revogação e segurança de simulador de carteira | `fix/vc-issuance-verification-audit` (#11) | Não autentica provedores financeiros reais |
| #14 | Consistência PostgreSQL/blockchain e reconciliação | `fix/authorize-vc-revocation-and-wallet-simulation` (#13) | Necessita decisão operacional e estratégia de integração |

**Sequência estrutural:** #11 → #13 → #14; #12 deve ser revisto de modo coordenado. Os PRs terem o sinal de `mergeable=true` **não** constitui aprovação de arquitectura, segurança, migrações ou compatibilidade.

Foi consultado o commit HEAD de #14 `2357ea7acb88f0e20031db4d3738d2a3ce9a8c60`, para o qual o GitHub apresentou três workflows de Pull Request com conclusão **`success`**: **Backend QA**, **VC Ganache integration** e **Independent Brownie smart-contract tests**. As evidências documentadas dos testes são **120/120 Django**, **1 cenário integrado PostgreSQL/Ganache** e **14/14 Brownie**, respectivamente. Estes resultados foram observados na branch experimental, **não** assumidos para `master`.

**Gate para demonstração:** usar um único commit do branch que tenha os três workflows aprovados; registar o SHA e a configuração. Não fazer merge automático, não usar a branch `master` como se contivesse as correcções. Antes de qualquer merge, rever a cadeia de PRs, alterações de BD e limitações operacionais.

## 2. Demonstração — versão de 5 minutos, baseada em evidência testada

Este é um **roteiro**, não uma afirmação de que a interface gráfica foi testada ou de que o vídeo já foi gravado. Os cenários abaixo estão cobertos por `integration_tests/test_vc_ganache.py` e as instruções de CI na branch #14; a equivalência de cada botão da interface React com o endpoint deve ser ensaiada antes da gravação.

| Tempo | Acção a demonstrar | Evidência e mensagem defensável |
|---|---|---|
| 0:00–0:35 | Explicar grupo Xitique, gestor e membro sintéticos; mostrar nome, regra de contribuição e contexto de contribuição | Contextualização, **sem** alegar amostra representativa |
| 0:35–1:20 | Mostrar contribuição de **1.000 MZN** confirmada **manualmente em ambiente de teste**, sem operação real de carteira móvel | O teste integra uma contribuição `CONFIRMED` criada no banco de teste; **não** comprova pagamento M-Pesa/e-Mola |
| 1:20–2:25 | Emitir credencial para o histórico do membro; apresentar `id`, `validUntil`, assinatura `proof` e hash ancorado no Ganache | API de emissão e contrato `CredentialRegistry`, validação E2E no CI |
| 2:25–3:15 | Verificar a credencial válida; alterar **apenas uma cópia** do montante e repetir verificação | Credencial original aceite, versão adulterada rejeitada; prova de detecção de adulteração após emissão |
| 3:15–4:10 | Tentar revogar enquanto membro comum (negado 403), revogar como gestor e verificar novamente | Permissão negada antes da transacção, revogação autorizada em contrato, VC revogada rejeitada |
| 4:10–5:00 | Resumir limites e resultados | Blockchain local Ganache, dados sintéticos, assinatura Ed25519 de aplicação; sem integração financeira real, adesão medida, interoperabilidade SSI universal ou redução observada da fraude |

**Opcional, se o fluxo acima couber em menos de 5 minutos:** preparar como evidência suplementar, **não obrigatória na gravação**, a demonstração de falha de escrita SQL após confirmação on-chain, registo `PENDING`, reconciliação a partir do evento e ausência de ancoragem duplicada. O cenário já foi validado via teste automatizado, mas é técnico e pode sobrecarregar os cinco minutos.

### Endpoints constatados no teste de integração

- `POST /api/v1/credentials/{group-id}/credentials/` — emitir VC por gestor autenticado;
- `POST /api/v1/credentials/verify/` — verificação, com documento VC no corpo;
- `POST /api/v1/credentials/{credential-id}/revoke/` — revogação com verificação de papel do gestor.

**Atenção:** estes são endpoints vistos no teste automatizado da branch #14. A interface final deve ser validada contra o código realmente executado. Nunca incluir chave privada, credenciais reais, participantes entrevistados ou números reais de telemóvel na gravação.

### Comandos de reprodução já presentes no repositório

Na branch do PR #14, com dependências e serviços de integração configurados conforme `.github/workflows/ganache-vc-integration.yml`:

```bash
python -m pytest -q
python -m pytest integration_tests/test_vc_ganache.py -q -s --ds=config.settings_integration
```

Testes de contratos, no ambiente Brownie compatível conforme `.github/workflows/brownie-contracts.yml`:

```bash
cd smart_contracts
brownie test -s --network development tests/
```

A execução integrada exige **PostgreSQL 16** e **Ganache 7.9.2**, rede de teste local com `chainId=1337`; um `pytest` simples **não** executa automaticamente os cenários Brownie/Ganache. Estas instruções não são um instalador local completo.

## 3. Lista de aceitação da demonstração

- [ ] Confirmar qual commit será mostrado, e que os três workflows são `success` no mesmo HEAD.
- [ ] Confirmar backend, frontend, PostgreSQL, Ganache, contratos e variáveis locais; não depender de chaves de produção.
- [ ] Preparar dados sintéticos estáveis e um estado inicial restaurável para 2–3 ensaios.
- [ ] Confirmar equivalência frontend→API nos três endpoints e capacidade de mostrar VC e hash.
- [ ] Executar em sequência emissão→verificação→adulteração→revogação→reverificação, e observar respostas reais.
- [ ] Gravar ensaio cronometrado abaixo de 5:00, com resolução legível e dados não sensíveis.
- [ ] Guardar evidência do commit, ambiente, logs/recibos e versão de vídeo para eventual pedido do júri.

## 4. Documentação académica — pendências separadas

- **Índices Word:** 43 legendas = 43 entradas e remissões coerentes; regeneração LibreOffice mudou 156→157 páginas devido à Lista de Figuras. Confirmar no **Microsoft Word** apenas, numa cópia, antes de submissão. Não comprimir margens.
- **FCTI/USTM:** contacto institucional já enviado; falta resposta sobre manual aplicável, limite de páginas e calendário.
- **Entrevistas E1–E7:** suficientemente documentadas para o propósito qualitativo exploratório no texto actual; não reabrir sem defeito ou solicitação institucional.
- **Integração financeira:** simulada; não afirmar pagamento confirmado por operadores reais.
- **Monografia:** não alterar interpretação de hipóteses em razão exclusiva da aprovação de testes unitários/integração em ambiente controlado.

## 5. Fontes e provas auditadas

1. PR #11: https://github.com/enoqueJonas/mono-backend/pull/11
2. PR #12: https://github.com/enoqueJonas/mono-backend/pull/12
3. PR #13: https://github.com/enoqueJonas/mono-backend/pull/13
4. PR #14: https://github.com/enoqueJonas/mono-backend/pull/14
5. Documento da prova E2E: `docs/audit/consistency-recovery-2026-10-29.md` na branch #14
6. Documento da suite Solidity: `docs/audit/brownie-contract-tests-2026-10-29.md` na branch #14
7. Teste: `integration_tests/test_vc_ganache.py` na branch #14
8. Workflow: `.github/workflows/ganache-vc-integration.yml` na branch #14
9. Regressão do índice: `docs/audit/monograph-appendix-b-index-refresh-regression-2026-10-30.md`

**Conclusão:** a revisão das telas e a auditoria do índice não exigem outra versão canónica do DOCX. O risco mais relevante para a preparação da defesa é **proveniência e integração da versão funcional**. O roteiro da demonstração pode começar a ser ensaiado, mas ainda não se deve afirmar que a demonstração através da interface ou o vídeo estão concluídos.