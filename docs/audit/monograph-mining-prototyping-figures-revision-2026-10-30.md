# Revisão da Figura 2.3.10 e dos esquemas de prototipagem 2.7.1–2.7.2

**Data:** 30 de Outubro de 2026  
**Versão de origem:** `Monografia_Canonica_Criptografia_e_Consenso_Revistos_30102026.docx` (158 pp.; SHA-256 `edebfa9ba32baff7f80d43bb27ecdc904268b483f36be3ca0180874e00f4e63f`).  
**Versão nova:** `Monografia_Canonica_Mineracao_e_Prototipagem_Revistas_30102026.docx` (158 pp.; SHA-256 `70a064be5a2bc82e80638e822c1cd0accb7e5fa90079678fa013efcbdafd66f7`).  
**Política:** patch OOXML sobre a última canónica, não regeneração integral do DOCX.

## 1. Figura 2.3.10 — mineração
A fonte primária `PET/UFMS (2021)`, referida secundariamente por Duarte (2025), **não ficou comprovada**. O desenho antigo continha uma sequência tecnicamente equívoca, com validação por mineradores, e não distinguiu a verificação independente dos nós. Substituiu-se **apenas `word/media/image10.png`** por um esquema original, cuja fonte editável é `docs/audit/figures/figura-2310-mineracao-bitcoin-original.svg`.

**Seis etapas representadas:** validação inicial das transacções; bloco candidato; procura de prova de trabalho; propagação; validação de bloco/transacções pelos nós; integração na cadeia de maior trabalho acumulado, com ressalva de bifurcações/reorganizações. A legenda e a lista de figuras mantêm o campo SEQ e indicam `elaboração própria; cf. Nakamoto, 2008`. Corrigido o texto adjacente para distinguir **pseudonímia de anonimato** e afastar a **imutabilidade absoluta**. A fonte Duarte 2025 não foi automaticamente removida da bibliografia; a auditoria bibliográfica residual deve verificar se existe outra citação efectiva antes de decidir a sua permanência.

Fontes primárias técnicas: 
- Bitcoin Developers — https://developer.bitcoin.org/devguide/block_chain.html
- Bitcoin Developers — https://developer.bitcoin.org/devguide/mining.html
- Nakamoto (2008), *Bitcoin: A Peer-to-Peer Electronic Cash System* — https://bitcoin.org/bitcoin.pdf

## 2. Figuras 2.7.1–2.7.2 — SmartArt editável
**As figuras não foram substituídas por imagens.** Foi mantida a estrutura nativa de SmartArt e corrigidos os textos internos em `data7/drawing7` e `data8/drawing8`.

- **2.7.1:** distinção entre finalidade (descartável/evolutiva) e fidelidade (baixa/alta); evitada a ideia de começar todo o sistema "do zero" após a avaliação e a afirmação incorrecta de que a UX surge apenas com protótipos de alta fidelidade. Fonte indicada como **conceptual**: Sommerville (2011).
- **2.7.2:** `Implementação e entrega` → `Apresentação e teste`, e `Avaliação pelo utilizador` → `Avaliação e feedback`. A participação de utilizadores reais foi descrita como **possível, não obrigatória em todas as experiências**, sem declarar testes de campo efectivamente realizados. O ciclo é um exemplo, não modelo obrigatório. Fonte conceptual: Sommerville (2011).
- **2.7.4:** quebra de página controlada inserida no início da secção para preservar a sua localização original (página impressa 42, física 59), sem acrescentar nem subtrair páginas.

## 3. QA documental
- **158 páginas**, iguais à base; renderização integral em PDF através de LibreOffice concluída.
- Comparação **raster de todas as 158 páginas**: diferenças apenas nas físicas **9, 42, 56, 57 e 58**; as outras **153 são idênticas**.
- Zero blocos de texto fora das áreas das páginas.
- Pacote OOXML íntegro: 129 partes, `testzip()=None`; exactamente seis partes modificadas: `word/document.xml`, `word/media/image10.png`, `word/diagrams/data7.xml`, `drawing7.xml`, `data8.xml`, `drawing8.xml`.
- **48 multimédia** (apenas uma imagem alterada), **26 tabelas**, **quatro partes de comentários idênticas**, **59 campos SEQ, 45 REF, quatro TOC e 361 bookmarks** preservados.
- Não houve regeneração global do índice; o autor confirmou previamente que o automático funciona no Microsoft Word.
- Verificadas visualmente as páginas **42, 57 e 58**, incluindo a legibilidade do novo esquema e a conservação dos SmartArt.

## 4. Pendências remanescentes
- Outras figuras externas e direitos de reprodução/atribuição; ver Issue #7.
- Regras USTM/FCTI e limite de páginas: e-mail enviado pelo autor, resposta pendente.
- Metadados de campo E1–E7: local, datas, selecção, consentimento, número de grupos.
- O render é uma validação LibreOffice; a aprovação institucional depende da USTM. 

**Estado:** correcção técnica das Figuras 2.3.10, 2.7.1 e 2.7.2 concluída. Esta nova cópia passa a ser a **versão canónica de trabalho**, sem os três gráficos hipotéticos anteriormente retirados.
