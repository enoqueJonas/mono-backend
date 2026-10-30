# Auditoria de privacidade dos registos E1–E7

**Data da revisão:** 30 de Outubro de 2026  
**Base canónica de trabalho:** `Monografia_Canonica_Entrevistas_Rastreabilidade_Revista_30102026.docx` (156 páginas; SHA-256 `e2c3fca4a369b51a3aa2386119b8aa7fe2ec8c8dd311d2283c3560e98751c9db`)  
**Nova versão:** `Monografia_Canonica_Entrevistas_Privacidade_Revista_30102026.docx` (156 páginas; SHA-256 `656a60ec72d15c6d64b22488e395cf17d2a6c30e67b66d7008161dbcbaef5c65`)

## 1. Achado

As sete fichas de síntese de entrevistas E1–E7, incorporadas nos Anexos como imagens rasterizadas, apresentavam uma linha de «Perfil» com **combinações de idade, género, profissão e, em alguns casos, características da função e actividade no grupo de poupança**. Nenhuma ficha mostrava nome civil, mas, numa comunidade de pequena dimensão, essas combinações podem permitir **reidentificação indirecta**. Não é necessário divulgar os pormenores pessoais na monografia quando a análise científica se centra em experiências com registos, contribuições, rotação e acesso digital.

**Limite ético:** não foi possível comprovar, a partir do material fornecido, a existência, o teor ou a autorização de divulgação específica do consentimento. Isto não prova que o consentimento não tenha sido obtido. O processo de recolha, recrutamento e armazenamento das fontes primárias continua sujeito a validação pelo autor.

## 2. Tratamento aplicado

- As **sete imagens** (`word/media/image39.png` a `image45.png`) foram regravadas, substituindo unicamente a faixa que apresentava a caracterização individual por «Perfil: dados de caracterização individual omitidos para a submissão».
- Mantidas integralmente as **perguntas e respostas**, a ordem E1–E7, os papéis «Tesoureira/Tesoureiro/Membro» e o formato gráfico dos cartões.
- A remoção foi realizada **nos próprios pixels das imagens** — não foi simplesmente sobreposto um rectângulo no PDF ou colocada uma caixa invisível no Word, métodos que poderiam manter visíveis os dados quando a camada fosse removida.
- O tratamento **não modifica** ou infere consentimento, datas, localidades, selecção de participantes ou resultado da pesquisa.
- As características individuais continuam na cópia de referência anterior; **não colocar essa cópia integral, imagens originais ou relatórios com perfis em repositórios públicos**. O acesso às fontes primárias deve ser restrito, em conformidade com os termos reais do consentimento.

**Advertência:** a nova versão faz **minimização de identificadores indirectos**, não certifica anonimização absoluta. O conteúdo das respostas pode conter contexto reconhecível por terceiros que conheçam os grupos. Uma avaliação ética final deve considerar o uso institucional e eventual publicação pública do PDF.

## 3. Regressão OOXML e visual

| Controlo | Resultado |
|---|---|
| Páginas em PDF após exportação LibreOffice | **156**, igual à origem |
| Diferença visual em renderização integral (156 pares) | **Somente páginas físicas 154, 155 e 156** |
| Restantes páginas | **153 páginas pixel a pixel idênticas** à mesma resolução de comparação |
| Texto extraído de 156 páginas | **Idêntico** à origem; respostas não editadas |
| Alteração interna DOCX | **Só as 7 imagens** `image39.png`–`image45.png` |
| Imagens Word | **48 no total; 7 revistas e 41 binariamente idênticas** |
| Tabelas | **26**, inalteradas |
| Comentários do supervisor | **4 partes XML**, binariamente idênticas |
| Campos automáticos | **59 SEQ, 45 REF, 4 TOC**, idênticos |
| Ficheiros internos ZIP | **129**, integridade ZIP validada |
| Texto fora das páginas | **0 blocos** |

O código da alteração insere uma substituição selectiva da linha do «Perfil» em cada PNG, compara os pixels alterados com os originais e exige que **qualquer mudança esteja estritamente dentro da mesma faixa** do cartão. Essa verificação demonstrou que nenhuma área contendo respostas sofreu alteração gráfica.

## 4. Questões metodológicas que continuam por provar

1. O autor deve apresentar, se existirem, registos **verificáveis** do período, locais e modo de recolha das entrevistas E1–E7.
2. Confirmar, com documentos reais, selecção dos entrevistados, número de grupos representados e relação do entrevistador com os participantes.
3. Identificar como foi obtido e documentado o **consentimento**, sobretudo a divulgação das respostas resumidas à universidade ou a terceiros.
4. Verificar o arquivo original: notas de campo, gravações, transcrições ou fichas originais (caso existam) e como se passou dessas fontes para os sete cartões.
5. Confrontar a eventual publicação pública da monografia com a confidencialidade assumida na recolha. Se não houver prova de autorização para divulgar excertos potencialmente reconhecíveis, solicitar orientação ética/institucional antes da distribuição pública.

**Não declarar:** que as fichas são transcrições integrais; que a amostra é representativa; que existiu saturação; que se mediu fraude; que houve consentimento informado devidamente arquivado; que há anonimato absoluto.

## 5. Fontes metodológicas consultadas

- UK Data Service, *Anonymisation for text data*: https://ukdataservice.ac.uk/learning-hub/data-producer-support/preparing-data-for-sharing-and-reuse/anonymising-data-and-protecting-participants/anonymisationfortextdata/ — risco de identificação indirecta pela combinação de pormenores contextuais.
- EQUATOR Network / Tong et al. (2007), *Consolidated Criteria for Reporting Qualitative Research (COREQ)*: https://equator-network.org/reporting-guidelines/coreq/ — orientação de reporte para entrevistas e grupos focais, **não norma institucional obrigatória da USTM**.
- UK Statistics Authority, *Ethical considerations associated with qualitative research methods*: https://uksa.statisticsauthority.gov.uk/publications/ethical-considerations-associated-with-qualitative-research-methods/pages/6/ — perigo de identificação dedutiva em relatos qualitativos.

## 6. Estado de submissão

**Concluído:** minimização de identificadores nas fichas do DOCX para submissão, conservação integral das respostas, regressão de 156 páginas e integridade OOXML.  
**Pendente:** comprovação documental do consentimento e dos metadados da recolha; regras institucionais FCTI, já solicitadas por e-mail pelo autor; apreciação de confidencialidade se o PDF for publicamente distribuído.  
**Nova canónica de trabalho:** `Monografia_Canonica_Entrevistas_Privacidade_Revista_30102026.docx`.