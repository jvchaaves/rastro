# Cenários de qualidade

Cinco cenários em seis partes (Bass, Clements e Kazman, 2021), um por item do envelope do PAUL (seção 10 do arc42). Cada medida vira critério de aceite e cita os requisitos e os testes que a comprovam. O brief do grupo exige os cinco itens em cada módulo; a linha "Módulos" de cada cenário diz quem responde por qual parte da medida (ver também o envelope por módulo em [README.md](README.md#envelope-de-cada-módulo-persistência-api-concorrência-desempenho-testes)).

Máquina de referência para medidas de tempo: o MacBook do autor (Apple Silicon, 16 GB), base de emendas 2025 completa, API com 1 worker Uvicorn. O modelo exato é registrado no relatório de carga.

## QA-01 · Persistência — lote interrompido não vaza para a consulta

| Parte | Conteúdo |
| :-- | :-- |
| Fonte | Operador ou agendador |
| Estímulo | O processo `rastro importar` é morto com `SIGKILL` no meio da gravação de um lote B, com o lote A publicado |
| Ambiente | Operação normal, API atendendo consultas |
| Artefato | `store.py` (lotes e publicação) + banco SQLite WAL |
| Resposta | O banco abre íntegro. As consultas continuam vendo só o lote A. Na execução seguinte da CLI, o lote B vira `falhou` com `motivo_falha = interrompido` |
| Medida | Em 20 execuções com morte em pontos aleatórios: 0 respostas da API com `lote_id` de B, `PRAGMA integrity_check = ok` em 20/20 e 20/20 lotes B marcados `falhou` |

Requisitos: REQ-07, REQ-10, REQ-76. Teste: `tests/test_store.py::test_lote_interrompido` (parametrizado com 20 sementes). Módulos: `ingestao` (gravação e marcação `falhou`), `consulta` (nenhuma leitura de lote não publicado).

## QA-02 · API — erros previsíveis e conforme o contrato

| Parte | Conteúdo |
| :-- | :-- |
| Fonte | Cliente da API (painel ou jornalista) |
| Estímulo | Requisições a `GET /api/emendas/{codigo}` com código malformado, inexistente, e sem lote publicado; `GET /api/emendas?municipio=…` sem `uf_gasto`; requisições acima de 60/min vindas de um mesmo navegador, pelo painel |
| Ambiente | API em execução, banco com e sem lote publicado |
| Artefato | `src/rastro/consulta/rotas.py`, `src/rastro/saida/rotas.py` + `contratos/openapi.yaml` |
| Resposta | 422 `codigo_malformado`, 422 `parametro_invalido`, 404 `emenda_nao_encontrada`, 503 `sem_lote_publicado`, 429 com `Retry-After` (o IP do navegador chega pelo `X-Forwarded-For` do painel), todos em `application/problem+json`, e 200 com proveniência, `estado_texto` e `traducao_versao` no caso válido |
| Medida | 100% das respostas de um conjunto de 200 requisições geradas a partir do contrato validam contra `openapi.yaml`, e 0 respostas 500 (erro interno); 503 só aparece no caso sem lote publicado, onde é a resposta esperada. `/openapi.json` é semanticamente igual ao arquivo versionado |

Requisitos: REQ-14, REQ-16, REQ-17, REQ-18, REQ-19, REQ-28, REQ-30, REQ-69, REQ-72, REQ-84 (AC-1, AC-4). Testes: `tests/test_api.py`, `tests/test_contrato.py`. Módulos: `consulta` (rotas de leitura e limite de taxa), `saida` (rotas com chave, mesmo formato de erro).

## QA-03 · Concorrência — leitura durante publicação e fan-out sem duplicata

| Parte | Conteúdo |
| :-- | :-- |
| Fonte | Agendador (`rastro sincronizar`) e leitores simultâneos |
| Estímulo | Publicação de um lote B enquanto 8 leitores consultam a mesma emenda em laço. Em seguida, o despachante de alertas avalia B em 2 execuções simultâneas dentro do mesmo processo (duas threads chamando `despachar(lote_B)`, já que a trava do ADR-0002 impede duas CLIs), com 500 assinaturas ativas |
| Ambiente | Base 2025 completa: lote A publicado; B com 300 `MudancaLote` em relação a A; máquina de referência |
| Artefato | `store.py` (snapshot), `alertas.py` (despachante), restrição UNIQUE(`assinatura_id`, `mudanca_id`) |
| Resposta | Cada leitura devolve só valores de A ou só valores de B, nunca uma mistura. Cada par (assinatura, mudança) que satisfaz a condição gera um único alerta |
| Medida | Em 100 execuções: 0 respostas com `lote_id` misto, 0 alertas duplicados, e `alertas_criados` da segunda execução = 0. Leitores com p95 < 150 ms durante a publicação. Cálculo das 300 mudanças (`duracao_etl_ms.publicacao`) ≤ 5 s; fan-out de 500 assinaturas (`alertas.gerados.duracao_ms`) ≤ 2 s |

Requisitos: REQ-08, REQ-09, REQ-11, REQ-35, REQ-36, REQ-56, REQ-92, REQ-93, REQ-94 (AC-3). Testes: `tests/test_store.py::test_leitura_durante_publicacao`, `tests/test_mudancas.py::test_mudancas_calculadas_na_publicacao`, `tests/test_alertas.py::test_sem_duplicata_concorrente`. Módulos: `ingestao` (troca atômica e escritor único), `nucleo` (mudanças na transação), `consulta` (leitura em snapshot), `saida` (despachante idempotente).

## QA-04 · Desempenho medido — consulta e ETL

| Parte | Conteúdo |
| :-- | :-- |
| Fonte | 20 usuários virtuais (script de carga reproduzível, semente fixa), a partir do loopback sem `X-Forwarded-For`, com a API em modo de medição (`RASTRO_MEDICAO=1`), único caso isento do limite de taxa (REQ-85) |
| Estímulo | (a) Mistura de 70% `GET /api/emendas/{codigo}`, 20% `GET /api/agregacoes?dimensao=uf\|autor\|funcao` e 10% `GET /api/emendas?…` por 60 s, após 10 s de aquecimento. (b) Uma execução de `rastro importar` com o ZIP completo de 2025 |
| Ambiente | Base 2025 completa publicada, máquina de referência, sem outra carga |
| Artefato | API + índices de `Emenda` e `RegistroExecucao` |
| Resposta | (a) Todas as requisições respondem 200. (b) O lote termina `validado` |
| Medida | `obter_emenda` p95 < 100 ms; `obter_agregacoes` p95 < 300 ms; 0% de erro. ETL do ZIP completo ≤ 10 min, com tempo por etapa em `duracao_etl_ms`. Os alvos são os do REQ-49 e do REQ-50; se o primeiro relatório (baseline) mostrar que estão errados, eles só mudam por uma ADR nova que altere esses requisitos |

Requisitos: REQ-49, REQ-50, REQ-82, REQ-85. Ferramentas: `scripts/carga.py` (`httpx` + `time.perf_counter`, relatório p50/p95/p99 em `docs/medicoes/`), `scripts/medir_etl.py`. Módulos: `consulta` (p95 das consultas), `ingestao` (tempo do ETL).

## QA-05 · Testes — cada requisito com um teste automático no CI

| Parte | Conteúdo |
| :-- | :-- |
| Fonte | Desenvolvedor (ou agente) fazendo push |
| Estímulo | Push ou pull request na `main` |
| Ambiente | GitHub Actions, Ubuntu, Python 3.12, Node 20 |
| Artefato | Repositório inteiro: `tests/`, `web/`, `e2e/` |
| Resposta | O pipeline roda `pytest` (banco temporário por teste), `ruff`, `tsc --noEmit`, `next lint` e os testes e2e com axe. O merge fica bloqueado se algo falhar |
| Medida | 100% dos REQ com teste automático ligado em `requisitos.md`, com três grupos de exceção declarados: REQ-13 (fase 6, Siga); REQ-49 e REQ-50 (medidos por script, QA-04); REQ-51 e REQ-83 (são o próprio pipeline e a proteção da `main`, verificados por inspeção do `ci.yml` e da regra do GitHub, e comprovados quando um PR com teste quebrado fica bloqueado). Cobertura de linhas ≥ 80% em cada `src/rastro/<modulo>`. Pipeline < 10 min. 0 violações axe `serious`/`critical` |

Requisitos: REQ-43, REQ-51, REQ-83 e a coluna "Verificação" de `requisitos.md`. Módulos: todos; cada módulo mede a própria cobertura e roda os próprios testes sozinho, com o duplo do lote publicado (`tests/fixtures/lote_minimo.sql`, ADR-0009).
