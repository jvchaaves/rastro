# ADR-0009 · Dividir o sistema nos quatro módulos do grupo, com o lote publicado como contrato central

- **Status:** aceita (segue a tabela "Módulos" do brief do grupo)
- **Data:** 26/10/2026
- **Requisitos ligados:** REQ-07, REQ-08, REQ-35, REQ-76

## Contexto

- O brief do grupo fixa quatro módulos independentes (`ingestao`, `nucleo`, `consulta`, `saida`), cada um com persistência, API, componente concorrente, desempenho medido e testes, "os cinco, sozinho".
- O brief também fixa o contrato principal: "o lote publicado. A ingestão publica; núcleo, consulta e saída leem — e nenhum deles sabe como o CSV da origem é lido."
- A arquitetura desta especificação foi escrita por contêineres (CLI, API, painel, banco; ver `../c4-conteineres.md`). Era preciso dizer, sem duplicar a arquitetura, a qual módulo pertence cada peça.

## Opções consideradas

1. **Um módulo por contêiner** (CLI = ingestão, API = consulta…): quebra o brief, porque assinaturas e mudanças ficariam sem dono e o módulo `saida` não teria API.
2. **Microsserviços**, um processo por módulo: contraria a restrição de execução local com dois processos (FI-01 §10.3) e multiplica a escrita no SQLite.
3. **Módulos de código** (`src/rastro/<modulo>/`) que rodam dentro dos contêineres existentes. A fronteira entre eles é o lote publicado (tabelas do lote + `PublicacaoAtiva`), uma porta de função e o evento `lote.publicado`.

## Decisão

Opção 3, com estas fronteiras:

| De → para | Contrato | Onde está |
| :-- | :-- | :-- |
| `ingestao` → todos | Lote publicado: `PublicacaoAtiva` + linhas do lote em `Emenda`, `RegistroExecucao`, `RegistroFavorecido` | `../contratos/modelo-de-dados.md`, REQ-07, REQ-76 |
| `ingestao` → `nucleo` | Porta `calcular_mudancas(lote_anterior_id, lote_novo_id) -> int`, chamada dentro da transação de publicação | REQ-08, REQ-75 |
| `ingestao` → `saida` | Evento `lote.publicado` | `../contratos/eventos.asyncapi.yaml`, REQ-35 |
| `nucleo` → `consulta`, `saida` | View `v_emenda_estado`, `MudancaLote` e `TabelaTraducao` | ADR-0006, ADR-0008 |
| `consulta`, `saida`, `nucleo`, `ingestao` → painel e jornalistas | Operações HTTP, cada uma marcada com `x-modulo` | `../contratos/openapi.yaml` |

- Os módulos `nucleo`, `consulta` e `saida` nunca importam o leitor de CSV (`ingestao/cgu.py`). Um teste de arquitetura (`tests/test_fronteiras.py`, com `import-linter`) falha se isso acontecer.
- Cada módulo é dono de suas tabelas: só ele escreve nelas (tabela "Mapa para os quatro módulos" em `../README.md`).
- Para testar um módulo sozinho, o duplo do contrato é um banco de teste com um lote publicado sintético (`tests/fixtures/lote_minimo.sql`).

## Consequências

- **(+)** Cada integrante do grupo pode rodar `/paul:init` no seu módulo com requisitos, telas e contratos já separados (coluna "Módulo" de `../requisitos.md`).
- **(+)** O lote imutável (ADR-0001) vira, de graça, o contrato estável entre módulos.
- **(−)** A publicação depende de duas portas síncronas (`calcular_mudancas` e o despachante). Uma falha no `nucleo` desfaz a publicação inteira, o que é o comportamento desejado (REQ-07).
- **(−)** A API é um único processo FastAPI com rotas de três módulos. A independência é de código e de dados, não de processo.
