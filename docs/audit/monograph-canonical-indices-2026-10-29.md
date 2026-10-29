# Continuação da auditoria formal — versão canónica sem gráficos

**Decisão do autor (29/10/2026):** `Monografia_Cientificamente_Consolidada_Alternativa_29102026.docx` (157 páginas) é a base canónica; a variante com Gráficos 4.2.1–4.2.3 não volta a ser usada.

## Revisão produzida no chat

`Monografia_Canonica_Sem_Graficos_Indices_Automaticos_29102026.docx`, derivada da base canónica; relatório: `Relatorio_Continuacao_Canonica_Indices_29102026.md`.

### Campo Word introduzido

- Índice geral: `TOC \\o "1-3" \\h \\z \\u`; preservadas as 91 entradas actualmente apresentadas.
- Lista de figuras: `TOC \\h \\z \\t "CaptionFigura,1"` com 43 legendas.
- Lista de gráficos: `TOC \\h \\z \\t "CaptionGrafico,1"` com **1 gráfico legítimo do capítulo 2**, sem reintroduzir os gráficos 4.2.
- Lista de quadros: `TOC \\h \\z \\t "CaptionQuadro,1"` com 15 legendas.
- Foram clonados os estilos de legendas para preservar sua tipografia; números individuais dos títulos e legendas ainda são texto estático e não são renumerados automaticamente.
- `updateFields` activado no pacote Word; a actualização interactiva do índice precisa ser verificada no Microsoft Word.

### QA reproducível

- **157/157 páginas**: mesma contagem e conteúdo de texto que a origem.
- **157/157 páginas visualmente idênticas**: rasterização comparada a resolução uniforme.
- **48 elementos de media** e **4 partes dos comentários** preservados byte a byte.
- 26 tabelas mantidas e gráficos/diagramas restantes intocados.
- Ficheiro Word revisado anexado apenas no ChatGPT, **não carregado no repositório do backend**.

### Pendências

1. Confirmar manual USTM/FCTI aplicável a 2026; extensão de **122 páginas entre Introdução e Referências** perante limite de 60 na cópia pública não autenticada.
2. Confirmar cronograma metodológico e APA 6/7; não reduzir arbitrariamente.
3. Actualizar campos no Microsoft Word e verificar comportamento de geração e manutenção do layout.
4. Se exigido, automatizar o número das próprias legendas (campos SEQ), que permanece texto.
5. Confirmar autoria e licenças de imagens externas.

Estado: **melhoria dos índices concluída tecnicamente; conformidade formal global ainda não comprovada.**
