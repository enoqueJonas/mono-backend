# Auditoria de regressão — índices automáticos após reorganização das telas

**Data:** 30 de Outubro de 2026.  
**Ficheiro:** `Monografia_Canonica_Telas_Reorganizadas_30102026.docx`  
**SHA-256:** `f1507fc0362226652affe1c709127a3faef0057a9442a11f27e831f94c7edea5`  
**Alteração da canónica:** nenhuma. Regeneração experimental realizada sem gravar o Word.

## 1. Resultado estrutural
- Capítulo 5.3 contém três interfaces centrais, numeradas **5.3.1–5.3.3**; Apêndice B contém as duas complementares, numeradas **B.1–B.2**.
- **43 legendas** `CaptionFigura` e **43 entradas** no índice automático: os identificadores coincidem exactamente.
- **Nenhuma referência textual** às antigas Figuras 5.3.4 ou 5.3.5.
- **45 campos REF**, todos com bookmarks existentes; **59 SEQ** e **4 TOC**.
- ZIP DOCX íntegro, **129 partes e 48 elementos multimédia**.

## 2. Regeneração dos quatro índices via LibreOffice UNO
O ficheiro foi aberto via UNO como read-only e invocado `DocumentIndexes.update()` para os quatro índices; exportou-se para PDF separado para comparação.

| Controlo | PDF com cache do Word | PDF após regeneração LibreOffice |
|---|---:|---:|
| Páginas físicas | **156** | **157** |
| Páginas da lista de figuras | 2 | **3** |
| Figuras 5.3.1–5.3.3 e B.1/B.2 | Correctas | Correctas |
| Páginas *impressas* B.1/B.2 | 131/133 | **131/133** |
| Apêndice B e Anexos no índice geral | Presentes | Presentes |

**Achado:** a actualização da lista de figuras no LibreOffice muda a composição/recuos das linhas, aumentando a matéria pré-textual numa página, mas não altera a numeração impressa do corpo nem perde entradas. Não está demonstrado que o Microsoft Word produza o mesmo resultado.

Um ensaio descartável alterando o recuo do estilo `TableofFigures` não eliminou a página adicional (continuou com 157 páginas). **Não modificar margens, estilos ou documento canónico com base só neste comportamento do LibreOffice.**

## 3. Critério antes da submissão
1. Abrir uma cópia da canónica no **Microsoft Word**.
2. Actualizar *índice completo*, tanto o geral como a lista de figuras; não apenas números de página.
3. Confirmar as **43 figuras**, com as entradas 5.3.1–5.3.3 e B.1/B.2, sem repor 5.3.4/5.3.5.
4. Conferir início de Discussão, Apêndice B, páginas B.1/B.2 e Anexos, e PDF exportado pelo Word.
5. Se a lista passar a três páginas, aferir a formatação segundo o **manual FCTI vigente**, ainda pendente de resposta, e não eliminar conteúdo para forçar 156 páginas.

**Estado:** reorganização e remissões correctas; apenas a estabilidade de paginação na actualização no Microsoft Word requer verificação final.