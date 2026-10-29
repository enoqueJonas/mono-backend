# Contrato de emissão e verificação de Credenciais Verificáveis

Estado: alteração proposta para revisão — Issue #8. **Não atestar testes de integração sem execução.**

## Âmbito da demonstração
O sistema implementa uma credencial de histórico contributivo emitida por um grupo registado.
A emissão no endpoint de grupo deve (1) validar elegibilidade, (2) construir o documento,
(3) incluir validade temporal, (4) assinar o documento com a chave Ed25519 do DID do grupo,
(5) calcular SHA-256 do documento **assinado**, (6) ancorar o hash, (7) persistir a mesma
versão assinada e (8) devolver a credencial.

A verificação pública deve devolver `data.valid=true` apenas se TODAS as condições
forem satisfeitas: formato reconhecido, período válido, emissor DID conhecido/activo,
assinatura Ed25519 válida, hash exacto presente na blockchain e registo não revogado.

Não confundir existência de hash com validade de credencial. O contrato
`credentialExists` retorna verdadeiro mesmo após revogação; a verificação
deve consultar `getCredential` e o campo `revoked`.

## Limitações e notas de segurança
- O protótipo utiliza assinatura `MonoEd25519Signature2026` e canonicalização
  JSON **próprias da aplicação**, não uma suite W3C Data Integrity interoperável.
- A identidade do emissor é resolvida na base de dados local da aplicação. Não
  se demonstra resolução pública e interoperável de DIDs ou confiança entre plataformas.
- Credenciais emitidas anteriormente sem `proof` ou sem `validUntil` falham fechadas
  nesta verificação; reemissão controlada é necessária, não adulteração do histórico.
- O hash on-chain verifica integridade de uma declaração emitida, **não prova
  a veracidade do pagamento originalmente declarado** ou a redução de fraudes.
- A autenticação/autorização da revogação e a segurança dos webhooks de pagamentos
  são temas separados da Issue #9.
- Há uma janela de consistência entre transacção blockchain e commit SQL; a
  atomicidade de Django não reverte transacções já confirmadas na blockchain.
  É necessária estratégia de reconciliação para falhas após ancoragem (Issue #5).

## Evidências necessárias antes de encerrar #8
- Recolha e execução de testes unitários para emissão/validade/revogação.
- Teste de assinatura Ed25519 com chave real de teste e conteúdo adulterado.
- Teste de integração Django + Ganache/Brownie: emissão, hash ancorado,
  verificação positiva, revogação e verificação negativa.
- Resultados reproduzíveis com versões, comandos, timestamps e logs.
- Revisão das alegações sobre assinatura e validade nas secções 5.4/5.5.
