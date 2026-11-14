# Auditoria residual das referências e correcção do X-Road

**Data:** 30/10/2026  
**Documento-base:** `Monografia_Canonica_Mineracao_e_Prototipagem_Revistas_30102026.docx` — 158 páginas; SHA-256 `70a064be5a2bc82e80638e822c1cd0accb7e5fa90079678fa013efcbdafd66f7`.  
**Novo DOCX de trabalho:** `Monografia_Canonica_Referencias_Conferidas_30102026.docx` — 156 páginas; SHA-256 `76e8ea37c55462119d86958e21de41c87f92344ac65aef95f3ec49d72290339a`.

## Objectivo e método
Reconciliar os 87 itens da secção de Referências Bibliográficas com todas as ocorrências textuais **anteriores** à bibliografia, incluindo parágrafos, legendas e texto de tabelas. Conferir os casos suspeitos pela sigla/autor institucional, para não apagar referências efectivamente utilizadas. Identificar citações ano–fonte inconsistentes e corrigir apenas o que possui suporte público verificável.

A normalização APA da lista depende ainda da versão oficial do manual FCTI/USTM solicitada pelo autor. O critério elementar *obras citadas no texto ↔ entradas da lista* é comum às versões APA 6 e 7. Referência de orientação: https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/reference_list_basic_rules.html

## 1. Resultado — bibliografia
- **Antes:** 87 entradas.
- **Retiradas:** 19 entradas cujos nomes de autor/organização não foram encontrados no texto ou nas tabelas/legendas antes da bibliografia; nenhuma possuía marcador, referência cruzada, campo ou comentário ancorado no parágrafo.
- **Conservada após confronto adicional:** INTIC (2026), porque a instituição é citada na secção 4 e a fonte foi verificada; corrigida a entrada institucional, data e URL.
- **Acrescentadas:** Mocnotícias (2026, 9 de Outubro), para o acontecimento X-Road em Moçambique; Nordic Institute for Interoperability Solutions (NIIS, s.d.), para a descrição técnica de X-Road.
- **Depois:** **70 entradas** (= 87 - 19 + 2).

### Lista exacta das 19 entradas retiradas por ausência de citação
1. Anggreani (2009)
2. Babarinde (s.d.)
3. Boot et al. (2021)
4. Cunha (2011)
5. Davenport (1994)
6. Dheka (s.d.)
7. Duarte (2025) — a antiga Figura 2.3.10 baseada numa citação secundária foi substituída por desenho original e já não há menção a Duarte no texto
8. Dutta et al. (2020)
9. Minayo (2010)
10. Oikos Cooperação e Desenvolvimento (2024)
11. Ozili (2022)
12. Paulo & Jaintilal (2007)
13. Quive & Patrício (2005)
14. Schall & Modena (2005)
15. SRM Consultoria (2019)
16. Szabo (1997)
17. Williams & Cockburn (2003)
18. Wood (2014)
19. York St John University (2018)

A exclusão **não** significa que a obra inexista, seja cientificamente inválida ou não tenha sido consultada; significa que **não sustenta uma citação identificável no manuscrito actual**. Não adicionar citações artificiais para conservar referências de rascunhos anteriores.

## 2. Correcção de citação incompleta
O **Gráfico 2.4.1** (legenda real e entrada da Lista de Gráficos) continha `W3C (2019; 2021)`; a bibliografia contém VC Data Model 1.0 **(2019)** e DID Core **(2022)**, não uma obra W3C 2021 correspondente. Ambas as ocorrências passaram a **`W3C (2019; 2022)`**. Códigos de legenda e campos automáticos mantidos.

Fonte: https://www.w3.org/TR/did-core/ e https://www.w3.org/TR/2019/REC-vc-data-model-20191119/

