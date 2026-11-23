# Cenários de qualidade (arc42 §10)

Formato de 6 partes (Bass, Clements, Kazman). Um cenário por item do envelope não funcional da disciplina. Valores entre ⟨ ⟩ são **metas provisórias**: o FI-01 (§7.2) define que a meta numérica final entra depois do baseline. O primeiro passo de Q4 é medir o baseline e revisar ⟨ ⟩.

## Q1 · Persistência — falha da carga não corrompe nem esconde dados

| Parte | Conteúdo |
|---|---|
| Fonte | Rotina de carga |
| Estímulo | Três falhas injetadas: (a) processo morto com `SIGKILL` depois de 50% das emendas gravadas; (b) zip com o CSV de emendas truncado em 10% das linhas; (c) cabeçalho com uma coluna renomeada |
| Ambiente | Operação normal, com versão ativa anterior existente |
| Artefato | `verificar_e_carregar`, `ativar_versao`, tabelas `versao_carga`, `emenda` e `pagamento_favorecido` |
| Resposta | (a) versão órfã marcada `falhou`/`erro_interno` na execução seguinte; (b) `falhou`/`queda_de_volume` (REQ-50); (c) `falhou`/`formato_inesperado` (REQ-48). Em todos os casos, a versão ativa continua a anterior e nenhuma tela mostra dado da versão incompleta |
| Medida | Em 20 execuções com falha injetada: 0 leituras de emendas de versão não ativa; contagem de `emenda_ativa` idêntica antes e depois; exatamente 1 linha com `ativa = true` |

Requisitos: REQ-33, REQ-34, REQ-35, REQ-48, REQ-50. Teste: `tests/test_carga_falha.py`, com o zip da T1 reduzido (`tests/dados/amostra_t1.zip`).

## Q2 · API com contrato — respostas sempre válidas contra o OpenAPI publicado

| Parte | Conteúdo |
|---|---|
| Fonte | Cliente da API (jornalista, telas HTML via serviço, teste de contrato) |
| Estímulo | Requisição a qualquer operação de `openapi.yaml`, com parâmetros válidos e inválidos (gerados por Schemathesis a partir do schema) |
| Ambiente | Base com uma carga de amostra concluída |
| Artefato | `/api/v1/*`, `/openapi.json` |
| Resposta | Status e corpo conformes ao schema; 404/422/503 com corpo `Erro`; o `/openapi.json` gerado é equivalente a `contratos/openapi.yaml` |
| Medida | 0 violações de schema em ⟨500⟩ casos gerados por operação; diff semântico `openapi.json` × `openapi.yaml` vazio no CI |

Requisitos: REQ-07, REQ-22, REQ-39, REQ-43.

## Q3 · Concorrência — leitores durante a troca de versão e cargas simultâneas

| Parte | Conteúdo |
|---|---|
| Fonte | ⟨50⟩ leitores simultâneos (Locust) + a rotina de carga + um disparo manual extra da carga |
| Estímulo | Leitores repetem `GET /api/v1/municipios/2507507` enquanto a carga grava e executa `ativar_versao`; ao mesmo tempo, um segundo `verificar_e_carregar` é disparado (com `--forcar`) |
| Ambiente | Carga em andamento sobre base com versão ativa |
| Artefato | View `emenda_ativa`, `ativar_versao`, lock consultivo |
| Resposta | Cada resposta reflete inteiramente a versão antiga ou inteiramente a nova (os `totais` são iguais aos de uma das duas versões); a segunda carga termina com código 3, sem criar versão |
| Medida | 0 respostas com totais que não batem com nenhuma das duas versões em ⟨10⟩ trocas; 0 respostas 5xx; sempre ≤ 1 versão `em_andamento` e exatamente 1 `ativa` |

Requisitos: REQ-33, REQ-34, REQ-36. Teste: `tests/test_troca_versao_concorrente.py` (pytest com threads) + cenário Locust `carga_durante_leitura`.

## Q4 · Desempenho medido — lista de emendas do município no celular

| Parte | Conteúdo |
|---|---|
| Fonte | Usuários simulados (Locust), perfil de celular |
| Estímulo | ⟨50⟩ usuários simultâneos navegando A01 → A03 → A04 → A05 → A14 (espera de 2 a 5 s entre passos) por 10 min; João Pessoa (2507507) em 30% das sessões, por ser o município com mais pagamentos |
| Ambiente | Docker Compose em máquina de referência (registrar CPU/RAM); base com a carga real da PB (≈ 2 780 emendas e 31 500 pagamentos, T1); cache do navegador frio |
| Artefato | `GET /municipios/{codigo_ibge}/emendas` (página e fragmento) e `listar_emendas_municipio` |
| Resposta | Página servida completa, sem erro |
| Medida | **Baseline primeiro.** Meta provisória: p95 do servidor < ⟨500 ms⟩; 0% de erros; HTML + CSS + JS da primeira abertura de A04 < ⟨100 KB⟩ comprimidos (medido com Lighthouse, perfil "Slow 4G") |

Requisitos: REQ-11, REQ-41. Script: `perf/locustfile.py`; relatório salvo em `perf/resultados/AAAA-MM-DD.md`.

## Q5 · Testes — a regra de fase e a tradução nunca regridem

| Parte | Conteúdo |
|---|---|
| Fonte | Desenvolvedor ou agente alterando código ou dados de tradução |
| Estímulo | Commit que toca `traducao.py`, a view `emenda_ativa`, `favorecidos.py`, `termo_traduzido` ou os templates |
| Ambiente | CI (pytest), banco PostgreSQL efêmero via Docker |
| Artefato | Regra REQ-13, tabela `termo_traduzido`, templates Jinja |
| Resposta | A suíte executa: (a) tabela de casos da regra de fase com todas as fronteiras, incluindo casos reais da T1 (pago só em restos a pagar; cancelada; empenhado 0 com cancelamento; transferência especial); (b) toda `fase_simples` tem `termo_traduzido` com fonte; (c) nenhum texto contém expressão proibida (REQ-15); (d) nenhum template contém "candidato" (REQ-27); (e) primeiro pagamento em anos e nunca em meses (REQ-74), rótulo de reserva antiga (REQ-76), objeto do convênio idêntico ao da fonte (REQ-72) e nenhuma palavra de REQ-77; (f) resolução de município com alias (`SERIDÓ` → 2515401) e categoria de favorecido; (g) pessoa física nunca gravada com nome (REQ-53); (h) AC-1 e AC-2 do FI |
| Medida | 100% dos ramos de `fase_simples` e de `categoria_favorecido` cobertos (`pytest --cov --cov-branch`); com o zip completo da T1, distribuição de fases igual à registrada em `modelo-dados.md` (2 006 / 438 / 234 / 100 / 2) e `valor_pago_total` = soma dos favorecidos em ≥ 93% das emendas com código; 100% dos termos com fonte; 0 ocorrências proibidas; suíte < ⟨2 min⟩ |

Requisitos: REQ-13, REQ-14, REQ-15, REQ-16, REQ-27, REQ-52, REQ-53, REQ-62, REQ-72, REQ-74, REQ-76, REQ-77.
