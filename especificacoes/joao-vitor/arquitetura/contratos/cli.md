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
rastro importar --fonte cgu --arquivo data/raw/emendas-parlamentares_2026-10-26.zip [--json] [--sem-cor]
```

### Pacote da CGU (conferido no arquivo de 26/10/2026)

O download oficial (`https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares/UNICO`) é um ZIP de cerca de 32 MB, sem data no nome, com três CSVs em Latin-1, separador `;` e todos os campos entre aspas. Ele traz **todos os anos** (2014 em diante), então o recorte de 2025 é feito na importação.

| Arquivo no ZIP | Uso | Linhas (26/10/2026) |
| :-- | :-- | --: |
| `EmendasParlamentares.csv` | uma linha por emenda: cadastro, local de aplicação e as seis etapas | 94 747 (6 310 de 2025) |
| `EmendasParlamentares_PorFavorecido.csv` | uma linha por emenda, favorecido e mês | 828 478 (88 162 de emendas de 2025) |
| `EmendasParlamentares_Convenios.csv` | convênios ligados às emendas | não é importado no MVP |

Colunas exigidas (contrato de importação, REQ-04):

- `EmendasParlamentares.csv`: Código da Emenda; Ano da Emenda; Tipo de Emenda; Código do Autor da Emenda; Nome do Autor da Emenda; Número da emenda; Localidade de aplicação do recurso; Código Município IBGE; Município; Código UF IBGE; UF; Região; Código Função; Nome Função; Código Subfunção; Nome Subfunção; Código Programa; Nome Programa; Código Ação; Nome Ação; Código Plano Orçamentário; Nome Plano Orçamentário; Valor Empenhado; Valor Liquidado; Valor Pago; Valor Restos A Pagar Inscritos; Valor Restos A Pagar Cancelados; Valor Restos A Pagar Pagos.
- `EmendasParlamentares_PorFavorecido.csv`: Código da Emenda; Código do Autor da Emenda; Nome do Autor da Emenda; Número da emenda; Tipo de Emenda; Ano/Mês; Código do Favorecido; Favorecido; Natureza Jurídica; Tipo Favorecido; UF Favorecido; Município Favorecido; Valor Recebido.

Formatos observados: valores como `250000,00` (sem separador de milhar; negativos só em Valor Recebido, que são estornos); `Ano/Mês` como `AAAAMM`; CPF de pessoa física já mascarado pela fonte (`***.999.999-**`); `UF` por extenso ("PARAÍBA") ou "Sem informação"; `Município` com nome, "Múltiplo" ou "Sem informação"; `Código da Emenda` com 12 dígitos ou "Sem informação".

### Passos

1. Calcula `hash_sha256` sobre o conteúdo dos dois CSVs importados, descompactados e lidos em ordem de nome (não sobre o ZIP, que a CGU regera a cada atualização mesmo sem mudança de dados). Se já existir lote `validado`/`publicado`/`substituido` com esse hash → "lote já importado (Lote #n)" e código 0 (REQ-05). Se existir lote `recusado` → "lote já recusado" e código 2 (REQ-52). Lotes `falhou` não contam e o arquivo é importado de novo (REQ-53).
2. Define `data_referencia` como a data de modificação das entradas do ZIP (a mesma nos três arquivos; 26/10/2026 no arquivo conferido).
3. Cria `LoteImportacao` (`estado = importando`) e lê os CSVs em fluxo. Cada linha recebe um destino: aceita; `codigo_ausente` (REQ-102) ou `ano_fora_do_recorte` (REQ-59), fora da taxa; ou `codigo_invalido`, `valor_malformado`, `linha_malformada`, `emenda_sem_cadastro` (REQ-02, REQ-03, REQ-97, REQ-98), dentro da taxa. Deriva UF e município do local de aplicação (REQ-21, REQ-66, REQ-78, REQ-88), classifica o favorecido (REQ-104), deriva a sede e a marca de órgão municipal do favorecido (REQ-107, REQ-108, REQ-109), agrega os recebimentos de pessoas físicas por emenda e mês sem guardar nome nem CPF (REQ-25) e grava as linhas aceitas em blocos de 5 000.
4. Ao terminar: `estado = validado`, ou `recusado` (REQ-06; ou REQ-73 quando nenhuma linha está no recorte), ou `falhou` (REQ-04). Grava `duracao_etl_ms` (REQ-82).
5. Ao iniciar, qualquer lote em `importando` sem trava ativa vira `falhou` com `motivo_falha = interrompido` (REQ-10).

Saída humana (resumo):

```
Rastro · importar · fonte CGU
Arquivo    emendas-parlamentares_2026-10-26.zip
Hash       9f2c…e41a (SHA-256 dos CSVs)
Referência 26/10/2026

Lendo …  923 225 linhas lidas (94 747 emendas, 828 478 por favorecido)
OK     Aceitas       94 472 (6 310 emendas de 2025, 88 162 registros por favorecido)
AVISO  Descartadas  828 753 (fora do recorte, não entram na taxa)
         ano_fora_do_recorte  743 896
         codigo_ausente        84 857
OK     Rejeitadas         0
       Taxa de rejeição 0,00% (0 de 94 472 linhas do recorte; limite 5%)
Tempo  leitura 6,1 s · validação 2,3 s · gravação 4,0 s

Lote #14 VALIDADO. Para publicar: rastro publicar --lote 14
```

Os números acima são os do arquivo real de 26/10/2026.

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
2. Exige exatamente os cinco estados (`sem_execucao`, `empenhada`, `liquidada`, `paga_em_parte`, `paga`); com falta ou sobra, sai com código 7 sem gravar nada (REQ-86).
3. Exige `--nota` (sem ela, código 1). Numa transação, insere as cinco linhas com `versao = máxima + 1`, `vigente_desde = agora` e a nota. As versões anteriores não mudam (REQ-70); o schema tem gatilhos que impedem `UPDATE` e `DELETE`.
4. A API passa a usar a versão nova na próxima requisição (REQ-69). A tela P11 mostra todas as versões (`listar_traducoes`).

Saída humana (resumo):

```
Rastro · traducao publicar · versão 2
OK  5 estados · vigente desde 26/10/2026 21:10
    liquidada  "A entrega foi conferida; falta pagar" → "Entrega conferida, pagamento pendente"
Versão 1 preservada (consulte em /dados/traducao?versao=1)
```
