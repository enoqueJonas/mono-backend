# Numeração automática das legendas — monografia canónica (29/10/2026)

A **única versão canónica** continua a ser a que exclui os gráficos hipotéticos 4.2.1–4.2.3. Revisão derivada de `Monografia_Canonica_Indice_Estrutural_Corrigido_29102026.docx`.

**Artefactos entregues na conversa:** `Monografia_Canonica_Legendas_Automaticas_29102026.docx` e `Relatorio_Legendas_Sequenciais_Canonica_29102026.md`. Nenhum DOCX foi carregado neste repositório backend.

## Implementação
- **59 legendas** passaram a ter campo nativo Word `SEQ` para o segmento final: **43 figuras** (35 do corpo + 8 do apêndice), **1 gráfico**, **15 quadros**.
- As 13 séries usam campo por secção, p.ex., `Figura 5.2.` + `{ SEQ CapFig5_2 \\* ARABIC }`, e a numeração em cache existente foi mantida.
- Prefixos de capítulo/secção permanecem estáticos; alterar legendas de secção exige rever série e prefixo.
- Os quatro campos `TOC` preexistentes e a disposição visível mantiveram-se; não foram acrescentados desenhos, gráficos, nem resultados estatísticos.

## Evidência de verificação
1. **157 páginas** na origem e na versão revista; texto extraído dos dois PDFs **idêntico em todas as 157 páginas**; diferenças de rasterização insignificantes em 11 páginas e nenhum deslocamento.
2. **157 PNG gerados** e folhas de contacto inspeccionadas.
3. Apenas **`word/document.xml`** foi alterado; **48 ficheiros media**, **4 partes de comentários** e **26 tabelas** preservados.
4. **59 campos `SEQ` e 4 `TOC`** identificados.
5. Num **ficheiro experimental** separado, LibreOffice UNO executou `getTextFields().refresh()`: as **59 legendas e respectivos números** permaneceram exactamente iguais à origem.
6. Auditoria textual: **43 referências numeradas** no corpo para **34 legendas distintas**, **zero referências órfãs** entre os padrões `Figura|Quadro|Gráfico + número`.

## Limitações
- O **ficheiro experimental guardado pelo LibreOffice** reclassificou a legenda **Figura 5.2.9** como estilo `Normal` e descartou duas partes modernas dos comentários. **Esse ficheiro não foi entregue nem substitui a versão canónica**; a versão entregue mantém os estilos e os comentários originais intactos.
- Falta testar a actualização simultânea dos índices e campos em **Microsoft Word**; não declarar compatibilidade completa.
- As referências numéricas no texto continuam escritas como texto, não como campos `REF`, embora não existam referências órfãs no conjunto auditado.
- Mantêm-se as pendências do manual USTM/FCTI, dos limites de páginas e do licenciamento das imagens.

**Estado:** implementação de campos `SEQ` e QA do Word canónico concluídos; Microsoft Word e conformidade institucional pendentes.