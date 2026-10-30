# Correcção técnica da Figura 2.4.4 — monografia canónica (30/10/2026)

## Ficheiros e proveniência
- **Origem:** `Monografia_Canonica_Entrevistas_e_Diagramas_DID_30102026.docx`.
- **Destino:** `Monografia_Canonica_Figura_2_4_4_Revista_30102026.docx` (157 páginas).
- SHA-256 da origem: `3669d5464016d0db9335b562c1c67ab35e6c2d6fed28c9e14ab9994f158bc33a`.
- SHA-256 do destino: `c0c154fabb1465525013f5e7ffa3aeab256760e14c7ff645bdcd2fed1f61c2c5`.
- Procedimento: **edição selectiva do OOXML**, não reconstrução do Word nem substituição do SmartArt por imagem.
- O ficheiro de saída foi entregue no chat e pode ser aberto no Word; PDF de verificação não é a versão de entrega.

## Alterações exactas
Três e apenas três partes internas foram alteradas:
1. `word/document.xml`: parágrafo introdutório à Figura 2.4.4, agora explicitamente conceptual e sem alegações de efeitos comprovados do protótipo.
2. `word/diagrams/data6.xml`: texto-fonte do SmartArt original.
3. `word/diagrams/drawing6.xml`: texto desenhado/cache de visualização do mesmo SmartArt.

Quatro blocos do SmartArt permanecem com a mesma geometria/estilo:
- **Verificação em cooperativas informais:** VCs/identificadores podem apoiar comprovativos; integridade criptográfica **não** comprova pagamento real nem impede toda fraude.
- **Eficiência na auditoria:** detecção de alterações e auditoria potencial; relevância de dados de origem fiáveis e responsabilidade humana.
- **Criação de histórico financeiro:** história de contribuições pode documentar a participação, mas aceitação por bancos depende de critérios e acordos **não avaliados**.
- **Interoperabilidade tecnológica:** possível articulação entre sistemas compatíveis, mas ligação a **M-Pesa/e-Mola não foi realizada**; apenas confirmação simulada.

Foram removidas do desenho atribuições excessivamente fortes a W3C (2021), EBSI (2021) e World Bank (2021), pois as frases originais não eram consequências garantidas dos respectivos modelos. A bibliografia e legendas foram preservadas, pois não se introduziu uma nova fonte gráfica ou figura externa.

## Evidência normativa
- [W3C, *Verifiable Credentials Data Model v2.0*](https://www.w3.org/TR/vc-data-model/): a verificação de uma credencial não demonstra a veracidade das afirmações nela contidas; a confiança no emissor e políticas do verificador são decisões externas à verificação criptográfica.
- [W3C, *Decentralized Identifiers 1.0*](https://www.w3.org/TR/did/): DID não pressupõe uma única implementação tecnológica, blockchain ou sistema de registo específico.
- [Comissão Europeia — EBSI](https://digital-strategy.ec.europa.eu/en/policies/european-blockchain-services-infrastructure): infraestrutura de nós e serviços partilhados, não eliminação da governação e dos responsáveis institucionais.
- [EBSI](https://ebsi.eu/about-us): camada de confiança partilhada que liga sistemas, não promessa de integração com operadores de carteira móvel em Moçambique.

## Auditoria técnica reprodutível
- ZIP/OOXML íntegro: `testzip()` sem erros.
- 157 páginas no PDF renderizado em LibreOffice, igual à origem.
- Comparação de **texto por página** e **rasterização de 157 páginas** (PyMuPDF): diferenças **apenas nas páginas físicas 49 e 50**; as outras 155 páginas não mudaram.
- Inspecção visual directa das páginas físicas **49–51**: caixas do SmartArt intactas, texto legível e sem sobreposição; legenda continua na página física 50 (número impresso 33).
- Todos os **48 ficheiros multimédia** binariamente idênticos.
- Todas as **quatro partes dos comentários Word** binariamente idênticas.
- **26 tabelas**; **59 campos SEQ**, **45 REF**, **4 TOC**; campos não alterados.
- **Não** foram mudadas as hipóteses HG/HE1–HE5, resultados de testes, anexos, imagens externas ou registos de entrevistas.
- As verificações em LibreOffice **não substituem** a confirmação final no Microsoft Word: actualizar campos/índices e inspeccionar comentários.

## Status
**Correcção científica e visual da Figura 2.4.4 concluída na nova versão de trabalho.** As pendências institucionais USTM/FCTI, os direitos de figuras externas, a proveniência primária dos dados das entrevistas e o teste final de actualização de campos no Word **continuam abertas**.

### Nova questão observada fora desta correcção
Na página física **51**, secção 2.5 sobre contratos inteligentes, permanecem expressões absolutas sobre `eliminação de intermediários`, `imutabilidade` e possibilidades de automatização não necessariamente demonstradas no protótipo. Requer auditoria separada, não alterada nesta revisão.
