# Matriz de rastreabilidade: HG e HE1–HE5 ↔ evidências (29/10/2026)

## Fontes e abordagem

**Texto de referência do autor:** `Monografia_Final_Revista.docx`, versão de
29/10/2026. Enunciados transcritos das secções **Hipóteses** (capítulo I)
e a interpretação actual foi comparada com a **secção 5.5.2**
(páginas impressas 108–109). O documento **não foi alterado**.

**Evidências verificáveis:**
- [Testes Django 120/120](https://github.com/enoqueJonas/mono-backend/actions/runs/40878541635).
- [Integração Django/PostgreSQL/Ganache e recuperação](https://github.com/enoqueJonas/mono-backend/actions/runs/40878029658).
- [Brownie 14/14](https://github.com/enoqueJonas/mono-backend/actions/runs/40878468432).
- [Falha original de consistência reproduzida](https://github.com/enoqueJonas/mono-backend/actions/runs/40877162687).
- [Correcção de consistência](consistency-recovery-2026-10-29.md) e
  [relatório Brownie](brownie-contract-tests-2026-10-29.md).
- Os testes executaram **dados sintéticos** em ambiente controlado.

**Critério de interpretação:** preservar enunciados originais, distinguir
mecanismo implementado de efeito social observado e não inferir causalidade
ou percentagens de fraude a partir de um protótipo.

## Matriz

| ID | Formulação original (capítulo I) | Evidência positiva real | Limitação decisiva | Veredicto defensável |
|---|---|---|---|---|
| **HG** | «A adopção de um sistema digital baseado em Blockchain e Identidade Descentralizada actua como um mecanismo de governação capaz de substituir a intermediação bancária formal, convertendo o capital social e o histórico de poupança da população informal moçambicana em credenciais de reputação financeira.» | Credenciais de histórico contributivo emitidas e verificadas; fluxo com PostgreSQL/Ganache demonstrado; grupos geridos em aplicação sem banco no circuito de teste | Não se demonstrou substituição jurídica/económica de intermediação, aceitação de reputação por terceiros, nem registo real de pagamento | **Parcialmente sustentada apenas na capacidade técnica de representar o histórico** |
| **HE1** | «O uso de Blockchain garante a integridade dos dados financeiros, eliminando assimetrias de informação e erros de registo manual comuns na gestão tradicional do Xitique.» | Hashes de documentos assinados ancorados; adulteração de montante rejeitada; consulta/reconciliação de transacções verificadas; testes Brownie | Hash protege contra alteração *posterior* à ancoragem, não contra entrada de dados errados, omissão ou assimetria informacional | **Parcialmente sustentada** (integridade sim; eliminação de erros e assimetrias não demonstrada) |
| **HE2** | «A adoção de protocolos de Identidade Descentralizada permite a autenticação segura dos membros e a protecção da privacidade, mitigando o risco de usurpação de identidade e práticas abusivas no seio das cooperativas.» | DID did:key dos emissores, assinatura Ed25519 real e verificação de credenciais; controlo de autorização revogação; casos de falsificação rejeitados | Sem ensaios de gestão de chaves comprometidas, resistência à usurpação real, divulgação selectiva ou privacidade empiricamente medida; identidade ainda resolvida na BD local | **Parcialmente sustentada** na integridade/autenticidade da credencial, não na mitigação de usurpação e privacidade real |
| **HE3** | «A rastreabilidade em tempo real das operações e a imutabilidade dos registos reduzem significativamente a probabilidade de fraudes internas e a má gestão de fundos comunitários.» | Detecção de alterações e revogações, duplicados rejeitados; rasto técnico de transacção e reconciliação; credencial adulterada rejeitada | Sem grupos reais, linha de base e medição de incidência de fraude/erros antes e depois; origem do pagamento não verificada em operador real | **Não demonstrada quanto à redução significativa de fraude** |
| **HE4** | «A criação de um histórico digital auditável de contribuições e reembolsos gera confiança digital, que fortalece a coesão do grupo e reduz a taxa de incumprimento a longo prazo.» | Histórico consultável e emissão de credenciais contributivas (demonstração de funcionalidade) | Sem estudo longitudinal, questionários pré/pós e indicadores de incumprimento ou coesão | **Não avaliada empiricamente nos efeitos comportamentais** |
| **HE5** | «A solução tecnológica baseada em arquitecturas peer-to-peer (P2P) é tecnicamente viável para a realidade moçambicana, permitindo que os grupos operem com autonomia regulatória e técnica, independentemente da infraestrutura dos bancos comerciais.» | Protótipo web com componentes blockchain locais e backend Django/PostgreSQL, suite de testes e integração operacional em CI | Django e PostgreSQL são serviços centralizados; não se demonstrou arquitectura P2P entre os membros, autonomia regulatória, custos, conectividade ou adopção no contexto moçambicano | **Parcialmente sustentada quanto à exequibilidade laboratorial**, não quanto ao P2P pleno nem à autonomia |

## Síntese — avaliação da secção 5.5.2

A **classificação actual das hipóteses continua intelectualmente defensável**
e não deve ser tornada mais optimista apenas porque aumentou a cobertura
de testes.

A melhoria académica relevante é **incluir resultados experimentais rastreáveis
com metodologia, ambiente, casos, entradas e saídas observadas** no capítulo
de resultados, e referi-los explicitamente em 5.5.2. A discussão actual
distingue adequadamente efeitos técnicos de impactos sociais, mas ainda não
apresenta a matriz com os logs e IDs de execução acima.

### Ponto crítico de coerência arquitectural

O enunciado de **HE5** afirma uma arquitectura P2P. O protótipo que foi
efectivamente testado utiliza API Django/DRF, PostgreSQL e blockchain local.
Isso **não prova** que todos os membros comuniquem numa arquitectura
P2P independente. Ao redigir a defesa, explicar que a descentralização
está concentrada na ancoragem/verificação dos registos, não em toda a
arquitectura da aplicação.

### Limite jurídico e de interoperabilidade

Assinatura Ed25519 própria da aplicação e identificadores `did:key` não
equivalem automaticamente a certificado digital nacional, conformidade
regulatória, reconhecimento por bancos ou interoperabilidade integral
de padrões W3C. Estes limites permanecem na secção 5.5.4.

## Recomendações para reforço textual posterior

1. Inserir secção **Validação experimental do protótipo** no capítulo 5,
   com tabela de cenários, ambiente e resultados **reais**, incluindo uma
   falha de consistência e a sua correcção.
2. Na discussão 5.5.2, relacionar cada hipótese com a tabela de resultados
   e distinguir *capacidade técnica demonstrada* de *impacto não medido*.
3. Preservar as classificações prudentes de HG/HE1–HE5, salvo se um
   estudo novo e verificável apresentar evidência empírica para uma
   conclusão mais forte.
4. Relacionar a avaliação de confiança cultural com as entrevistas
   existentes na monografia, **sem afirmar** que entrevistas equivalem
   a avaliação longitudinal de uso real.
5. **Não alterar os gráficos nem os diagramas**.

## Estado

Matriz concluída para **triagem científica** com base no documento
e nos testes GitHub. Uma revisão final de redacção pode ser efectuada
quando a versão de código dos PRs #11–#14 estiver integrada e a secção
de resultados experimentais estiver pronta para o manuscrito.
