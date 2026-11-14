# Relatório de reorganização das interfaces — Capítulo 5.3 e Apêndice B

**Data:** 30 de Outubro de 2026  
**Base editorial:** `Monografia_Canonica_Entrevistas_Documento_Original_Verificado_30102026.docx`, com as entrevistas E1–E7 já reconciliadas com o documento fornecido pelo autor.  
**Nova versão de trabalho:** `Monografia_Canonica_Telas_Reorganizadas_30102026.docx`  
**SHA-256:** `f1507fc0362226652affe1c709127a3faef0057a9442a11f27e831f94c7edea5`  
**Paginação final renderizada em LibreOffice:** 156 páginas. 

## Decisão editorial e fundamentação

O capítulo 5.3 apresentava **cinco figuras compostas**, cada uma agregando mais de uma captura da interface Web e acompanhada de parágrafo explicativo. Seleccionaram-se para o corpo principal **três fluxos que materializam aspectos centrais do sistema de confiança proposto**:

| Figura anterior | Processo | Decisão | Nova figura |
|---|---|---|---|
| 5.3.1 | Autenticação e painel principal | Transferida, por ser apoio à navegação e não a contribuição técnica específica | **B.1** |
| 5.3.2 | Criação/consulta dos parâmetros do grupo | Mantida: parametrização das regras do Xitique | **5.3.1** |
| 5.3.3 | Gestão de membros e contribuições | Mantida: rastreabilidade do histórico contributivo | **5.3.2** |
| 5.3.4 | Rotação e desembolsos | Transferida: processo já explicado na modelação e no diagrama de sequência A.8 | **B.2** |
| 5.3.5 | Emissão e consulta de credenciais verificáveis | Mantida: resultado distintivo da proposta baseada em DID/VC | **5.3.3** |

As interfaces transferidas **não foram eliminadas**: tanto as capturas como os parágrafos explicativos e as legendas integrais estão no novo **Apêndice B — Interfaces complementares**, colocado depois do Apêndice A e antes dos Anexos. A introdução do subcapítulo 5.3 remete para o novo apêndice e evita apresentar as capturas como teste de usabilidade ou prova de integração financeira externa.

## Estrutura e campos do Microsoft Word

1. As três legendas do capítulo usam sequências **`SEQ CapFig5_3`** com caches consecutivos 1, 2 e 3.
2. As duas novas legendas usam sequências **`SEQ CapFigB`** com caches consecutivos 1 e 2.
3. Os cinco campos `REF` nos parágrafos de descrição e os respectivos bookmarks foram actualizados para as novas referências, sem convertê-los em texto fixo. Os **45 campos REF** existentes mantêm destinos válidos.
4. A lista automática de figuras conserva **43 entradas** no total, agora com três entradas do capítulo 5.3 e duas entradas B.1/B.2 após A.8. O marcador de fim do campo `TOC` dessa lista foi reposicionado após B.2, para as duas entradas pertencerem ao próprio índice automático.
5. O índice geral inclui **9 APÊNDICE B — INTERFACES COMPLEMENTARES** e renumera **10 ANEXOS**. As legendas, a lista de figuras e os números de página em cache foram reconciliados com a renderização actual.
6. Permanecem **59 SEQ, 45 REF e quatro índices TOC** (geral, figuras, gráficos, quadros). Não foi executada uma regeneração integral automática destes índices em LibreOffice; já existia confirmação do autor de que os índices automáticos funcionam no Microsoft Word.

## Paginação observada

| Elemento | Página impressa no PDF revisto |
|---|---:|
| Início de 5.3 | 98 |
| Figura 5.3.1 — Parâmetros do grupo | 99 |
| Figura 5.3.2 — Contribuições | 101 |
| Figura 5.3.3 — Credenciais verificáveis | 103 |
| Início de 5.4 — Discussão dos resultados | **104** |
| Quadro 5.4.1 — Ensaios | 105 |
| Capítulo 6 — Conclusão | 110 |
| Referências bibliográficas | 112 |
| Apêndice A | 118 |
| **Apêndice B** | **130** |
| Figura B.1 — Autenticação/painel | 131 |
| Figura B.2 — Rotação/desembolsos | 133 |
| Anexos | 134 |

**Nota sobre contagem:** as capturas transferidas reduzem em quatro páginas a extensão do capítulo 5.3 no corpo principal; isto não equivale a eliminar quatro páginas do total do documento porque as imagens reaparecem no apêndice. A renderização final tem **156 páginas**, sem paginação incorrecta nas listas depois da intervenção.

## Testes de regressão

- Edição localizada **unicamente em `word/document.xml`**; nenhuma outra parte OOXML foi alterada, conforme comparação SHA-256 de todas as **129 partes** do DOCX de origem e de destino.
- Teste ZIP de integridade: **aprovado**.
- **48 media/imagens originais preservados byte a byte**; nenhuma captura foi comprimida, redesenhada ou apagada.
- **26 tabelas preservadas**, sem reescrita das respectivas células.
- **Quatro partes de comentários** do supervisor, cabeçalhos, rodapés, secções, estilos, relações e conteúdos dos Anexos preservados byte a byte.
- Campos: **59 SEQ**, **45 REF** e **quatro TOC**, sem referências a bookmarks em falta; os marcadores de campo do índice geral e da lista de figuras foram revistos.
- Renderização PDF a partir do DOCX revisto: **156 páginas**, nenhuma página vazia, **zero blocos de texto fora da área da página** no teste geométrico automatizado.
- Conferência visual da lista de figuras, índice geral, páginas 115–121, Apêndice A, Apêndice B (físicas 147–150) e início dos Anexos. Todas as cinco legendas estão legíveis e associadas à imagem correspondente.
- Confirmação das legendas no PDF: **5.3.1 física 116; 5.3.2 física 118; 5.3.3 física 120; B.1 física 148; B.2 física 150**. As páginas impressas reflectem a diferença de 17 páginas pré-textuais.

## O que não foi alterado

- Testes técnicos e resultados experimentais do capítulo 5.4.
- Conteúdo das entrevistas E1–E7 e os respectivos cartões com minimização de dados.
- Oito diagramas do Apêndice A.
- Referências bibliográficas, legislação e discussão das hipóteses.
- Margens, estilos de corpo, entrelinha e configuração de papel.

## Pendente antes da entrega institucional

**Verificação final no Microsoft Word após a reorganização**, actualizando os campos na *cópia de entrega* e confirmando que `Figura B.1`/`B.2`, `Apêndice B` e `Anexos` permanecem correctos após a actualização. A renderização foi efectuada por LibreOffice; não constitui teste do motor de campos do Word.

A resposta da FCTI ao pedido já enviado pelo autor sobre o manual vigente, a extensão e as datas da defesa continua pendente. Não se deve eliminar evidência técnica ou alterar a paginação com base numa norma ainda não confirmada para 2026.

**Estado:** reorganização editorial aplicada e validada tecnicamente; nova versão canónica de trabalho é o ficheiro referido acima.