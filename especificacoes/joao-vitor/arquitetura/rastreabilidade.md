# Matriz de rastreabilidade

Gerada por `verificar.py` a partir das fichas em `../telas/`, de `requisitos.md` e de `contratos/openapi.yaml`. Não editar à mão.

## Tela → requisitos → contratos

| Tela | Requisitos | Operações (contrato) |
| :-- | :-- | :-- |
| D01 | REQ-14, REQ-16, REQ-17, REQ-18, REQ-19, REQ-28, REQ-30, REQ-44, REQ-45, REQ-46, REQ-47, REQ-65 | `obter_contrato`, `obter_emenda` |
| O01 | REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-10, REQ-11, REQ-12, REQ-21, REQ-50, REQ-52, REQ-53, REQ-54, REQ-56, REQ-59 | `cli:importar`, `cli:sincronizar` |
| O02 | REQ-07, REQ-08, REQ-09, REQ-12, REQ-35, REQ-36, REQ-37, REQ-38, REQ-50, REQ-56, REQ-57, REQ-63, REQ-64 | `cli:publicar` |
| P01 | REQ-14, REQ-15, REQ-16, REQ-19, REQ-20, REQ-28, REQ-44, REQ-45, REQ-46, REQ-47, REQ-48, REQ-60 | `listar_mudancas`, `listar_opcoes_filtro`, `obter_emenda`, `obter_status` |
| P02 | REQ-14, REQ-15, REQ-19, REQ-20, REQ-21, REQ-28, REQ-34, REQ-44, REQ-45, REQ-46, REQ-47, REQ-48, REQ-60, REQ-65 | `listar_emendas`, `listar_opcoes_filtro` |
| P03 | REQ-13, REQ-14, REQ-15, REQ-16, REQ-17, REQ-18, REQ-19, REQ-21, REQ-28, REQ-44, REQ-45, REQ-46, REQ-47, REQ-48, REQ-60 | `listar_favorecidos`, `obter_autor`, `obter_emenda`, `obter_linha_do_tempo`, `obter_status` |
| P04 | REQ-14, REQ-15, REQ-16, REQ-17, REQ-18, REQ-19, REQ-23, REQ-28, REQ-44, REQ-45, REQ-46, REQ-47, REQ-60 | `obter_emenda`, `obter_linha_do_tempo` |
| P05 | REQ-14, REQ-15, REQ-17, REQ-18, REQ-19, REQ-25, REQ-26, REQ-28, REQ-44, REQ-45, REQ-46, REQ-47, REQ-60, REQ-65 | `listar_favorecidos`, `obter_emenda` |
| P06 | REQ-14, REQ-15, REQ-19, REQ-20, REQ-21, REQ-22, REQ-28, REQ-44, REQ-45, REQ-46, REQ-47, REQ-49, REQ-60 | `listar_opcoes_filtro`, `obter_agregacoes`, `obter_autor` |
| P07 | REQ-14, REQ-15, REQ-19, REQ-22, REQ-28, REQ-29, REQ-44, REQ-45, REQ-46, REQ-47, REQ-55, REQ-60 | `obter_autor` |
| P08 | REQ-08, REQ-14, REQ-19, REQ-20, REQ-24, REQ-27, REQ-28, REQ-44, REQ-45, REQ-46, REQ-47, REQ-55, REQ-60, REQ-61 | `listar_lotes`, `listar_mudancas`, `listar_opcoes_filtro` |
| P09 | REQ-06, REQ-10, REQ-12, REQ-13, REQ-14, REQ-19, REQ-27, REQ-28, REQ-44, REQ-45, REQ-46, REQ-47, REQ-48, REQ-50, REQ-55, REQ-60 | `listar_lotes`, `obter_lote`, `obter_status` |
| S01 | REQ-19, REQ-20, REQ-31, REQ-32, REQ-33, REQ-34, REQ-37, REQ-41, REQ-42, REQ-44, REQ-46, REQ-47, REQ-60, REQ-62, REQ-63, REQ-64 | `criar_assinatura`, `listar_assinaturas`, `listar_opcoes_filtro`, `obter_status` |
| S02 | REQ-31, REQ-32, REQ-41, REQ-44, REQ-47, REQ-58 | `criar_assinatura` |
| S03 | REQ-28, REQ-32, REQ-44, REQ-45, REQ-46, REQ-47 | `listar_assinaturas` |
| S04 | REQ-32, REQ-38, REQ-40, REQ-42, REQ-44, REQ-45, REQ-46, REQ-47 | `atualizar_assinatura`, `excluir_assinatura`, `listar_assinaturas` |
| S05 | REQ-14, REQ-32, REQ-35, REQ-36, REQ-37, REQ-39, REQ-44, REQ-45, REQ-46, REQ-47, REQ-63, REQ-64 | `atualizar_alerta`, `listar_alertas`, `listar_assinaturas` |

## Requisito → telas

