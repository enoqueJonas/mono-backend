# Reparação estrutural do índice da monografia canónica — 29/10/2026

## Base canónica e alcance
O autor definiu como única versão canónica a monografia **sem os Gráficos 4.2.1–4.2.3**. Esta intervenção parte do ficheiro `Monografia_Canonica_Referencias_Verificadas_29102026.docx`; entrega na conversa: `Monografia_Canonica_Indice_Estrutural_Corrigido_29102026.docx`, 157 páginas. Relatório detalhado no chat: `Relatorio_Correccao_Estrutural_Indices_29102026.md`.

## Defeitos reproduzidos
O LibreOffice Writer UNO regenerava quatro índices, mas numerava indevidamente o título do índice geral (resultando em `1 ÍNDICE` e `2 INTRODUÇÃO`) e incluía cinco fluxos alternativos do caso de uso UC04 como entradas do índice (`A1` a `A5`).

## Correcção
- Separado o título de índice do controlo `w:sdt` anterior, com estilo `TOC Heading`, numeração 0 e sem nível de contorno.
- Mantido o campo `TOC` de Word, removida a opção redundante `\\u`.
- Nos cinco parágrafos de fluxos alternativos dentro da tabela UC04, alterado apenas `outlineLvl` de 2 para 9, sem mudar estilo aparente, texto ou desenho.
- Mantidas as outras três listas automáticas de figuras, gráficos e quadros.

## Testes e resultado
- Regeneração real em LibreOffice UNO (`getDocumentIndexes().getByIndex(i).update()` para os quatro índices) numa cópia experimental: `ÍNDICE` sem número, `INTRODUÇÃO` como capítulo 1, cinco fluxos A1–A5 ausentes; os títulos de apêndice e anexos continuam presentes.
- Paginação após actualização no LibreOffice: **159 páginas** por reflow das listas, sobretudo lista de figuras (2→3 páginas).
- A cópia experimental salva pelo LibreOffice perdeu `commentsIds.xml` e `commentsExtensible.xml`; **não foi entregue como monografia**.
- A versão canónica foi recomposta directamente a partir do pacote DOCX original, alterando-se exclusivamente **`word/document.xml`**. Os **48 ficheiros `word/media`**, os **quatro ficheiros de comentários** e todos os restantes componentes permaneceram idênticos por SHA-256.
- Conteúdo visível: todos os **4.881 segmentos `w:t`** iguais entre origem e entrega; **26 tabelas** mantidas.
- Renderização de entrega: **157 páginas**; **157 PNGs gerados**; inspeccionados títulos/listas, texto e inexistência de blocos textuais fora dos limites.

## Ainda por verificar
- [ ] Actualização em **Microsoft Word** (não disponível no ambiente): confirmar entradas, campos e paginação real após actualizar todos os índices.
- [ ] Normalização da numeração individual das legendas (os números `SEQ` ainda são estáticos).
- [ ] Manual oficial da **USTM/FCTI** aplicável a 2026 (60 páginas, cronograma e APA).
- [ ] Fontes/licenças de algumas imagens restantes.

**Estado:** reparação estrutural validada em LibreOffice; não declarar conformidade integral com Microsoft Word ou normas institucionais. Não reintroduzir gráficos hipotéticos.