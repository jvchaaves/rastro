# ADR-0002 · Usar SQLite em modo WAL, com escritor único e leitura em snapshot

- **Status:** aceita
- **Data:** 26/10/2026
- **Requisitos ligados:** REQ-07, REQ-09, REQ-11, REQ-36, REQ-49

## Contexto

- O sistema roda localmente no macOS, em dois processos (API e painel) mais a CLI, sem servidor dedicado (FI-01 §10.3).
- O recorte de 2025 cabe com folga num arquivo local.
- O brief traz um gancho de concorrência: sincronização periódica de múltiplas fontes e fan-out de alertas.
- O FI-01 §6.2 lista "isolamento de leitura no SQLite enquanto a importação escreve" como algo ainda não dominado.

## Opções consideradas

1. **PostgreSQL** com MVCC completo.
2. **SQLite no modo padrão (rollback journal)**: leitores bloqueiam o escritor, e vice-versa.
3. **SQLite em WAL**: leitores enxergam um snapshot estável enquanto um único escritor grava.

## Decisão

Opção 3.

- `PRAGMA journal_mode=WAL`, `synchronous=NORMAL`, `busy_timeout=5000`, `foreign_keys=ON`.
- Nas consultas, a API usa conexões só de leitura (`mode=ro`) e executa cada requisição dentro de uma transação de leitura. Com isso, o lote ativo lido no início vale para a requisição inteira (REQ-09).
- Dados de fonte (lotes, emendas, execução, favorecidos, mudanças) e alertas novos: só a CLI escreve. Uma trava de arquivo (`data/rastro.lock`) impede duas CLIs ao mesmo tempo, e a publicação usa `BEGIN IMMEDIATE`.
- A API tem uma conexão de escrita separada, restrita a transações curtas sobre `Assinante`, `Assinatura` e `Alerta.lido_em`. Essas tabelas não são escritas pela CLI, exceto a inserção de alertas, que nunca altera linhas existentes.
- A concorrência fica onde não há disputa por escrita:
  - downloads paralelos das fontes;
  - avaliação paralela das assinaturas;
  - a gravação final é serializada e idempotente (UNIQUE).

## Consequências

- **(+)** Não há servidor de banco: o projeto roda com `venv` + `node` e cada teste cria um banco temporário.
- **(+)** Leitura durante importação sem bloqueio e sem mistura de lotes, testável com dois processos (QA-03).
- **(−)** Um só escritor: duas publicações simultâneas são serializadas, e a segunda espera ou sai com código 5. É aceitável na cadência de atualização da CGU.
- **(−)** O checkpoint do WAL precisa de atenção. Leitores longos impedem o checkpoint, por isso a API não mantém transações abertas entre requisições.
- **(−)** Migrar para PostgreSQL exigiria reescrever a camada `store`. O contrato HTTP não muda.
