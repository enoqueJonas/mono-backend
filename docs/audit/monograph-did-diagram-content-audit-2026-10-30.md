# Auditoria visual do conteúdo técnico dos diagramas DID/VC — 30/10/2026

**Referência canónica:** `Monografia_Canonica_Proveniencia_DID_Revista_30102026.docx` (157 páginas, sem gráficos hipotéticos).  
**Material realmente inspeccionado nesta sessão:** páginas físicas **45 e 46** da versão anterior `Monografia_Canonica_Fontes_Xitique_Revistas_30102026.docx` (imagem renderizada da p.45 e texto da p.46).  
**Registo anterior:** `docs/audit/monograph-did-image-provenance-2026-10-30.md` informa que a revisão canónica alterou somente `word/document.xml`, preservou os 48 media e **não modificou imagens/diagramas**, corrigindo apenas a legenda 2.4.2 e o parágrafo relativo à Figura 2.4.1. Não foi possível nesta etapa inspeccionar os bytes do DOCX **mais recente**: por isso o estado da figura final exige revalidação após obter o ficheiro.

## Problemas observados que subsistem nos desenhos

| Elemento | Texto do desenho anterior | Problema científico | Formulação tecnicamente defensável sugerida |
|---|---|---|---|
| **Figura 2.4.1 — Emissor** (p.45) | «Entidade responsável pela emissão de credencias criptografadas» | Criptografia/assinatura de integridade não equivale a cifragem/confidencialidade; VCs não são necessariamente cifradas | **«Entidade que emite e assina digitalmente credenciais verificáveis»** |
| **Figura 2.4.1 — Verificador** (p.45) | «Validador da autenticidade da credencial dentro da blockchain» | Verificador não precisa de executar verificação criptográfica dentro da blockchain; pode consultar registo de chaves/estado se a arquitectura o utilizar | **«Entidade que verifica assinatura, emissor e estado da credencial; pode consultar um registo de confiança»** |
| **Figura 2.4.1 — Titular** (p.45) | «Único detentor e gestor da identidade na carteira digital» | Generalização do controlo exclusivo inconsistente com protótipo: DID e vínculo são mantidos na aplicação; não há wallet autossoberana completa | **«Entidade a quem a credencial é emitida; armazena ou apresenta a credencial conforme o modelo da solução»** |
| **Figura 2.4.3 — VCs** (p.46) | «Declaração digital feitas pelo emissor sobre o titular, criptografadas para evitar a alduteração» | Imprecisão conceptual e gramatical; integridade por assinatura/prova, não cifragem obrigatória | **«Declarações digitais sobre um titular, emitidas com mecanismos criptográficos de autenticidade e integridade»** |
| **Figura 2.4.3 — Ledger** (p.46) | «Infraestrututra que documentos DID são permitidos a resolução de identificadores e verificação de chaves públicas» | Construção ininteligível; nem todos DID resolvem via blockchain, nem a assinatura exige ledger | **«Registo opcional de identificadores, material de verificação e/ou estado, conforme o método DID»** |
| **Figura 2.4.3 — Wallets** (p.46) | «Interface primário do utilizador, dado com agentes digitais utilizados pelo titular para armazenar, gerir e apresentar as credenciais de forma segura e privada» | Problemas de redacção; apresenta capacidades que o protótipo não implementa integralmente | **«Aplicação que pode permitir ao titular gerir e apresentar credenciais verificáveis; não integrada como carteira autossoberana completa no protótipo»** |
| **Figura 2.4.3 — estrutura visual** (p.46) | Blocos `Ledger`, `VCs`, `Wallets` em forma de três camadas | Pode sugerir arquitectura DID universal obrigatória, contrariando parágrafo que já ressalva ser apenas uma representação conceptual | Adicionar explícito **«elementos possíveis do ecossistema DID/VC; não são camadas obrigatórias»** ou redesenhar mediante aprovação |

**Sem modificação da monografia nesta etapa.** Não substituir o desenho, pois o utilizador determinou preservar as imagens até decisão expressa; preparar apenas proposta de alteração e inspeccionar impacto em remissões e paginação.

## Comparação de proveniência da Figura 2.4.2 (imagem de p.45)
O desenho incorporado representa emissor (ícones de instituições), smartphone central com `Wallet App` e verificador (edifício azul), acima de uma faixa turquesa com cubos Blockchain. O artigo de **Davi Albergaria (03/01/2024)** refere explicitamente um *outro* diagrama retirado de Microsoft e ilustra um caso Woodgrove/Alice/Proseware. A documentação Microsoft Entra Verified ID mostra o mesmo caso nominativo. **Nenhuma correspondência visual exacta com a Figura 2.4.2 foi demonstrada.** A actual atribuição `esquema ilustrativo; cf. Albergaria, 2024` é mais cautelosa, mas não resolve proveniência e licença da imagem concreta.

- Albergaria: https://www.identityacademy.com.br/post/o-que-s%C3%A3o-identidades-descentralizadas---dids-na-pr%C3%A1tica
- Microsoft: https://learn.microsoft.com/en-us/entra/verified-id/decentralized-identifier-overview

## Fontes técnicas de referência
- W3C, *Verifiable Credentials Data Model v2.0*, Recomendação de 15/05/2025: https://www.w3.org/TR/vc-data-model/
- W3C, *Verifiable Credential Data Integrity 1.0*, Recomendação de 15/05/2025: https://www.w3.org/TR/vc-data-integrity/
- W3C, *DID Core 1.0*, Recomendação de 19/07/2022: https://www.w3.org/TR/did-core/
- A bibliografia do manuscrito menciona W3C 2019/2022; usar documentos de 2025 como base de **auditoria**, sem alterar de imediato o quadro teórico ou declarar que o protótipo implementa VC 2.0.

## Critérios de aceitação
- [ ] Reabrir a **última versão canónica DOCX** e confrontar os textos específicos dos desenhos 2.4.1/2.4.3.
- [ ] Aprovar a correcção de cada rótulo materialmente incorrecto, evitando criar promessas de funcionalidades não implementadas.
- [ ] Resolver proveniência/licença de 2.4.2; se não comprovada, escolher entre autorização e desenho original que não reproduza iconografia protegida.
- [ ] Executar controlo de regressão: 157 páginas ou justificar variação, 26 tabelas, 4 partes de comentários, 59 SEQ, 45 REF, 4 TOC, 48 media antigos preservados excepto substituições aprovadas.
- [ ] Actualizar lista de figuras e entradas bibliográficas se a autoria/fonte mudar.
- [ ] Manter as issues de direitos/imagens **abertas** até prova suficiente.

**Estado:** inconformidades **observadas na versão anterior**, ainda **não corrigidas**; revalidar DOCX DID final antes de editar.
