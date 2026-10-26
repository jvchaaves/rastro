# Matriz de rastreabilidade

Gerada por `verificar.py` a partir das fichas em `../telas/`, de `requisitos.md` e de `contratos/openapi.yaml`. Não editar à mão.

## Tela → requisitos → contratos

| Tela | Requisitos | Operações (contrato) |
| :-- | :-- | :-- |
| P01 | REQ-14, REQ-15, REQ-16, REQ-19, REQ-20, REQ-22, REQ-24, REQ-28, REQ-44, REQ-45, REQ-46, REQ-47, REQ-48, REQ-60, REQ-66, REQ-67, REQ-74 | `listar_emendas`, `listar_lotes`, `listar_mudancas`, `listar_opcoes_filtro`, `obter_agregacoes`, `obter_emenda`, `obter_municipio`, `obter_status` |
| P02 | REQ-14, REQ-15, REQ-19, REQ-20, REQ-21, REQ-28, REQ-34, REQ-44, REQ-45, REQ-46, REQ-47, REQ-48, REQ-60, REQ-65, REQ-66, REQ-68, REQ-69, REQ-72, REQ-74 | `listar_emendas`, `listar_lotes`, `listar_opcoes_filtro`, `obter_emenda`, `obter_municipio` |
| P03 | REQ-13, REQ-14, REQ-15, REQ-16, REQ-17, REQ-18, REQ-19, REQ-21, REQ-28, REQ-44, REQ-45, REQ-46, REQ-47, REQ-48, REQ-60, REQ-66, REQ-69, REQ-74, REQ-77 | `listar_favorecidos`, `listar_opcoes_filtro`, `listar_traducoes`, `obter_autor`, `obter_emenda`, `obter_linha_do_tempo`, `obter_lote`, `obter_municipio`, `obter_status` |
| P04 | REQ-14, REQ-15, REQ-16, REQ-17, REQ-18, REQ-19, REQ-23, REQ-28, REQ-44, REQ-45, REQ-46, REQ-47, REQ-60, REQ-69, REQ-74 | `listar_opcoes_filtro`, `obter_emenda`, `obter_linha_do_tempo`, `obter_lote` |
| P05 | REQ-14, REQ-15, REQ-17, REQ-18, REQ-19, REQ-25, REQ-26, REQ-28, REQ-44, REQ-45, REQ-46, REQ-47, REQ-60, REQ-65, REQ-74 | `listar_favorecidos`, `listar_lotes`, `obter_emenda` |
| P06 | REQ-14, REQ-15, REQ-19, REQ-20, REQ-21, REQ-22, REQ-28, REQ-44, REQ-45, REQ-46, REQ-47, REQ-49, REQ-60, REQ-71, REQ-72, REQ-74, REQ-79 | `listar_emendas`, `listar_lotes`, `listar_opcoes_filtro`, `obter_agregacoes`, `obter_autor` |
| P07 | REQ-14, REQ-15, REQ-19, REQ-22, REQ-28, REQ-29, REQ-44, REQ-45, REQ-46, REQ-47, REQ-55, REQ-60, REQ-69, REQ-71, REQ-79 | `listar_emendas`, `listar_lotes`, `listar_opcoes_filtro`, `obter_agregacoes`, `obter_autor`, `obter_emenda` |
| P08 | REQ-08, REQ-14, REQ-19, REQ-20, REQ-24, REQ-27, REQ-28, REQ-44, REQ-45, REQ-46, REQ-47, REQ-55, REQ-60, REQ-61, REQ-66, REQ-69, REQ-72, REQ-75 | `listar_lotes`, `listar_mudancas`, `listar_opcoes_filtro`, `obter_emenda`, `obter_linha_do_tempo`, `obter_lote` |
| P09 | REQ-06, REQ-10, REQ-12, REQ-13, REQ-14, REQ-19, REQ-27, REQ-28, REQ-44, REQ-45, REQ-46, REQ-47, REQ-48, REQ-50, REQ-55, REQ-60, REQ-69, REQ-70, REQ-73, REQ-74, REQ-82 | `listar_lotes`, `listar_mudancas`, `listar_traducoes`, `obter_lote`, `obter_status` |
| P10 | REQ-14, REQ-19, REQ-20, REQ-21, REQ-28, REQ-44, REQ-45, REQ-46, REQ-47, REQ-48, REQ-55, REQ-60, REQ-66, REQ-67, REQ-68, REQ-69, REQ-70, REQ-71, REQ-72, REQ-74, REQ-77 | `listar_emendas`, `listar_lotes`, `listar_opcoes_filtro`, `listar_traducoes`, `obter_emenda`, `obter_municipio` |
| D01 | REQ-14, REQ-16, REQ-17, REQ-18, REQ-19, REQ-28, REQ-30, REQ-44, REQ-45, REQ-46, REQ-47, REQ-65, REQ-69, REQ-72, REQ-74, REQ-84 | `listar_lotes`, `listar_traducoes`, `obter_contrato`, `obter_emenda`, `obter_municipio` |
| S01 | REQ-19, REQ-20, REQ-31, REQ-32, REQ-33, REQ-34, REQ-37, REQ-41, REQ-42, REQ-44, REQ-46, REQ-47, REQ-60, REQ-62, REQ-63, REQ-64, REQ-66, REQ-72, REQ-74, REQ-80 | `criar_assinatura`, `listar_assinaturas`, `listar_opcoes_filtro`, `obter_status` |
| S02 | REQ-31, REQ-32, REQ-41, REQ-44, REQ-47, REQ-58, REQ-74 | `criar_assinatura`, `listar_assinaturas` |
| S03 | REQ-28, REQ-32, REQ-44, REQ-45, REQ-46, REQ-47, REQ-74, REQ-84 | `listar_alertas`, `listar_assinaturas`, `listar_opcoes_filtro` |
| S04 | REQ-32, REQ-38, REQ-40, REQ-42, REQ-44, REQ-45, REQ-46, REQ-47, REQ-55, REQ-74 | `atualizar_assinatura`, `excluir_assinatura`, `listar_alertas`, `listar_assinaturas`, `listar_opcoes_filtro`, `obter_emenda`, `obter_municipio` |
| S05 | REQ-14, REQ-32, REQ-35, REQ-36, REQ-37, REQ-39, REQ-44, REQ-45, REQ-46, REQ-47, REQ-55, REQ-63, REQ-64, REQ-69, REQ-81 | `atualizar_alerta`, `listar_alertas`, `listar_assinaturas`, `listar_mudancas`, `obter_emenda`, `obter_linha_do_tempo` |
| O01 | REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-10, REQ-11, REQ-12, REQ-21, REQ-50, REQ-52, REQ-53, REQ-54, REQ-56, REQ-59, REQ-66, REQ-73, REQ-78, REQ-82 | `cli:importar`, `cli:sincronizar` |
| O02 | REQ-07, REQ-08, REQ-09, REQ-12, REQ-35, REQ-36, REQ-37, REQ-38, REQ-50, REQ-56, REQ-57, REQ-63, REQ-64, REQ-75, REQ-82 | `cli:publicar`, `listar_lotes`, `listar_mudancas` |

