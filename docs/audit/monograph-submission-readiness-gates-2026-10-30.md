# Porta de submissão — auditoria consolidada da monografia, 30/10/2026

## Referência exacta
**Canónica de trabalho, não alterada nesta auditoria:** `Monografia_Canonica_Indices_Conferidos_30102026.docx` (158 páginas); SHA-256 `b3ae57beeda7acc476fe470f9ed542c06f9d962f4f11b6ba4183e82e62d63861`.

Documento analisado a partir do DOCX local recuperado e PDF com **158 páginas** já renderizado. Não se efectuou actualização simultânea de campos nem substituição do DOCX. Este relatório consolida o estado **sem reabrir as secções científicas anteriormente corrigidas**.

## 1. Reconciliação adicional das legendas e listas

Comparação automatizada das listas de páginas físicas 9–12 com os inícios de legenda no corpo, através da extracção de texto do PDF, seguida de inspecção visual da lista de quadros (página física **12**):

| Lista | Entradas no índice | Legendas únicas presentes no corpo | Número e página coincidem? |
|---|---:|---:|---|
| Figuras | **43** | **43** | **43/43** |
| Quadros | **15** | **15** | **15/15** (a numeração de Quadro 2.7.3 foi conferida visualmente: p. 44) |
| Gráficos | **1** | **1** | **1/1** |
| **Total** | **59** | **59** | **59/59** |

**Achados de apresentação:** a lista de quadros tem duas entradas cuja tabulação pontilhada não aparece adequadamente na renderização LibreOffice:
- `Quadro 2.3.1`, página correcta **19**: legenda longa e número final sem pontilhado visível, embora o parágrafo contenha tabulação automática.
- `Quadro 2.7.3`, página correcta **44**: nome extenso, fonte incorporada na legenda, número final colado ao último ponto: `(2021).44`. Fonte e número estão presentes, mas há defeito visual evidente.

**Causa estrutural observada:** ambos os parágrafos usam estilo `TableofFigures`, tabulação à direita com `w:leader="dot"` e marcações `<w:tab/>`. A ausência visual de pontos parece resultar da combinação de legenda muito extensa e quebra de linha no motor de layout, **não** da ausência de tabulação nem de erro no número da página. **Não substituir tabulação por pontos escritos manualmente** antes do ensaio no Microsoft Word; isso seria uma correcção frágil e sujeita a regeneração automática.

## 2. Estado dos índices e referências
- **4 campos TOC**, **59 SEQ** e **45 REF** preservados (auditoria anterior).
- 4 erros efectivos no índice geral **já corrigidos** na última versão canónica: 1.5 (6), 2.3.1 (12), 2.3.4 (15) e 6.2 (115).
- Ensaio de actualização integral **apenas em LibreOffice** alterou 158→159 páginas e converteu romanos preliminares no índice; portanto a **interoperabilidade de campos continua sem aprovação no Microsoft Word**.
- **59/59 etiquetas e números de página da lista de figuras/quadros/gráficos foram reconciliados** na versão canónica actual, sem mudar o conteúdo do ficheiro.

## 3. Conformidade institucional: bloqueio externo

**Fontes oficiais verificadas no próprio dia**:
1. USTM, regras da Conferência Científica 2026, 08/04/2026, declaram APA **6.ª edição actualmente em uso** e remetem ao Manual de Investigação Científica de 2018: https://conferencias.ustm.ac.mz/index.php/IIICNDAMS2026/about . **Nota de escopo:** regras para submissões de artigos da conferência, não prova vinculativa para monografia da FCTI.
2. USTM, workshop de 03/04/2025: manual harmonizado APA **7.ª edição era proposta** a aprovar: https://ustm.ac.mz/index.php/component/content/article/27-workshop?Itemid=101&catid=36 . Não foi localizada publicação oficial de entrada em vigor da versão.
3. Página oficial de contactos da USTM: **fcti@ustm.ac.mz; +258 84 309 2249**: https://www.ustm.ac.mz/index.php/component/sppagebuilder/page/37 . **Nota:** página de perfil FCTI também exibe +258 84 309 224 (aparentemente truncado); preferir contactos gerais actualizados e confirmar ao telefonar.
4. Cópia pública **não autenticada** do manual de Agosto de 2018 aponta, no anexo FCTI, **60 páginas da Introdução às Referências**. O PDF canónico actual tem **123 páginas nesse intervalo (páginas impressas 1–123; físicas 18–140)**. **Não declarar não-conformidade vigente** sem manual oficial 2026, autorização da FCTI e regras para anexos/diagramas.
5. Não foi encontrado em busca oficial um calendário específico de defesa FCTI para o remanescente de **2026**. O calendário público da FCTI disponível é anterior; **não inferir prazos reais** de defesa.

### Resposta escrita que é necessária
- Manual e anexo oficial aplicáveis à FCTI para monografias de Licenciatura em Desenvolvimento de Softwares entregues em 2026.
- Se **60 páginas** continuam obrigatórias, contagem exacta, excepções/apêndices para diagramas, código e validação experimental.
- Versão APA (6/7), obrigatoriedade de cronograma no *relatório final* versus no projecto, e qualquer regra de orçamento.
- Prazo **efectivo** de entrega, apreciação pela Comissão Científica, datas ainda disponíveis de defesa em 2026, documentos exigidos, condições para substituição de supervisor quando falta resposta.
- Quem tem competência para aprovar afastamento justificado de regras gerais, caso o manual permita.

## 4. Outras pendências externas, sem inferências
- Figuras externas: autorização de reprodução ou base legal específica da 2.4.2 e outras imagens originais; **citação bibliográfica não é licença**.
- Entrevistas E1–E7: selecção, datas, localidade, número de grupos, consentimento, nível de identificação indirecta; **não inventar dados de campo**.
- Microsoft Word: inspeccionar as duas entradas visuais do índice de quadros antes/depois da regeneração, as páginas preliminares em romano, lista de figuras, apêndices e comentários do supervisor.

## 5. Decisão operacional
**Não foi produzida nova versão canónica neste passo**: as 59 legendas e páginas estão correctas e a irregularidade visual depende do motor de actualização do Word. Editar caches manualmente agora poderia introduzir novas diferenças que uma actualização futura desfaria. Prioridade: pedir validação **institucional por escrito**, realizar ensaio em cópia no **Microsoft Word para Mac**, obter evidência do resultado, e só depois efectuar a última correcção editorial.

Não encerrar as issues #1, #7, #15 e #17 com base nesta revisão. As correcções históricas de hipóteses, DID/VC e contratos inteligentes permanecem preservadas.