## 3. Correcção material da secção 4 — X-Road e políticas nacionais
**Anomalia anterior:** o capítulo 4 citava `Club of Mozambique, 2026` sobre X-Road, mas a única referência existente dessa entidade era um artigo de 2022 sobre dinheiro electrónico. A passagem descrevia X-Road como sistema **centralizado de interoperabilidade**, sem distinguir gestão do ecossistema da troca de dados.

**Revisão:** o parágrafo fundamenta a estratégia digital nacional em **INTIC (2026)** e a capacitação dos técnicos em **Mocnotícias (2026)**; explica, com base na documentação do **NIIS**, que X-Road tem gestão centralizada do ecossistema, mas **troca de mensagens descentralizada/directa entre sistemas das organizações**. Não é uma base única centralizada de todos os dados.

Fontes verificadas:
- INTIC, 26/01/2026: https://intic.gov.mz/governo-desenvolve-estrategia-nacional-de-transformacao-digital/
- Mocnotícias, 09/10/2026: https://mocnoticias.com/2026/10/09/mocambique-reforca-integracao-digital-do-estado-atraves-da-tecnologia-x-road/
- NIIS (documentação oficial): https://x-road.global/x-road-technology-overview e https://x-road.global/data-exchange

A antiga citação à publicação Club of Mozambique de 2022 **permanece na bibliografia**, pois é utilizada na legenda da Figura 4.1.1 (carteiras móveis).

## 4. Paginação, caches de índices e QA
A redução das referências passou o documento de **158 para 156 páginas**. **Não houve redução de margens, de entrelinha ou remoção de evidência do protótipo**. O Capítulo VII/Referências continua a começar na página física 133 (impressa 116). O Apêndice A passou da física 141 para **139** (impressa **122**); os Anexos da física 153 para **151** (impressa **134**).

Os dez valores em cache do índice foram ajustados **sem alterar os códigos dos campos**:
- Índice geral: `8 APÊNDICE A` **124→122**; `9 ANEXOS` **136→134**.
- Lista de figuras: `Figura A.1–A.8` com **–2 páginas em cada entrada**, conferidas com o PDF do ficheiro novo (páginas impressas **122, 123, 125, 128, 130, 132, 132, 133**).

Regressão:
- **Única parte OOXML modificada:** `word/document.xml`; ZIP íntegro (`testzip()=None`) e mesmo conjunto de **129** partes.
- **48 ficheiros multimédia**, **26 tabelas**, **4 partes dos comentários do supervisor**, **361 bookmarks**, **59 SEQ**, **45 REF**, **4 TOC**: todas as contagens idênticas à origem; imagens e comentários binariamente preservados.
- Renderização pela ferramenta de DOCX e exportação PDF: **156 páginas**, **156 PNGs**.
- Inspecção visual: índice (incluindo páginas dos apêndices), lista de gráficos, Capítulo 4, bibliografia e apêndices; contacto visual do documento completo. Não foram identificados defeitos de recorte, perda de capítulos ou de referências de figuras.
- Auditoria geométrica PyMuPDF: **zero blocos de texto fora das 156 páginas**; nenhum PDF vazio; deslocação de –2 páginas após bibliografia esperada.
- **Não** foi efectuada actualização global do índice no Word; o autor já confirmou que o índice automático funciona.

## 5. Pendências independentes
1. Resposta da FCTI ao e-mail **já enviado** pelo autor: manual, limite de páginas, APA, cronograma e calendário de defesa.
2. Documentação primária do campo E1–E7: critérios de selecção, local, datas, grupos e consentimento, sem inventar recolha.
3. Direitos/proveniência residual de fontes gráficas e referências específicas remanescentes (não declarar todas as 70 fontes verificadas individualmente).
4. Se, numa revisão posterior, o texto voltar a citar algum dos autores retirados, a referência correspondente deverá ser restabelecida com fonte completa e citação verdadeira.

**Estado:** limpeza residual concluída quanto às 19 entradas sem citação e às duas incongruências W3C/X-Road; novo Word com **156 páginas** é a versão canónica de trabalho mais recente. Não declarar certificação institucional.
