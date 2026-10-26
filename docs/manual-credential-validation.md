# Validação manual — ciclo de credenciais (Ganache + PostgreSQL)

> Estado: roteiro de execução, **não** evidência de testes concluídos. Executar num ambiente local descartável com dados de demonstração.

## Preparação

1. Iniciar PostgreSQL, Ganache e o backend com as configurações do projecto.
2. Confirmar que as migrações foram aplicadas e que o contrato CredentialRegistry está implantado no endereço configurado.
3. Criar um grupo com DID activo, um gestor activo, um membro activo com DID e pelo menos uma contribuição CONFIRMED dentro do período pretendido.
4. Obter tokens de autenticação válidos do gestor e do membro.
5. Antes dos cenários, executar `python manage.py check` e `python manage.py migrate --check` no ambiente do backend. Guardar o resultado.

## Cenários manuais

| ID | Acção | Resultado esperado |
| --- | --- | --- |
| VC-01 | Gestor emite credencial para o membro e período com contribuições confirmadas | HTTP 201; documento contém `id`, `issuer`, `proof`, `expirationDate`; hash e transacção registados |
| VC-02 | Consultar a credencial emitida usando o identificador devolvido | HTTP 200; `credential_document.id` = `urn:uuid:<id do registo>` |
| VC-03 | Enviar `credential_document` original ao endpoint de verificação | `data.valid: true` |
| VC-04 | Alterar `credentialSubject` numa cópia do documento e verificar | `data.valid: false` |
| VC-05 | Remover `proof` numa cópia e verificar | `data.valid: false` |
| VC-06 | Repetir emissão para mesmo membro e período enquanto a primeira está activa | Rejeição por duplicado; nenhuma nova ancoragem |
| VC-07 | Tentar emissão por membro sem papel MANAGER | Rejeição por autorização; nenhuma ancoragem |
| VC-08 | Gestor revoga a credencial; verificar novamente o documento original | Revogação bem-sucedida; `data.valid: false` |
| VC-09 | Tentar revogação por membro não gestor | Rejeição por autorização |
| VC-10 | Verificar documento expirado com assinatura/ancoragem coerentes num ambiente controlado | `data.valid: false` |

## Endpoints

- `POST /api/v1/credentials/<group_id>/credentials/` — emissão (gestor).
- `GET /api/v1/credentials/<credential_id>/` — consulta.
- `POST /api/v1/credentials/verify/` — corpo: `{"credential": <documento>}`.
- `POST /api/v1/credentials/<credential_id>/revoke/` — corpo: `{"reason": "Validação manual"}`.

## Evidências a recolher

Para cada cenário: data/hora, actor, identificador do grupo e da credencial, código HTTP, resposta sanitizada, hash do documento, hash da transacção blockchain e resultado PASS/FAIL. Nunca guardar tokens, chaves privadas ou dados pessoais reais.

## Risco de consistência

`IssueCredentialService.issue()` executa uma transacção externa na blockchain dentro de `transaction.atomic`. Se a escrita PostgreSQL falhar após a ancoragem, a transacção blockchain não é revertida. Registar o caso como risco de recuperação/reconciliação; não declarar atomicidade entre os dois sistemas.
