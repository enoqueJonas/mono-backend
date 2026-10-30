# Validação conjunta de campos e três lacunas bibliográficas — 30/10/2026

**Canónica aprovada:** monografia sem Gráficos 4.2.1–4.2.3.
**Documento produzido na conversa:** `Monografia_Canonica_Citacoes_Verificadas_30102026.docx` (**157 páginas**).
**Relatório do autor:** `Relatorio_Validacao_Conjunta_e_Citacoes_30102026.md`.

## Teste conjunto Word
Na cópia experimental, o LibreOffice UNO executou `getTextFields().refresh()`, regenerou os **4 índices TOC** e repetiu `getTextFields().refresh()`. Resultado: hierarquia de capítulos correcta, apêndices e listas presentes, sem referências quebradas visíveis. **A cópia regenerada tem 158 páginas** devido à expansão da lista de figuras; *não foi usada como versão final*, pois LibreOffice anteriormente eliminou partes modernas dos comentários. Teste no Microsoft Word pendente.

## Correcções científicas incorporadas
1. **Allessie, Sobolewski & Vaccari (2019)** — *Blockchain for digital government*, relatório JRC115049, DOI 10.2760/942739, inserido com referência oficial https://publications.jrc.ec.europa.eu/repository/handle/JRC115049. Duas alegadas citações directas não verificadas foram substituídas por paráfrases e uma alegação sobre consensos foi qualificada.
2. **“Fare (2011)”** — substituída atribuição incompleta por **Carrilho & Teyssier (2011)**, *Grupos de poupança e crédito em Moçambique, 10 anos depois* (FARE/PAFR). Corroboração bibliográfica em https://www.iese.ac.mz/lib/publication/livros/des2014/IESE-Desafios2014_06_FinRur.pdf. Removida equiparação indevida entre todas as modalidades de poupança e Xitique rotativo.
3. **45% de adultos sem identificação na África Subsaariana** — estatística sem suporte correspondente removida. Texto actualizado para cerca de **60% da população geral de Moçambique** sem ID civil em comunicado do Banco Mundial de **22/10/2021**, **não** indicador de adultos nem de participantes de Xitique. Fonte: https://www.worldbank.org/en/news/press-release/2021/10/22/world-bank-supports-mozambique-s-efforts-towards-access-to-identification-and-digital-transformation.

## QA
- 157/157 páginas na versão entregue, alterações somente nas páginas físicas **25, 38, 41, 49, 133–139**.
- Só `word/document.xml` alterado.
- **48 media**, **4 partes de comentários**, **26 tabelas**, **59 SEQ**, **45 REF** com destinos válidos, **4 TOC** preservados.
- PNGs e bibliografia revistos; nenhum gráfico ou diagrama modificado.

## Pendências
- [ ] Testar actualização completa no Microsoft Word.
- [ ] Manual FCTI/USTM vigente, limite de páginas, cronograma e APA aplicável.
- [ ] Confirmar autoria/licenciamento de imagens externas e outras citações directas antigas.
- [ ] PRs de ensaios técnicos experimentais permanecem não incorporados à branch principal.

**Não fechar as issues #1, #7 ou #15.**