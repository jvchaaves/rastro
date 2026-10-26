# Contrato da CLI de dados (`rastro`)

Superfície do **operador de dados** e do **agendador** (launchd/cron na máquina local). Este é o contrato das telas O01 e O02 e da publicação da tabela de tradução (ADR-0008). Módulos donos: `importar`, `publicar`, `sincronizar` e `lotes` são do módulo `ingestao`; `traducao publicar` é do `nucleo`; o despachante chamado por `publicar` é do `saida`. A CLI escreve no mesmo banco SQLite que a API lê (ADR-0002) e é o único escritor de dados de fonte.

Regras comuns:

- Saída para humanos em `stdout`. Com `--json`, uma linha JSON por evento, útil para teste e para o agendador.
- Sem dependência de cor: todo estado tem um rótulo em texto (`OK`, `AVISO`, `ERRO`). `--sem-cor` desliga ANSI e `NO_COLOR` é respeitado.
- Um processo escritor por vez: a CLI toma `fcntl.flock(LOCK_EX | LOCK_NB)` sobre `data/rastro.lock`. Se a trava estiver tomada, sai na hora com código 5, sem esperar (REQ-56). O sistema operacional solta a trava quando o processo morre, inclusive por `SIGKILL`, então um arquivo de trava deixado para trás não bloqueia a execução seguinte.
- Progresso em terminal: linhas lidas a cada 10 000, etapa atual e tempo decorrido; sem terminal ou com `--json`, um evento por marco (REQ-90); sem terminal ou com `--json`, um evento JSON por marco (REQ-100).

## Códigos de saída

| Código | Significado | Requisito |
| :-: | :-- | :-- |
| 0 | Sucesso, inclusive "lote já importado" (no-op) | REQ-05 |
| 1 | Uso inválido: argumento ausente, arquivo inexistente ou sem permissão de leitura do arquivo ou de escrita em `data/` | — |
| 2 | Lote recusado na validação (rejeições acima de 5% ou nenhuma linha no recorte) ou arquivo de lote já recusado | REQ-06, REQ-73, REQ-52 |
| 3 | Formato do pacote alterado (colunas ausentes) | REQ-04 |
| 4 | Fonte indisponível (download falhou) | REQ-12 |
| 5 | Outro processo escritor em execução | REQ-56 |
| 6 | `publicar` sobre lote que não está `validado` (ou, com `--reprocessar-alertas`, que não está `publicado`), ou lote com `data_referencia` igual ou anterior à do lote ativo | REQ-57, REQ-95 |
| 7 | `traducao publicar` com tabela incompleta (falta ou sobra estado) | REQ-86 |

## `rastro importar` · `cli:importar` (tela O01)

```
rastro importar --fonte cgu --arquivo data/raw/EmendasParlamentares_2026-10-20.zip [--json] [--sem-cor]
```

1. Calcula `hash_sha256`. Se já existir lote `validado`/`publicado`/`substituido` com esse hash → "lote já importado (Lote #n)" e código 0 (REQ-05). Se existir lote `recusado` → "lote já recusado" e código 2 (REQ-52). Lotes `falhou` não contam e o arquivo é importado de novo (REQ-53).
2. Cria `LoteImportacao` (`estado = importando`) e lê os CSVs em fluxo (Latin-1, `;`). Valida cada linha (REQ-02, REQ-03, REQ-59, REQ-97, REQ-98), deriva UF e município do gasto (REQ-21, REQ-66, REQ-78, REQ-88), agrega os recebimentos de pessoas físicas por emenda e mês sem guardar nome nem CPF (REQ-25) e grava as aceitas em lotes de 5 000 linhas na tabela do lote.
3. Ao terminar: `estado = validado`, ou `recusado` (REQ-06; ou REQ-73 quando nenhuma linha está no recorte), ou `falhou` (REQ-04). Grava `duracao_etl_ms` (REQ-82).
4. Ao iniciar, qualquer lote em `importando` sem trava ativa vira `falhou` com `motivo_falha = interrompido` (REQ-10).

Saída humana (resumo):

```
Rastro · importar · fonte CGU
Arquivo   EmendasParlamentares_2026-10-20.zip
Hash      9f2c…e41a (SHA-256)
Referência 20/10/2026

Lendo …  148 312 linhas lidas
OK     Aceitas      146 905
AVISO  Rejeitadas     1 407
         ano_fora_do_recorte   1 210  (fora da taxa)
         codigo_invalido         162
         valor_malformado         35
       Taxa de rejeição 0,13% (197 de 147 102 linhas do recorte; limite 5%)
Tempo  leitura 41,2 s · validação 12,8 s · gravação 33,0 s

Lote #14 VALIDADO. Para publicar: rastro publicar --lote 14
```

Eventos `--json`: `{"evento":"lote_criado",...}`, `{"evento":"progresso","linhas_lidas":n}`, `{"evento":"lote_validado"|"lote_recusado"|"lote_falhou", "lote": <Lote>}`.

## `rastro publicar` · `cli:publicar` (tela O02)

```
rastro publicar --lote 14 [--simular | --reprocessar-alertas] [--json] [--sem-cor]
```

1. Exige o lote em `validado` e com `data_referencia` posterior à do lote ativo; caso contrário, sai com código 6 (REQ-57, REQ-95). Com `--reprocessar-alertas`, exige o lote `publicado`.
2. Abre uma transação `BEGIN IMMEDIATE` e, dentro dela: calcula `MudancaLote` contra o lote ativo (REQ-08, porta `calcular_mudancas` do `nucleo`), marca o lote como `publicado` com `publicado_em`, troca `PublicacaoAtiva.lote_id` e marca o lote anterior como `substituido` (REQ-07); depois faz o commit.
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

## `rastro traducao publicar` · `cli:traducao`

```
rastro traducao publicar --arquivo traducoes/v2.yaml --nota "motivo da mudança" [--json]
```

Publica uma versão nova da tabela que traduz `estado_execucao` para linguagem simples (ADR-0008).

1. Lê o arquivo YAML com uma entrada por estado: `estado_execucao`, `texto_simples` (≤ 60 caracteres) e `explicacao` (≤ 280).
2. Exige exatamente os quatro estados (`sem_execucao`, `empenhada`, `liquidada`, `paga`); com falta ou sobra, sai com código 7 sem gravar nada (REQ-86).
3. Exige `--nota` (sem ela, código 1). Numa transação, insere as quatro linhas com `versao = máxima + 1`, `vigente_desde = agora` e a nota. As versões anteriores não mudam (REQ-70); o schema tem gatilhos que impedem `UPDATE` e `DELETE`.
4. A API passa a usar a versão nova na próxima requisição (REQ-69). A tela P11 mostra todas as versões (`listar_traducoes`).

Saída humana (resumo):

```
Rastro · traducao publicar · versão 2
OK  4 estados · vigente desde 26/10/2026 21:10
    liquidada  "A entrega foi conferida; falta pagar" → "Entrega conferida, pagamento pendente"
Versão 1 preservada (consulte em /dados/traducao?versao=1)
```
