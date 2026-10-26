# Trabalho 1 — Telas e arquitetura · João Vitor Chaves

Especificação individual do sistema completo **Rastro**, feita a partir do FI-01 (Formulário de Ideação do Rastro, 24/09/2026; brief visual em `docs/references/rastro-conceito.png`). As telas estão em [`telas/`](telas/) e a arquitetura em [`arquitetura/`](arquitetura/).

| Parte | Comece por | Conteúdo |
| :-- | :-- | :-- |
| (a) Interface | [telas/diretrizes.md](telas/diretrizes.md) → [telas/inventario.md](telas/inventario.md) | 17 telas (P01–P09, D01, S01–S05, O01–O02), 4 atores, 3 superfícies, mapa de navegação e 8 fluxos |
| (b) Arquitetura | [arquitetura/README.md](arquitetura/README.md) | arc42 enxuto: C4 1 e 2, 7 ADRs, 65 REQ em EARS, OpenAPI 3.1 + AsyncAPI 3.0 + CLI + modelo de dados, 5 cenários de qualidade, glossário |
| Rastreabilidade | [arquitetura/rastreabilidade.md](arquitetura/rastreabilidade.md) | Tela ↔ requisito ↔ contrato, gerada por [`verificar.py`](verificar.py) |

Mockups de referência (anexo opcional): [`telas/anexos/`](telas/anexos/), exportados do canvas "Rastro — telas" no Claude Design, com um arquivo por id de tela.

## Checklist do enunciado

**Parte (a), seção 2:**

- [x] `diretrizes.md`: público, plataforma e orientação, tom, 5 princípios verificáveis, referência visual, pt-BR e WCAG 2.2 AA.
- [x] `inventario.md`: 17 telas (≥ 10) com id, nome, ator e superfície; mapa de navegação; cobertura de atores, superfícies e funcionalidades.
- [x] Uma ficha por tela, com os 11 campos do template e os 6 estados.

**Parte (b), seção 3.3:**

- [x] `README.md`: padrão, referência e justificativa pelas 6 informações da seção 3.1.
- [x] `c4-contexto.md` e `c4-conteineres.md`.
- [x] `adr/`: 7 ADRs (≥ 3).
- [x] `requisitos.md`: REQ-01…REQ-65 em EARS, usando os cinco moldes.
- [x] `contratos/`: `openapi.yaml`, `eventos.asyncapi.yaml`, `cli.md`, `modelo-de-dados.md`.
- [x] `qualidade.md`: 5 cenários de 6 partes (persistência, API, concorrência, desempenho medido, testes).
- [x] `glossario.md`.
