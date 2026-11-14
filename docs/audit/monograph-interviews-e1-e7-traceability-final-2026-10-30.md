# Auditoria metodológica das entrevistas E1–E7 e rastreabilidade dos requisitos

**Data:** 30 de Outubro de 2026  
**Entrada:** `Monografia_Canonica_Fontes_Xitique_Revistas_30102026.docx` — 156 páginas, SHA-256 `a8ea2364f33d8bbdfce1188e0450f2bbbbf5608015c57d2ab607451bde6063fa`.  
**Saída:** `Monografia_Canonica_Entrevistas_Rastreabilidade_Revista_30102026.docx` — **156 páginas**, SHA-256 `e2c3fca4a369b51a3aa2386119b8aa7fe2ec8c8dd311d2283c3560e98751c9db`.

## 1. Material primário efectivamente disponível

O anexo da monografia (páginas impressas **137–139**, físicas **154–156** no PDF de entrada) contém **sete fichas gráficas** com perguntas e respostas resumidas, duas de tesoureiros/coordenadores e cinco de membros. As fichas estão **incorporadas como imagens**, não como texto editável/pesquisável do Word; esta constatação foi confirmada pela extracção do texto das páginas do PDF, que só devolve cabeçalho e número de página nas duas últimas páginas. **Uma ficha-resumo não permite garantir a literalidade, integralidade ou contexto das respostas originais.** Não há prova fornecida nesta monografia sobre a existência ou inexistência de gravações, notas de campo ou consentimentos armazenados noutro local.

- E1 (tesoureira): anotação manual em caderno, perda de registos, discussão sobre confirmação de pagamentos, consulta de outros membros e interesse em confirmação e consulta.
- E2 (tesoureiro): ficheiro Excel no telefone, perda de dados após troca de aparelho, dificuldades relacionadas com conhecimento da posição da rotação.
- E3 (membro): confiança na coordenadora sem possibilidade de verificação independente; interesse em consultar contribuições e ordem de recebimento.
- E4 (membro): referência a esquecimento de pagamento e interesse em lembretes.
- E5 (membro): uso de M-Pesa sem smartphone, necessidade de mensagens e dificuldades com aplicações. **Não confundir uso de carteira móvel com posse de smartphone**.
- E6 (membro): dúvidas sobre quantias entregues, confirmação por caderno e procura de comprovativos.
- E7 (membro): nega ocorrência de fraude, relata desaparecimento de registos e recorre à confiança no coordenador.

Esta síntese omite intencionalmente combinações identificadoras de idade, sexo e profissão, que constam das imagens e podem criar risco de reidentificação em grupos de pequena dimensão.

## 2. Matriz de suporte qualitativo e rastreabilidade temática

| Tema exploratório | Fichas com elementos relevantes | Requisitos existentes com relação plausível | Limite interpretativo |
|---|---|---|---|
| Fragilidade/recuperação de registos | **E1, E2, E7** | RF-018 (manter histórico), RF-029 (consulta auditável) | Não prova desaparecimento frequente nem recuperação garantida após desastre |
| Verificação de contribuição e comprovativo | **E1, E3, E6** | RF-019 (consultar histórico), RF-020 (comprovativo), RF-029 (consulta) | Não demonstra redução empírica de conflitos/fraude; E3 relata impossibilidade de verificar, não fraude |
| Ordem de recebimento/rotação | **E2, E3** | RF-014 (definir ordem), RF-015 (consultar ordem) | Só indica necessidades situadas; não valida regras de rotação de todos os grupos |
| Acesso e competências digitais | **E2, E4, E5** | Critérios de usabilidade, RF-024 e RF-025 (notificações) | Diferenças entre uso de smartphone, utilização de M-Pesa e literacia digital; sem prevalências |
| Consulta e notificações | **E1, E3, E4, E5, E6, E7** | RF-019, RF-024, RF-025 e RF-029 | Interesse expressado não é prova de adopção ou implementação completa |
| Confiança interpessoal/resolução de divergências | **E1, E3, E6, E7** | RF-020, RF-029 e procedimentos de resolução | Não permite medir confiança, incumprimento ou efeito social longitudinal |

**Nota de causalidade:** os códigos RF são requisitos **documentados no manuscrito**. Esta matriz evidencia **compatibilidade de temas**; não comprova que esses requisitos tenham sido *descobertos originalmente* nas entrevistas, nem que todas as funcionalidades tenham sido demonstradas em laboratório.