## Requisito → telas

| Requisito | Módulo | Telas | Também em |
| :-- | :-- | :-- | :-- |
| REQ-01 | ingestao | O01 | — |
| REQ-02 | ingestao | O01 | — |
| REQ-03 | ingestao | O01 | — |
| REQ-04 | ingestao | O01 | — |
| REQ-05 | ingestao | O01 | ADR-0001 |
| REQ-06 | ingestao | P09, O01 | ADR-0001 |
| REQ-07 | ingestao | O02 | ADR-0001, ADR-0002, ADR-0009, qualidade |
| REQ-08 | nucleo | P08, O02 | ADR-0004, ADR-0009, qualidade |
| REQ-09 | consulta | O02 | ADR-0001, ADR-0002, qualidade |
| REQ-10 | ingestao | P09, O01 | ADR-0001, qualidade |
| REQ-11 | ingestao | O01 | ADR-0002, qualidade |
| REQ-12 | ingestao | P09, O01, O02 | — |
| REQ-13 | ingestao | P03, P09 | qualidade |
| REQ-14 | consulta | P01, P02, P03, P04, P05, P06, P07, P08, P09, P10, D01, S05 | ADR-0001, ADR-0003, qualidade |
| REQ-15 | consulta | P01, P02, P03, P04, P05, P06, P07 | ADR-0007 |
| REQ-16 | consulta | P01, P03, P04, D01 | qualidade |
| REQ-17 | consulta | P03, P04, P05, D01 | qualidade |
| REQ-18 | consulta | P03, P04, P05, D01 | qualidade |
| REQ-19 | consulta | P01, P02, P03, P04, P05, P06, P07, P08, P09, P10, D01, S01 | qualidade |
| REQ-20 | consulta | P01, P02, P06, P08, P10, S01 | — |
| REQ-21 | ingestao | P02, P03, P06, P10, O01 | — |
| REQ-22 | consulta | P01, P06, P07 | — |
| REQ-23 | consulta | P04 | ADR-0006 |
| REQ-24 | nucleo | P01, P08 | ADR-0004 |
| REQ-25 | consulta | P05 | ADR-0007 |
| REQ-26 | consulta | P05 | ADR-0007 |
| REQ-27 | ingestao | P08, P09 | — |
| REQ-28 | consulta | P01, P02, P03, P04, P05, P06, P07, P08, P09, P10, D01, S03 | qualidade |
| REQ-29 | consulta | P07 | — |
| REQ-30 | consulta | D01 | ADR-0003, qualidade |
| REQ-31 | saida | S01, S02 | ADR-0005 |
| REQ-32 | saida | S01, S02, S03, S04, S05 | ADR-0005 |
| REQ-33 | saida | S01 | — |
| REQ-34 | saida | P02, S01 | — |
| REQ-35 | saida | S05, O02 | ADR-0004, ADR-0006, ADR-0009, qualidade |
| REQ-36 | saida | S05, O02 | ADR-0002, ADR-0004, qualidade |
| REQ-37 | saida | S01, S05, O02 | ADR-0004 |
| REQ-38 | saida | S04, O02 | — |
| REQ-39 | saida | S05 | — |
| REQ-40 | saida | S04 | — |
| REQ-41 | saida | S01, S02 | ADR-0005 |
| REQ-42 | saida | S01, S04 | ADR-0005 |
| REQ-43 | todos | — | ADR-0003, qualidade |
| REQ-44 | todos | P01, P02, P03, P04, P05, P06, P07, P08, P09, P10, D01, S01, S02, S03, S04, S05 | — |
| REQ-45 | todos | P01, P02, P03, P04, P05, P06, P07, P08, P09, P10, D01, S03, S04, S05 | — |
| REQ-46 | todos | P01, P02, P03, P04, P05, P06, P07, P08, P09, P10, D01, S01, S03, S04, S05 | — |
| REQ-47 | todos | P01, P02, P03, P04, P05, P06, P07, P08, P09, P10, D01, S01, S02, S03, S04, S05 | — |
| REQ-48 | todos | P01, P02, P03, P09, P10 | — |
| REQ-49 | consulta | P06 | ADR-0002, ADR-0008, qualidade |
| REQ-50 | ingestao | P09, O01, O02 | ADR-0004, qualidade |
| REQ-51 | todos | — | ADR-0003, qualidade |
| REQ-52 | ingestao | O01 | — |
| REQ-53 | ingestao | O01 | — |
| REQ-54 | ingestao | O01 | — |
| REQ-55 | consulta, saida | P07, P08, P09, P10, S04, S05 | — |
| REQ-56 | ingestao | O01, O02 | qualidade |
| REQ-57 | ingestao | O02 | — |
| REQ-58 | saida | S02 | — |
| REQ-59 | ingestao | O01 | — |
| REQ-60 | todos | P01, P02, P03, P04, P05, P06, P07, P08, P09, P10, S01 | — |
| REQ-61 | nucleo | P08 | — |
| REQ-62 | saida | S01 | — |
| REQ-63 | saida | S01, S05, O02 | — |
| REQ-64 | saida | S01, S05, O02 | — |
| REQ-65 | consulta | P02, P05, D01 | — |
| REQ-66 | ingestao | P01, P02, P03, P08, P10, S01, O01 | — |
| REQ-67 | consulta | P01, P10 | ADR-0008 |
| REQ-68 | consulta | P02, P10 | — |
| REQ-69 | nucleo | P02, P03, P04, P07, P08, P09, P10, D01, S05 | ADR-0008, qualidade |
| REQ-70 | nucleo | P09, P10 | ADR-0008 |
| REQ-71 | consulta | P06, P07, P10 | — |
| REQ-72 | consulta | P02, P06, P08, P10, D01, S01 | qualidade |
| REQ-73 | ingestao | P09, O01 | — |
| REQ-74 | todos | P01, P02, P03, P04, P05, P06, P09, P10, D01, S01, S02, S03, S04 | — |
| REQ-75 | nucleo | P08, O02 | ADR-0009 |
| REQ-76 | consulta | — | ADR-0009, qualidade |
| REQ-77 | consulta | P03, P10 | — |
| REQ-78 | ingestao | O01 | — |
| REQ-79 | consulta | P06, P07 | — |
| REQ-80 | saida | S01 | — |
| REQ-81 | saida | S05 | — |
| REQ-82 | ingestao | P09, O01, O02 | qualidade |
| REQ-83 | todos | — | qualidade |
| REQ-84 | consulta | D01, S03 | qualidade |
| REQ-85 | consulta | — | qualidade |
| REQ-86 | nucleo | — | ADR-0008 |

