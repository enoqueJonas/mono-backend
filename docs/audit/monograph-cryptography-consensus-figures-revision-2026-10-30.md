# Revisão científica e gráfica — Figuras 2.3.3–2.3.6 e mecanismos de consenso
**Data:** 30/10/2026  
**Base canónica:** `Monografia_Canonica_Figuras_DLT_Blockchain_Originais_30102026.docx` (158 páginas), SHA-256 `d9883cd96b6eb5856e607fa5286bd52335d53a3f0a05a127c7d67c7b7aef67d1`.  
**Nova versão:** `Monografia_Canonica_Criptografia_e_Consenso_Revistos_30102026.docx` (158 páginas), SHA-256 `edebfa9ba32baff7f80d43bb27ecdc904268b483f36be3ca0180874e00f4e63f`.

## 1. Evidência e estatuto das fontes gráficas
- **2.3.3/2.3.4:** Pigatto (2012), dissertação da USP, é fonte académica existente. Há referência à adaptação de Pires (2010) em materiais anteriores; no entanto **não foi certificada a autoria/permissão de cada pixel** do desenho que estava no Word. A nova imagem foi construída como composição autónoma, com fonte SVG editável, preservando Pigatto apenas como fonte conceptual precedida de `cf.`.
- **2.3.5/2.3.6:** publicação de Latif et al. (2021), DOI 10.1002/ett.4337, é fonte académica comprovada; a correspondência visual exacta dos desenhos antigos com o artigo editorial não foi demonstrada. As imagens foram substituídas por composições originais com a indicação `elaboração própria; cf. Latif et al., 2021`.
- **As quatro figuras novas** são esquemas de elaboração própria com fonte SVG versionada, não reproduções/traçados das figuras antigas. Isso resolve o risco editorial **das imagens incorporadas** sem afirmar que o uso das anteriores constituía violação de direitos.

## 2. Fontes SVG editáveis
- [2.3.3 — Criptografia simétrica](figures/figura-233-criptografia-simetrica.svg) — mesma chave secreta K para cifrar e decifrar; não equivale a assinatura.
- [2.3.4 — Criptografia assimétrica](figures/figura-234-criptografia-assimetrica.svg) — dois fluxos distintos: cifragem (pública do destinatário / privada para decifrar) e assinatura (privada do emissor / pública para verificar).
- [2.3.5 — Proof of Work](figures/figura-235-proof-of-work.svg) — preparação, procura de solução, verificação, propagação e extensão da cadeia; **não afirma imutabilidade definitiva**.
- [2.3.6 — Proof of Stake](figures/figura-236-proof-of-stake.svg) — elegibilidade, selecção, proposta/atestação, escolha da cadeia e finalidade; regras de slashing variáveis.

**Citação editorial nos quatro casos:** `elaboração própria; cf. [autor]`, tanto nas legendas do corpo como nos valores em cache da lista de figuras. Os campos automáticos e a numeração SEQ foram preservados.

## 3. Erros científicos adicionais corrigidos no entorno
- Distinção entre confidencialidade por cifragem simétrica, cifragem de chave pública e autenticidade/integridade por assinatura digital. A assinatura do protótipo **não cifra** os dados.
- Introdução de PoW com referência a **Nakamoto (2008)**, sem falsa alegação de invenção original da prova de trabalho.
- Eliminação das afirmações `bloco anexado definitivamente`, `transacções imutáveis em qualquer circunstância` e `ataques financeiramente inviáveis como garantia absoluta`.
- Descrição da selecção de proponentes PoS **dependente do protocolo**, sem generalização de proporcionalidade directa ao valor bloqueado.
- Distinção entre penalidades e `slashing` conforme a rede; não é condição universal de todo o PoS.
- Correcção da generalização de que DLT dispensa qualquer autoridade/governação e da alegação de que mecanismos de consenso substituem automaticamente bancos e certificadores.
- **Quadro 2.3.1** actualizado em critérios de validação, selecção e eficiência, eliminando generalizações como `mais eficiente`.
- Exemplo anacrónico `Ethereum 2.0 (ETH2), Avalanche (AVAX)` substituído por **`Ethereum (ETH)`**, coerente com a transição da rede para PoS desde 2022; linha `ETH2` na tabela de siglas ajustada para `ETH`/Ether.

