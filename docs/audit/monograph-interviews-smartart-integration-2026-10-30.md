# Revisão canónica — integração de entrevistas e correcção SmartArt DID/VC
**Data:** 30 de Outubro de 2026  
**Ficheiro de origem:** `Monografia_Canonica_Proveniencia_DID_Revista_30102026.docx`  
**Novo ficheiro Word:** `Monografia_Canonica_Entrevistas_e_Diagramas_DID_30102026.docx`  
**Origem SHA-256:** `4ff0ff3f70a4ba7ec08a95aba0bf6454d33a76112f2ff6f6b6f08d8447748f88`  
**Novo SHA-256:** `3669d5464016d0db9335b562c1c67ab35e6c2d6fed28c9e14ab9994f158bc33a`

## Recuperação / política de integridade
O ficheiro original foi recuperado em bytes da Biblioteca do projecto para `/mnt/data`. A intervenção foi efectuada por **patch selectivo do pacote OOXML**, sem regenerar o Word a partir de texto extraído, sem abrir/salvar pela API python-docx e sem converter a versão canónica através do LibreOffice. O LibreOffice foi usado **apenas para renderização QA de cópia de trabalho**. O documento-base sem os gráficos hipotéticos permaneceu a única fonte; a variante com gráficos não foi recuperada.

**As únicas cinco partes OOXML que diferem em bytes entre as duas versões são:**
- `word/document.xml`
- `word/diagrams/data3.xml`
- `word/diagrams/drawing3.xml`
- `word/diagrams/data4.xml`
- `word/diagrams/drawing4.xml`

## 1. Alterações científicas aplicadas no texto

| Localização | Modificação aplicada | Motivo |
|---|---|---|
| §1.5, enquadramento metodológico | `estudo de caso` → `levantamento qualitativo exploratório` na descrição das três fases | Sem unidade/caso concreto delimitado nos sete registos |
| §3.1.4, procedimentos | Relacionadas análise documental, entrevistas e desenvolvimento experimental, com limites de representatividade explícitos | Não atribuir ao trabalho de campo prova social/estatística inexistente |
| §3.2.1, técnicas de recolha | Especificados **sete registos anexados E1–E7**, dois de coordenação/tesouraria e cinco de membros; assinalada ausência no anexo de datas, locais, recrutamento e número de grupos | Rastreabilidade e integridade metodológica |
| §3.2.1, proveniência RF | Passagem de `requisitos extraídos das entrevistas` para `alguns requisitos relacionados com necessidades descritas` | Associação temática não prova origem histórica dos requisitos |
| §3.2.2, tratamento qualitativo | Descritos seis eixos de categorização exploratória produzidos nesta revisão | Não inventar codificação prévia à recolha |
| Título e abertura do capítulo 4 | `CASO DE ESTUDO` → `CONTEXTO DE APLICAÇÃO` no corpo e no texto em cache do índice geral | Capítulo apresenta contexto nacional e perfis conceptuais, não caso empírico delimitado |
| Final do §4.2 | Novo parágrafo curto com correspondências E1–E7 para perda de registos, confirmação, rotação, consulta e notificações; E7 distingue perda documental de fraude | Evidência contextual com fronteiras claras |

**Não se alteraram** HG/HE1–HE5, §5.4.4, referências bibliográficas, tabelas de requisitos, conclusões, dados de campo, listas de figuras ou imagem 2.4.2.

## 2. Correcções dos diagramas SmartArt originais — sem substituição de imagem

**Figura 2.4.1 (SmartArt 3, página física 45)**: textos de emissor, titular e verificador foram revistos para `Emite e assina credenciais verificáveis`, `Recebe e apresenta a credencial` e `Verifica assinatura, emissor e estado da credencial`. Removida a falsa localização da validação `dentro da blockchain`. Conteúdo actualizado em **data3 e drawing3**, mantendo a mesma estrutura e elementos gráficos.

**Figura 2.4.3 (SmartArt 4, página física 46)**: revistos os textos de `Ledger`, `VCs` e `Wallets` para explicitar registo opcional consoante método DID, integridade/autenticidade **sem cifragem obrigatória**, e carteira/aplicação como possibilidade conceptual. Conteúdo actualizado em **data4 e drawing4**, mantendo SmartArt editável.

As representações continuam conceptuais e não demonstram uma implementação de carteira SSI completa, método DID público ou interoperabilidade W3C Data Integrity.

## 3. Testes de regressão documental
| Controlo | Resultado |
|---|---|
| Pacote ZIP OOXML | Integridade aprovada |
| Renderização por LibreOffice/PDF | **157 páginas**, iguais à origem |
| XML OOXML alterados | Apenas os cinco explicitados acima |
| **48 ficheiros multimédia** | Binariamente idênticos |
| **4 partes de comentários Word** | Binariamente idênticas |
| **26 tabelas** | Mesma contagem |
| **59 SEQ**, **45 REF**, **4 TOC** | Mesmas contagens, referências preservadas |
| Campos, estilos, numeração, relações, partes de media | Intactos fora dos cinco XML modificados |
| Páginas verificadas visualmente | 45–46 (SmartArt); 65–68 (metodologia); 71–75 (capítulo 4); 129–131 (discussão/conclusão); restantes por comparação de páginas antes/depois |
| Inspecção do conteúdo fora dos limites da página | Zero caixas textuais fora da página |
| Páginas diferentes na rasterização comparativa | 5, 23, 45, 46, 66–68, 71–75; restante conteúdo visual inalterado ao limiar de 0,08% |

**Iteração:** a primeira versão de ensaio tinha 158 páginas devido a prolongamento do §5.4.4; o novo texto redundante foi retirado mantendo a síntese E1–E7 em §4.2, e a versão final voltou a **157**. Não houve reescrita global.

## 4. Pendências NÃO encerradas
1. **Faculdade / USTM FCTI**: confirmação oficial do limite de 60 páginas mencionado numa cópia não autenticada do Manual de 2018, APA e cronograma. A monografia possui 122 páginas de Introdução até fim das Referências; **não declarar conformidade**.
2. **Word Microsoft**: revalidar `Actualizar todos os campos` nos 4 TOC/59 SEQ/45 REF, verificar listas, páginação e comentários (renderização em LibreOffice não equivale ao teste no Word).
3. **Entrevistas**: recuperar de fonte primária a amostragem, datas, local, grupos e documentação de consentimento. A matriz E1–E7 não demonstra origem histórica dos requisitos, representatividade ou saturação.
4. **Figuras externas**: direitos de reprodução da Figura 2.4.2 e outros desenhos não foram comprovados; sem edição da imagem 2.4.2.
5. **Revisão de conteúdo de Figura 2.4.4**: foi observada em SmartArt 6 terminologia que pode sugerir prevenção de fraude, eliminação de autoridade central e integração financeira; requer auditoria própria antes de submissão.
6. **Validação científica**: hipóteses sobre redução de fraude e confiança comportamental continuam não demonstradas empiricamente. Não criar dados ou estatísticas retrospectivos.

**Estado editorial:** versão integrada disponível como DOCX, **canónica de trabalho** derivada exclusivamente da última versão aprovada; **não certificada para submissão** enquanto subsistirem os pontos anteriores.
