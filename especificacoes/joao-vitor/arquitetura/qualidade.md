# Cenários de qualidade

Cinco cenários em seis partes (Bass, Clements e Kazman, 2021), um por item do envelope do PAUL (seção 10 do arc42). Cada medida vira critério de aceite e cita os requisitos e os testes que a comprovam.

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

Requisitos: REQ-07, REQ-10. Teste: `tests/test_store.py::test_lote_interrompido` (parametrizado com 20 sementes).

## QA-02 · API — erros previsíveis e conforme o contrato

| Parte | Conteúdo |
| :-- | :-- |
| Fonte | Cliente da API (painel ou jornalista) |
| Estímulo | Requisições a `GET /api/emendas/{codigo}` com código malformado, inexistente, e sem lote publicado; requisições acima de 60/min |
| Ambiente | API em execução, banco com e sem lote publicado |
| Artefato | `api.py` + `contratos/openapi.yaml` |
| Resposta | 422 `codigo_malformado`, 404 `emenda_nao_encontrada`, 503 `sem_lote_publicado`, 429 com `Retry-After`, todos em `application/problem+json`, e 200 com proveniência no caso válido |
| Medida | 100% das respostas de um conjunto de 200 requisições geradas a partir do contrato validam contra `openapi.yaml`, e 0 respostas 5xx. `/openapi.json` é semanticamente igual ao arquivo versionado |

Requisitos: REQ-14, REQ-16, REQ-17, REQ-18, REQ-19, REQ-28, REQ-30 (AC-1, AC-4). Testes: `tests/test_api.py`, `tests/test_contrato.py`.

## QA-03 · Concorrência — leitura durante publicação e fan-out sem duplicata

| Parte | Conteúdo |
| :-- | :-- |
| Fonte | Agendador (`rastro sincronizar`) e leitores simultâneos |
| Estímulo | Publicação de um lote B enquanto 8 leitores consultam a mesma emenda em laço. Em seguida, o despachante de alertas avalia B em 2 execuções simultâneas dentro do mesmo processo (duas threads chamando `despachar(lote_B)`, já que a trava do ADR-0002 impede duas CLIs), com 500 assinaturas ativas |
| Ambiente | Lote A publicado; B com 300 `MudancaLote` |
| Artefato | `store.py` (snapshot), `alertas.py` (despachante), restrição UNIQUE(`assinatura_id`, `mudanca_id`) |
| Resposta | Cada leitura devolve só valores de A ou só valores de B, nunca uma mistura. Cada par (assinatura, mudança) que satisfaz a condição gera um único alerta |
| Medida | Em 100 execuções: 0 respostas com `lote_id` misto, 0 alertas duplicados, e `alertas_criados` da segunda execução = 0. Leitores com p95 < 150 ms durante a publicação |

Requisitos: REQ-09, REQ-11, REQ-35, REQ-36 (AC-3). Testes: `tests/test_store.py::test_leitura_durante_publicacao`, `tests/test_alertas.py::test_sem_duplicata_concorrente`.

## QA-04 · Desempenho medido — consulta e ETL

| Parte | Conteúdo |
| :-- | :-- |
| Fonte | 20 usuários virtuais (script de carga reproduzível, semente fixa), a partir do loopback, isento do limite de taxa (REQ-28) |
| Estímulo | Mistura de 70% `GET /api/emendas/{codigo}`, 20% `GET /api/agregacoes?dimensao=uf\|autor\|funcao` e 10% `GET /api/emendas?…` por 60 s, após 10 s de aquecimento |
| Ambiente | Base 2025 completa publicada, máquina de referência, sem outra carga |
| Artefato | API + índices de `Emenda` e `RegistroExecucao` |
| Resposta | Todas as requisições respondem 200 |
| Medida | `obter_emenda` p95 < 100 ms; `obter_agregacoes` p95 < 300 ms; 0% de erro. ETL do ZIP completo ≤ 10 min, com tempo por etapa em `duracao_etl_ms`. **Alvos provisórios:** o primeiro relatório estabelece o baseline e os alvos são revistos a partir dele, com registro em ADR |

Requisitos: REQ-49, REQ-50. Ferramentas: `scripts/carga.py` (`httpx` + `time.perf_counter`, relatório p50/p95/p99 em `docs/medicoes/`), `scripts/medir_etl.py`.

## QA-05 · Testes — cada requisito com um teste automático no CI

| Parte | Conteúdo |
| :-- | :-- |
| Fonte | Desenvolvedor (ou agente) fazendo push |
| Estímulo | Push ou pull request na `main` |
| Ambiente | GitHub Actions, Ubuntu, Python 3.12, Node 20 |
| Artefato | Repositório inteiro: `tests/`, `web/`, `e2e/` |
| Resposta | O pipeline roda `pytest` (banco temporário por teste), `ruff`, `tsc --noEmit`, `next lint` e os testes e2e com axe. O merge fica bloqueado se algo falhar |
| Medida | 100% dos REQ com teste automático ligado em `requisitos.md`, exceto REQ-13 (fase 6, Siga) e REQ-49/REQ-50 (medidos por script, QA-04). Cobertura de linhas ≥ 80% em `src/rastro`. Pipeline < 10 min. 0 violações axe `serious`/`critical` |

Requisitos: REQ-43, REQ-51 e a coluna "Verificação" de `requisitos.md`.