## Operação → telas

| Operação | Módulo | Método e caminho | Telas |
| :-- | :-- | :-- | :-- |
| `obter_status` | consulta | `GET /api/status` | P01, P03, P09, S01 |
| `listar_opcoes_filtro` | consulta | `GET /api/filtros/opcoes` | P01, P02, P03, P04, P06, P07, P08, P10, S01, S03, S04 |
| `listar_emendas` | consulta | `GET /api/emendas` | P01, P02, P06, P07, P10 |
| `obter_emenda` | consulta | `GET /api/emendas/{codigo}` | P01, P02, P03, P04, P05, P07, P08, P10, D01, S04, S05 |
| `obter_linha_do_tempo` | consulta | `GET /api/emendas/{codigo}/linha-do-tempo` | P03, P04, P08, S05 |
| `listar_favorecidos` | consulta | `GET /api/emendas/{codigo}/favorecidos` | P03, P05 |
| `obter_agregacoes` | consulta | `GET /api/agregacoes` | P01, P06, P07 |
| `obter_municipio` | consulta | `GET /api/municipios/{uf}/{municipio}` | P01, P02, P03, P10, D01, S04 |
| `obter_autor` | consulta | `GET /api/autores/{codigo}` | P03, P06, P07 |
| `listar_mudancas` | nucleo | `GET /api/mudancas` | P01, P08, P09, S05, O02 |
| `listar_traducoes` | nucleo | `GET /api/traducoes` | P03, P09, P10, D01 |
| `listar_lotes` | ingestao | `GET /api/lotes` | P01, P02, P05, P06, P07, P08, P09, P10, D01, O02 |
| `obter_lote` | ingestao | `GET /api/lotes/{lote_id}` | P03, P04, P08, P09 |
| `criar_assinatura` | saida | `POST /api/assinaturas` | S01, S02 |
| `listar_assinaturas` | saida | `GET /api/assinaturas` | S01, S02, S03, S04, S05 |
| `atualizar_assinatura` | saida | `PATCH /api/assinaturas/{assinatura_id}` | S04 |
| `excluir_assinatura` | saida | `DELETE /api/assinaturas/{assinatura_id}` | S04 |
| `listar_alertas` | saida | `GET /api/alertas` | S03, S04, S05 |
| `atualizar_alerta` | saida | `PATCH /api/alertas/{alerta_id}` | S05 |
| `obter_contrato` | consulta | `GET /openapi.json` | D01 |
| `cli:importar` | ingestao | CLI (`contratos/cli.md`) | O01 |
| `cli:lotes` | ingestao | CLI (`contratos/cli.md`) | — (agendador ou operador) |
| `cli:publicar` | ingestao | CLI (`contratos/cli.md`) | O02 |
| `cli:sincronizar` | ingestao | CLI (`contratos/cli.md`) | O01 |
| `cli:traducao` | nucleo | CLI (`contratos/cli.md`) | — (agendador ou operador) |
