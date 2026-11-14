# Auditoria das fontes do Xitique e do enquadramento jurídico — 30/10/2026

## Documento de referência
- **Entrada:** `Monografia_Canonica_EBSI_e_Grafico_241_Revistos_30102026.docx` (156 pp.).
- **Saída:** `Monografia_Canonica_Fontes_Xitique_Revistas_30102026.docx` (156 pp.), SHA-256 `a8ea2364f33d8bbdfce1188e0450f2bbbbf5608015c57d2ab607451bde6063fa`.
- **Escopo:** 8 parágrafos do manuscrito, incluindo uma referência bibliográfica, alterados após confronto com documentação. Não foram alteradas hipóteses, testes do protótipo, entrevistas nem figuras.

## Achados documentais verificáveis

| Obra | Evidência consultada | Decisão |
|---|---|---|
| **Trindade**, *“Xitiki é compromisso”* | A dissertação de mestrado da Unicamp apresenta **2015**, título completo *“Xitiki é compromisso”: Os sentidos de uma prática de sociabilidade na cidade de Maputo, Moçambique*. A autora confirma data e título no artigo científico de 2019. | Corrigir citação de **2017 para 2015** e referência completa; retirar falsa atribuição de dados técnicos e agrícolas (p. impressa 54). |
| **Nhane (2013)** | Folhas iniciais e metodologia de *Dinâmicas do Xitique entre vendedores do mercado 25 de Setembro...*, Universidade Eduardo Mondlane. | Conservar: suporte para as variações de periodicidade, regras internas, membros e coordenadores. Não extrapolar para todo o país. |
| **Nhatsave (2011)** | Catálogo IHSN com resumo e ficheiro original; também citado explicitamente em artigo da USP de 2019. | Conservar: pesquisa económica sobre protecção social, rendimentos e limites da poupança. Não inferir fraude estatística. |
| **Carrilho e Teyssier (2011)** | Relatório final *Grupos de Poupança e Crédito em Moçambique, 10 anos depois*, FARE/PAFR, com autores João Carrilho e Sophie Teyssier. | Conservar, evitando equiparar todos os grupos ASCA ao Xitique rotativo. |
| **Dava, Low e Matusse (1998)** | Capítulo 6 *Mecanismos de Ajuda Mútua e Redes Informais de Protecção Social*, em *Pobreza e Bem-Estar em Moçambique: 1996–97*. | Conservar; fonte histórica de enquadramento, não estatística actual. |

### Discrepância de Trindade
O parágrafo da secção 4.1 anteriormente dizia que Trindade (2017) caracterizava a economia informal por registos em papel, ausência de comprovativos para empréstimos bancários, má gestão e exemplos agrícolas em Zambézia, Nampula e Niassa. A dissertação identificada estuda **sociabilidade, compromisso, reciprocidade e a vida comunitária no Xitiki da cidade de Maputo**. Os exemplos atribuídos no parágrafo não foram demonstrados na obra. A versão revista descreve apenas aquilo que a pesquisa sustenta, separando **riscos de sistema hipotetizados** das **observações do estudo antropológico**.

### Generalizações revistas na Introdução e secção 2.1.1
1. A percentagem agregada do FinScope de 2019 não demonstra que os mecanismos informais sejam a **principal solução de subsistência** da população.
2. A ausência de procedimentos internos padronizados não demonstra que **todos** os grupos estejam fora de qualquer enquadramento jurídico ou não disponham de protecção.
3. O tratamento de ROSCAs em Bouman/Aryeetey não é prova de incidência quantificada de **fraude em grupos Xitique**.
4. Os efeitos sobre a sustentabilidade e a confiança são **riscos potenciais**, não resultados medidos neste estudo.
5. Não se pode inferir que a **maioria dos cidadãos rurais e periurbanos** esteja excluída do sector financeiro formal a partir da descrição operacional de Varadharajan.
6. A dimensão comunitária referida em Trindade deve integrar o contexto sem ser reduzida a questões de registo contabilístico.

