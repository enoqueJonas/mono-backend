# RN06 — Validação do livro de contribuições e alterações durante a votação

**Data:** 7 de Novembro de 2026  
**Ramo:** `feat/rn06-independent-disbursement-approval` / PR #26  
**Commit de evidência:** `ec03019942d737a4ea59c1def822250f4fa9a94b`  
**Issue:** #28

## Defeito reproduzido por testes de regressão

A implementação anterior comparava a **quantidade** de contribuições confirmadas do período com a quantidade de membros activos. Uma contribuição de um ex-membro, apesar de não pertencer ao conjunto activo, podia compensar uma contribuição em falta. O montante de contribuições de membros inactivos também podia ser incluído no valor do desembolso.

Além disso, a conclusão de uma proposta já aprovada não revalidava o seu estado financeiro; uma contribuição revertida ou um montante alterado depois dos votos podia passar despercebido.

**Prova antes da correcção:** CI do commit `79855f201247da0f4b31c558e5562db70640df30`: 131 testes anteriores aprovados e **4 regressões falhadas**, exactamente por não se lançar `IncompleteContributions`.

## Controlo provisório implementado

Em `DisbursementService._verified_contribution_total`:

1. Determinar os identificadores concretos de membros actualmente activos.
2. Obter contribuições do grupo, versão de configurações e período da rotação. Lock de linhas com `select_for_update` em transacção de criação/conclusão.
3. Rejeitar uma proposta sem nenhuma contribuição confirmada.
4. Exigir correspondência **exacta** entre os membros activos e aqueles com contribuições confirmadas para o período. Qualquer contribuição confirmada de um ex-membro activa um bloqueio em vez de ser transferida silenciosamente para o beneficiário.
5. Validar montante individual contra a quota da versão vigente no ciclo e a moeda associada.
6. Na conclusão, exigir que o conjunto actual de contas activas corresponda ao conjunto fixado quando a proposta foi apresentada (proponente, beneficiário e votantes elegíveis). Exigir também que o total confirmado continue igual ao valor guardado na proposta.
7. Se alguma validação falhar, não avançar a rotação nem marcar o registo como concluído.

**Não há nova regra para redistribuir ou reembolsar dinheiro de ex-membros.** Uma divergência bloqueia a proposta; a política financeira deve ser definida antes de resolver o bloqueio.

## Validação verde

No commit `ec03019942d737a4ea59c1def822250f4fa9a94b`, três workflows GitHub Actions concluídos com sucesso:

- **Backend QA:** 138/138 testes Django aprovados (sete regressões adicionais sobre a base anterior de 131).
- **Independent Brownie:** 18/18 testes de contratos.
- **VC Ganache integration:** 1/1 teste de emissão/verificação/revogação e controlo `onlyOperator`.

Os cenários adicionados verificam contribuição de ex-membro a encobrir omissão de membro activo, montante adicional de ex-membro, reversão após os votos, alteração do montante, mudança de membros após a proposta, moeda incompatível e contribuição de ex-membro adicionada depois da aprovação.

## Limites científicos e de implementação

- A validação utiliza o **estado do grupo na proposta**, não uma lista certificada de participantes obrigados a contribuir **no início do ciclo**. Entradas e saídas legítimas durante o ciclo podem originar bloqueio. Ainda falta um modelo versionado e imutável de participantes do ciclo.
- Alterações transitórias de membro que retornem exactamente ao estado anterior não são necessariamente rastreadas pelo instantâneo de contas. Falta um histórico de filiação/versionamento ou um modelo de eventos.
- O bloqueio é administrativo. O protótipo **não comprova o recebimento real** de M-Pesa, e-Mola ou banco e não controla levantamentos externos.
- O gestor ainda pode registar contribuições manualmente; é necessário verificar comprovativos por uma fonte independente.
- `select_for_update` melhora o controlo de concorrência em PostgreSQL, mas não constitui prova de serialização de todas as alterações de filiação e todos os canais de escrita. Testes de concorrência numa base PostgreSQL real ainda são necessários.
- Se o grupo contém contribuição confirmada de ex-membro, não existe política implementada de reembolso, retenção, nem de inclusão excepcional no ciclo; a decisão precisa de regras de governação aprovadas e documentadas.
- A interface Next.js ainda não foi ensaiada com três sessões reais autenticadas em browsers independentes; testes Django API não substituem E2E de UI.

**Estado da issue #28:** os cenários que permitiam contagem enganosa e conclusão com total alterado foram bloqueados no ramo experimental. Mantêm-se em aberto a política financeira de entradas/saídas, o instantâneo dos participantes no início do ciclo e os testes concorrentes em PostgreSQL antes de considerar a área de desembolsos pronta para produção.
