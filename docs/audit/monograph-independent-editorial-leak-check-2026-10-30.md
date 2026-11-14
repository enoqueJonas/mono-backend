# Verificação independente de vestígios editoriais e operacionais

**Data:** 30 de Outubro de 2026  
**Documento analisado:** `Monografia_Canonica_Revisao_Cientifica_30102026.docx`  
**SHA-256:** `94204bcba3bf67a8c88557005e563fb659d149fe2c8cad2031ac6ad6fb8c4feb`  
**Documento-base:** versão mais recente enviada pelo autor, com gráficos alterados, após remoção do Quadro 5.4.1 e referências operacionais.

## Método de verificação

1. Leitura integral automatizada do texto visível em **1.622 parágrafos não vazios**, incluindo células de tabelas, legendas e os índices existentes, directamente no `word/document.xml` do DOCX.
2. Pesquisa adicional em **todas as partes XML do pacote Word** e nos textos extraídos de **todas as 158 páginas** do PDF obtido mediante nova conversão isolada do documento actual.
3. Pesquisa por identificadores de commits (40 e 64 caracteres hexadecimais), `commit`, `branch`, `pull request`, `PR #`, `workflow`, `GitHub Actions`, `CI/CD`, `docs/audit`, `audit/chain`, `Issue #`, `SHA-256`, códigos `TA-01`/`IT-01`/`CT-01`, `Quadro 5.4.1`, e instruções editoriais como `a pedido do autor`, `revisão editorial`, `relatório de auditoria`, `corrigimos`, `ChatGPT`, `OpenAI` ou `texto interno`.
4. Inspecção visual das **páginas físicas 124 e 125**, nas quais começa a secção 5.4 (página impressa 105), e conferência contextual da discussão dos resultados, hipóteses, limitações e conclusões.
5. Inspecção estrutural do DOCX e das coordenadas de blocos de texto de todas as páginas do PDF.

## Resultados

| Controlo | Resultado |
|---|---:|
| Ocorrências de marcadores operacionais de desenvolvimento | **0** |
| Ocorrências do Quadro 5.4.1 e códigos internos de casos | **0** |
| Ocorrências de instruções editoriais ou identificadores do assistente segundo as expressões pesquisadas | **0** |
| Referências ao GitHub no PDF | **2 páginas**, apenas na bibliografia como URLs de ferramentas/projectos terceiros, não de PRs da monografia |
| Páginas do PDF final | **158** |
| Páginas vazias | **0** |
| Blocos de texto fora da área da página | **0** |
| Erros ZIP | **0** |
| Ficheiros multimédia no DOCX | **47** |
| Tabelas Word | **25** |
| Legendas de figuras (`CaptionFigura`) | **43** |
| Campos SEQ / REF / TOC | **58 / 43 / 4** |
| Partes de comentários do supervisor | **0 na versão fornecida como base**, não removidas nesta verificação |

As referências a **avaliação experimental**, **dados sintéticos**, **Django**, **Ganache**, **PostgreSQL**, **Solidity** e **120/14 testes aprovados** são conteúdos científicos pertinentes para descrever o objecto, método e resultados da investigação; não são vestígios do diálogo com o assistente. A palavra «auditoria» ocorre legitimamente em explicações sobre segurança e rastreabilidade.

A secção 5.4.1 já apresenta os ensaios em linguagem académica, sem identificadores de execução, commits ou PRs. O Quadro 5.4.1 foi eliminado sem deixar uma entrada na lista de quadros ou uma remissão no corpo do texto.

## Limites da conclusão

A auditoria **confirma a ausência das classes de vestígios pesquisadas** no conteúdo textual do DOCX e do PDF renderizado; não pode demonstrar logicamente a ausência de qualquer formulação editorial desconhecida. Não constitui revisão científica exaustiva das 69 referências, certificação de correspondência entre o protótipo e todas as afirmações, aprovação institucional da FCTI nem actualização final dos índices no Microsoft Word. A validação do fluxo real frontend/backend permanece independente.

**Decisão:** sem nova alteração ao DOCX. A versão auditada continua a ser a canónica de trabalho; qualquer revisão futura deve partir deste mesmo ficheiro, que contém as figuras alteradas pelo autor.