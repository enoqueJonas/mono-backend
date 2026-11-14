# Auditoria canónica — Bitcoin, UTXO, ION e Hyperledger Indy

**Data:** 30/10/2026  
**Issue:** #20 — Revisão da secção 2.6  
**Documento de entrada:** `Monografia_Canonica_Contratos_Inteligentes_Revistos_30102026.docx`  
**Documento de saída:** `Monografia_Canonica_Bitcoin_ION_Indy_Revistos_30102026.docx`  
**SHA-256 entrada:** `3d27ec1d39c9bcc8bfa9fe3de237f760a5588bbde3d706f9558fafd0fdcb6398`  
**SHA-256 saída:** `100b7baa3485ee08c52f997150eb2dc9d536327545e21ecc653a529465e659ed`

## 1. Alterações científicas realizadas

Na secção **2.6 — Análise de soluções que utilizam Blockchain e Identidade Descentralizada** (página física **52**, numeração impressa **35**), foram substituídos **exactamente três parágrafos**, conservando os restantes capítulos:
- O Bitcoin foi **proposto** como meio de dinheiro electrónico peer-to-peer, não definido como utilização «exclusiva» que impediria serviços em camadas superiores; não contém método DID nem emissão de VC **nativos**.
- O saldo de uma carteira Bitcoin foi explicado por **UTXO** (saídas de transacções não gastas), em vez de contas mantidas pela rede; chaves/endereços por si só não garantem identidade civil.
- Distinção arquitectural: **ION/Sidetree** opera sobre Bitcoin; **Hyperledger Indy** disponibiliza registo de identidade específico com regras de participação e governação. O protótipo da monografia **não implementou** ION, Indy nem resolução pública interoperável de DIDs.

### Fontes primárias adicionadas à bibliografia
- `Bitcoin.org. (s.d.). Transactions. Bitcoin Developer Guide. https://developer.bitcoin.org/devguide/transactions.html`
- `Decentralized Identity Foundation. (s.d.). ION: The Identity Overlay Network [Código-fonte e documentação]. https://github.com/decentralized-identity/ion`
- `Hyperledger Foundation. (s.d.). Indy DID Method Specification. https://hyperledger.github.io/indy-did-method/`

A entrada **Nakamoto (2008)** já existia e foi preservada. As novas fontes foram inseridas alfabeticamente, evitando referências sem correspondência no corpo.

## 2. Revisão do índice e impacto na extensão

**Consequência verificada na renderização:** as três referências primárias fizeram a bibliografia ocupar **oito páginas em vez de sete**, criando uma **página física adicional** antes do Apêndice A. Total: **158 páginas**, contra **157** da versão anterior. **Não** foram comprimidas margens, fonte ou entrelinha para esconder a diferença.

Foram actualizados os **valores em cache** — não convertidos em texto sem campo — das dez entradas dependentes da deslocação:
- Índice geral: `8 APÊNDICE A` **123 → 124**; `9 ANEXOS` **135 → 136**.
- Lista de figuras: `Figura A.1–A.8` com +1 página cada (**123–134** → **124–135**, de acordo com a entrada individual).

As páginas anteriores à bibliografia permanecem nas mesmas posições físicas. O teste completo dos campos **no Microsoft Word** continua obrigatório; não assumir que o refresh automático é igual ao comportamento do LibreOffice.

## 3. QA reprodutível e integridade
- DOCX criado por **patch OOXML selectivo**: unicamente `word/document.xml` foi modificado, com preservação integral das restantes partes do pacote.
- Integridade ZIP: `testzip()` sem erros.
- **48 ficheiros word/media** preservados binariamente.
- **4 partes de comentários Word** preservadas binariamente.
- **26 tabelas**, **59 campos SEQ**, **45 REF** e **4 TOC**: contagens inalteradas.
- **158 páginas** renderizadas em PDF a partir do DOCX com LibreOffice.
- Verificação visual de índice, Figura 2.6 na página 52, bibliografia (páginas 134/136/140), abertura do apêndice (página 141) e diagramas subsequentes.
- Comparação de texto por página: das primeiras 51 páginas, apenas as físicas **6 e 10** mudaram (entradas de índices); entre as **53 e 132** não houve mudança de texto; do antigo apêndice físico **140–157** para o novo **141–158** todo o texto coincidiu quando se excluem os números de página dinâmicos.
- Auditoria geométrica de todas as **158 páginas**: **zero blocos de texto fora da página**.
- Conteúdos experimentais, hipóteses, gráficos, SmartArt e anexos de entrevistas não foram alterados nesta revisão.

## 4. Pendências
1. Verificar os **4 TOC / 59 SEQ / 45 REF** por actualização conjunta no **Microsoft Word**, incluindo paginação e comentários.
2. Confirmar manual vigente FCTI/USTM, limite de páginas e APA antes de submissão.
3. Comprovar direitos de figuras de terceiros e proveniência exacta da Figura 2.4.2.
4. Recuperar dados de campo primários sobre as entrevistas (recrutamento, locais, datas, consentimento).

**Estado:** Issue #20 tecnicamente corrigida e verificada em PDF/OOXML; versão canónica de trabalho agora **158 páginas**, sem gráficos hipotéticos. Não declarar submissão institucional aprovada.
