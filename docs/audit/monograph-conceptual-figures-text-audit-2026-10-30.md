# Auditoria integral das ilustrações da monografia — 30/10/2026

## Documento resultante
- **Versão canónica anterior:** `Monografia_Canonica_Telas_Reorganizadas_30102026.docx` (156 páginas).
- **Nova versão:** `Monografia_Canonica_Ilustracoes_Auditadas_30102026.docx` (156 páginas).
- **SHA-256:** `26a5f1b488507e71f88ce81b8c2529d88a96efdc534ce704461d497d552ede04`.
- **Regra de intervenção:** conservar dentro de figuras apenas títulos, rótulos, relações e descrições mínimas necessárias à leitura; manter explicações e reservas metodológicas no texto da monografia.

## Âmbito
- Conferidas as **43 legendas de figuras** da monografia, as representações conceptuais dos capítulos 2.1, 2.3, 2.4 e 2.7, os **oito SmartArt nativos** (`data1`–`data8`), as ilustrações de UML, sequência, actividades e arquitectura e as capturas das interfaces.
- A revisão identificou **10 PNGs conceptuais** com notas periféricas e **5 SmartArt** cujo texto era longo, redundante ou demasiado absoluto. Os restantes diagramas técnicos e capturas de ecrã não foram alterados: os seus rótulos identificam actores, estados, mensagens e componentes necessários à interpretação, e os dados dos participantes E1–E7 já haviam sido minimizados na versão anterior.

## Alterações aplicadas aos PNGs conceptuais
| Figura | Intervenção |
|---|---|
| 2.3.1 — Registo distribuído | Retirada nota genérica de rodapé sobre variabilidade dos protocolos; rede/nós e relação mantidos. |
| 2.3.2 — Encadeamento entre blocos | Retirada nota ilustrativa de rodapé; campos e relação entre blocos mantidos. |
| 2.3.3 — Criptografia simétrica | Retirada frase «Cifrar dados não equivale a assinar digitalmente uma credencial»; chave K, fluxo e ligação mantidos. |
| 2.3.4 — Criptografia assimétrica | Retirada nota «Assinatura não cifra automaticamente os dados»; cifragem e assinatura continuam separados. |
| 2.3.5 — Proof of Work | Retirada nota geral de confirmação/finalidade; todas as cinco etapas mantidas. |
| 2.3.6 — Proof of Stake | Retirada nota genérica sobre variabilidade; todas as quatro etapas mantidas. |
| 2.3.7 — Blockchain pública | Retirada nota de rodapé redundante; admissão, rede e nós mantidos. |
| 2.3.8 — Blockchain privada | Retirada nota de rodapé redundante; permissões e nós mantidos. |
| 2.3.10 — Mineração Bitcoin | Retirado quadro periférico de ressalva; seis etapas com distinção entre minerador e nó validador preservadas. |
| 2.4.2 — Emissor/titular/verificador | Retirada nota genérica sobre dependência do método DID, preservando registo de confiança opcional, os três actores, emissor/verificador e as ligações. |

Estas imagens foram reconstruídas a partir da versão anterior **não mascarada** para evitar os cortes de contornos observados em pré-visualizações de uma tentativa intermédia de limpeza. Foram removidos apenas os pixels de notas acessórias, não as caixas ou fluxos.

## Alterações aos cinco SmartArt originais (editabilidade mantida)
- **2.1.1 — Etapas do Xitique:** três descrições longas condensadas em formação do grupo, fixação do valor/periodicidade e rotação.
- **2.3.9 — Vantagens/limitações da blockchain:** substituídos os absolutismos «imutabilidade», «integridade permanente», «redução de custos» e «ataques de 51% em redes pequenas» por características condicionadas: auditabilidade, detecção de alterações, partilha de registos, riscos de concentração, desempenho e consumo de PoW.
- **2.4.3 — Componentes DID/VC:** textos encurtados para o papel do ledger opcional, declarações assinadas e gestão/apresentação de credenciais em carteiras, sem confundir cifragem com assinatura.
- **2.4.4 — Aplicações conceptuais:** substituídos quatro parágrafos integrais dentro de caixas por enunciados breves. Mantida a ressalva essencial em cada caso: verificabilidade ≠ confirmação financeira; auditabilidade depende dos dados de origem; aceitação externa não demonstrada; integração com pagamentos móveis simulada. Textos alinhados verticalmente ao centro no SmartArt, para evitar a aparência de caixas vazias.
- **2.7.1 — Classificação dos protótipos:** descrições condensadas, sem perder a diferença entre descartável/evolutivo e baixa/alta fidelidade. 
- **2.7.2:** apenas cinco rótulos necessários já existentes; **sem alteração**.
- **2.3.9** e **2.4.4** foram mantidos como SmartArt editável e não convertidos em imagem.

## Validação integral do Word
- **156 páginas** após renderização em PDF; nenhuma página nova e nenhum conteúdo técnico removido.
- Diferenças visuais apenas nas páginas físicas **26, 29, 30, 32, 34, 35, 37, 38, 40, 42, 45, 46, 50, 57**; **142 páginas idênticas** à versão anterior.
- Texto PDF com diferenças apenas nas páginas **26, 40, 46, 50, 57** devido à simplificação de SmartArt; texto de parágrafos corridos, conclusões e entrevistas igual.
- **Zero blocos de texto fora das páginas**.
- ZIP DOCX íntegro, **129 partes** idênticas em inventário; apenas **20 partes** alteradas (**10 imagens PNG**, **10 partes de SmartArt**); `word/document.xml` **inalterado byte a byte**.
- **48 ficheiros de media, 26 tabelas, 4 partes de comentários, 361 bookmarks, 59 SEQ, 45 REF e 4 TOC** preservados.
- Legendas, lista de figuras, remissões, imagens dos anexos, dados das entrevistas, critérios de aceitação e protocolo de índice automático intocados.

## Pendências não reabertas
1. **Índices no Word:** teste de actualização automática em cópia no Microsoft Word continua necessário devido à diferença de paginação observada no LibreOffice; não alterar margens por isso.
2. **USTM/FCTI:** aguarda-se confirmação do manual e calendário. E-mail já enviado.
3. **Protótipo para defesa:** validar frontend com o backend/contratos da branch experimental; não declarar que `master` possui os PRs #11–#14 enquanto continuarem em rascunho.

**Conclusão:** as figuras conceptuais foram revistas quanto à pertinência, concisão e precisão dos textos internos. O documento actual é a nova referência canónica de trabalho, com paginação e mecanismos automáticos preservados.