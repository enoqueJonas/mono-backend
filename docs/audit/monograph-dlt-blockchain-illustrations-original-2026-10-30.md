# Auditoria e substituição de quatro figuras — CFI / GeeksforGeeks
**Data:** 30/10/2026  
**Documento-base:** `Monografia_Canonica_Figura_2_4_2_Original_30102026.docx` (158 páginas; SHA-256 `f26953649359790c544ee783fb83fede8bf39d13a2b1fcb7045d90596806423a`).  
**Novo documento:** `Monografia_Canonica_Figuras_DLT_Blockchain_Originais_30102026.docx` (158 páginas; SHA-256 `4d5eaea17f23d9c8ca508d247a95a110d771e4408c7e67b2febdaf06eb1bca74`).  
**Estado:** nova versão **canónica de trabalho**, não certificação de conformidade institucional ou de direitos das restantes figuras.

## 1. Descobertas documentais
As figuras originais do Word eram visualmente associadas a conteúdos de CFI e GeeksforGeeks:
- **2.3.1:** gráfico de registo distribuído, legenda `CFI Team (2020)`. Artigo: https://corporatefinanceinstitute.com/resources/cryptocurrency/distributed-ledger-technology/ ; termos actualizados em 24/09/2026: https://corporatefinanceinstitute.com/about-cfi/website-terms-of-use/.
- **2.3.2, 2.3.7 e 2.3.8:** gráficos da estrutura blockchain e redes pública/privada, com referência GeeksforGeeks (2025): https://www.geeksforgeeks.org/ethical-hacking/blockchain-structure/ ; copyright: https://www.geeksforgeeks.org/legal/copyright-information/ ; regras comunitárias: https://www.geeksforgeeks.org/legal/intellectual-property-rights-legal/.

Ambos os editores reservam direitos sobre o conteúdo visual. O âmbito exacto das excepções académicas da legislação moçambicana para uma utilização individual depende das condições factuais; **não foi declarado que o manuscrito anterior necessariamente infringia direitos**. Sem prova de autorização individual, preferiu-se produzir diagramas independentes a partir dos conceitos e eliminar a incerteza de reutilização desses quatro visuais.

## 2. Quatro novas figuras independentes

| Figura | Imagem substituída dentro do DOCX | Fonte SVG editável |
|---|---|---|
| **2.3.1 DLT** | `word/media/image2.png` | [figura-231-dlt-elaboracao-propria.svg](figures/figura-231-dlt-elaboracao-propria.svg) |
| **2.3.2 Encadeamento de blocos** | `word/media/image3.png` | [figura-232-encadeamento-blocos-original.svg](figures/figura-232-encadeamento-blocos-original.svg) |
| **2.3.7 Rede pública** | `word/media/image8.png` | [figura-237-blockchain-publica-original.svg](figures/figura-237-blockchain-publica-original.svg) |
| **2.3.8 Rede privada** | `word/media/image9.png` | [figura-238-blockchain-privada-original.svg](figures/figura-238-blockchain-privada-original.svg) |

Os esquemas foram construídos como composição gráfica original (SVG), e convertidos para PNG com a dimensão nativa mantida nos espaços já usados no Word; não foram efectuados traçados dos desenhos anteriores. **As legendas e os caches da Lista de Figuras** passaram a indicar `elaboração própria; cf. CFI Team, 2020` ou `elaboração própria; cf. GeeksforGeeks, 2025`: trata-se de **apoio conceptual**, não de autoria gráfica dos sites. As entradas bibliográficas CFI/GFG foram preservadas porque continuam citadas.

**Limites conceptuais dos desenhos:** DLT não equivale a ledger centralizado nem toda DLT implica blockchain; campos internos de bloco e propriedades de rede dependem do protocolo; uma rede pública não significa que qualquer participante possa validar independentemente de regras; uma rede privada inclui critérios de admissão e governação.

## 3. Correcções no texto adjacente, motivadas pela verificação das figuras
Na página física **29**, secção 2.3.1:
- A frase que definia DLT como `registo centralizado de transações` foi substituída por definição de registos sincronizados em múltiplos nós, com blockchain como implementação possível.
- A alegação de que DLT reduz automaticamente custos e ataques cibernéticos foi delimitada: resultados dependem de protocolo, governação e contexto.
- O argumento de substituição bancária foi removido: DLT pode ajudar na rastreabilidade, mas não valida por si a veracidade dos dados nem substitui serviços financeiros formais.

Na página física **30**, secção 2.3.2:
- A enumeração de campos foi qualificada: são **exemplos possíveis conforme o protocolo**, não todos obrigatórios.
- `Nonce` passou a estar associado a determinados mecanismos de prova de trabalho, sem ser atributo universal.
- `Raiz de Merkle` passou a ser `quando prevista`, sem alegação de indispensabilidade para toda blockchain.

**Nota:** as afirmações restantes fora desses trechos não foram reescritas; podem merecer auditoria autónoma se houver inconsistência comprovada.

## 4. Controlo técnico de integridade
- Patch selectivo OOXML: apenas **cinco partes** diferem, `word/document.xml` e `word/media/image2.png`, `image3.png`, `image8.png`, `image9.png`.
- ZIP íntegro: `testzip() = None`.
- Número de partes idêntico: **129**.
- **48 ficheiros multimédia** (quatro imagens substituídas, outras 44 preservadas byte a byte).
- **4 partes de comentários** idênticas.
- **26 tabelas**, **59 SEQ**, **45 REF**, **4 TOC**: contagens intactas.
- PDF de verificação gerado com LibreOffice: **158 páginas**, sem mudança de contagem.
- Comparação de texto e pixels (baixa resolução) de **todas as 158 páginas**: diferenças apenas nas páginas físicas **9, 29, 30, 37 e 38**. As outras **153 páginas mantêm o mesmo texto e imagem** no PDF verificado.
- Inspecção visual de páginas 9, 29, 30, 37 e 38: diagramas legíveis no contexto impresso, figuras/legendas sem sobreposição. **Zero** blocos de texto fora das páginas.
- Fonte Word mais recente, com os três gráficos hipotéticos **4.2.1–4.2.3 ausentes**, preservada como base.

**Restrição de QA:** os resultados de layout decorrem de LibreOffice. O autor já confirmou que o índice automático funciona no Microsoft Word; não foi necessário nem realizado refresh dos campos nesta versão. Se alterações futuras deslocarem páginas, testar de novo em cópia no Word.

## 5. Pendências que NÃO foram resolvidas
- Origem e base de reprodução das Figuras **2.3.3–2.3.6**, **2.3.10** e outras ilustrações externas de maior risco.
- Regra vigente USTM/FCTI 2026, APA e limite de páginas: e-mail enviado pelo autor, **resposta pendente**.
- Metadados primários do trabalho de campo E1–E7 (datas, localidades, selecção, consentimento).

**Não encerrar a Issue #7**, que ainda acompanha outras fontes e direitos; marcar concluídas apenas as quatro substituições desta etapa.