## 3. Discrepância sistemática descoberta nas fichas de requisitos

Na secção de requisitos, **30 células** apresentavam `Fonte: Análise documental e caso de estudo`, embora o capítulo 3 afirme não ter delimitado qualquer caso/organização concreta. Foi substituído em cada célula por `Fonte: Análise documental e concepção`, formulação coerente com o processo documental e com a concepção do protótipo descritos no capítulo 3. A entrada de proveniência para **RF-022** foi alterada de `Fonte: Análise documental e entrevistas` para `Fonte: Análise documental; entrevistas (contexto)`, explicitando que as entrevistas *contextualizaram* a necessidade, sem serem prova exclusiva da origem do requisito.

O novo texto do **capítulo 3** explicita que os anexos contêm fichas sintéticas em imagem, sem metadados suficientes para reproduzir o trabalho de campo; descreve a codificação temática com códigos E1–E7 e distingue suporte contextual de validação funcional. A secção **5.4.6** passa a identificar a auditabilidade qualitativa como limitação adicional, sem questionar a realidade da recolha nem inventar resultados.

## 4. Pendências que só documentação original pode resolver

1. **Datas, locais e modo de realização** das entrevistas: recolha presencial/remota; datas exactas ou intervalo comprovado; localidade e critério de escolha.
2. **Recrutamento e amostra:** participantes convidados, critérios de elegibilidade, número de grupos de Xitique abrangidos, forma de obter permissão para entrevista.
3. **Consentimento e privacidade:** forma como foi obtido e documentado o consentimento; autorização de divulgação das sínteses; avaliar a remoção/generalização de idade e profissão combinadas, para evitar reidentificação.
4. **Rastreio das fontes primárias:** notas originais, gravações/transcrições se existirem, transformação das respostas integrais em cartões sintéticos, identidade do codificador e procedimento de revisão temática.
5. **Separação metodológica:** não declarar amostragem representativa, saturação teórica, comparação geográfica urbana/periurbana/rural, adopção efectiva, redução da fraude, conhecimento de literacia digital da população nem avaliações de UX com utilizadores reais a partir destas sete fichas.

**Importante:** não foram criados registos falsos para preencher essas lacunas. A ausência dessas informações no DOCX **não demonstra que nunca tenham sido recolhidas**; significa que não estão documentadas nos materiais auditados.

## 5. Controlo do Word e resultados da renderização

- **Alteração OOXML limitada a `word/document.xml`**. Todos os restantes ficheiros internos foram preservados binariamente.
- Mantidas **48 partes multimédia**, **26 tabelas**, **4 partes de comentários** do Word e os campos **59 SEQ / 45 REF / 4 TOC**; ZIP testado com êxito (`testzip() = None`).
- Nenhuma imagem de entrevista foi editada, nenhuma pergunta/resposta foi inventada, nenhum comentário apagado.
- **Renderização PDF:** **156 páginas**, iguais à entrada (156); a versão inicial de ensaio chegou a produzir **157 páginas**, mas a redacção foi condensada antes da versão aprovada para preservar a paginação sem omitir as limitações.
- **Comparação integral de texto e raster** (156 pares de páginas, mesma resolução): **diferenças apenas nas páginas físicas 67–70, 81–89 e 130 (14 páginas)**; outras **142 páginas idênticas**.
- **Inspecção visual das páginas afectadas:** verificação em contacto de 14 páginas; revisão ampliada das páginas 67 (metodologia) e 130 (limitações); sem sobreposição, clipping ou cortes.
- **Controlo geométrico:** zero blocos de texto fora da área útil das 156 páginas. As figuras/imagens anexas E1–E7 não sofreram alterações.
- **Índices e paginação:** Introdução, Capítulo 3, Discussão, Referências, Apêndice A e Anexos mantiveram as páginas da versão-base; nenhuma actualização global de TOC foi guardada. O autor já confirmou o funcionamento do índice no Microsoft Word.

## 6. Estado para fecho

**Concluído:** reconciliação temática com E1–E7, distinção entre fichas sintéticas e transcrições, correcção das **30 origens de requisitos** e RF-022, explicitação de limitações na metodologia/discussão.  
**Aberto:** provas primárias de recolha/consentimento; risco de identificabilidade indirecta; resposta oficial USTM/FCTI sobre manual e extensão.  
**Proibido no fecho:** presumir que houve fraude comprovada, que as entrevistas provam causalidade, que o protótipo foi validado em produção ou que existem registos de consentimento sem os ver.