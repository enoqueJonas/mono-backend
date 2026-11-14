# Auditoria final de índices, legendas e remissões — 30/10/2026

## Referência documental
- **Entrada:** `Monografia_Canonica_Bitcoin_ION_Indy_Revistos_30102026.docx` — 158 páginas, SHA-256 `100b7baa3485ee08c52f997150eb2dc9d536327545e21ecc653a529465e659ed`.
- **Saída, após correcção pontual:** `Monografia_Canonica_Indices_Conferidos_30102026.docx` — 158 páginas, SHA-256 `b3ae57beeda7acc476fe470f9ed542c06f9d962f4f11b6ba4183e82e62d63861`.
- **Política:** nenhuma regeneração automática foi guardada no DOCX canónico; a experiência de refresh foi executada **sem regravar o Word**, apenas exportando PDF experimental do LibreOffice.

## 1. Auditoria dos campos do Word
O pacote OOXML contém:
- **4 TOC** nativos (índice geral, figuras, gráficos, quadros);
- **59 SEQ** para legendas;
- **45 REF** referindo 34 marcadores distintos; **0 alvos de bookmark em falta**;
- **2 campos ADDIN CSL_CITATION** oriundos do gestor bibliográfico;
- **26 tabelas**, **48 ficheiros multimédia** e **quatro partes XML de comentários do supervisor**.

Os campos **existem e são sintacticamente recuperáveis**. Isso **não** significa que a actualização conjunta seja visualmente estável no Microsoft Word.

## 2. Resultado da actualização experimental
Procedimento controlado:
1. Abrir cópia da monografia via LibreOffice Writer/UNO em modo oculto e de leitura.
2. Confirmar `getDocumentIndexes().getCount() == 4`.
3. Chamar `update()` sequencialmente nos quatro índices, seguido de `getTextFields().refresh()`.
4. Exportar **apenas** um PDF experimental — não guardar uma nova versão .docx no LibreOffice.
5. Comparar PDF com PDF da origem por texto extraído e pixéis renderizados.

**Defeito reproduzido em LibreOffice:**
- Paginação: **158 → 159 páginas**.
- Lista de figuras: ocupa **três** páginas em vez de **duas**; deslocação de uma página física da lista de gráficos e das secções subsequentes.
- No índice geral regenerado, a numeração preliminar originalmente apresentada como **romana I–X** passa a **valores árabes** — por exemplo `DEDICATÓRIA I` transforma-se em `DEDICATÓRIA 5`.
- A actualização inclui também subtítulos verdadeiros do Apêndice A que não constavam no cache original (8.1–8.3).

**Interpretação:** há uma **falha real de estabilidade de regeneração no LibreOffice** e os valores antigos de algumas entradas estavam desactualizados. O ensaio **não prova** que o Word para macOS irá apresentar o mesmo comportamento, pois os motores de campos/paginação são distintos.

## 3. Correcção dos caches existentes — quatro entradas
Um confronto estrito do número e título da secção com o texto das páginas físicas do PDF canónico (a numeração impressa do corpo corresponde a **página física – 17**) verificou **82 entradas numeradas** do índice geral; **78 estavam correctas, quatro divergiam**:

| Entrada | Valor armazenado no índice | Página impressa efectiva | Correcção |
|---|---:|---:|---|
| 1.5 Metodologia | 5 | **6** | 5 → 6 |
| 2.3.1 Tecnologia de Registo Distribuído | 11 | **12** | 11 → 12 |
| 2.3.4 Mecanismos de consenso | 16 | **15** | 16 → 15 |
| 6.2 Recomendações | 114 | **115** | 114 → 115 |

Todas as correcções foram feitas apenas **no texto visível em cache** dos respectivos parágrafos TOC. **Os códigos TOC foram preservados**, não congelados ou removidos. A alteração foi feita por patch selectivo de OOXML.

## 4. QA da nova versão
- Integridade ZIP aprovada.
- **Única parte OOXML modificada:** `word/document.xml`.
- Contagens iguais à origem: **4 TOC, 59 SEQ, 45 REF, 2 ADDIN, 26 tabelas, 48 media e quatro partes dos comentários**.
- 45 REF → **0 bookmarks em falta**; nenhum nome duplicado de bookmark.
- Renderização completa por LibreOffice: **158 páginas PNG + PDF**.
- Comparação integral de texto e raster entre a origem e a cópia corrigida, nas **158 páginas**: **diferenças apenas nas páginas físicas 3, 4 e 6**, correspondentes aos números corrigidos no índice. Outras **155 páginas visual e textualmente idênticas**.
- Inspecção visual das três páginas do índice com diferenças: valores corrigidos, sem clipping, sobreposição ou alteração de tipografia.
- Não alteradas as hipóteses, resultados experimentais, figuras, bibliografia, diagramas SmartArt, entrevistas ou comentários.

## 5. Ensaio obrigatório no Microsoft Word antes da submissão
**Nunca testar sobre a única cópia canónica.**
1. Duplicar o ficheiro `Monografia_Canonica_Indices_Conferidos_30102026.docx` no Finder e abrir a **cópia** no Microsoft Word para Mac.
2. Verificar previamente **158 páginas**, os comentários do supervisor, as quatro listas e o índice.
3. Actualizar os quatro índices um de cada vez, usando o comando Word «Actualizar campo» → «Actualizar todo o índice» (e não apenas números de página).
4. Actualizar as restantes referências cruzadas e legendas, reabrir cada índice e repetir uma vez; registar erros de campo `Error! Reference source not found`, alterações de número e deslocações de secções.
5. **Não guardar por cima da versão canónica se surgir alteração inesperada**. Guardar a cópia de teste e reportar páginas e exemplos.
6. Confirmar que as 82 entradas numeradas do índice geral continuam coerentes com a numeração impressa, com especial atenção às quatro agora corrigidas.
7. Confirmar o tratamento da **numeração romana preliminar**, que o ensaio LibreOffice não reproduziu correctamente.
8. Validar a lista de figuras e a paginação dos Apêndices A.1–A.8, e verificar se todas as quatro partes dos comentários permanecem acessíveis.
9. Exportar um PDF **pelo próprio Microsoft Word** e comparar as páginas/chapter breakpoints com a versão aprovada.

**Critério de fecho:** só declarar o índice geral, as listas e as 45 REF **certificados para entrega** depois do resultado observado no Word, com número final de páginas, comentários e capturas registados. Uma mera presença de campos ou um ensaio LibreOffice não basta.

## 6. Questões externas ainda bloqueadas
- Manual oficial USTM/FCTI aplicável em 2026 e eventual limite **60 páginas da Introdução às Referências**, referido no anexo da cópia pública de 2018; o texto permanece com extensão bastante superior, mas **não há confirmação escrita de vigência e excepções**.
- Conferência USTM 2026 refere APA 6 no âmbito dos artigos científicos, não prova inequívoca da norma vigente para esta monografia: https://conferencias.ustm.ac.mz/index.php/IIICNDAMS2026/about.
- Direitos de reprodução das imagens externas, proveniência específica da 2.4.2 e elementos primários das entrevistas (local, período, recrutamento, consentimento).

**Estado:** quatro erros reais do índice corrigidos. **Refresh final no Microsoft Word e conformidade institucional ainda pendentes; não fechar Issue #15 nem #1.**
