# Auditoria de conteúdo académico — remoção de elementos operacionais

**Data:** 30 de Outubro de 2026.

## Documento de origem

`Monografia_Canonica_Terminologia_Visual_Uniformizada_30102026(3).docx`, **fornecido pelo autor nesta etapa**. Foi utilizado directamente, sem regressar à versão canónica anterior nem repor imagens antigas. A versão enviada renderizava **159 páginas** e continha 47 ficheiros multimédia. O pacote de origem não continha as quatro partes de comentários do supervisor existentes em algumas versões anteriores; não foram restauradas, para respeitar o documento enviado.

## Documento revisto

`Monografia_Canonica_Revisao_Cientifica_30102026.docx`, **158 páginas** na exportação de controlo LibreOffice, SHA-256 **`94204bcba3bf67a8c88557005e563fb659d149fe2c8cad2031ac6ad6fb8c4feb`**.

## Alterações

1. **Removido integralmente o Quadro 5.4.1** com os códigos TA/IT/CT, bem como a legenda, a entrada da Lista de Quadros e as remissões correspondentes na discussão das hipóteses.
2. **Removido o parágrafo com o identificador do commit, a branch e as referências a PRs**, substituído por apresentação científica dos resultados laboratoriais observados.
3. **Removidos os identificadores de execução do GitHub Actions e os caminhos `docs/audit/...`**, não adequados como prosa académica no corpo da monografia. Estes detalhes mantêm-se nos registos técnicos externos, mas não são reproduzidos no DOCX.
4. Reescrita a descrição do ensaio de recuperação de inconsistência PostgreSQL/blockchain em linguagem científica, sem enumeração de casos de teste internos e sem pretender provar atomicidade universal.
5. Revisto o parágrafo do procedimento experimental para apresentar níveis de avaliação sem detalhes irrelevantes de CI ou identificação de execução.
6. Uniformizada a formulação de uma conclusão: 'em ambiente controlado', sem referência a uma 'versão experimental de desenvolvimento' ligada ao fluxo Git.
7. **Actualizados 60 números em cache** do índice geral, da Lista de Figuras e da Lista de Quadros, com base nas páginas realmente renderizadas. Os quatro índices automáticos e os seus campos foram mantidos.

## Critério científico

Mantiveram-se as conclusões directamente sustentadas pelos ensaios: 120 testes de aplicação e 14 testes de contratos aprovados, um único cenário integrado PostgreSQL/Ganache, emissão e verificação de credenciais, rejeição de adulteração, controlo de autorizações, revogação e reconciliação após falha simulada. O texto continua a reconhecer que não foram testados pagamentos móveis reais, redução de fraude em campo nem reconhecimento jurídico da solução.

## Controlo de regressão

- **Somente `word/document.xml` mudou**. Todas as outras partes da versão fornecida são binariamente idênticas, incluindo as **47 imagens** e os dados SmartArt. Os gráficos alterados pelo autor não foram modificados.
- DOCX ZIP válido; mesmo conjunto de **112 partes**.
- **25 tabelas** (26 no documento de origem), sendo removida apenas a tabela solicitada.
- **58 campos `SEQ`** (= 43 figuras + 14 quadros + 1 gráfico); **43 `REF`**; **4 `TOC`**. Campos e etiquetas remanescentes preservados.
- Renderização PDF final: **158 páginas**, sem páginas vazias e **0 blocos de texto fora da página**. Páginas de controlo inspeccionadas: índice geral, Lista de Figuras, Lista de Quadros, secção 5.4.1, discussão de hipóteses, conclusão, apêndices e anexos.
- Segunda passagem do reconciliador de índices: **0 novas alterações**. As duas correspondências não extraídas automaticamente (secções 2.3.1 e 2.3.8) já tinham os números correctos.
- Pesquisa no Word e no PDF: **0 ocorrências** de `commit`, `branch`, `GitHub Actions`, `PRs #`, `docs/audit`, `Quadro 5.4.1` ou identificadores TA-01/IT-01/CT-01. Permanecem links públicos GitHub apenas como **fontes bibliográficas legítimas**, sem relação com o fluxo de desenvolvimento do protótipo.

## Limitação independente

O teste foi efectuado pela exportação do LibreOffice. A actualização integral dos campos no Microsoft Word pode ter um comportamento de paginação diferente e deve ser conferida apenas antes da submissão definitiva. O manual institucional aplicável continua pendente de confirmação pela FCTI.

**Estado:** nova base canónica de trabalho: o documento fornecido pelo autor, com conteúdo operacional removido e alterações às figuras preservadas.