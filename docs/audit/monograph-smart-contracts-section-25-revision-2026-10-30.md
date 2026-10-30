# Revisão crítica da secção 2.5 — contratos inteligentes e automatização cooperativa

**Data:** 30 de Outubro de 2026  
**Documento de origem:** `Monografia_Canonica_Figura_2_4_4_Revista_30102026.docx`  
**Documento actualizado:** `Monografia_Canonica_Contratos_Inteligentes_Revistos_30102026.docx`  
**SHA-256 da origem:** `c0c154fabb1465525013f5e7ffa3aeab256760e14c7ff645bdcd2fed1f61c2c5`  
**SHA-256 de saída:** `3d27ec1d39c9bcc8bfa9fe3de237f760a5588bbde3d706f9558fafd0fdcb6398`

## Fundamentação
A antiga secção 2.5 (página física 51, numeração impressa 34) continha quatro riscos de extrapolação: (1) execução «imparcial» como consequência do código; (2) eliminação universal de intermediários e autoridade central; (3) imutabilidade/transparência absolutas das regras, sem considerar permissões, migrações ou actualizações; (4) exemplos de alertas em tempo real, penalizações e rotação/desembolso que podiam sugerir implementação no protótipo.

Referências de corroboração consultadas:
- Ethereum Foundation: https://ethereum.org/developers/docs/smart-contracts/ — execução, contratos e limitações relativas a fontes externas.
- Ethereum Foundation: https://ethereum.org/developers/docs/smart-contracts/upgrading/ — padrões e implicações de actualização de lógica.
- Ethereum Foundation: https://ethereum.org/developers/docs/oracles/ — veracidade e dependência de informações externas.
- Evidência específica do protótipo: `docs/audit/brownie-contract-tests-2026-10-29.md` (14 testes Brownie aprovados para GroupRegistry, ContributionRegistry e CredentialRegistry).
- Evidência adicional: `docs/audit/consistency-recovery-2026-10-29.md` (ancoragem e reconciliação em PostgreSQL/Ganache com falha induzida).

A bibliografia original de Molina-Jimenez et al. (2019), Christidis e Devetsikiotis (2016) e Buterin (2014) foi conservada; estas novas fontes serviram à **auditoria técnica**, sem se pretender que tenham sido incluídas no corpo da bibliografia.

## Alterações efectuadas
Foram reescritos **nove parágrafos/bullets consecutivos** da secção 2.5, mantendo a estrutura e o formato Word:

1. Definição dos contratos inteligentes como programas executáveis, sem alegar imparcialidade garantida.
2. Separação entre automatização e eliminação de todos os intervenientes de governação.
3. Execução determinística nas condições programadas, sem prova da veracidade dos dados de origem; distinção entre resistência à alteração de registos e possibilidade de actualização/migração da lógica.
4. Quatro aplicações apresentadas como **possibilidades condicionadas**, não capacidades demonstradas: registo/alertas, atrasos/penalizações, rotação e ancoragem de contribuições para credenciais.
5. Último parágrafo limitado ao que os contratos **GroupRegistry, ContributionRegistry e CredentialRegistry** fazem e ao que os testes Ganache/Brownie realmente demonstraram: hashes, consultas, revogação. Não foram validados alertas em tempo real, desembolsos/penalizações automáticas, nem confirmação de operadores reais de carteira móvel.

**Não se alteraram** hipóteses HG/HE1–HE5, demais capítulos, gráficos, diagramas SmartArt, dados experimentais ou a bibliografia. Não foi criada uma nova estatística ou fonte de dados.

## QA de integridade documental
- Edição aplicada como **patch OOXML selectivo** exclusivamente no ficheiro interno `word/document.xml`.
- Integridade ZIP: `testzip()` sem erros; 129 componentes OOXML.
- Preservados **48 ficheiros em word/media**, **26 tabelas**, **quatro partes de comentários Word**, **59 campos SEQ**, **45 REF** e **quatro TOC**.
- Renderização integral do DOCX pela rotina da competência Word: **157 PNGs/páginas** produzidos.
- Renderização independente por LibreOffice para PDF: **157 páginas**, iguais à origem.
- Comparação programática de texto e raster entre PDF anterior e actualizado, página a página: **apenas a página física 51 mudou**. As outras **156 páginas** mantiveram-se visual e textualmente idênticas.
- Inspecção visual directa da página física 51 (numeração impressa 34): sem cortes, sobreposição ou extravasamento para margens.
- Auditoria geométrica de texto nas 157 páginas: **zero blocos fora dos limites**.
- **Não** se executou a actualização conjunta dos campos no Microsoft Word; essa verificação mantém-se pendente.

## Estado e próxima pendência
A correcção científica desta secção encontra-se **implementada e verificada estruturalmente**. O DOCX actualizado foi entregue no chat e a versão permanece sem os três gráficos hipotéticos.

O seguinte ponto de revisão lexical/científica visível na página física 52, início da secção 2.6, é a frase `O Bitcoin foi concebido exclusivamente como um sistema de dinheiro eletrónico peer-to-peer`, as formulações `a rede sabe quanto dinheiro uma morada possui`, `não é ma solução de DID` e o tratamento de Microsoft ION/Hyperledger Indy como se ambos dependessem da mesma arquitectura blockchain. Esta questão **não foi modificada** nesta revisão e requer verificação própria.

### Limitações para a submissão final
Continuam pendentes a confirmação do manual vigente USTM/FCTI, o teste final de campos no Microsoft Word, a prova de direitos de reprodução de algumas figuras e a documentação primária dos procedimentos de entrevista.