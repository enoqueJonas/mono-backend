# Reprodução dos testes do protótipo — monografia

Estado: preparações de QA, **não um registo de execução bem-sucedida**.

## Setup (Python 3.12, ambiente isolado)

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest --collect-only -q
python -m pytest -q
```

O modo de teste define SQLite em memória, chave e conta de desenvolvimento
apenas como valores fictícios, e não abre por si só ligação ao Ganache. Os
ficheiros `tests.py` são recolhidos juntamente com `test_*.py`.

## Registo de evidências para a monografia
Para cada execução, guardar:
- versão Git (`git rev-parse HEAD`), `python --version`, pip freeze e hora UTC;
- comando, número de testes recolhidos, número aprovado/falhado/ignorado e logs;
- IDs e resultados relevantes para cada requisito/hipótese;
- separação de testes com `Mock` de testes com infraestrutura real.

## Testes de contratos inteligentes
Os testes em `smart_contracts/tests/` utilizam Brownie e **não** fazem parte
da suite Django. Com Brownie e Ganache configurados, executar:

```bash
cd smart_contracts
brownie test tests/test_credential_registry.py
brownie test tests/test_group_registry.py
brownie test tests/test_contribution_registry.py
```

Para evidência end-to-end: iniciar PostgreSQL, Ganache, implementar os
contratos, configurar RPC/endereço/chave no ambiente de desenvolvimento,
e efectuar emissão, verificação, revogação e nova verificação via API.

**A execução em CI com SQLite não demonstra por si só a integração com
PostgreSQL nem com Ganache**, nem prova redução de fraude ou alterações
comportamentais dos participantes.
