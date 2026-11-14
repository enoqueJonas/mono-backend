# Monografia blockchain/Xitique — Etapa 22: ordem canónica de aplicação
**Data de controlo:** 14/11/2026  
**Estado:** instruções de edição, **não alterações aplicadas ao DOCX**.  
**Ficheiro-fonte único:** `Monografia_Blockchain_Etapa20_Tabelas_Integrais_Indices_Conferidos_13112026.docx` (conteúdo consultado na Library; bytes originais não autorizados para cópia neste turno).  
**Issue de execução:** https://github.com/enoqueJonas/mono-backend/issues/33

> A presente especificação substitui as instruções editoriais conflituantes dos pacotes Etapa 21/V2 e dos comentários anteriores. Os respectivos comentários conservam as **redacções completas**, mas devem ser interpretados segundo a hierarquia abaixo. Não reconstruir o DOCX canónico a partir de texto extraído.

## 1. Hierarquia de fontes, emendas e precedência
1. **Texto e artefactos do DOCX canónico de 13/11/2026** são a base, não a versão de Outubro.
2. **Correcções factuais de maior confiança** (referências, identificadores, conceitos errados) precedem cortes editoriais.
3. **Cortes da Etapa 22 por secção** substituem propostas anteriores de adição de parágrafos na mesma secção. Não somar dois textos de substituição.
4. **Resultados do código/testes** são evidência de comportamento experimental; não justificam alegar redução de fraude real, autonomia financeira ou consenso blockchain.
5. **Qualquer deslocação de quadros para apêndices** fica suspensa até confirmação da aplicabilidade do limite USTM/FCTI de 60 páginas (issue #15).

**Fontes dos textos integrais da Etapa 22:**
- Cap. II (2.1.2, 2.4.2, 2.5, 2.7.3 e Quadro 2.3.1): https://github.com/enoqueJonas/mono-backend/issues/33#issuecomment-6873832521
- Caps. III–IV (3.3, 3.4–3.4.4, abertura IV, 4.1, 4.2): https://github.com/enoqueJonas/mono-backend/issues/33#issuecomment-6873877769
- Cap. V (5.2.7, 5.3, 5.4.2, 5.4.4, 5.4.6): https://github.com/enoqueJonas/mono-backend/issues/33#issuecomment-6873932763
- Rectificações dos casos de uso e da transacção de criação de grupo: https://github.com/enoqueJonas/mono-backend/issues/33#issuecomment-6864237101

## 2. Ordem única de aplicação, sem sobreposições

### Fase A — Fixar o original e o inventário
- [ ] Obter **o DOCX original**, nunca o TXT; gravar uma cópia de trabalho com novo nome de versão.
- [ ] Comparar ZIP/OOXML antes das edições: imagens, diagramas, tabelas, comentários, campos TOC/SEQ/REF, bookmarks e relações internas. Contagens de referência de auditorias históricas (48 media, 4 TOC, 59 SEQ, 45 REF) **são expectativas a conferir** contra o original actual, não certificados para a Etapa 20.
- [ ] Congelar edição dos Apêndices A/B e das entrevistas/anexos, salvo identificadores claramente errados.

### Fase B — Correcções factuais pontuais
- [ ] **Quadro 2.3.1**: substituir classificações absolutas ("Segurança alta", "Transparência total", "Descentralização total", "Eficiência energética baixa") por qualificações dependentes do protocolo, validadores e governação. Usar a proposta do comentário Cap. II; evitar classificar Corda como blockchain global e atribuir ineficiência PoW ao Ethereum actual.
- [ ] **§2.4.1**: substituir *conjuntamente* o parágrafo iniciado por "No âmbito do protótipo desenvolvido nesta pesquisa..." e o parágrafo seguinte iniciado por "A auditoria ao código do protótipo esclareceu..." pelo texto único abaixo. **Não conservar os dois parágrafos originais nem acrescentar outro texto de DID/VC**:
  
  > No protótipo, utilizadores e grupos recebem DIDs do método did:key, associados a pares de chaves Ed25519 gerados no servidor. As chaves privadas são armazenadas cifradas com Fernet em PostgreSQL e podem ser recuperadas pela aplicação mediante a chave de cifragem mantida na sua configuração. A aplicação assina as Credenciais Verificáveis com a chave do DID emissor do grupo, cuja identidade é reconhecida pelos seus próprios registos. Separadamente, uma conta Ethereum operadora, gerida no servidor, submete as transacções de ancoragem e revogação aos contratos inteligentes na rede Ganache. O método did:key permite obter informação pública de verificação a partir do identificador, mas o fluxo de verificação implementado depende dos serviços da aplicação. Não existem carteiras autocustodiadas dos membros nem assinaturas autónomas das decisões de governação.

  Manter os parágrafos subsequentes de **recomendações e responsabilidades futuras**, sem os confundir com a implementação demonstrada.
- [ ] **RF-010, observação:** substituir "Não deve permitir a criação de uma credencial verificável para o mesmo período" por "Não são permitidas duas Credenciais Verificáveis activas do mesmo tipo para o mesmo membro e período; a substituição exige revogação da anterior." A declaração principal de RF-010 já está correcta.
- [ ] **RF-023:** "Consultar histórico de desembolsos efectuados" pode confundir conclusão administrativa com liquidação. Corrigir para histórico de **registos de desembolsos administrativamente concluídos** e actualizar observação com igual distinção.
- [ ] **RF-026:** a notificação é do **registo de conclusão administrativa**, não da transferência financeira verificada; corrigir declaração e observação sem prometer integração externa.
- [ ] **RF-030:** corrigir "registos armazenados na blockchain" para "correspondência entre os dados mantidos na aplicação e os hashes ancorados na blockchain". Evitar "autenticidade" no sentido de veracidade de pagamento.
- [ ] **Quadro 5.2.3 (RNF):** corrigir IDs e relações de rastreabilidade. RNF-001 -> RN05/RF-016/RF-031; RNF-002 -> RN04/RF-005/RF-007; RNF-003 -> RF-002/RF-008 (sem métricas quantitativas demonstradas); RNF-004 -> RF-019/RF-027 (objectivo de disponibilidade, não evidência de SLA); RNF-005 -> RF-002/RF-003; RNF-006 -> RN17/RN18/RF-027 (integração simulada); RNF-007 -> RN05/RF-016/RF-029/RF-031. Conferir se a faculdade requer apenas ligações aos RN ou aceita mistos RN/RF; não inventar RN inexistentes.
- [ ] **Quadro C.1:** alterar somente RF01 -> RF-001.
- [ ] **Quadro C.3:** alterar somente "RF06" incorrecto para RF-011, RF-012 e RF-016, com descrições correctas. **NÃO alterar Actor: Utilizador** e a pós-condição de criação/atribuição de gestor: já estão correctos. Nota sobre A2: o rollback de transacção SQL não desfaz uma transacção Ethereum minerada; não alegar atomicidade entre sistemas.
- [ ] **Quadro C.4:** alterar RF04 para RF-004, RF-006 e RF-007; **não adicionar RF-008** sem um caso completo de verificação independente.
- [ ] **§5.2.2:** corrigir a duplicação literal "descentralizada.Os casos de uso..." e eliminar a expressão editorial "diagramas ... recuperados, sem redesenho". Figuras 5.2.1 = UC02 Contribuições; 5.2.2 = UC03 Grupos. Manter quadro e figuras intactos.
- [ ] **§5.2.4:** remover "não foi criado nenhum diagrama novo nesta revisão"; manter Figura 5.2.5 e referências ao Apêndice A.

### Fase C — Cortes editoriais (versão única por secção)
- [ ] Aplicar **uma única vez** os cortes completos do comentário do **Capítulo II**, sobre §2.1.2, §2.4.2, §2.5, §2.7.3, mantendo Figura 2.7.1 e todas as fontes.
- [ ] Aplicar os cortes completos do comentário **Caps. III–IV**, sobre §3.3, §3.4/3.4.1–3.4.4, abertura IV, §4.1 e §4.2. Preservar Figura 4.1.1 no lugar lógico. Não excluir as fichas reais E1–E7, as suas correspondências, nem a ressalva do indicador INFOR 2021.
- [ ] Aplicar os cortes completos do comentário **Capítulo V**, sobre §5.2.7, §5.3, §5.4.2, §5.4.4 e §5.4.6. A Figura 5.2.8 deve ficar na abertura do §5.2.7, entre o texto de apresentação da arquitectura e a explicação de processos; a Figura 5.3.1 deve permanecer em §5.3. Não remover nem substituir qualquer imagem por descrição textual.
- [ ] **§5.4.3:** **não** substituir integralmente por uma terceira versão. Conservar a HG e HE1–HE5 da canónica, apenas clarificar em HE2 que autenticação da conta usa palavra-passe/JWT e que DID/VC apoia verificação de documentos, e em HE3 que reconciliação de ancoragens pendentes impede garantir rastreabilidade continuamente em tempo real. **Não mudar as hipóteses** do Capítulo I.
- [ ] **§5.4.1:** manter íntegros resultados de integração Django/PostgreSQL/Ganache e os **4/4 cenários adversos** de RN06 (parte da suite Playwright 5/5), bem como metodologias e limites. Não adicionar métricas inventadas.
- [ ] **§5.4.5:** manter análise jurídica e cultural, incluindo a Lei 3/2017, Decreto 59/2019 e limitação de certificação; só corrigir referências verificadamente erradas.
- [ ] **§5.4.6:** a versão integral mais recente **substitui** a anterior; não acrescentar novamente o parágrafo de custódia sugerido na Etapa 21 nem duplicar limitações da §2.4.1. Preservar no texto final a ameaça de operador com acesso à base de dados e à chave Fernet, a reversão apenas injectada em base de testes, a ausência de prova de pagamento e o estado de ancoragem pendente.
- [ ] **§6.1:** condensar segundo os quatro objectivos específicos (análise exploratória, arquitectura, protótipo, testes/condicionantes) e fechar com resposta explícita à pergunta de investigação; manter a natureza laboratorial dos resultados e ausência de medição de fraudes.
- [ ] **§6.2:** manter recomendações existentes; para avaliar efeitos sobre confiança/incumprimento (HE4), privilegiar estudo-piloto de **vários ciclos**, em vez de afirmar que um único ciclo comprova impactos longitudinais.

### Fase D — Revisão sem alterações desnecessárias
- [ ] Não criar módulos, classes, subprocessos ou hipóteses para colmatar lacunas de redacção.
- [ ] RN08–RN11 penalizações **estão implementadas** no backend, mas não declarar avaliação experimental de eficácia sem testes específicos comprovados.
- [ ] RN13: a alteração CONFIRMED→REVERSED foi usada como injecção de falha para bloquear conclusão; não alegar fluxo operacional de reversão/estorno.
- [ ] RN06: votos de **contas autenticadas** no PostgreSQL, não consenso Ethereum nem assinaturas autocustodiadas; em grupo pequeno sem dois elegíveis o sistema bloqueia a proposta.
- [ ] Confirmar que rótulos de figura, índices e tabelas não passam a usar linguagem editorial ("nesta revisão", "recuperado", "corrigido nesta auditoria").
- [ ] Não retirar referências bibliográficas automaticamente após cortes; rever citações órfãs e fontes secundárias em segunda passagem.

### Fase E — Redução estrutural **condicional**
- [ ] Antes de deslocar quadros, obter da USTM/FCTI confirmação escrita: manual aplicável em 2026, limite 60 páginas, contagem até referências, APA 6/7 e necessidade de cronograma.
- [ ] Se exigido, transferir os quadros integrais RN01–RN18, RF-001–RF-031 e RNF-001–RNF-007 para um Apêndice D, com síntese rastreável no corpo. Atualizar legendas, remissões, índices e referências; não encurtar os próprios quadros.
- [ ] Partida: Introdução a Recomendações = **73** páginas; Introdução a Referências = **79** páginas. Sem renderização não há prova de quantas páginas foram realmente removidas.

## 3. Validação de entrega — gates obrigatórios
- [ ] Comparar inventário de media e hashes com o original, tabelas, comentários e campos Word.
- [ ] Renderizar DOCX para PDF **apenas para QA**, contar páginas físicas e verificar legibilidade de todas as figuras/tabelas.
- [ ] Testar actualização conjunta de TOC/SEQ/REF em **cópia experimental**; não permitir que o editor desfigure o documento canónico ou elimine comentários.
- [ ] Conferir Quadros C.1–C.4, RF-010/023/026/030, RNF e a coerência da terminologia "conclusão administrativa".
- [ ] Rever todas as alterações como **diferença de conteúdo** contra a Etapa 20; proibir texto de instruções editoriais ou comentários internos na monografia.
- [ ] Só entregar documento como Etapa 22 canónica depois de revisão visual, documental e de paginação.

## 4. Estado verificável
- Cortes textuais propostos II e III–IV: **redigidos**, não aplicados.
- Cortes textuais V: **redigidos**, não aplicados; estimativa informativa 1685→845 palavras nos cinco trechos.
- Revisão pontual VI e tabelas C/RNF: **indicada**, não aplicada.
- **DOCX fonte não montado**: bloquear alegações de edição concluída.
