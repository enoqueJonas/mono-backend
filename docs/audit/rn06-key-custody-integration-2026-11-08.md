# Auditoria de integração e custódia de chaves — RN06 / DID / EVM

**Data:** 8 de Novembro de 2026  
**Âmbito:** leitura e testes sobre PRs do backend #11, #13, #14, #22 e #26 e frontend #1. Os PRs encontram-se em rascunho; este relatório **não** autoriza merge ou deployment de produção.

## 1. Cadeia real de alterações

| Ordem | PR | Base | Responsabilidade |
|---|---|---|---|
| 1 | #11 | `master` | VCs assinadas, validação de prova e revogação |
| 2 | #13 | ramo #11 | autorização de revogação e HMAC do simulador de carteira |
| 3 | #14 | ramo #13 | consistência e recuperação PostgreSQL ↔ contrato |
| 4 | #22 | ramo #14 | restrições `onlyOperator` nos três contratos |
| 5 | #26 | ramo #22 | RN06, quórum de membros e verificações financeiras |
| 6 | frontend #1 | `master` | UX da votação RN06 e ensaio com browsers reais |

O PR #12 também modifica `.github/workflows/backend-tests.yml`, `config/settings_test.py`, `pytest.ini`, `requirements-dev.txt` e testes de carteira. Estes ficheiros também aparecem no PR #11. É necessária reconciliação antes de merge, não há fundamento para integrar os dois indiscriminadamente.

**Plano de integração:** rever e integrar por ordem de dependência, recalcular o diff de cada PR contra a nova base, actualizar o ramo-base no GitHub e repetir os testes na cabeça real após cada alteração. Não fazer squash/rebase/merge automático sem verificar a ascendência e alterações sobrepostas. O frontend só pode ser integrado depois de a API da RN06 estar disponível.

## 2. Quem controla as chaves implementadas?

| Chave | Criada/guardada por | Utilização verificada | Natureza |
|---|---|---|---|
| Ethereum EVM | `BLOCKCHAIN_PRIVATE_KEY` em configuração do backend; conta validada por `TransactionService` | Assinar transacções de escrita nos três registos; `operator` imutável nos contratos | **Operador único, custódia centralizada** |
| Ed25519 de utilizador | `DIDService.create_for_user` e `generate_did_key_pair`; chave privada cifrada no campo `UserDID.encrypted_private_key` | Associar `did:key` e chave pública; servidor possui função de decifragem | **Servidor detém possibilidade de decifragem** |
| Ed25519 de grupo/emissor | `DIDService.create_for_group`; `GroupDID.encrypted_private_key` | `CredentialSigner.sign` decifra e assina VCs, tendo o grupo como emissor | **Emissão controlada pela aplicação** |
| Aprovação RN06 | Conta web autenticada por JWT, `DisbursementApproval` em PostgreSQL | Autorizar mudança de estado `AWAITING_CONSENSUS` → `APPROVED` | **Não é assinatura de carteira individual** |

A chave Fernet `DID_KEY_ENCRYPTION_KEY` é obtida da configuração do servidor. A cifragem da base é relevante, mas qualquer processo com acesso a esta chave e às entradas cifradas pode recuperar as chaves privadas. Não foram encontrados no código avaliado um KMS/HSM, carteira autocustodiada, multisig de fundos ou uma política operacional completa de rotação/recuperação.

## 3. Modelo de ameaça e garantias limitadas

