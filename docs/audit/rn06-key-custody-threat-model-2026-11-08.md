# Modelo de confiança e custódia de chaves — monografia de Xitique

**Data da auditoria:** 8 de Novembro de 2026
**Âmbito:** ramo `feat/rn06-independent-disbursement-approval` (PR #26), dependente dos PRs #11 → #13 → #14 → #22. Não descreve produção.

## 1. Quem detém as chaves — resposta verificável no código

| Identidade / chave | Geração e armazenamento | Quem assina | O que isto NÃO prova |
|---|---|---|---|
| Ed25519 DID dos membros | `identity/utils/keys.py::generate_did_key_pair` gera no servidor e cifra com Fernet; `identity/models/base_did.py::encrypted_private_key` conserva na BD; `DID_KEY_ENCRYPTION_KEY` reside na configuração do backend | Aplicação pode recuperar bytes via `decrypt_private_key` | Membro não controla sozinho a chave; DID não implica autocustódia |
| Ed25519 DID do grupo / emissor de VC | Mesmo mecanismo de geração/armazenamento, associado a `GroupDID` | `credentials/services/credential_signer.py::CredentialSigner.sign` decifra a chave do grupo e assina o JSON canonizado da VC | Assinatura do emissor não equivale a assinatura de cada participante |
| EVM da blockchain | `BLOCKCHAIN_PRIVATE_KEY` + `BLOCKCHAIN_ACCOUNT_ADDRESS` nas settings do backend | `blockchain/services/transaction_service.py` assina e envia `eth_sendRawTransaction` | Não existe multisig de membros nem ligação técnica de uma aprovação a um movimento bancário |

O código `blockchain/security/registry_operator.py` confirma em runtime ID de rede, existência de bytecode implantado e igualdade entre operador de contrato e conta EVM configurada. Os contratos `GroupRegistry`, `ContributionRegistry` e `CredentialRegistry` usam `onlyOperator`. Assim, **só esta conta backend** pode alterar os registos — isso é autorização centralizada on-chain, não quórum da blockchain.

## 2. O que RN06 realmente impede

A RN06 bloqueia **pela API Django**, dentro das regras do sistema, a conclusão administrativa de uma proposta sem maioria estrita de contas elegíveis, mínimo dois aprovadores independentes do proponente e do beneficiário. Os votos estão em PostgreSQL, vinculados a autenticação do backend, não assinados por chaves privadas pessoais em dispositivos dos membros. A implementação revista bloqueia também conclusão quando os montantes ou participantes do ciclo divergem do estado aprovado.

**Protecção comprovada:** testes automáticos Django, contratos Solidity e cenários browser API/Next.js com contas separadas e dados sintéticos.

**Fora do modelo:** impedir que tesoureiro efectue levantamento no M-Pesa, e-Mola, banco ou numerário por canal externo; confirmar que contribuição manual foi paga; impedir manipulação directa do PostgreSQL por operador privilegiado; impedir cadastro de identidades fictícias se não houver verificação humana.

## 3. Modelo de ameaças e falhas

| Adversário | Controlo / capacidade | Protecção existente | Risco residual |
|---|---|---|---|
| Membro comum autenticado | Tenta votar duas vezes ou votar sem elegibilidade | Autorização no serviço, unicidade do voto, testes negativos | Conta comprometida ou suplantação de identidade |
| Gestor desonesto sem acesso à infraestrutura | Propõe e tenta completar unilateralmente | Proponente/beneficiário excluídos da votação; quórum >= 2; validação do livro | Pode registar contribuições manuais inverídicas antes de serem ancoradas |
| Tesoureiro com acesso a fundos externos | Move dinheiro fora do software | Nenhuma regra desta versão impede o pagamento externo | Desvio de fundos pode ocorrer apesar do quórum administrativo |
| Operador de aplicação/infraestrutura comprometido | Lê BD, obtém variáveis de ambiente, altera código, contas ou votos | Chaves cifradas em repouso; restrições on-chain ao operador | Se possui a chave Fernet e a chave EVM pode assinar VCs e ancorar/revogar registos; votos DB não são prova independente |
| Terceiro Ethereum sem chave autorizada | Submete transacções a registos | `onlyOperator` testado no Ganache | Não garante autenticidade do evento económico que originou o hash |
| Perda de chave Fernet ou EVM | Não consegue decifrar DID ou assinar transacções | Não há processo completo de recuperação/rotação demonstrado | Indisponibilidade e risco de perda permanente de acesso às assinaturas |

## 4. Controlo vs hipótese

**Demonstrado em ambiente experimental:** emissão e verificação de VC com assinatura Ed25519; integridade/revogação de hash on-chain por operador; aprovação RN06 por duas contas distintas num grupo com quatro membros; rejeição de votos repetidos e ineligíveis; bloqueio de conclusão quando pagamento sintético é revertido; recuperação de uma falha transitória entre Ganache e PostgreSQL.

**Não demonstrado:** redução estatística de fraude num Xitique real; SSI com custódia exclusiva dos participantes; assinatura multiparticipante de transacção económica; segregação de funções entre operadores de infraestrutura; bloqueio do movimento financeiro pelo prestador.

## 5. Prioridades antes de uma implantação não experimental

1. Decisão formal do modelo de custódia de chaves: central, híbrido, ou autocustodiado; rotação, revogação, perda, backups e compromissos.
2. Política comunitária de admissão/identidade, revogação de votos, resolução de conflitos, saída de membros, quórum alternativo para grupos pequenos.
3. Confirmação financeira independente para todas as contribuições; autorização de débito controlada por prestador financeiro ou sistema multisig, se for alegada prevenção efectiva de fraude de tesoureiro.
4. Auditoria externa das credenciais e da infra-estrutura; isolamento de segredos; separar operador administrativo do operador de assinatura; MFA para operações sensíveis.
5. Verificação de migrações e deploy de novos contratos, actualização e validação de ABI/bytecode, gestão de endereços e proveniência.
6. Não confundir simulação Ganache e conta centralizada com rede blockchain operada por várias entidades independentes.

## 6. Formulação recomendada à pergunta do júri

> **Quem detém as chaves?** Na implementação experimental, o backend gera e conserva, cifradas, as chaves Ed25519 dos DIDs de pessoas e grupos. A chave Ethereum de operação está configurada no servidor. A aplicação assina credenciais do grupo e transacções de registo. Portanto, a versão testada **não é autocustodiada**, embora use identificadores descentralizados e assinaturas digitais.
>
> **Como se protege um membro de um tesoureiro desonesto?** A RN06 impede que um gestor aprove sozinho um desembolso *dentro da aplicação*: requer votos independentes e revalida contribuições/participantes. Mas não impede desvio de numerário nem transferências externas, e não certifica a veracidade de contribuições manuais. Para proteger fundos reais seria necessária a integração de uma autoridade de pagamento que imponha o quórum, além de identidade verificável, recuperação de chaves e auditoria independente.
>
> **Porquê blockchain?** É útil como prova de integridade de registos fora da base de dados transaccional principal, verificável desde que a rede e o contrato sejam administrados de forma confiável. Não é necessária para a autenticação, grupos, pagamentos ou quórum RN06, que poderiam funcionar numa aplicação centralizada. Um sistema com PostgreSQL, assinaturas e trilho de auditoria protegido poderia satisfazer grande parte dos requisitos com menor complexidade. A blockchain só acrescenta valor se a independência e a verificabilidade dessa ancoragem forem relevantes e devidamente comprovadas.

**Limitação importante:** este memorando descreve código e testes de um protótipo; não é uma auditoria de segurança em produção nem uma certificação de identidade auto-soberana.
