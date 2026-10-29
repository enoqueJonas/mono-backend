# Simulação de carteira móvel — limites de segurança

## Regras de activação
- Endpoint de confirmação do simulador **desactivado por defeito**.
- Para testes de integração controlados definir `MOBILE_WALLET_WEBHOOK_ENABLED=true`
  e `MOBILE_WALLET_WEBHOOK_SECRET` com uma chave própria do ambiente.
- Não usar estas credenciais para um operador real M-Pesa/e-Mola.

## Autenticação da simulação
- `X-Mono-Timestamp`: segundos Unix; admissível desvio máximo de 300 segundos.
- `X-Mono-Signature`: `HMAC-SHA256(secret, timestamp + "." + raw_request_body)`
  em hexadecimal.
- Comparação em tempo constante, rejeição de cabeçalhos inválidos, assinatura
  incorrecta ou timestamp antigo.
- A referência de contribuição é única e os registos duplicados são rejeitados.

## O que **não** foi demonstrado
- Integração real com provedores móveis, liquidação financeira ou reconciliação.
- Garantia absoluta contra replay em mensagens não confirmadas: para produção
  será necessária idempotência por evento e verificação de identificador do fornecedor.
- Autenticidade de um pagamento efectuado fora da aplicação: o segredo identifica
  somente o **simulador**, não uma transacção financeira verdadeira.

## Revogação de VC
A API requer JWT e apenas um gestor activo do mesmo grupo pode revogar a
credencial. A autorização é verificada na camada de aplicação antes de iniciar
qualquer transacção blockchain.

## Relação académica
Segurança na simulação não comprova impacto real na redução de fraude.
Estes testes fornecem evidência técnica e limites para as hipóteses da monografia.
