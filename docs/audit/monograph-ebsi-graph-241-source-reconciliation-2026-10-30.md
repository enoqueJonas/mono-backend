# Auditoria residual — EBSI (2021) e Gráfico 2.4.1

**Data:** 30/10/2026  
**Origem:** `Monografia_Canonica_Referencias_Conferidas_30102026.docx` — 156 páginas, SHA-256 `76e8ea37c55462119d86958e21de41c87f92344ac65aef95f3ec49d72290339a`  
**Nova versão:** `Monografia_Canonica_EBSI_e_Grafico_241_Revistos_30102026.docx` — 156 páginas, SHA-256 `29b4a6b85cfb42a4158f550a53b965cbe554f8fe9bbe11dc510f621d99e61476`

## 1. Problema comprovado

- A bibliografia da versão-base continha **European Blockchain Services Infrastructure (EBSI). (2021). European self-sovereign identity framework (ESSIF). European Commission**, sem ligação, versão, edição ou documento primário identificado. A referência **não foi encontrada como publicação concreta com aqueles metadados**, embora a Comissão Europeia tenha efectivamente documentado projectos EBSI/SSI em 2021. Não declarar que o projecto ESSIF não existiu.
- O **Gráfico 2.4.1** apresentava «Inclusão Financeira», «Privacidade Seletiva» e «Interoperabilidade e Portabilidade» como benefícios categóricos, contrastando com os próprios parágrafos que os qualificam como condicionados à implementação.
- A legenda do Gráfico 2.4.1 dizia «Adaptado de» com uma lista extensa de sete autores/organizações e anos não necessariamente vinculados ao desenho exacto. A figura **é um SmartArt conceptual**, não um resultado quantitativo ou uma reprodução gráfica comprovada.
- Uma passagem sobre reconhecimento jurídico sugeria ausência generalizada de reconhecimento das identidades descentralizadas, sem delimitação territorial ou jurídica.

## 2. Correcção selectiva

**Ficheiros internos alterados, apenas três:**
1. `word/document.xml` — legenda e entrada na Lista de Gráficos, duas citações EBSI 2021, um parágrafo sobre reconhecimento jurídico, remoção da referência bibliográfica incompleta.
2. `word/diagrams/data5.xml` — texto fonte do Gráfico 2.4.1.
3. `word/diagrams/drawing5.xml` — cache de desenho do SmartArt 2.4.1.

**Nova legenda:** «Gráfico 2.4.1 Comparação entre as potencialidades e limitações da identidade digital descentralizada (elaboração própria; cf. Allen, 2016; W3C, 2019; 2022; World Bank, 2019; European Commission, 2026)».

**Rótulos principais actualizados:**
- `Vantagens` → `Potencialidades`
- `Soberania e Controlo Individual` → `Maior controlo do titular`
- `Privacidade Seletiva` → `Divulgação selectiva opcional`
- `Segurança e Integridade` → `Integridade das credenciais`
- `Interoperabilidade e Portabilidade` → `Portabilidade condicionada`
- `Inclusão Financeira` → `Possível apoio à inclusão`
- `Limitações` → `Condições e riscos`, com quatro descrições breves das condições técnicas/institucionais.

O parágrafo de comparação da secção 5.4.2 passou de `EBSI, 2021` para `European Commission, 2026`, fonte já especificada e citada na monografia. A entrada bibliográfica incompleta **EBSI 2021 foi removida**, passando a bibliografia de **70 para 69** entradas; a documentação EBSI 2026 **foi preservada** e nenhum outro item foi eliminado. O texto sobre reconhecimento passou a indicar que os efeitos jurídicos variam conforme os regimes aplicáveis, sem afirmar uma ausência universal de reconhecimento.

## 3. Validação factual adicional — World Bank 2021

A afirmação da monografia segundo a qual **60% da população moçambicana não dispunha de identificação civil oficial**, atribuída ao Banco Mundial (2021), tem **fonte primária identificada**: comunicado de imprensa de **22/10/2021**, que apresenta exactamente esse valor. Este indicador **não** se refere especificamente aos membros de Xitique, nem ao conjunto dos adultos titulares de BI, e não deve ser comparado directamente com inquéritos de posse de BI por faixa etária.

Fonte: https://www.worldbank.org/en/news/press-release/2021/10/22/world-bank-supports-mozambique-s-efforts-towards-access-to-identification-and-digital-transformation

## 4. Fontes técnicas consultadas

- W3C, **DID Core 1.0**, Recomendação de 19/07/2022 — https://www.w3.org/TR/did-core/
- W3C, **Verifiable Credentials Data Model 1.0**, Recomendação de 19/11/2019 — https://www.w3.org/TR/2019/REC-vc-data-model-20191119/
- Comissão Europeia, projecto-piloto EBSI/SSI em 2021 — https://ec.europa.eu/digital-building-blocks/sites/spaces/DIGITAL/blog/2021/10/04/533365427/University%2Bpilot%2Bproves%2Bvalue%2Bof%2Ba%2BEuropean%2BBlockchain
- EBSI DevHub — https://hub.ebsi.eu/docs/use-cases/verifiable-credentials/trust-chains/holder

## 5. QA estrutural e visual

- **156 páginas** renderizadas no DOCX, exactamente como no documento-base.
- Partes OOXML: somente **`document.xml`, `data5.xml`, `drawing5.xml`** modificadas; ZIP íntegro.
- **48 multimédia**, **26 tabelas**, **4 partes de comentários do supervisor**, **361 bookmarks**, **59 SEQ**, **45 REF**, **4 TOC** preservados.
- Comparação de texto das 156 páginas: diferenças nas físicas **11, 47, 48, 127, 128, 134, 135 e 136**; é esperado haver diferenças visuais também na página **49** por refluência local. A comparação de pixels encontrou diferenças nas físicas **11, 47, 48, 49, 127, 128, 134, 135 e 136**; **147 páginas rasterizadas ficaram idênticas**.
- Revisão visual do Gráfico 2.4.1 (página física **47**), lista de gráficos (11), discussão (127–128), bibliografia (134–136) e página seguinte ao gráfico (48–49). Sem corte de texto, sobreposição ou página em branco introduzida.
- Auditoria geométrica: **zero** blocos de texto fora das páginas.
- Não foi feito refresh global dos índices automáticos; o autor já confirmou que funcionam no Word.

## 6. Estado

A correcção do gráfico conceptual e a eliminação da referência EBSI 2021 sem identificação bibliográfica estão **concluídas**. Isto **não equivale à validação individual das 69 referências restantes**, nem resolve direitos de terceiros, manual FCTI ou proveniência primária dos sete registos de entrevistas. Aguardamos resposta da Universidade ao e-mail já enviado pelo autor. Esta cópia é a versão canónica de trabalho mais recente, sem os três gráficos quantitativos hipotéticos já removidos.