- **Membro não autorizado a escrever directamente na cadeia:** `onlyOperator` impede a escrita externa nos três registos, desde que o contrato actual e a chave do operador não estejam comprometidos. A API de revogação tem verificações de papel adicionais.
- **Gestor ou tesoureiro desonesto:** um gestor ainda pode confirmar contribuições manuais e introduzir dados inicialmente falsos; os hashes mantêm rastreabilidade posterior, não autenticidade financeira inicial. A RN06 dificulta conclusão unilateral dentro da aplicação, mas não bloqueia o acesso externo aos fundos.
- **Comprometimento do servidor/chaves:** o servidor consegue assinar os registos EVM e as credenciais do emissor. A restrição `onlyOperator` **não** protege contra o próprio operador comprometido.
- **Perda de chave EVM:** `operator` é `immutable`; os contratos não implementam mudança de operador. Recuperação exige plano de migração e contratos substitutos, e pode afectar a verificabilidade do histórico.
- **Colusão ou usurpação de contas:** duas aprovações de contas distintas não comprovam, por si só, duas pessoas independentes presentes no momento do voto. O sistema não tem segundo factor nem assinaturas autocustodiadas demonstradas nesta auditoria.
- **Relação blockchain ↔ pagamentos:** assinatura de credencial, ancoragem de contribuição e aprovação RN06 não demonstram liquidação por M-Pesa, e-Mola ou bancos.

## 4. Controlos novos no ramo experimental

- `blockchain/security/registry_operator.py`: verifica `chainId`, bytecode implantado e `operator()` correspondente a `BLOCKCHAIN_ACCOUNT_ADDRESS`, antes de utilizar qualquer um dos três clientes. `TransactionService` confirma separadamente correspondência entre endereço declarado e chave EVM.
- `integration_tests/test_registry_custody_ganache.py`: implanta bytecode compilado da fonte do commit, prova escrita legítima e rejeição de escrita por carteira adversária nos três registos; prova recusa de contrato implantado por conta estrangeira, rede errada e endereço sem bytecode.
- `identity/test_key_custody.py`: provas executáveis de que o backend decifra as chaves Ed25519 de utilizador e grupo, de que os documentos DID não expõem chaves privadas e de que chave Fernet não correspondente não decifra.
- `smart_contracts/scripts/deploy_guard.py`: exige que a conta Brownie que implanta os contratos corresponda ao endereço configurado e à chave EVM de backend no `.env`.
- `smart_contracts/scripts/deploy.py`: deixou de anunciar sincronização concluída depois de uma excepção ao copiar os artefactos ou actualizar o `.env`. A verificação real de operadores também foi acrescentada.
- `blockchain/test_deploy_guard.py`: testa a recusa de configuração ausente, endereço incompatível e conta implantadora incompatível sem usar contas reais.

## 5. Evidência e o que falta provar

**Executado na CI do ramo experimental:**
- 148 testes Django/segurança (incluindo regressões de chaves), aprovados.
- 5 testes de integração Django/Ganache e de custódia dos três registos, aprovados.
- 18 testes Brownie independentes em Ganache: a confirmar na CI específica deste commit quando este registo foi redigido.
- No frontend, 5 testes Playwright entre browsers autenticados distintos passaram antes da revisão de custódia; o backend SHA fixado no ensaio de frontend deve ser actualizado para o head correspondente e a suite deve repetir-se.

**Ainda pendente:**
- A execução real do script `brownie run deploy` com a pré-verificação e a cópia de ABI/`.env` não foi comprovada por CI (o teste de `deploy_guard.py` testa apenas a condição isolada).
- Não existe sincronização transaccional/atómica de todos os três artefactos ABI e endereços de deployment.
- Faltam plano de chaves e recuperação, segregação de funções, autorização de movimentação financeira, verificação independente de contribuições e política financeira de ex-membros (#28).
- A configuração actual não é um perfil endurecido de produção: `CORS_ALLOW_ALL_ORIGINS=True` e `ALLOWED_HOSTS=[]` devem ser revistos por ambiente.
- Falta rever o conflito com #12 e executar as suites após a integração real dos PRs em `master`.

**Conclusão:** o protótipo evidencia restrição à escrita on-chain, assinatura de credenciais e aprovação multiparticipante no sistema web, em ambiente de testes. Não é uma solução com custódia independente de identidade, governação blockchain por membros nem mecanismo que impeça fraude financeira fora da aplicação. A utilização da expressão *mitigação de riscos* na monografia deve referir-se a mecanismos técnicos específicos, não a uma redução de fraude medida empiricamente.
