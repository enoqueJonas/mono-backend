# Auditoria da consistência terminológica das ilustrações — MONO

**Data:** 30 de Outubro de 2026  
**Versão-base:** `Monografia_Canonica_Ilustracoes_Auditadas_30102026.docx` — 156 páginas.  
**Nova versão:** `Monografia_Canonica_Terminologia_Visual_Uniformizada_30102026.docx` — **156 páginas**, SHA-256 `3f7107d586e803b39243fe87f8f1775d09192c54d8346901cab81e71aa031b7f`.

## Regra editorial aprovada
- **Criptografia** refere a área e as famílias de técnicas; **«Criptografia simétrica»** e **«Criptografia assimétrica»** são títulos de figuras e secções.
- **Cifragem**, **cifrar** e **decifrar** designam as operações de confidencialidade. São termos legítimos nos rótulos e não são sinónimos a eliminar mecanicamente.
- **Assinatura digital**, autenticação de origem e integridade não equivalem a cifragem/confidencialidade. A Figura 2.3.4 mantém as duas operações distintas.
- **Credenciais verificáveis** e **carteiras digitais** são os termos preferidos nas ilustrações DID/VC; `Wallets` foi substituído onde representava a categoria em português.
- **Recolha e refinamento de requisitos** é a designação uniforme do ciclo de prototipagem.
- `Proof of Work`/`Proof of Stake`, `DID`, `VC`, `hash`, `Blockchain` no início de título e nomes de componentes técnicos permanecem quando identificam padrões/termos próprios ou estão definidos no capítulo; não se traduzem artificialmente.

## Auditoria das 43 figuras
Confrontadas as **43 legendas efectivas** com a lista automática, capítulos e descrições/rótulos das figuras: 2.1.1; 2.3.1–2.3.10; 2.4.1–2.4.4; 2.7.1–2.7.2; 4.1.1; 5.2.1–5.2.12; 5.3.1–5.3.3; A.1–A.8; B.1–B.2. As capturas e diagramas UML mantêm vocabulário funcional e identificadores de entidades. Não se alterou código, fluxos, evidência experimental nem identidades dos participantes.

### Alterações efectivas
1. **Figura 2.3.3:** imagem `word/media/image4.png`: título interno alterado de **«CIFRAGEM SIMÉTRICA»** para **«CRIPTOGRAFIA SIMÉTRICA»**, em conformidade com a legenda, a Lista de Figuras e o subtítulo 2.3.3.1. As operações «CIFRAR», «DECIFRAR» e a indicação da chave K foram preservadas. Fonte SVG original actualizada no GitHub.
2. **Figura 2.3.4:** nenhuma mudança necessária: a legenda na canónica é **«Criptografia assimétrica»**, correctamente; o desenho contém «A · CIFRAGEM — confidencialidade» e «B · ASSINATURA DIGITAL — autenticidade e integridade», operações distintas e terminologicamente apropriadas. A captura de ecrã apresentada pelo autor mostrava uma legenda antiga/incoerente, não encontrada na canónica agora auditada.
3. **Figura 2.4.3:** rótulo `Wallets` → **`Carteiras digitais`** nas duas partes nativas do SmartArt `word/diagrams/data4.xml` e `drawing4.xml`. A legenda e as descrições científicas permaneceram.
4. **Figura 2.7.2:** `Colecta e/ou refinamento de requisitos` → **`Recolha e refinamento de requisitos`** em `data8.xml` e `drawing8.xml`; primeira alínea descritiva do texto adjacente também ajustada de `Colecta` para `Recolha`.
5. **Correcção de precisão científica adjacente à Figura 2.3.3:** «a cifragem simétrica, a criptografia assimétrica, as assinaturas digitais...» → «a cifragem (simétrica ou assimétrica), as assinaturas digitais...», separando operação e disciplina.
6. **Defeito de campo cruzado detectado na renderização:** a introdução da Figura 2.7.2 terminava visualmente com `etapas:2.7.2`, embora o Word apresentasse o campo `REF` vazio depois da frase. Reposicionou-se o **campo REF existente** para dentro de «A Figura 2.7.2 sintetiza ... etapas:» e preencheu-se o seu resultado em cache. O campo continua automático e a contagem de 45 `REF` foi preservada.

## Regressão documental e visual
- **156 páginas** no PDF exportado; nenhuma nova página ou deslocação de capítulos.
- Comparação de **todas as 156 páginas** na mesma resolução, antes/depois: diferenças somente nas páginas físicas **30, 31, 46 e 58**; **152 páginas visualmente idênticas**.
- Comparação do texto extraído: diferenças nas mesmas quatro páginas; zero textos fora dos limites das páginas.
- Inspecção ampliada da imagem da Figura 2.3.3, SmartArt da Figura 2.4.3 e Figura 2.7.2: sem recortes ou sobreposição, campo REF agora no lugar correcto.
- ZIP DOCX íntegro com **129 partes**; somente **seis partes alteradas**: `word/document.xml`, `word/media/image4.png`, `word/diagrams/data4.xml`, `drawing4.xml`, `data8.xml`, `drawing8.xml`.
- **48 ficheiros de imagem/media**, **26 tabelas**, **4 partes de comentários do supervisor**, **361 bookmarks**, **59 campos SEQ, 45 REF e 4 TOC**. Todos preservados; nenhuma remoção de anexos, imagens ou legenda.
- Legendas reais 2.3.3 e 2.3.4 conferidas no Word, não apenas na lista automática.

## Pendências não reabertas
- **Actualização final dos índices no Microsoft Word** numa cópia, tendo em conta que uma experiência anterior no LibreOffice com regeneração da lista de figuras introduziu uma página adicional. A presente revisão **não** fez actualização global dos índices.
- **Resposta da FCTI/USTM** ao e-mail já enviado, quanto ao manual vigente e calendário de defesa.
- **Validação funcional no navegador** do frontend Next.js contra o backend na branch de auditoria com testes aprovados, antes de gravar a demonstração. Não declarar a integração gráfica validada apenas por correspondência de endpoints.

**Conclusão:** padronização terminológica das ilustrações concluída; termos tecnicamente diferentes permaneceram distintos e a canónica conserva as **156 páginas**. A versão validada é `Monografia_Canonica_Terminologia_Visual_Uniformizada_30102026.docx`.