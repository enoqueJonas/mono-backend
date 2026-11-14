# Auditoria de consistência — PostgreSQL e blockchain (29/10/2026)

## Questão experimental

O sistema garante que uma credencial assinada pode ser recuperada quando a
transacção blockchain é confirmada mas a gravação final em PostgreSQL falha?

**Antes da correcção: não.** O hash era ancorado antes de criar a credencial
na BD, dentro de uma transacção `transaction.atomic` que não abrange a
blockchain. Uma falha SQL deixava uma ancoragem órfã e perdia o UUID, o
documento assinado e a relação entre o membro e o hash.

## Evidência da falha original

- [GitHub Actions 40877162687](https://github.com/enoqueJonas/mono-backend/actions/runs/40877162687).
- Teste de injecção de falha após `CredentialRegistry.registerCredentialHash`.
- Resultado observado: `chain_confirmed=True local_record_missing=True`.
- **O teste passou por verificar a reprodução da falha, não por comprovar segurança.**

## Desenho de recuperação implementado nesta branch

1. **Preparar (PostgreSQL):** com transacção SQL e bloqueio da associação
   ao grupo, verificar requisitos, construir e assinar a VC. Persistir UUID,
   documento assinado, hash e estado `PENDING`; concluir essa transacção.
2. **Ancorar (Ganache/Ethereum):** enviar hash da mesma VC. Se ocorrer
   indisponibilidade, o documento pendente permanece durável.
3. **Finalizar (PostgreSQL):** numa transacção SQL, guardar metadados da
   transacção confirmada e alterar a credencial para `ACTIVE`.
4. **Recuperar (operador):** localizar o registo `PENDING`, verificar que
   o mesmo hash existe no contrato e não está revogado, recuperar o recibo
   através do evento `CredentialAnchored` e completar a finalização.
   A operação é idempotente para registos já `ACTIVE`.
5. Uma restrição única de base de dados impede emissões concorrentes
   activas/pendentes para o mesmo membro, tipo e período.

Comando administrativo (por defeito exige pelo menos 5 minutos de idade):

```bash
python manage.py reconcile_credential_issuance <credential-uuid>
# Apenas para ensaios controlados:
python manage.py reconcile_credential_issuance <credential-uuid> --force
```

A rotina **não envia outra transacção** se a ancoragem ainda não estiver
confirmada; a ausência de confirmação exige investigação do operador.

## Resultado experimental da correcção

- Ambiente: Django/DRF + PostgreSQL 16 + Ganache local, chain ID 1337.
- [GitHub Actions 40877884560](https://github.com/enoqueJonas/mono-backend/actions/runs/40877884560): **1 cenário integrado aprovado**.
- [GitHub Actions 40878029658](https://github.com/enoqueJonas/mono-backend/actions/runs/40878029658): **1 cenário integrado aprovado**.
- Procedimento: emitir VC 1, verificar, adulterar e rejeitar,
  revogar e rejeitar; emitir VC 2 com uma falha provocada na escrita
  do registo de ancoragem; recuperar VC 2 a partir do evento on-chain.
- Observado após a falha injectada:
  `chain_confirmed=True intent_durable=True reconciled=True duplicate_anchoring=False`.
- Testada segunda reconciliação da mesma VC: sem nova transacção,
  sem duplicação de ancoragem e com estado `ACTIVE`.

## Limitações e riscos residuais

- A recuperação é administrativa, **não automática nem agendada**.
- Uma transacção enviada, mas ainda não confirmada, pode exigir
  consulta da mempool e das confirmações; a rotina actual falha
  de forma segura em vez de criar outra ancoragem.
- O método de recuperação consulta eventos desde o bloco 0:
  apropriado para Ganache e demonstração, não para cadeias extensas
  sem indexação e bloco inicial de implantação.
- A reconciliação bloqueia uma linha PostgreSQL durante a chamada Web3;
  necessita timeout, observabilidade e operação escalável em produção.
- Sem ensaios de reorganização de blockchain, falha prolongada do nó,
  múltiplos signatários, corrupção da chave privada ou migração entre redes.
- A consistência transaccional é **eventual e recuperável**, não
  atomicidade ACID distribuída entre PostgreSQL e Ethereum.
- Os testes não provam origem financeira de contribuição, diminuição
  de fraude real nem confiança sociocultural dos membros.

## Relevância para a monografia

A demonstração fornece evidência de que o protótipo pode preservar
rastreabilidade e reconciliar uma falha específica entre subsistemas,
sem fingir que uma transacção Ethereum pode ser revertida por uma
transacção PostgreSQL. As hipóteses sobre redução estatística de
fraude, autonomia operacional ou adesão social não ficam confirmadas
por este cenário.

**Gráficos e diagramas da monografia não foram modificados.**
