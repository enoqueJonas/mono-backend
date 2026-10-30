# Figura 2.4.2 — substituição documentada por esquema original (30/10/2026)

## Motivo
A figura original, contida em `word/media/image11.png`, mostra emissor, titular, verificador, smartphone/carteira e uma barra blockchain. A legenda anterior citava Albergaria (2024) como apoio conceptual, mas a **proveniência exacta e os direitos de reprodução da imagem não puderam ser confirmados** após comparação com o artigo de Albergaria e documentação Microsoft Entra Verified ID. A ausência de identificação não prova qualquer infração; para remover a incerteza, foi criado um esquema original.

## Artefactos
- **Base canónica:** `Monografia_Canonica_Indices_Conferidos_30102026.docx`, SHA256 `b3ae57beeda7acc476fe470f9ed542c06f9d962f4f11b6ba4183e82e62d63861`.
- **Nova cópia:** `Monografia_Canonica_Figura_2_4_2_Original_30102026.docx`, SHA256 `f26953649359790c544ee783fb83fede8bf39d13a2b1fcb7045d90596806423a`.
- **Fonte do desenho original:** `docs/audit/figures/figura-2.4.2-arquitectura-did-vc-original-2026-10-30.svg` (código SVG editável). O gráfico no DOCX é um PNG rasterizado a 1568×1000 pixels, inserido mantendo o `rId41`, dimensões e âncora anteriores.
- **Design:** três papéis (emissor, titular, verificador); fluxo credencial emitida → apresentada; registo de confiança **opcional**. Não pressupõe carteira SSI implementada, DID público nem que a blockchain seja obrigatória em todos os métodos.
- Fundamentação conceptual: W3C [VC Data Model 1.0 (2019)](https://www.w3.org/TR/2019/REC-vc-data-model-20191119/) e [DID Core 1.0 (2022)](https://www.w3.org/TR/did-core/). O artigo [Albergaria (2024)](https://www.identityacademy.com.br/post/o-que-s%C3%A3o-identidades-descentralizadas---dids-na-pr%C3%A1tica) continua citado **apenas no parágrafo adjacente como explicação conceptual**, sem reivindicar autoria gráfica.

## Alteração localizada no OOXML
**Exactamente duas partes binárias foram alteradas**:
1. `word/media/image11.png`: imagem nova e original, preservando posição, relação `rId41` e dimensões no DOCX;
2. `word/document.xml`: legenda no corpo e cache da lista de figuras alteradas de `esquema ilustrativo; cf. Albergaria, 2024` para `elaboração própria; cf. W3C, 2019; 2022`. O parágrafo adjacente passou a mencionar `W3C, 2022; Albergaria, 2024`, mantendo coerência com bibliografia. Texto alternativo do gráfico actualizado.

Os códigos `SEQ`, `REF` e `TOC` originais não foram substituídos, os marcadores não foram apagados, não houve regravação integral do Word pelo LibreOffice nem alteração das demais figuras.

## Verificação de integridade e layout
- ZIP/OOXML íntegro (`testzip()` sem erros).
- **158 páginas** no PDF da cópia editada, mesmas **158** do documento-base.
- Comparação automatizada de texto e raster das **158 páginas** contra o PDF-base: **diferenças apenas nas páginas físicas 9 e 45** (lista de figuras e figura).
- Ambas foram inspeccionadas visualmente; legenda, imagem e texto permanecem dentro da página, sem sobreposição/corte. A legenda continua identificada como **Figura 2.4.2**, página impressa **28**.
- Geometria: **zero** blocos textuais fora da página nas 158 páginas.
- **48 ficheiros `word/media`**, dos quais 47 binariamente idênticos à versão-base; a única substituição foi `image11.png`.
- **4 partes de comentários Word**, **26 tabelas**, **59 campos SEQ**, **45 REF** e **4 TOC** preservados.

## Estado
A questão da **proveniência específica da antiga Figura 2.4.2 está resolvida editorialmente**, por deixar de incorporar a imagem de autoria incerta. **Não declara que todos os direitos das restantes imagens externas estejam resolvidos** (CFI, GeeksforGeeks, Pigatto, Latif, PET/UFMS etc.). Não alterar o índice automático no Word senão se ocorrer um problema concreto, dado que o autor já confirmou o seu funcionamento. A resposta da USTM/FCTI sobre o manual e extensão permanece pendente.

**Nova versão canónica de trabalho:** `Monografia_Canonica_Figura_2_4_2_Original_30102026.docx` (158 páginas), ainda sujeita a revisão de figuras externas restantes e decisão institucional.