| Requisito | Telas | Também em |
| :-- | :-- | :-- |
| REQ-01 | O01 | — |
| REQ-02 | O01 | — |
| REQ-03 | O01 | — |
| REQ-04 | O01 | — |
| REQ-05 | O01 | ADR-0001 |
| REQ-06 | O01, P09 | ADR-0001 |
| REQ-07 | O02 | ADR-0001, ADR-0002, qualidade |
| REQ-08 | O02, P08 | ADR-0004 |
| REQ-09 | O02 | ADR-0001, ADR-0002, qualidade |
| REQ-10 | O01, P09 | ADR-0001, qualidade |
| REQ-11 | O01 | ADR-0002, qualidade |
| REQ-12 | O01, O02, P09 | — |
| REQ-13 | P03, P09 | qualidade |
| REQ-14 | D01, P01, P02, P03, P04, P05, P06, P07, P08, P09, S05 | ADR-0001, ADR-0003, qualidade |
| REQ-15 | P01, P02, P03, P04, P05, P06, P07 | ADR-0007 |
| REQ-16 | D01, P01, P03, P04 | qualidade |
| REQ-17 | D01, P03, P04, P05 | qualidade |
| REQ-18 | D01, P03, P04, P05 | qualidade |
| REQ-19 | D01, P01, P02, P03, P04, P05, P06, P07, P08, P09, S01 | qualidade |
| REQ-20 | P01, P02, P06, P08, S01 | — |
| REQ-21 | O01, P02, P03, P06 | — |
| REQ-22 | P06, P07 | — |
| REQ-23 | P04 | ADR-0006 |
| REQ-24 | P08 | ADR-0004 |
| REQ-25 | P05 | ADR-0007 |
| REQ-26 | P05 | ADR-0007 |
| REQ-27 | P08, P09 | — |
| REQ-28 | D01, P01, P02, P03, P04, P05, P06, P07, P08, P09, S03 | qualidade |
| REQ-29 | P07 | — |
| REQ-30 | D01 | ADR-0003, qualidade |
| REQ-31 | S01, S02 | ADR-0005 |
| REQ-32 | S01, S02, S03, S04, S05 | ADR-0005 |
| REQ-33 | S01 | — |
| REQ-34 | P02, S01 | — |
| REQ-35 | O02, S05 | ADR-0004, ADR-0006, qualidade |
| REQ-36 | O02, S05 | ADR-0002, ADR-0004, qualidade |
| REQ-37 | O02, S01, S05 | ADR-0004 |
| REQ-38 | O02, S04 | — |
| REQ-39 | S05 | — |
| REQ-40 | S04 | — |
| REQ-41 | S01, S02 | ADR-0005 |
| REQ-42 | S01, S04 | ADR-0005 |
| REQ-43 | — | ADR-0003, qualidade |
| REQ-44 | D01, P01, P02, P03, P04, P05, P06, P07, P08, P09, S01, S02, S03, S04, S05 | — |
| REQ-45 | D01, P01, P02, P03, P04, P05, P06, P07, P08, P09, S03, S04, S05 | — |
| REQ-46 | D01, P01, P02, P03, P04, P05, P06, P07, P08, P09, S01, S03, S04, S05 | — |
| REQ-47 | D01, P01, P02, P03, P04, P05, P06, P07, P08, P09, S01, S02, S03, S04, S05 | — |
| REQ-48 | P01, P02, P03, P09 | — |
| REQ-49 | P06 | ADR-0002, qualidade |
| REQ-50 | O01, O02, P09 | ADR-0004, qualidade |
| REQ-51 | — | ADR-0003, qualidade |
| REQ-52 | O01 | — |
| REQ-53 | O01 | — |
| REQ-54 | O01 | — |
| REQ-55 | P07, P08, P09 | — |
| REQ-56 | O01, O02 | — |
| REQ-57 | O02 | — |
| REQ-58 | S02 | — |
| REQ-59 | O01 | — |
| REQ-60 | P01, P02, P03, P04, P05, P06, P07, P08, P09, S01 | — |
| REQ-61 | P08 | — |
| REQ-62 | S01 | — |
| REQ-63 | O02, S01, S05 | — |
| REQ-64 | O02, S01, S05 | — |
| REQ-65 | D01, P02, P05 | — |

## Operação → telas

| Operação | Método e caminho | Telas |
| :-- | :-- | :-- |
| `obter_status` | `GET /api/status` | P01, P03, P09, S01 |
| `listar_opcoes_filtro` | `GET /api/filtros/opcoes` | P01, P02, P06, P08, S01 |
| `listar_emendas` | `GET /api/emendas` | P02 |
| `obter_emenda` | `GET /api/emendas/{codigo}` | D01, P01, P03, P04, P05 |
| `obter_linha_do_tempo` | `GET /api/emendas/{codigo}/linha-do-tempo` | P03, P04 |
| `listar_favorecidos` | `GET /api/emendas/{codigo}/favorecidos` | P03, P05 |
| `obter_agregacoes` | `GET /api/agregacoes` | P06 |
| `obter_autor` | `GET /api/autores/{codigo}` | P03, P06, P07 |
| `listar_mudancas` | `GET /api/mudancas` | P01, P08 |
| `listar_lotes` | `GET /api/lotes` | P08, P09 |
| `obter_lote` | `GET /api/lotes/{lote_id}` | P09 |
| `criar_assinatura` | `POST /api/assinaturas` | S01, S02 |
| `listar_assinaturas` | `GET /api/assinaturas` | S01, S03, S04, S05 |
| `atualizar_assinatura` | `PATCH /api/assinaturas/{assinatura_id}` | S04 |
| `excluir_assinatura` | `DELETE /api/assinaturas/{assinatura_id}` | S04 |
| `listar_alertas` | `GET /api/alertas` | S05 |
| `atualizar_alerta` | `PATCH /api/alertas/{alerta_id}` | S05 |
| `obter_contrato` | `GET /openapi.json` | D01 |
| `cli:importar` | CLI (`contratos/cli.md`) | O01 |
| `cli:lotes` | CLI (`contratos/cli.md`) | — (agendador) |
| `cli:publicar` | CLI (`contratos/cli.md`) | O02 |
| `cli:sincronizar` | CLI (`contratos/cli.md`) | O01 |