**Não se alteraram** testes do protótipo, hipóteses HG/HE, conclusões, listas de resultados de laboratório, bibliografia ou os anexos de entrevistas. As novas especificações públicas apoiaram a auditoria, **não foram artificialmente inseridas como obras lidas originalmente na bibliografia**.

### Fontes verificadas
- Daniel Fernando Pigatto (2012), USP: https://teses.usp.br/teses/disponiveis/55/55134/tde-06092012-154011/pt-br.html
- Latif et al. (2021), Wiley DOI: https://onlinelibrary.wiley.com/doi/10.1002/ett.4337
- NIST, digital signature: https://csrc.nist.gov/glossary/term/digital_signature
- Ethereum.org, princípios PoS e selecção de validadores: https://ethereum.org/developers/docs/consensus-mechanisms/pos/
- Ethereum.org, funcionamento e limitações do PoW: https://ethereum.org/developers/docs/consensus-mechanisms/pow/
- Ethereum.org, mecanismo de consenso em geral: https://ethereum.org/developers/docs/consensus-mechanisms

## 4. Processo técnico e regressão
- **Patch OOXML selectivo**. As únicas cinco partes internas alteradas foram:
  - `word/document.xml`;
  - `word/media/image4.png`, `image5.png`, `image6.png`, `image7.png`.
- A edição dos quatro desenhos manteve as mesmas relações internas e dimensões; as formas originais tinham efeitos de **recorte** e, na Figura 2.3.3, filtro **grayscale**. Esses atributos de apresentação foram retirados somente das imagens substituídas para evitar cortes e perda de cor; as outras figuras não foram modificadas.
- Um ensaio inicial exibiu **duplicação do REF da Figura 2.3.5** quando o parágrafo foi substituído integralmente; a versão final foi **corrigida com substituição apenas do texto ao redor do REF**, preservando o código de campo e evitando a duplicação.
- ZIP/OOXML `testzip()`: **aprovado**, 129 partes, sem adicionar/eliminar ficheiros.
- **48 media**, dos quais **44 binariamente idênticos** e **4 alterados intencionalmente**.
- **4 partes de comentários idênticas**; **26 tabelas**.
- **59 SEQ, 45 REF, 4 TOC** e **361 bookmarks**: mesmas contagens antes/depois; quatro `commentReference` intactos.
- PDF renderizado integralmente via LibreOffice: **158 páginas**, igual à base.
- Comparação automática de texto e píxeis entre PDFs **em todas as 158 páginas**: diferenças apenas nas **11 páginas físicas 9, 13 e 29–37**. As restantes **147 páginas não apresentaram diferenças** ao nível do texto nem da rasterização comparada.
- Controlo geométrico de texto em 158 páginas: **zero blocos fora da área**.
- Figuras verificadas visualmente nas páginas físicas 31, 32, 34 e 35 após remover filtros/crops. **Nenhum texto cortado, legenda desassociada ou sobreposição observada** no resultado final.
- O autor já confirmou previamente que o índice automático funciona no Word; **não houve refresh global de TOC**. Esta revisão mantém a mesma paginação e os números das quatro figuras.

## 5. Estado e pendências
**Concluídas nesta etapa:** eliminação de imagens com autoria/licença gráfica incerta 2.3.3–2.3.6, correção das confusões de criptografia, revisão PoW/PoS, actualização do quadro e rótulo ETH. **Nova canónica de trabalho:** `Monografia_Canonica_Criptografia_e_Consenso_Revistos_30102026.docx`.

**Ainda pendentes** (não criar falsos estados de fecho):
- Figura **2.3.10** (PET/UFMS via Duarte 2025): fonte gráfica primária/direito de reprodução.
- Figuras de prototipagem 2.7.1–2.7.2: autoria do desenho e proveniência.
- Resposta oficial FCTI ao e-mail já enviado pelo autor sobre manual, APA e extensão; o risco institucional **não** está resolvido.
- Dados de campo primários das entrevistas (período, local, amostragem, grupos, consentimento).
