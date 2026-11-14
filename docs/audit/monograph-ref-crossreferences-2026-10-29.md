# Referências cruzadas REF — monografia canónica (29/10/2026)

## Base
O autor escolheu exclusivamente a monografia **sem os Gráficos 4.2.1–4.2.3**. A nova revisão deriva de `Monografia_Canonica_Legendas_Automaticas_29102026.docx`.

**Entregáveis na conversa:**
- `Monografia_Canonica_Referencias_Cruzadas_Automaticas_29102026.docx`
- `Relatorio_Referencias_Cruzadas_Canonica_29102026.md`

## Alteração efectuada
- [x] Foram introduzidos **59 marcadores Word** (`bookmarkStart`/`bookmarkEnd`) cobrindo o prefixo numérico da secção e o campo `SEQ` da legenda.
- [x] Foram substituídas **45 remissões numéricas**, em 43 parágrafos do corpo/apêndices, por campos nativos `REF` que apontam para os marcadores exactos das legendas.
- [x] Intervalos `Figuras A.2 a A.4` e `Figuras A.5 a A.8` têm campos nos dois extremos.
- [x] Não foram encontradas referências numéricas órfãs nesse conjunto.
- [x] A referência `Figura 2.1.1` estava correcta na origem; uma pré-visualização truncada sugerira falsamente `Figura 2.1.`. Não foi necessária correcção do texto.
- [x] Preservados os **59 SEQ** e os **4 TOC** da etapa anterior; prefixos e rótulos estão em texto normal.

## Evidência de regressão
- [x] **Actualização real em cópia de ensaio LibreOffice UNO** com `getTextFields().refresh()`: os **45 valores REF** permaneceram exactamente iguais; sem erros de marcador inexistente.
- [x] Pacote Word final: **apenas `word/document.xml` alterado**; 48 ficheiros media, 4 partes de comentários e 26 tabelas intactos.
- [x] **157 páginas** renderizadas (157 antes). Todas as palavras do PDF permanecem iguais em 157/157 páginas; em seis páginas o extractor de texto PDF mostrou ligeira alteração de espaços na separação dos campos, sem alteração de palavras.
- [x] Variação geométrica máxima das palavras inferior a 1 pt, sem deslocação de linhas nem quebra adicional; folhas de contacto e páginas relevantes revistas.
- [x] A cópia regravada pelo LibreOffice **não foi usada** como nova versão canónica devido ao risco já demonstrado de perda de metadados modernos dos comentários.

## Continua pendente
- [ ] Teste de actualização simultânea de `SEQ`, `REF` e `TOC` em **Microsoft Word**.
- [ ] Confirmação do manual USTM/FCTI 2026, limite de páginas, cronograma e edição APA aplicável.
- [ ] Confirmação de autoria/licença das figuras externas.
- [ ] Os prefixos da numeração são fixos por secção; caso uma legenda mude de secção, ajustar manualmente o prefixo e a série `SEQ`.

**Estado:** referências cruzadas implantadas e validadas em ambiente de ensaio; nenhuma mudança no texto científico nem na decisão de excluir os três gráficos hipotéticos.