## Verificação do enquadramento jurídico (secção 5.4.5)
Foi confrontado o **texto da Lei n.º 3/2017, de 9 de Janeiro**, incluindo a página do Boletim com os artigos 22.º–25.º, com os parágrafos do documento:
- **22.º:** assinatura electrónica, identificação e método apropriado;
- **23.º:** documento original e integridade;
- **24.º:** admissibilidade e força probatória da mensagem de dados;
- **25.º:** conservação das mensagens;
- **63.º:** responsabilidades de tratamento e protecção de dados pessoais, corroboradas pelo INTIC.

A distinção já presente entre assinaturas criptográficas do protótipo e **certificação formal no SCDM** é prudente. O **Decreto n.º 59/2019** continua identificado na página institucional do INTIC. **Não foi necessária alteração deste parágrafo.** O estudo **não** equivale a um parecer de conformidade legal para produção. As Leis **13/2026** (Segurança Cibernética) e **14/2026** (Crimes Cibernéticos) constam na lista oficial do INTIC, mas a mera existência dessas leis não permite afirmar que uma implantação hipotética já cumpre os seus requisitos; a análise de aplicabilidade permanece tarefa futura.

## QA do DOCX — regressão
- **156 páginas** antes e depois, verificadas por exportação PDF.
- Alterada **apenas** a parte `word/document.xml` do pacote OOXML; ZIP íntegro e **129 partes** preservadas.
- **48 multimédia**, **26 tabelas**, **quatro partes XML de comentários**, **361 bookmarks**, **59 SEQ, 45 REF e 4 TOC** intactos.
- Comparação de texto **e de raster de todas as 156 páginas:** diferenças apenas nas físicas **18, 19, 25, 26, 27, 71, 72, 73, 74, 75 e 138**. As outras **145 páginas** são visualmente idênticas no motor de exportação.
- Geometria: **zero spans de texto fora dos limites** de página.
- Inspeccionadas imagens ampliadas da secção 4.1 e da bibliografia e contacto visual do documento completo. Os capítulos, o Apêndice e os Anexos mantêm as páginas de início.
- Os campos do índice não foram regenerados; o autor confirmou anteriormente que funcionam no Microsoft Word. Não foi introduzida qualquer discrepância de paginação.

## Referências de auditoria
- Trindade, dissertação integral: https://www.ophenta.org.mz/wp-content/uploads/2017/03/XITIKI-E-COMPROMISSO-compactado.pdf
- Trindade, artigo de 2019, com nota sobre dissertação de 2015: https://doi.org/10.11606/issn.2316-9141.rh.2019.145419
- Nhane, monografia de 2013: https://pt.scribd.com/document/817153393/2013-Nhane-Agostinho-Joao
- Nhatsave, catálogo IHSN: https://catalog.ihsn.org/citations/26347
- Carrilho & Teyssier, relatório de 2011: https://pt.scribd.com/document/375521248/10-Anos-de-ASCAS-Relatorio
- Dava et al., capítulo histórico: https://livrozilla.com/doc/609749/cap%C3%ADtulo-6-mecanismos-de-ajuda-m%C3%BAtua-e-redes-informais-de
- Lei 3/2017 (OAM, Boletim): https://oam.org.mz/wp-content/uploads/2017/07/Lei-das-Transaccoes-eletronicas.pdf
- INTIC, legislação relevante 2026: https://intic.gov.mz/sectorial/
- INTIC, art. 63: https://intic.gov.mz/lourino-chemane-participa-do-painel-sobre-promocao-da-implementacao-de-controles-de-privacidade-nas-instituicoes-mocambicanas/

## Pendências separadas
A resposta ao e-mail **já enviado** à FCTI sobre regras e extensão da monografia está pendente. Os dados primários das entrevistas (locais, datas, recrutamento, consentimento e número de grupos) continuam por documentar a partir de registos autênticos. Não afirmar certificação individual de todas as 69 referências nem validade jurídica automática do protótipo.

**Decisão:** a cópia revista constitui a **nova canónica de trabalho**, preservando a variante sem os três gráficos hipotéticos anteriormente excluídos.