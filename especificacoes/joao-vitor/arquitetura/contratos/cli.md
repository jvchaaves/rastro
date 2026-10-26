# Contrato da CLI de dados (`rastro`)

Superfície do **operador de dados** e do **agendador** (launchd/cron na máquina local). Este é o contrato das telas O01 e O02. A CLI escreve no mesmo banco SQLite que a API lê (ADR-0002) e é o único escritor de dados de fonte.

Regras comuns:

- Saída para humanos em `stdout`. Com `--json`, uma linha JSON por evento, útil para teste e para o agendador.
- Sem dependência de cor: todo estado tem um rótulo em texto (`OK`, `AVISO`, `ERRO`). `--sem-cor` desliga ANSI e `NO_COLOR` é respeitado.
- Um processo escritor por vez. Há uma trava de arquivo em `data/rastro.lock`, e uma segunda execução sai com código 5.

## Códigos de saída

| Código | Significado | Requisito |
| :-: | :-- | :-- |
| 0 | Sucesso, inclusive "lote já importado" (no-op) | REQ-05 |
| 1 | Uso inválido (argumento ausente ou arquivo inexistente) | — |
| 2 | Lote recusado na validação (rejeições acima de 5%) ou arquivo de lote já recusado | REQ-06, REQ-52 |
| 3 | Formato do pacote alterado (colunas ausentes) | REQ-04 |
| 4 | Fonte indisponível (download falhou) | REQ-12 |
| 5 | Outro processo escritor em execução | REQ-56 |
| 6 | `publicar` sobre lote que não está `validado` | REQ-57 |

## `rastro importar` · `cli:importar` (tela O01)

```
rastro importar --fonte cgu --arquivo data/raw/EmendasParlamentares_2026-10-20.zip [--json] [--sem-cor]
```

1. Calcula `hash_sha256`. Se já existir lote `validado`/`publicado`/`substituido` com esse hash → "lote já importado (Lote #n)" e código 0 (REQ-05). Se existir lote `recusado` → "lote já recusado" e código 2 (REQ-52). Lotes `falhou` não contam e o arquivo é importado de novo (REQ-53).
2. Cria `LoteImportacao` (`estado = importando`) e lê os CSVs em fluxo (Latin-1, `;`). Valida cada linha (REQ-02, REQ-03, REQ-21) e grava as aceitas em lotes de 5 000 linhas na tabela do lote.
3. Ao terminar: `estado = validado`, ou `recusado` (REQ-06), ou `falhou` (REQ-04). Grava `duracao_etl_ms` (REQ-50).
4. Ao iniciar, qualquer lote em `importando` sem trava ativa vira `falhou` com `motivo_falha = interrompido` (REQ-10).

Saída humana (resumo):

```
Rastro · importar · fonte CGU
Arquivo   EmendasParlamentares_2026-10-20.zip
Hash      9f2c…e41a (SHA-256)
Referência 20/10/2026

Lendo …  148 312 linhas lidas
OK     Aceitas      146 905
AVISO  Rejeitadas     1 407 (0,95%)
         ano_fora_do_recorte   1 210
         codigo_invalido         162
         valor_malformado         35
Tempo  leitura 41,2 s · validação 12,8 s · gravação 33,0 s

Lote #14 VALIDADO. Para publicar: rastro publicar --lote 14
```

Eventos `--json`: `{"evento":"lote_criado",...}`, `{"evento":"progresso","linhas_lidas":n}`, `{"evento":"lote_validado"|"lote_recusado"|"lote_falhou", "lote": <Lote>}`.

## `rastro publicar` · `cli:publicar` (tela O02)

```
rastro publicar --lote 14 [--simular] [--json] [--sem-cor]
```

1. Exige o lote em `validado`; caso contrário, sai com código 6 (REQ-57). Com `--reprocessar-alertas`, exige o lote `publicado`.
2. Abre uma transação `BEGIN IMMEDIATE` e, dentro dela: calcula `MudancaLote` contra o lote ativo (REQ-08), troca `PublicacaoAtiva.lote_id` (REQ-07), marca o lote anterior como `substituido` e faz o commit.
3. Emite `lote.publicado`. O despachante avalia as assinaturas e grava os alertas (REQ-35, REQ-36), depois emite `alertas.gerados` (ver `eventos.asyncapi.yaml`).
4. `--simular` calcula e mostra as mudanças sem fazer commit.
5. `rastro publicar --lote 14 --reprocessar-alertas` executa só o passo 3 para um lote já publicado. É idempotente: com os alertas já gravados, o resultado é `alertas_criados = 0` (ADR-0004).

Saída humana (resumo):

```
Rastro · publicar · Lote #14 (CGU, referência 20/10/2026)
Lote ativo atual  #13 (referência 13/10/2026)

Mudanças em relação ao #13
  nova_emenda        12
  valor_alterado    318
  estado_alterado    41

OK  Lote #14 publicado às 21:04:12 (troca atômica)
Alertas  57 assinaturas ativas avaliadas · 23 alertas criados · 0 já existentes · 0,4 s
```

## `rastro sincronizar` · `cli:sincronizar`

```
rastro sincronizar [--fontes cgu,siga] [--json]
```

Baixa as fontes habilitadas em paralelo (`ThreadPoolExecutor`, uma tarefa por fonte) e, para cada download concluído, executa `importar` e depois `publicar` **em série**, com um único escritor (REQ-11). Falha de download → lote `falhou` com `fonte_indisponivel` e código 4 ao final, se nenhuma fonte tiver sido publicada (REQ-12).

## `rastro lotes` · `cli:lotes`

```
rastro lotes [--fonte cgu] [--json]
```

Lista os lotes com os mesmos campos de `GET /api/lotes` (REQ-27).
